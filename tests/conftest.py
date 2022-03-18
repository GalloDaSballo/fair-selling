from time import time
from brownie import *
from rich.console import Console
import pytest

console = Console()

DEV_MULTI = "0xB65cef03b9B89f99517643226d76e286ee999e77"
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

## Contracts ##
@pytest.fixture
def pricer():
  return OnChainPricingMainnet.deploy({"from": a[0]})

@pytest.fixture
def seller(pricer):
  return CowSwapDemoSeller.deploy(pricer, {"from": a[0]})

@pytest.fixture
def usdc():
  return interface.ERC20(USDC)

@pytest.fixture
def weth():
  return interface.ERC20(WETH)

@pytest.fixture
def manager(seller):
  return accounts.at(seller.manager(), force=True)

## Forces reset before each test
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass