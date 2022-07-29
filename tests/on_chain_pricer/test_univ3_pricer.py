import brownie
from brownie import *
import pytest   

"""
    test case for COW token to fix reported issue https://github.com/GalloDaSballo/fair-selling/issues/26
"""
def test_get_univ3_price_cow(oneE18, weth, usdc_whale, pricer):  
  ## 1e18
  token = "0xdef1ca1fb7fbcdc777520aa7f396b4e015f497ab"
  sell_count = 12209
  sell_amount = sell_count * oneE18
    
  ## minimum quote for COW in ETH(1e18)
  quoteInV2 = pricer.getUniPrice(pricer.UNIV2_ROUTER(), weth.address, token, sell_amount)
  assert quoteInV2 == 0
  p = sell_count * 0.00005 * oneE18   
  quote = pricer.simulateUniV3Swap(weth.address, sell_amount, token, 10000, False, "0xFCfDFC98062d13a11cec48c44E4613eB26a34293")
  assert quote >= p 
  
  ## check against quoter
  quoterP = interface.IV3Quoter(pricer.UNIV3_QUOTER()).quoteExactInputSingle.call(token, weth.address, 10000, sell_amount, 0, {'from': usdc_whale.address})
  assert quoterP == quote

"""
    getUniV3Price quote for token A swapped to token B directly: A - > B
"""
def test_get_univ3_price_in_range(oneE18, weth, usdc, usdc_whale, pricer):  
  ## 1e18
  sell_count = 1
  sell_amount = sell_count * oneE18
    
  ## minimum quote for ETH in USDC(1e6) ## Rip ETH price
  p = sell_count * 900 * 1000000 
  quoteInRange = pricer.checkUniV3InRangeLiquidity(usdc.address, weth.address, sell_amount, 500, False, "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640")
  assert quoteInRange[1] >= p
  
  ## check against quoter
  quoterP = interface.IV3Quoter(pricer.UNIV3_QUOTER()).quoteExactInputSingle.call(weth.address, usdc.address, 500, sell_amount, 0, {'from': usdc_whale.address})
  assert quoterP == quoteInRange[1]

"""
    getUniV3Price quote for token A swapped to token B directly: A - > B
"""
def test_get_univ3_price_cross_tick(oneE18, weth, usdc, usdc_whale, pricer):  
  ## 1e18
  sell_count = 2000
  sell_amount = sell_count * oneE18
    
  ## minimum quote for ETH in USDC(1e6) ## Rip ETH price
  p = sell_count * 900 * 1000000 
  quoteCrossTicks = pricer.simulateUniV3Swap(usdc.address, sell_amount, weth.address, 500, False, "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640")
  assert quoteCrossTicks >= p
  
  ## check against quoter
  quoterP = interface.IV3Quoter(pricer.UNIV3_QUOTER()).quoteExactInputSingle.call(weth.address, usdc.address, 500, sell_amount, 0, {'from': usdc_whale.address})
  assert (abs(quoterP - quoteCrossTicks) / quoterP) <= 0.0015 ## thousandsth in quote diff for a millions-dollar-worth swap

"""
    getUniV3PriceWithConnector quote for token A swapped to token B with connector token C: A -> C -> B
"""
def test_get_univ3_price_with_connector(oneE18, wbtc, usdc, weth, dai, pricer):  
  ## 1e8
  sell_amount = 100 * 100000000
  
  ## minimum quote for WBTC in USDC(1e6)
  p = 100 * 15000 * 1000000
  assert pricer.sortUniV3Pools(wbtc.address, sell_amount, usdc.address)[0] >= p
  
  quoteWithConnector = pricer.getUniV3PriceWithConnector(wbtc.address, sell_amount, usdc.address, weth.address)

  ## min price 
  assert quoteWithConnector >= p  
  
  ## test case for stablecoin DAI -> USDC
  daiQuoteWithConnector = pricer.getUniV3PriceWithConnector(dai.address, 10000 * oneE18, usdc.address, weth.address)
  assert daiQuoteWithConnector >= 10000 * 0.99 * 1000000
 
