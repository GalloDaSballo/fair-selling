import brownie
from brownie import *
import pytest

"""
    getBalancerPrice quote for token A swapped to token B directly using given balancer pool: A - > B
"""
## @pytest.mark.skip(reason="WETH2USDC")
def test_get_balancer_price(oneE18, weth, usdc, pricer):  
  ## 1e18
  sell_amount = 1 * oneE18
    
  ## minimum quote for ETH in USDC(1e6)
  p = 1 * 500 * 1000000  
  quote = pricer.getBalancerPrice.call(weth.address, sell_amount, usdc.address) 
  assert quote >= p   
  
"""
    getBalancerPriceWithConnector quote for token A swapped to token B with connector token C: A -> C -> B
"""
## @pytest.mark.skip(reason="WBTC2USDC")
def test_get_balancer_price_with_connector(oneE18, wbtc, usdc, weth, pricer):  
  ## 1e8
  sell_amount = 10 * 100000000
    
  ## minimum quote for WBTC in USDC(1e6)
  p = 10 * 10000 * 1000000  
  quote = pricer.getBalancerPriceWithConnector.call(wbtc.address, sell_amount, usdc.address, weth.address) 
  assert quote >= p   
  
"""
    getBalancerPrice quote for token A swapped to token B directly using given balancer pool: A - > B
"""
## @pytest.mark.skip(reason="WETH2CVX")
def test_get_balancer_price2(oneE18, cvx, weth, pricer):  
  ## 1e18
  sell_amount = 100 * oneE18
    
  ## no proper pool in Balancer for WETH in CVX
  quote = pricer.getBalancerPrice.call(weth.address, sell_amount, cvx.address) 
  assert quote == 0  