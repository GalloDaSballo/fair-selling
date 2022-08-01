import brownie
from brownie import *
import pytest

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
  
  quoteSETH2 = pricer.sortUniV3Pools(weth.address, sell_amount, "0xFe2e637202056d30016725477c5da089Ab0A043A")
  assert quoteSETH2[0] >= 10 * 0.999 * oneE18 
  
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
  
  quoteUSDM = pricer.sortUniV3Pools(usdc.address, sell_amount, "0xbbAec992fc2d637151dAF40451f160bF85f3C8C1")
  assert quoteUSDM[0] >= 10000 * 0.999 * 1000000
  
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
  
def test_only_sushi_support(oneE18, xsushi, usdc, pricer):  
  ## 1e18
  sell_amount = 100 * oneE18

  supported = pricer.isPairSupported(xsushi.address, usdc.address, sell_amount)
  assert supported == True
  
def test_only_curve_support(oneE18, usdc, badger, aura, pricerwrapper):
  pricer = pricerwrapper   
  ## 1e18
  sell_amount = 1000 * oneE18
  
  ## USDI
  supported = pricer.isPairSupported("0x2a54ba2964c8cd459dc568853f79813a60761b58", usdc.address, sell_amount)
  assert supported == True
  quoteTx = pricer.findOptimalSwap("0x2a54ba2964c8cd459dc568853f79813a60761b58", usdc.address, sell_amount)
  assert quoteTx[1][1] > 0
  assert quoteTx[1][0] == 0
  
  ## not supported yet
  isBadgerAuraSupported = pricer.isPairSupported(badger.address, aura.address, sell_amount * 100)
  assert isBadgerAuraSupported == False
 