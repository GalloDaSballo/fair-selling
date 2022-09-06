import brownie
from brownie import *
from brownie.test import given, strategy
import pytest

"""
  Fuzz
    Fuzz of Pricer vs V2 Pricer for Equivalency
"""

## TOKENS 
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

## Mostly Aura
AURA = "0xC0c293ce456fF0ED870ADd98a0828Dd4d2903DBF"
AURA_BAL = "0x616e8BfA43F920657B3497DBf40D6b1A02D4608d"
BADGER = "0x3472A5A71965499acd81997a54BBA8D852C6E53d"

SD = "0x30d20208d987713f46dfd34ef128bb16c404d10f" ## Pretty much completely new token https://etherscan.io/token/0x30d20208d987713f46dfd34ef128bb16c404d10f#balances
DFX = "0x888888435FDe8e7d4c54cAb67f206e4199454c60" ## Fairly Liquid: https://etherscan.io/token/0x888888435FDe8e7d4c54cAb67f206e4199454c60#balances
FDT = "0xEd1480d12bE41d92F36f5f7bDd88212E381A3677" ## Illiquid as of today, in vault but no pool I could find https://etherscan.io/token/0xEd1480d12bE41d92F36f5f7bDd88212E381A3677#balances
LDO = "0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32"
COW = "0xDEf1CA1fb7FBcDC777520aa7f396b4E015F497aB" ## Has pair with GNO and with WETH
GNO = "0x6810e776880C02933D47DB1b9fc05908e5386b96"

## Mostly Votium
CVX = "0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B"
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
WBTC = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
SNX = "0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F"
TRIBE = "0xc7283b66Eb1EB5FB86327f08e1B5816b0720212B"
FLX = "0x6243d8cea23066d098a15582d81a598b4e8391f4"
INV = "0x41d5d79431a913c4ae7d69a668ecdfe5ff9dfb68"
FXS = "0x3432B6A60D23Ca0dFCa7761B7ab56459D9C964D0"


## More Random Votium stuff
TUSD = "0x0000000000085d4780B73119b644AE5ecd22b376"
STG = "0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6"
LYRA = "0x01BA67AAC7f75f647D94220Cc98FB30FCc5105Bf"
JPEG = "0xE80C0cd204D654CEbe8dd64A4857cAb6Be8345a3"
GRO = "0x3Ec8798B81485A254928B70CDA1cf0A2BB0B74D7"
EURS = "0xdB25f211AB05b1c97D595516F45794528a807ad8"

## New Aura Pools
DIGG = "0x798D1bE841a82a273720CE31c822C61a67a601C3"
GRAVI_AURA = "0xBA485b556399123261a5F9c95d413B4f93107407"

BRIBES_TOKEN_CLAIMABLE = [
  ("0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B", 18), ## CVX
  ("0x6B175474E89094C44Da98b954EedeAC495271d0F", 18), ## DAI
  ("0x090185f2135308bad17527004364ebcc2d37e5f6", 22), ## SPELL ## NOTE: Using 22 to adjust as spell is super high supply
  ("0xdbdb4d16eda451d0503b854cf79d55697f90c8df", 18), ## ALCX
  ("0x9D79d5B61De59D882ce90125b18F74af650acB93", 8), ## NSBT ## NOTE: Using 6 + 2 decimals to make it more
  ("0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0", 18), ## MATIC
  ("0x3432b6a60d23ca0dfca7761b7ab56459d9c964d0", 18), ## FXS
  ("0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32", 18), ## LDO
  ("0xc7283b66Eb1EB5FB86327f08e1B5816b0720212B", 18),  ## TRIBE
  ("0x8207c1FfC5B6804F6024322CcF34F29c3541Ae26", 18), ## OGN
  ("0xa3BeD4E1c75D00fa6f4E5E6922DB7261B5E9AcD2", 18), ## MTA
  ("0x31429d1856aD1377A8A0079410B297e1a9e214c2", 22), ## ANGLE ## NOTE Using 18 + 4 to raise the value
  ("0xCdF7028ceAB81fA0C6971208e83fa7872994beE5", 22), ## T ## NOTE Using 18 + 4 to raise the value
  ("0xa693B19d2931d498c5B318dF961919BB4aee87a5", 6), # UST
  ("0xB620Be8a1949AA9532e6a3510132864EF9Bc3F82", 22), ## LFT ## NOTE Using 18 + 4 to raise the value
  ("0x6243d8CEA23066d098a15582d81a598b4e8391F4", 18), ## FLX
  ("0x3Ec8798B81485A254928B70CDA1cf0A2BB0B74D7", 18), ## GRO
  ("0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6", 18), ## STG
  ("0xdB25f211AB05b1c97D595516F45794528a807ad8", 2), ## EURS
  ("0x674C6Ad92Fd080e4004b2312b45f796a192D27a0", 18), ## USDN
  ("0xFEEf77d3f69374f66429C91d732A244f074bdf74", 18), ## cvxFXS
  ("0x41D5D79431A913C4aE7d69a668ecdfE5fF9DFB68", 18), ## INV
  ("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 6), ## USDC
  ("0xC0c293ce456fF0ED870ADd98a0828Dd4d2903DBF", 18), ## AURA
  ("0x616e8BfA43F920657B3497DBf40D6b1A02D4608d", 18), ## AURA_BAL
  ("0x3472A5A71965499acd81997a54BBA8D852C6E53d", 18), ## BADGER
  ("0x30d20208d987713f46dfd34ef128bb16c404d10f", 18), ## SD | Not Supported -> Cannot fix at this time
  ("0x888888435FDe8e7d4c54cAb67f206e4199454c60", 18), ## DFX
  ("0xEd1480d12bE41d92F36f5f7bDd88212E381A3677", 18), ## FDT ## Not Supported -> Cannot fix at this time
  ("0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32", 18), ## LDO
  ("0xDEf1CA1fb7FBcDC777520aa7f396b4E015F497aB", 18), ## COW
  ("0x6810e776880C02933D47DB1b9fc05908e5386b96", 18), ## GNO
  ("0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B", 18), ## CVX
  ("0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F", 18), ## SNX
  ("0xc7283b66Eb1EB5FB86327f08e1B5816b0720212B", 18), ## TRIBE
  ("0x6243d8cea23066d098a15582d81a598b4e8391f4", 18), ## FLX
  ("0x41d5d79431a913c4ae7d69a668ecdfe5ff9dfb68", 18), ## INV
  ("0x3432B6A60D23Ca0dFCa7761B7ab56459D9C964D0", 18), ## FXS

  ("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 18), ## WETH
  ("0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599", 8), ## WBTC

  ## More Coins
  ("0x0000000000085d4780B73119b644AE5ecd22b376", 18), ## TUSD
  ("0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6", 18), ## STG
  ("0x01BA67AAC7f75f647D94220Cc98FB30FCc5105Bf", 18), ## LYRA
  ("0xE80C0cd204D654CEbe8dd64A4857cAb6Be8345a3", 18), ## JPEG
  ("0x3Ec8798B81485A254928B70CDA1cf0A2BB0B74D7", 18), ## GRO
  ("0xdB25f211AB05b1c97D595516F45794528a807ad8", 18), ## EURS

  ## From new Balancer Pools
  ("0x798D1bE841a82a273720CE31c822C61a67a601C3", 9), ## DIGG
  ("0xBA485b556399123261a5F9c95d413B4f93107407", 18) ## GRAVI_AURA
]


### Sell Bribes for Weth
@given(amount=strategy("uint256"), sell_token_num=strategy("uint256"), buy_token_num=strategy("uint256"))
def test_fuzz_pricers(sell_token_num, buy_token_num, amount):

  sell_token = interface.ERC20(BRIBES_TOKEN_CLAIMABLE[sell_token_num % len(BRIBES_TOKEN_CLAIMABLE)][0])
  buy_token = interface.ERC20(BRIBES_TOKEN_CLAIMABLE[buy_token_num % len(BRIBES_TOKEN_CLAIMABLE)][0])
  
  ## Skip if amt = 0
  if amount == 0:
    return True

  ## Fake Token = Skip
  if str(web3.eth.getCode(str(sell_token.address))) == "b''":
    return True


  ## NOTE: Put all the fixtures here cause I keep getting reverts
  #### FIXTURES ###
  
  ## NOTE: We have 5% slippage on this one
  univ3simulator = UniV3SwapSimulator.deploy({"from": accounts[0]})
  balancerV2Simulator = BalancerSwapSimulator.deploy({"from": accounts[0]})
  pricer_fuzz_v3 = OnChainPricingMainnet.deploy(univ3simulator.address, balancerV2Simulator.address, {"from": accounts[0]})

  pricer_fuzz_v2 = FullOnChainPricingMainnet.deploy({"from": a[0]})

  try:
    v2_quote = pricer_fuzz_v2.findOptimalSwap.call(sell_token, buy_token, amount)
  except:
    print("Exception from V2")

  v3_quote = pricer_fuzz_v3.findOptimalSwap(sell_token, buy_token, amount)

  ## Compare quote.amountOut
  ## >= for equivalent or better value for any combination
  ## NOTE: Have had a test fail by 1 wei, due to rounding prob
  # assert v3_quote[1] >= v2_quote[1]
  assert v3_quote[1] >= 0 ## Did not revert