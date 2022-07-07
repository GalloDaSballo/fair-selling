import brownie
from brownie import *
import pytest

"""
    getUniV3Price quote for token A swapped to token B directly: A - > B
"""
## @pytest.mark.skip(reason="WETH2USDC")
def test_get_univ3_price(oneE18, weth, usdc, pricer):  
  ## 1e18
  sell_amount = 1 * oneE18
    
  ## minimum quote for ETH in USDC(1e6) ## Update based on market conditions
  p = 1 * 1150 * 1000000  
  quote = pricer.getUniV3Price.call(weth.address, sell_amount, usdc.address) 
  assert quote >= p    

"""
    getUniV3PriceWithConnector quote for token A swapped to token B with connector token C: A -> C -> B
"""
## @pytest.mark.skip(reason="WBTC2USDC")
def test_get_univ3_price_with_connector(oneE18, wbtc, usdc, weth, pricer):  
  ## 1e8
  sell_amount = 100 * 100000000
  
  quote = pricer.getUniV3Price.call(wbtc.address, sell_amount, usdc.address)
  quoteWithConnector = pricer.getUniV3PriceWithConnector.call(wbtc.address, sell_amount, usdc.address, weth.address)

  ## min price 
  assert quoteWithConnector > quote  

"""
    getUniV3PriceWithConnector quote for stablecoin A swapped to stablecoin B with connector token C: A -> C -> B
"""
## @pytest.mark.skip(reason="DAI2USDC")
def test_get_univ3_price_with_connector_stablecoin(oneE18, dai, usdc, weth, pricer):  
  ## 1e18
  sell_amount = 10000 * oneE18

  quote = pricer.getUniV3Price.call(dai.address, sell_amount, usdc.address)  
  quoteWithConnector = pricer.getUniV3PriceWithConnector.call(dai.address, sell_amount, usdc.address, weth.address)

  ## min price 
  assert quoteWithConnector < quote  