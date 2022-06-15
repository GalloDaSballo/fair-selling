from time import time
from brownie import *
from rich.console import Console
import pytest

console = Console()

DEV_MULTI = "0xB65cef03b9B89f99517643226d76e286ee999e77"
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
BADGER = "0x3472A5A71965499acd81997a54BBA8D852C6E53d"
CVX = "0x4e3fbd56cd56c3e72c1403e103b45db9da5b9d2b"
DAI = "0x6b175474e89094c44da98b954eedeac495271d0f"
WBTC = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
USDC_WHALE = "0x0a59649758aa4d66e25f08dd01271e891fe52199"
BADGER_WHALE = "0xd0a7a8b98957b9cd3cfb9c0425abe44551158e9e"
CVX_WHALE = "0xcf50b810e57ac33b91dcf525c6ddd9881b139332"
DAI_WHALE = "0xe78388b4ce79068e89bf8aa7f218ef6b9ab0e9d0"
WETH_WHALE = "0xe78388b4ce79068e89bf8aa7f218ef6b9ab0e9d0"
CRV = "0xD533a949740bb3306d119CC777fa900bA034cd52"
WBTC_WHALE = "0xe78388b4ce79068e89bf8aa7f218ef6b9ab0e9d0"

## Contracts ##
@pytest.fixture
def swapexecutor():
  return OnChainSwapMainnet.deploy({"from": a[0]})
  
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
def oneE18():
  return 1000000000000000000

@pytest.fixture
def wbtc():
  return interface.ERC20(WBTC)
  
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
def manager(seller):
  return accounts.at(seller.manager(), force=True)

@pytest.fixture
def strategy(processor):
  return accounts.at(processor.STRATEGY(), force=True)

@pytest.fixture
def bve_cvx(processor):
  return interface.ERC20(processor.BVE_CVX())

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