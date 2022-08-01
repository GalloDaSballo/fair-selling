import pytest
from brownie import *

## NOTE: Removed as we're testing with 1e18
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"


## Mostly Aura
AURA = "0xC0c293ce456fF0ED870ADd98a0828Dd4d2903DBF"
AURA_BAL = "0x616e8BfA43F920657B3497DBf40D6b1A02D4608d"

SD = "0x30d20208d987713f46dfd34ef128bb16c404d10f" ## Pretty much completely new token https://etherscan.io/token/0x30d20208d987713f46dfd34ef128bb16c404d10f#balances

DFX = "0x888888435FDe8e7d4c54cAb67f206e4199454c60" ## Fairly Liquid: https://etherscan.io/token/0x888888435FDe8e7d4c54cAb67f206e4199454c60#balances

FDT = "0xEd1480d12bE41d92F36f5f7bDd88212E381A3677" ## Illiquid as of today, in vault but no pool I could find https://etherscan.io/token/0xEd1480d12bE41d92F36f5f7bDd88212E381A3677#balances

LDO = "0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32"
COW = "0xDEf1CA1fb7FBcDC777520aa7f396b4E015F497aB" ## Has pair with GNO and with WETH
GNO = "0x6810e776880C02933D47DB1b9fc05908e5386b96"

## Mostly Votium
CVX = "0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B"
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
SNX = "0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F"
TRIBE = "0xc7283b66Eb1EB5FB86327f08e1B5816b0720212B"
FLX = "0x6243d8cea23066d098a15582d81a598b4e8391f4"
INV = "0x41d5d79431a913c4ae7d69a668ecdfe5ff9dfb68"
FXS = "0x3432B6A60D23Ca0dFCa7761B7ab56459D9C964D0"


TOKENS_18_DECIMALS = [
  AURA,
  AURA_BAL, ## Not Supported -> To FIX TODO ADD BAL POOL
  #SD, ## Not Supported -> Cannot fix at this time
  DFX,
  #FDT, ## Not Supported -> Cannot fix at this time
  LDO,
  COW,
  GNO,
  CVX,
  SNX,
  TRIBE,
  FLX,
  INV,
  FXS
]

@pytest.mark.parametrize("token", TOKENS_18_DECIMALS)
def test_are_bribes_supported(pricerwrapper, token):
  pricer = pricerwrapper 
  """
    Given a bunch of tokens historically used as bribes, verifies the pricer will return non-zero value
    We sell all to WETH which is pretty realistic
  """

  ## 1e18 for everything, even with insane slippage will still return non-zero which is sufficient at this time
  AMOUNT = 1e18
  
  res = pricer.isPairSupported(token, WETH, AMOUNT)
  assert res
  
  quote = pricer.findOptimalSwap.call(token, WETH, AMOUNT)
  assert quote[1][1] > 0

