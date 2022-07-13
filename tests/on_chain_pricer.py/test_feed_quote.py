import brownie
from brownie import *
import pytest

"""
    quoteWithPriceFeed quote for token A swapped to token B with price feed directly
"""
## @pytest.mark.skip(reason="CVX2USDC+CVX2ETH")
def test_feed_quote(oneE18, cvx, usdc, weth, pricer):  
  ## 1e18
  sell_amount = 10000 * oneE18
    
  ## minimum quote for CVX in USDC(1e6) ## Update based on market conditions
  p = 40000 * 1000000  
  quote = pricer.quoteWithPriceFeed(cvx.address, usdc.address, sell_amount)
  assert quote >= p 
    
  ## minimum quote for CVX in WETH(1e18) ## Update based on market conditions
  pEth = 40 * oneE18  
  quoteEth = pricer.quoteWithPriceFeed(cvx.address, weth.address, sell_amount)
  assert quoteEth >= pEth 

"""
    quoteWithPriceFeed quote for token A swapped to token B with price feed directly
"""
## @pytest.mark.skip(reason="USDC2CVX+ETH2CVX")
def test_feed_quote_reciprocal(oneE18, cvx, usdc, weth, pricer):  
  ## 1e6
  usdc_sell_amount = 10000 * 1000000
    
  ## minimum quote for USDC(1e6) in CVX ## Update based on market conditions
  p = 1500 * oneE18  
  quote = pricer.quoteWithPriceFeed(usdc.address, cvx.address, usdc_sell_amount)
  assert quote >= p 
    
  ## 1e18
  sell_amount = 10 * oneE18
  
  ## minimum quote for ETH(1e18) in CVX ## Update based on market conditions
  pEth = 1500 * oneE18  
  quoteEth = pricer.quoteWithPriceFeed(weth.address, cvx.address, sell_amount)
  assert quoteEth >= pEth 

"""
    quoteWithPriceFeed quote for token A swapped to token B with price feed directly
"""
## @pytest.mark.skip(reason="FXS2USDC+ETH2FXS")
def test_usd_feed_quote(oneE18, fxs, usdc, weth, pricer):  
  ## 1e18
  sell_amount = 10000 * oneE18
    
  ## minimum quote for FXS in USDC(1e6) ## Update based on market conditions
  p = 30000 * 1000000  
  quote = pricer.quoteWithPriceFeed(fxs.address, usdc.address, sell_amount)
  assert quote >= p 
    
  eth_sell_amount = 10 * oneE18
  ## minimum quote for WETH(1e18) in FXS ## Update based on market conditions
  pEth = 1500 * oneE18  
  quoteEth = pricer.quoteWithPriceFeed(weth.address, fxs.address, sell_amount)
  assert quoteEth >= pEth 
