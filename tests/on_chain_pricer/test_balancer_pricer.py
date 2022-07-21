import brownie
from brownie import *

#import sys
#from scripts.get_price import get_coingecko_price, get_coinmarketcap_price, get_coinmarketcap_metadata

import pytest     
  
"""
    getBalancerPrice quote for token A swapped to token B directly using given balancer pool: A - > B
"""
def test_get_balancer_price_stable_analytical(oneE18, usdc, dai, pricer):  
  ## 1e18
  sell_count = 50000
  sell_amount = sell_count * oneE18
  
  ## minimum quote for DAI in USDC(1e6)
  p = sell_count * 0.999 * 1000000  
    
  ## there is a proper pool in Balancer for DAI in USDC
  poolId = pricer.BALANCERV2_DAI_USDC_USDT_POOLID()
  q = pricer.getBalancerPriceWithinPool(poolId, dai.address, sell_amount, usdc.address).return_value
  assert q >= p  
  quote = pricer.getBalancerQuoteWithinPoolAnalytcially(poolId, dai.address, sell_amount, usdc.address)
  assert quote == q 

"""
    getBalancerPrice quote for token A swapped to token B directly using given balancer pool: A - > B
"""
def test_get_balancer_price(oneE18, weth, usdc, pricer):  
  ## 1e18
  sell_amount = 1 * oneE18
    
  ## minimum quote for ETH in USDC(1e6)
  p = 1 * 500 * 1000000  
  quote = pricer.getBalancerPrice(weth.address, sell_amount, usdc.address).return_value
  assert quote >= p 
  
  ## price sanity check with fine liquidity
  #p1 = get_coingecko_price('ethereum')
  #p2 = get_coingecko_price('usd-coin')
  #assert (quote / 1000000) >= (p1 / p2) * 0.98
  
"""
    getBalancerPriceWithConnector quote for token A swapped to token B with connector token C: A -> C -> B
"""
def test_get_balancer_price_with_connector(oneE18, wbtc, usdc, weth, pricer):  
  ## 1e8
  sell_count = 10
  sell_amount = sell_count * 100000000
    
  ## minimum quote for WBTC in USDC(1e6)
  p = sell_count * 15000 * 1000000  
  quote = pricer.getBalancerPriceWithConnector(wbtc.address, sell_amount, usdc.address, weth.address).return_value
  assert quote >= p    
  
  ## price sanity check with dime liquidity
  #yourCMCKey = 'b527d143-8597-474e-b9b2-5c28c1321c37'
  #p1 = get_coinmarketcap_price('3717', yourCMCKey) ## wbtc
  #p2 = get_coinmarketcap_price('3408', yourCMCKey) ## usdc
  #assert (quote / 1000000 / sell_count) >= (p1 / p2) * 0.75
  
"""
    getBalancerPrice quote for token A swapped to token B directly using given balancer pool: A - > B
"""
def test_get_balancer_price_nonexistence(oneE18, cvx, weth, pricer):  
  ## 1e18
  sell_amount = 100 * oneE18
    
  ## no proper pool in Balancer for WETH in CVX
  quote = pricer.getBalancerPrice(weth.address, sell_amount, cvx.address).return_value
  assert quote == 0  
  
"""
    getBalancerPriceAnalytically quote for token A swapped to token B directly using given balancer pool: A - > B analytically
"""
def test_get_balancer_price_analytical(oneE18, weth, usdc, pricer):  
  ## 1e18
  sell_amount = 1 * oneE18
    
  ## minimum quote for ETH in USDC(1e6)
  p = 1 * 500 * 1000000  
  quote = pricer.getBalancerPriceAnalytically(weth.address, sell_amount, usdc.address)
  assert quote >= p  
  
"""
    getBalancerPriceWithConnectorAnalytically quote for token A swapped to token B directly using given balancer pool: A - > B analytically
"""
def test_get_balancer_price_with_connector_analytical(oneE18, wbtc, usdc, weth, pricer):  
  ## 1e8
  sell_count = 10
  sell_amount = sell_count * 100000000
    
  ## minimum quote for WBTC in USDC(1e6)
  p = sell_count * 15000 * 1000000  
  quote = pricer.getBalancerPriceWithConnectorAnalytically(wbtc.address, sell_amount, usdc.address, weth.address)
  assert quote >= p       
  
"""
    getBalancerPriceAnalytically quote for token A swapped to token B directly using given balancer pool: A - > B analytically
"""
def test_get_balancer_price_ohm_analytical(oneE18, ohm, dai, pricer):  
  ## 1e8
  sell_count = 1000
  sell_amount = sell_count * 1000000000 ## 1e9
    
  ## minimum quote for OHM in DAI(1e18)
  p = sell_count * 10 * oneE18  
  quote = pricer.getBalancerPriceAnalytically(ohm.address, sell_amount, dai.address)
  assert quote >= p     
  
"""
    getBalancerPrice quote for token A swapped to token B directly using given balancer pool: A - > B
"""
def test_get_balancer_price_aurabal_analytical(oneE18, aurabal, weth, pricer):  
  ## 1e18
  sell_count = 1000
  sell_amount = sell_count * oneE18
  
  ## minimum quote for AURABAL in WETH(1e18)
  p = sell_count * 0.006 * oneE18  
    
  ## there is a proper pool in Balancer for AURABAL in WETH
  quote = pricer.getBalancerPriceAnalytically(aurabal.address, sell_amount, weth.address)
  assert quote >= p 
  