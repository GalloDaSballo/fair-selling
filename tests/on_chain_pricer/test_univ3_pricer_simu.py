import brownie
from brownie import *
import pytest

"""
    simulateUniV3Swap quote for token A swapped to token B directly: A - > B
"""
def test_simu_univ3_swap(oneE18, weth, usdc, pricer):  
  ## 1e18
  sell_count = 10;
  sell_amount = sell_count * oneE18
    
  ## minimum quote for ETH in USDC(1e6) ## Rip ETH price
  p = sell_count * 900 * 1000000  
  quote = pricer.simulateUniV3Swap(pricer.uniV3Simulator(), weth.address, sell_amount, usdc.address, 500, 100)
  
  assert quote >= p  

"""
    simulateUniV3Swap quote for token A swapped to token B directly: A - > B
"""
def test_simu_univ3_swap2(oneE18, weth, wbtc, pricer):  
  ## 1e8
  sell_count = 10;
  sell_amount = sell_count * 100000000
    
  ## minimum quote for BTC in ETH(1e18) ## Rip ETH price
  p = sell_count * 14 * oneE18  
  quote = pricer.simulateUniV3Swap(pricer.uniV3Simulator(), wbtc.address, sell_amount, weth.address, 500, 100)
  
  assert quote >= p  