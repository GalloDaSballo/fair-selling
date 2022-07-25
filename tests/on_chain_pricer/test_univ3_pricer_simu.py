import brownie
from brownie import *
import pytest

"""
    simulateUniV3Swap quote for token A swapped to token B directly: A - > B
"""
def test_simu_univ3_swap(oneE18, weth, usdc, pricer):  
  ## 1e18
  sell_count = 10
  sell_amount = sell_count * oneE18
    
  ## minimum quote for ETH in USDC(1e6) ## Rip ETH price
  p = sell_count * 900 * 1000000  
  quote = pricer.simulateUniV3Swap(usdc.address, sell_amount, weth.address, 500, False, "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640")
  
  assert quote >= p  

"""
    simulateUniV3Swap quote for token A swapped to token B directly: A - > B
"""
def test_simu_univ3_swap2(oneE18, weth, wbtc, pricer):  
  ## 1e8
  sell_count = 10
  sell_amount = sell_count * 100000000
    
  ## minimum quote for BTC in ETH(1e18) ## Rip ETH price
  p = sell_count * 14 * oneE18  
  quote = pricer.simulateUniV3Swap(wbtc.address, sell_amount, weth.address, 500, True, "0x4585FE77225b41b697C938B018E2Ac67Ac5a20c0")
  
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
  
def test_simu_univ3_swap_sort_pools_usdt(oneE18, usdt, weth, pricer):  
  ## 1e18
  sell_amount = 10 * oneE18

  ## minimum quote for WETH in USDT(1e6)
  p = 10 * 600 * 1000000  
  quoteInRangeAndFee = pricer.sortUniV3Pools(weth.address, sell_amount, usdt.address)

  ## min price
  assert quoteInRangeAndFee[0] >= p 
  assert quoteInRangeAndFee[1] == 500 ## fee-0.05% pool 
  
def test_simu_univ3_swap_usdt_usdc(oneE18, usdt, usdc, pricer):  
  ## 1e18
  sell_amount = 10000 * 1000000

  ## minimum quote for USDC in USDT(1e6)
  p = 10000 * 0.999 * 1000000  
  quoteInRangeAndFee = pricer.sortUniV3Pools(usdc.address, sell_amount, usdt.address)

  ## min price
  assert quoteInRangeAndFee[0] >= p 
  assert quoteInRangeAndFee[1] == 100 ## fee-0.01% pool
  
def test_simu_univ3_swap_tusd_usdc(oneE18, tusd, usdc, pricer):  
  ## 1e18
  sell_amount = 10000 * 1000000

  ## minimum quote for USDC in TUSD(1e18)
  p = 10000 * 0.999 * oneE18  
  quoteInRangeAndFee = pricer.sortUniV3Pools(usdc.address, sell_amount, tusd.address)

  ## min price
  assert quoteInRangeAndFee[0] >= p 
  assert quoteInRangeAndFee[1] == 100 ## fee-0.01% pool
  
def test_get_univ3_with_connector_no_second_pair(oneE18, balethbpt, usdc, weth, pricer):  
  ## 1e18
  sell_amount = 10000 * 1000000

  ## no swap path for USDC -> WETH -> BALETHBPT in Uniswap V3
  quoteInRangeAndFee = pricer.getUniV3PriceWithConnector(usdc.address, sell_amount, balethbpt.address, weth.address)
  assert quoteInRangeAndFee == 0
  
def test_get_univ3_with_connector_first_pair_quote_zero(oneE18, badger, usdc, weth, pricer):  
  ## 1e18
  sell_amount = 10000 * 1000000

  ## not enough liquidity for path for BADGER -> WETH -> USDC in Uniswap V3
  quoteInRangeAndFee = pricer.getUniV3PriceWithConnector(badger.address, sell_amount, usdc.address, weth.address)
  assert quoteInRangeAndFee == 0 
 