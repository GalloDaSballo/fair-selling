import brownie
from brownie import *

import sys
from scripts.get_price import get_coingecko_price, get_coinmarketcap_price, get_coinmarketcap_metadata

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
  
  ## price sanity check with fine liquidity
  p1 = get_coingecko_price('ethereum')
  p2 = get_coingecko_price('usd-coin')
  assert (quote / 1000000) >= (p1 / p2) * 0.98
  
"""
    getBalancerPriceWithConnector quote for token A swapped to token B with connector token C: A -> C -> B
"""
## @pytest.mark.skip(reason="WBTC2USDC")
def test_get_balancer_price_with_connector(oneE18, wbtc, usdc, weth, pricer):  
  ## 1e8
  sell_count = 10
  sell_amount = sell_count * 100000000
    
  ## minimum quote for WBTC in USDC(1e6)
  p = sell_count * 10000 * 1000000  
  quote = pricer.getBalancerPriceWithConnector.call(wbtc.address, sell_amount, usdc.address, weth.address) 
  assert quote >= p    
  
  ## price sanity check with dime liquidity
  yourCMCKey = 'b527d143-8597-474e-b9b2-5c28c1321c37'
  p1 = get_coinmarketcap_price('3717', yourCMCKey) ## wbtc
  p2 = get_coinmarketcap_price('3408', yourCMCKey) ## usdc
  assert (quote / 1000000 / sell_count) >= (p1 / p2) * 0.75
  
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