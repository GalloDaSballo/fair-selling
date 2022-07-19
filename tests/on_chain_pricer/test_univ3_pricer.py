import brownie
from brownie import *
import pytest

"""
    getUniV3Price quote for token A swapped to token B directly: A - > B
"""
def test_get_univ3_price_in_range(oneE18, weth, usdc, usdc_whale, pricer):  
  ## 1e18
  sell_amount = 1 * oneE18
    
  ## minimum quote for ETH in USDC(1e6) ## Rip ETH price
  p = 1 * 900 * 1000000  
  quote = pricer.sortUniV3Pools(weth.address, sell_amount, usdc.address)
  print(quote)
  assert quote[0] >= p 
  quoteInRange = pricer.checkUniV3InRangeLiquidity(weth.address, usdc.address, sell_amount, quote[1], 100)
  print(quoteInRange)
  assert quote[0] == quoteInRange[1]
  
  ## check against quoter
  quoterP = interface.IV3Quoter(pricer.UNIV3_QUOTER()).quoteExactInputSingle(weth.address, usdc.address, quote[1], sell_amount, 0, {'from': usdc_whale.address}).return_value
  print(quoterP)
  assert quoterP == quote[0]
  
  ## fee-0.05% pool is the chosen one among (0.05%, 0.3%, 1%)!
  assert quote[1] == 500 

"""
    getUniV3Price quote for token A swapped to token B directly: A - > B
"""
def test_get_univ3_price_cross_tick(oneE18, weth, usdc, usdc_whale, pricer):  
  ## 1e18
  sell_count = 2000
  sell_amount = sell_count * oneE18
    
  ## minimum quote for ETH in USDC(1e6) ## Rip ETH price
  p = sell_count * 900 * 1000000  
  quote = pricer.sortUniV3Pools(weth.address, sell_amount, usdc.address)
  print(quote)
  assert quote[0] >= p 
  quoteCrossTicks = pricer.simulateUniV3Swap(weth.address, sell_amount, usdc.address, quote[1], 100)
  print(quoteCrossTicks)
  assert quote[0] == quoteCrossTicks
  
  ## check against quoter
  slot0 = interface.IUniswapV3Pool("0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640").slot0()
  currentPX96 = slot0[0]
  limitP = currentPX96 * (100 + 10000) / 10000
  quoterP = interface.IV3Quoter(pricer.UNIV3_QUOTER()).quoteExactInputSingle(weth.address, usdc.address, quote[1], sell_amount, limitP, {'from': usdc_whale.address}).return_value
  print(quoterP)
  assert (abs(quoterP - quote[0]) / quoterP) <= 0.0003 ## tens of thousandsth in quote error for a millions-dollar-worth swap
  
  ## fee-0.05% pool is the chosen one among (0.05%, 0.3%, 1%)!
  assert quote[1] == 500  

"""
    getUniV3PriceWithConnector quote for token A swapped to token B with connector token C: A -> C -> B
"""
def test_get_univ3_price_with_connector(oneE18, wbtc, usdc, weth, pricer):  
  ## 1e8
  sell_amount = 100 * 100000000
  
  ## minimum quote for WBTC in USDC(1e6)
  p = 100 * 15000 * 1000000  
  quoteWithConnector = pricer.getUniV3PriceWithConnector(wbtc.address, sell_amount, usdc.address, weth.address)

  ## min price 
  assert quoteWithConnector >= p  

"""
    getUniV3PriceWithConnector quote for stablecoin A swapped to stablecoin B with connector token C: A -> C -> B
"""
def test_get_univ3_price_with_connector_stablecoin(oneE18, dai, usdc, weth, pricer):  
  ## 1e18
  sell_amount = 10000 * oneE18

  ## minimum quote for DAI in USDC(1e6)
  p = 10000 * 0.99 * 1000000  
  quoteWithConnector = pricer.getUniV3PriceWithConnector(dai.address, sell_amount, usdc.address, weth.address)

  ## min price 
  assert quoteWithConnector >= p    