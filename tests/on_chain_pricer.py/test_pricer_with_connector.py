import brownie
from brownie import *
import pytest

"""
    getUniPriceWithConnectorFeed quote for token A swapped to token B with ETH->WBTC in between as connectors
"""
## @pytest.mark.skip(reason="CVX2WETH->WBTC2BADGER")
def test_get_uni_price_with_connectors_feed(oneE18, cvx, weth, wbtc, badger, pricer):  
  ## 1e18
  sell_amount = 10000 * oneE18
    
  ## minimum quote for CVX in BADGER(1e18) ## Update based on market conditions
  p = 12000 * oneE18 
  quote = pricer.getUniPriceWithConnectorFeed('0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F', cvx.address, sell_amount, badger.address, weth.address, wbtc.address)
  assert quote >= p 

"""
    getUniV3PriceWithConnectorFeed quote for token A swapped to token B with ETH->WBTC in between as connectors
"""
## @pytest.mark.skip(reason="CVX2WETH->WBTC2BADGER")
def test_get_univ3_price_with_connectors_feed(oneE18, cvx, weth, wbtc, badger, pricer):  
  ## 1e18
  sell_amount = 10000 * oneE18
    
  ## minimum quote for CVX in BADGER(1e18) ## Update based on market conditions
  p = 12000 * oneE18 
  quote = pricer.getUniV3PriceWithConnectorFeed(cvx.address, sell_amount, badger.address, weth.address, wbtc.address).return_value
  assert quote[0] >= p  

"""
    isPairSupported indicate if swap quote between A and B exist with given pricer
"""
## @pytest.mark.skip(reason="PairSupported")
def test_pair_not_supported(oneE18, cvx, pricer):  
  ## 1e18
  sell_amount = 10000 * oneE18
    
  cvx2DeadSupported = pricer.isPairSupported(cvx.address, '0x000000000000000000000000000000000000dEaD', sell_amount).return_value  
  assert cvx2DeadSupported == False