import brownie
from brownie import *
import pytest

"""
    getUniV3Price quote for token A swapped to token B directly: A - > B
"""
def test_get_univ3_price(oneE18, weth, usdc, pricer):  
  ## 1e18
  sell_amount = 1 * oneE18
    
  ## minimum quote for ETH in USDC(1e6) ## Rip ETH price
  p = 1 * 900 * 1000000  
  quote = pricer.getUniV3Price(weth.address, sell_amount, usdc.address)
  
  assert quote >= p    

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