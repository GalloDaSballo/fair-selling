from time import time
from brownie import *
from brownie import (
  accounts,
  interface,
  UniV3SwapSimulator,
  BalancerSwapSimulator,
  OnChainPricingMainnet,
  CowSwapDemoSeller,
  VotiumBribesProcessor,
  AuraBribesProcessor,
  OnChainPricingMainnetLenient,
  FullOnChainPricingMainnet,
  OnChainSwapMainnet
)
import eth_abi
from rich.console import Console
import pytest

console = Console()

MAX_INT = 2**256 - 1
DEV_MULTI = "0xB65cef03b9B89f99517643226d76e286ee999e77"
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
BADGER = "0x3472A5A71965499acd81997a54BBA8D852C6E53d"
CVX = "0x4e3fbd56cd56c3e72c1403e103b45db9da5b9d2b"
DAI = "0x6b175474e89094c44da98b954eedeac495271d0f"
WBTC = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
OHM="0x64aa3364F17a4D01c6f1751Fd97C2BD3D7e7f1D5"
USDC_WHALE = "0x0a59649758aa4d66e25f08dd01271e891fe52199"
BADGER_WHALE = "0xd0a7a8b98957b9cd3cfb9c0425abe44551158e9e"
CVX_WHALE = "0xcf50b810e57ac33b91dcf525c6ddd9881b139332"
DAI_WHALE = "0xe78388b4ce79068e89bf8aa7f218ef6b9ab0e9d0"
AURA = "0xC0c293ce456fF0ED870ADd98a0828Dd4d2903DBF"
AURABAL = "0x616e8BfA43F920657B3497DBf40D6b1A02D4608d"
BVE_CVX = "0xfd05D3C7fe2924020620A8bE4961bBaA747e6305"
BVE_AURA = "0xBA485b556399123261a5F9c95d413B4f93107407"
AURA_WHALE = "0x43B17088503F4CE1AED9fB302ED6BB51aD6694Fa"
BALANCER_VAULT = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
BVE_AURA_WETH_AURA_POOL_ID = "0xa3283e3470d3cd1f18c074e3f2d3965f6d62fff2000100000000000000000267"
CVX_BVECVX_POOL = "0x04c90C198b2eFF55716079bc06d7CCc4aa4d7512"
BALETH_BPT = "0x5c6Ee304399DBdB9C8Ef030aB642B10820DB8F56"
USDT = "0xdac17f958d2ee523a2206206994597c13d831ec7"
TUSD = "0x0000000000085d4780B73119b644AE5ecd22b376"
XSUSHI = "0x8798249c2E607446EfB7Ad49eC89dD1865Ff4272"

WETH_WHALE = "0xe78388b4ce79068e89bf8aa7f218ef6b9ab0e9d0"
CRV = "0xD533a949740bb3306d119CC777fa900bA034cd52"
WBTC_WHALE = "0xbf72da2bd84c5170618fbe5914b0eca9638d5eb5"

## Contracts ##
  
@pytest.fixture
def swapexecutor():
  return OnChainSwapMainnet.deploy({"from": accounts[0]})
  
@pytest.fixture
def pricerwrapper():
  univ3simulator = UniV3SwapSimulator.deploy({"from": accounts[0]})
  balancerV2Simulator = BalancerSwapSimulator.deploy({"from": accounts[0]})
  pricer = OnChainPricingMainnet.deploy(univ3simulator.address, balancerV2Simulator.address, {"from": accounts[0]})  
  return PricerWrapper.deploy(pricer.address, {"from": accounts[0]})

@pytest.fixture
def pricer():
  univ3simulator = UniV3SwapSimulator.deploy({"from": accounts[0]})
  balancerV2Simulator = BalancerSwapSimulator.deploy({"from": accounts[0]})
  return OnChainPricingMainnet.deploy(univ3simulator.address, balancerV2Simulator.address, {"from": accounts[0]})

@pytest.fixture
def pricer_legacy():
  return FullOnChainPricingMainnet.deploy({"from": accounts[0]})

@pytest.fixture
def lenient_contract():
  ## NOTE: We have 5% slippage on this one
  univ3simulator = UniV3SwapSimulator.deploy({"from": accounts[0]})
  balancerV2Simulator = BalancerSwapSimulator.deploy({"from": accounts[0]})
  c = OnChainPricingMainnetLenient.deploy(univ3simulator.address, balancerV2Simulator.address, {"from": accounts[0]})
  c.setSlippage(499, {"from": accounts.at(c.TECH_OPS(), force=True)})

  return c

@pytest.fixture
def seller(lenient_contract):
  return CowSwapDemoSeller.deploy(lenient_contract, {"from": accounts[0]})

@pytest.fixture
def processor(lenient_contract):
  return VotiumBribesProcessor.deploy(lenient_contract, {"from": accounts[0]})

@pytest.fixture
def oneE18():
  return 1000000000000000000

@pytest.fixture
def xsushi():
  return interface.ERC20(XSUSHI)

@pytest.fixture
def tusd():
  return interface.ERC20(TUSD)

@pytest.fixture
def usdt():
  return interface.ERC20(USDT)

@pytest.fixture
def balethbpt():
  return interface.ERC20(BALETH_BPT)

@pytest.fixture
def aurabal():
  return interface.ERC20(AURABAL)

@pytest.fixture
def ohm():
  return interface.ERC20(OHM)

@pytest.fixture
def wbtc():
  return interface.ERC20(WBTC)
  
@pytest.fixture
def aura_processor(pricer):
    return AuraBribesProcessor.deploy(pricer, {"from": accounts[0]})

@pytest.fixture
def balancer_vault():
  return interface.IBalancerVault(BALANCER_VAULT)

@pytest.fixture
def cvx_bvecvx_pool():
  return interface.ICurvePool(CVX_BVECVX_POOL)

@pytest.fixture
def crv():
  return interface.ERC20(CRV)

@pytest.fixture
def usdc():
  return interface.ERC20(USDC)

@pytest.fixture
def weth():
  return interface.ERC20(WETH)

@pytest.fixture
def badger():
  return interface.ERC20(BADGER)

@pytest.fixture
def cvx():
  return interface.ERC20(CVX)
  
@pytest.fixture
def dai():
  return interface.ERC20(DAI)

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
def weth_whale():
  return accounts.at(WETH_WHALE, force=True)

@pytest.fixture
def wbtc_whale():
  return accounts.at(WBTC_WHALE, force=True)

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
def setup_processor(processor, strategy, usdc, usdc_whale, badger, cvx, badger_whale, cvx_whale, bve_cvx):
  ## Do the donation / Transfer Bribes
  usdc.transfer(processor, 6e10, {"from": usdc_whale})

  ## Also transfer some BADGER and CVX for later processing
  cvx.transfer(processor, 3e22, {"from": cvx_whale})

  badger.transfer(processor, 6e22, {"from": badger_whale})

  ## Also approve contract access from bveCVX
  interface.ISettV4(bve_cvx).approveContractAccess(processor, {"from": accounts.at(interface.ISettV4(bve_cvx).governance(), force=True)})

  ## Notify new round, 28 days before anyone can unlock tokens
  processor.notifyNewRound({"from": strategy})

  return processor


@pytest.fixture
def setup_aura_processor(aura_processor, aura_strategy, usdc, usdc_whale, badger, aura, badger_whale, aura_whale, bve_aura):
  ## Do the donation / Transfer Bribes
  usdc.transfer(aura_processor, 6e10, {"from": usdc_whale})

  ## Also transfer some BADGER and Aura for later processing
  aura.transfer(aura_processor, 1e18, {"from": aura_whale})

  badger.transfer(aura_processor, 6e22, {"from": badger_whale})

  ## Notify new round, 28 days before anyone can unlock tokens
  aura_processor.notifyNewRound({"from": aura_strategy})

  return aura_processor

@pytest.fixture
def add_aura_liquidity(balancer_vault, aura_whale, aura, bve_aura):
  # Add extra liquidity to meta stable pool to improve pricing
  liquidity_amount = int(6000e18)
  account = {'from': aura_whale}
  bve_aura.approve(BALANCER_VAULT, MAX_INT, account)
  aura.approve(BALANCER_VAULT, MAX_INT, account)
  aura.approve(BVE_AURA, MAX_INT, account)
  interface.IVault(BVE_AURA).deposit(liquidity_amount, account)
  liquidity_amount = bve_aura.balanceOf(AURA_WHALE)
  join_kind = 1
  balances = [liquidity_amount, 0, liquidity_amount]
  abi = ['uint256', 'uint256[]', 'uint256']
  user_data = [join_kind, balances, 0]
  user_data_encoded = eth_abi.encode_abi(abi, user_data)
  join_request = ([BVE_AURA, WETH, AURA], balances, user_data_encoded, False)
  balancer_vault.joinPool(BVE_AURA_WETH_AURA_POOL_ID, AURA_WHALE, AURA_WHALE, join_request, account)  
      
@pytest.fixture
def make_aura_pool_unprofitable(balancer_vault, aura_whale, add_aura_liquidity):
  # Buy BVE_AURA to imbalance pool
  pool_purchase_amount = balancer_vault.getPoolTokens(BVE_AURA_WETH_AURA_POOL_ID)[1][0]
  swap = (BVE_AURA_WETH_AURA_POOL_ID, 0, AURA, BVE_AURA, pool_purchase_amount // 4, 0) ## Can only buy up to 30% of pool
  fund = (AURA_WHALE, False, AURA_WHALE, False)
  balancer_vault.swap(swap, fund, 1, MAX_INT, {'from': aura_whale})

@pytest.fixture
def make_aura_pool_profitable(balancer_vault, aura_whale, add_aura_liquidity, bve_aura):
  # Buy AURA to imbalance pool
  pool_purchase_amount = balancer_vault.getPoolTokens(BVE_AURA_WETH_AURA_POOL_ID)[1][2]
  interface.IVault(BVE_AURA).deposit(pool_purchase_amount, {'from': aura_whale})
  deposit_amount = bve_aura.balanceOf(AURA_WHALE) // 4 ## Can only buy up to 30% of pool
  swap = (BVE_AURA_WETH_AURA_POOL_ID, 0, BVE_AURA, AURA, deposit_amount, 0)
  fund = (AURA_WHALE, False, AURA_WHALE, False) 
  balancer_vault.swap(swap, fund, 0, MAX_INT, {'from': aura_whale})

@pytest.fixture
def make_cvx_pool_profitable(cvx, bve_cvx, cvx_bvecvx_pool, cvx_whale):
  cvx_balance = cvx.balanceOf(CVX_BVECVX_POOL)
  whale = {'from': cvx_whale}
  cvx.approve(BVE_CVX, MAX_INT, whale)
  interface.IVault(BVE_CVX).deposit(cvx_balance, whale)
  deposit_amount = bve_cvx.balanceOf(CVX_WHALE)
  bve_cvx.approve(CVX_BVECVX_POOL, MAX_INT, whale)
  cvx_bvecvx_pool.exchange(1, 0, deposit_amount, 0, whale)

@pytest.fixture
def make_cvx_pool_unprofitable(cvx, bve_cvx, cvx_bvecvx_pool, cvx_whale):
  bvecvx_balance = bve_cvx.balanceOf(CVX_BVECVX_POOL)
  cvx.approve(CVX_BVECVX_POOL, MAX_INT, {'from': cvx_whale})
  cvx_bvecvx_pool.exchange(0, 1, bvecvx_balance, 0, {'from': cvx_whale})

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