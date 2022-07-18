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
  quote = pricer.simulateUniV3Swap(weth.address, sell_amount, usdc.address, 500, 100)
  
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
  quote = pricer.simulateUniV3Swap(wbtc.address, sell_amount, weth.address, 500, 100)
  
  assert quote >= p  

"""
    sortUniV3Pools quote for stablecoin A swapped to stablecoin B which try for in-range swap before full-simulation
    https://info.uniswap.org/#/tokens/0x6b175474e89094c44da98b954eedeac495271d0f
"""
def test_simu_univ3_swap_sort_pools(oneE18, dai, usdc, weth, pricer):  
  ## 1e18
  sell_amount = 10000 * oneE18

  ## minimum quote for DAI in USDC(1e6)
  p = 10000 * 0.999 * 1000000  
  quoteInRangeAndFee = pricer.sortUniV3Pools(dai.address, sell_amount, usdc.address)

  ## min price
  assert quoteInRangeAndFee[0] >= p 
  assert quoteInRangeAndFee[1] == 100 ## fee-0.01% pool got better quote than fee-0.05% pool