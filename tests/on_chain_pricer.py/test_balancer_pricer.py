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
  p = 1 * 1500 * 1000000  
  quote = pricer.getBalancerPrice.call('0x96646936b91d6b9d7d0c47c496afbf3d6ec7b6f8000200000000000000000019', weth.address, sell_amount, usdc.address) 
  assert quote >= p   
  
"""
    getBalancerPriceWithConnector quote for token A swapped to token B with connector token C: A -> C -> B
"""
## @pytest.mark.skip(reason="WBTC2USDC")
def test_get_balancer_price_with_connector(oneE18, wbtc, usdc, weth, pricer):  
  ## 1e8
  sell_amount = 100 * 100000000
    
  ## minimum quote for WBTC in USDC(1e6)
  p = 100 * 20000 * 1000000  
  quote = pricer.getBalancerPriceWithConnector.call('0xa6f548df93de924d73be7d25dc02554c6bd66db500020000000000000000000e', '0x96646936b91d6b9d7d0c47c496afbf3d6ec7b6f8000200000000000000000019', wbtc.address, sell_amount, usdc.address, weth.address) 
  assert quote >= p   