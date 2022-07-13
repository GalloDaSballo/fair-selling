import brownie
from brownie import *
import pytest

"""
    getUniPriceWithConnectorFeed quote for token A swapped to token B with ETH->WBTC in between as connectors
"""
## @pytest.mark.skip(reason="CVX2WETH->WBTC2BADGER")
def test_get_uni_price_with_connectors_feed(oneE18, cvx, badger, feedpricer):  
  ## 1e18
  sell_amount = 10000 * oneE18
    
  ## minimum quote for CVX in BADGER(1e18) ## Update based on market conditions
  p = 12000 * oneE18 
  
  ## favor this `static call` over direct call and retrive return_value to void tx stuck/crash
  quote = feedpricer.findOptimalSwap.call(cvx.address, badger.address, sell_amount)
  assert quote[1] >= p 
  assert quote[0] == 15 ## UNIV3WITHWETHWBTC 