from brownie import (
  OnChainPricingMainnet,
  CowSwapDemoSeller,
  VotiumBribesProcessor,
  interface,
  a,
  accounts
)
from rich.console import Console
import pytest

console = Console()

DEV_MULTI = "0xB65cef03b9B89f99517643226d76e286ee999e77"
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
USDC_WHALE = "0x0a59649758aa4d66e25f08dd01271e891fe52199"
BADGER_WHALE = "0xd0a7a8b98957b9cd3cfb9c0425abe44551158e9e"
CVX_WHALE = "0xcf50b810e57ac33b91dcf525c6ddd9881b139332"

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
def usdc():
  return interface.ERC20(USDC)

@pytest.fixture
def weth():
  return interface.ERC20(WETH)

@pytest.fixture
def badger():
  return interface.ERC20(WETH)

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
def manager(seller):
  return accounts.at(seller.manager(), force=True)

@pytest.fixture
def admin(processor):
  return accounts.at('0x576cD258835C529B54722F84Bb7d4170aA932C64', force=True)

@pytest.fixture
def strategy(processor):
  return accounts.at(processor.STRATEGY(), force=True)

@pytest.fixture
def bve_cvx(processor):
  return interface.ERC20(processor.BVE_CVX())

@pytest.fixture
def setup_processor(processor, strategy, usdc, usdc_whale, badger, cvx, badger_whale, cvx_whale, bve_cvx, rewards, admin):
  ## Do the donation / Transfer Bribes
  usdc.transfer(processor, 6e10, {"from": usdc_whale})

  ## Also transfer some BADGER and CVX for later processing
  cvx.transfer(processor, 3e22, {"from": cvx_whale})

  badger.transfer(processor, 6e22, {"from": badger_whale})

  ## Also approve contract access from bveCVX
  interface.ISettV4(bve_cvx).approveContractAccess(processor, {"from": accounts.at(interface.ISettV4(bve_cvx).governance(), force=True)})

  ## Give strat permissions to set emissions
  MANAGER_ROLE = rewards.MANAGER_ROLE()
  rewards.grantRole(MANAGER_ROLE, processor, {'from': admin})

  ## Notify new round, 10 days before anyone can unlock tokens
  processor.notifyNewRound({"from": strategy})

  return processor

@pytest.fixture
def badger(processor):
  return interface.ERC20(processor.BADGER())

@pytest.fixture
def cvx(processor):
  return interface.ERC20(processor.CVX())



@pytest.fixture
def settlement(processor):
  return interface.ICowSettlement(processor.SETTLEMENT())

@pytest.fixture
def rewards(processor):
  return interface.IRewardsLogger(processor.REWARDS_LOGGER())

## Forces reset before each test
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass
