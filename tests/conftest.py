from time import time
from brownie import *
from rich.console import Console
import pytest

console = Console()

MAX_INT = 2**256 - 1
DEV_MULTI = "0xB65cef03b9B89f99517643226d76e286ee999e77"
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
AURA = "0xC0c293ce456fF0ED870ADd98a0828Dd4d2903DBF"
BVE_AURA = "0xBA485b556399123261a5F9c95d413B4f93107407"
USDC_WHALE = "0x0a59649758aa4d66e25f08dd01271e891fe52199"
BADGER_WHALE = "0xd0a7a8b98957b9cd3cfb9c0425abe44551158e9e"
CVX_WHALE = "0xcf50b810e57ac33b91dcf525c6ddd9881b139332"
AURA_WHALE = "0x43B17088503F4CE1AED9fB302ED6BB51aD6694Fa"
BALANCER_VAULT = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
AURA_POOL_ID = "0x9f40f06ea32304dc777ecc661609fb6b0c5daf4a00020000000000000000026a"


## Contracts ##
@pytest.fixture
def pricer():
  return OnChainPricingMainnet.deploy({"from": a[0]})

@pytest.fixture
def seller(pricer):
  return CowSwapDemoSeller.deploy(pricer, {"from": a[0]})

@pytest.fixture
def processor(pricer):
  return VotiumBribesProcessor.deploy(pricer, {"from": a[0]})

@pytest.fixture
def aura_processor(pricer):
    return AuraBribesProcessor.deploy(pricer, {"from": a[0]})

@pytest.fixture
def balancer_vault():
  return interface.IBalancerVault(BALANCER_VAULT)

@pytest.fixture
def usdc():
  return interface.ERC20(USDC)

@pytest.fixture
def weth():
  return interface.ERC20(WETH)

@pytest.fixture
def badger():
  return interface.ERC20(WETH)

@pytest.fixture
def aura():
  return interface.ERC20(AURA)

@pytest.fixture
def usdc_whale():
  return accounts.at(USDC_WHALE, force=True)

@pytest.fixture
def badger_whale():
  return accounts.at(BADGER_WHALE, force=True)

@pytest.fixture
def cvx_whale():
  return accounts.at(CVX_WHALE, force=True)

@pytest.fixture
def aura_whale():
  return accounts.at(AURA_WHALE, force=True)

@pytest.fixture
def manager(seller):
  return accounts.at(seller.manager(), force=True)

@pytest.fixture
def strategy(processor):
  return accounts.at(processor.STRATEGY(), force=True)

@pytest.fixture
def aura_strategy(aura_processor):
  return accounts.at(aura_processor.STRATEGY(), force=True)

@pytest.fixture
def bve_cvx(processor):
  return interface.ERC20(processor.BVE_CVX())

@pytest.fixture
def bve_aura(aura_processor):
  return interface.ERC20(aura_processor.BVE_AURA())

@pytest.fixture
def bve_aura_vault():
  return interface.IVault(BVE_AURA)

@pytest.fixture
def setup_processor(processor, strategy, usdc, usdc_whale, badger, cvx, badger_whale, cvx_whale, bve_cvx):
  ## Do the donation / Transfer Bribes
  usdc.transfer(processor, 6e10, {"from": usdc_whale})

  ## Also transfer some BADGER and CVX for later processing
  cvx.transfer(processor, 3e22, {"from": cvx_whale})

  badger.transfer(processor, 6e22, {"from": badger_whale})

  ## Also approve contract access from bveCVX
  interface.ISettV4(bve_cvx).approveContractAccess(processor, {"from": accounts.at(interface.ISettV4(bve_cvx).governance(), force=True)})


  ## Notify new round, 28 days before anyone can unlock tokens
  processor.notifyNewRound({"from": strategy})

  return processor


@pytest.fixture
def setup_aura_processor(aura_processor, aura_strategy, usdc, usdc_whale, badger, aura, badger_whale, aura_whale, bve_aura):
  ## Do the donation / Transfer Bribes
  usdc.transfer(aura_processor, 6e10, {"from": usdc_whale})

  ## Also transfer some BADGER and Aura for later processing
  aura.transfer(aura_processor, 3e22, {"from": aura_whale})

  badger.transfer(aura_processor, 6e22, {"from": badger_whale})

  ## Also approve contract access from bveaura
  #interface.ISettV4(bve_aura_sett.approveContractAccess(aura_processor, {"from": accounts.at(interface.ISettV4(bve_aura).governance(), force=True)})


  ## Notify new round, 28 days before anyone can unlock tokens
  aura_processor.notifyNewRound({"from": aura_strategy})

  return aura_processor


@pytest.fixture
def make_aura_pool_unprofitable(balancer_vault, aura_whale, aura, bve_aura_vault, bve_aura):
  # Buy AURA to make pool unprofitable

  amount = 5e18
  bve_aura.approve(BALANCER_VAULT, MAX_INT, {'from': aura_whale})

  aura.approve(BVE_AURA, MAX_INT, {'from': aura_whale})
  bve_aura_vault.deposit(amount, {'from': aura_whale})

  swap = (AURA_POOL_ID, 0, BVE_AURA, AURA, amount, 0)
  fund = (AURA_WHALE, False, AURA_WHALE, False)
  balancer_vault.swap(swap, fund, 0, MAX_INT, {'from': aura_whale})

@pytest.fixture
def make_aura_pool_profitable(balancer_vault, aura_whale, aura):
  # Buy bveAURA to make pool profitable

  amount = 5e18
  aura.approve(BALANCER_VAULT, MAX_INT, {'from': aura_whale})
  swap = (AURA_POOL_ID, 0, AURA, BVE_AURA, amount, 0)
  fund = (AURA_WHALE, False, AURA_WHALE, False) 
  balancer_vault.swap(swap, fund, 0, MAX_INT, {'from': aura_whale})


@pytest.fixture
def badger(processor):
  return interface.ERC20(processor.BADGER())

@pytest.fixture
def cvx(processor):
  return interface.ERC20(processor.CVX())



@pytest.fixture
def settlement(processor):
  return interface.ICowSettlement(processor.SETTLEMENT())

## Forces reset before each test
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass