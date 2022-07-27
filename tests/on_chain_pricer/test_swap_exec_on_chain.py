import brownie
from brownie import *

import pytest

"""
    test swap in Curve from token A to token B directly
"""
def test_swap_in_curve(oneE18, weth_whale, weth, crv, pricer, swapexecutor):
  ## 1e18
  sell_amount = 1 * oneE18

  ## minimum quote for ETH in CRV
  p = 1 * 1000 * oneE18  
  pool = '0x8e764bE4288B842791989DB5b8ec067279829809'
  quote = pricer.getCurvePrice(pool, weth.address, crv.address, sell_amount) 
  assert quote[1] >= p 

  ## swap on chain
  slippageTolerance = 0.95
  weth.transfer(swapexecutor.address, sell_amount, {'from': weth_whale})
  
  minOutput = quote[1] * slippageTolerance
  balBefore = crv.balanceOf(weth_whale)
  poolBytes = pricer.convertToBytes32(quote[0])
  swapexecutor.doOptimalSwapWithQuote(weth.address, crv.address, sell_amount, (0, minOutput, [poolBytes], []), {'from': weth_whale})
  balAfter = crv.balanceOf(weth_whale)
  assert (balAfter - balBefore) >= minOutput

"""
    test swap in Uniswap V2 from token A to token B directly
"""
def test_swap_in_univ2(oneE18, weth_whale, weth, usdc, pricer, swapexecutor):
  ## 1e18
  sell_amount = 1 * oneE18
  uniV2Router = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'

  ## minimum quote for ETH in USDC(1e6)
  p = 1 * 500 * 1000000  
  quote = pricer.getUniPrice(uniV2Router, weth.address, usdc.address, sell_amount) 
  assert quote >= p 

  ## swap on chain
  slippageTolerance = 0.95  
  weth.transfer(swapexecutor.address, sell_amount, {'from': weth_whale})
  
  minOutput = quote * slippageTolerance  
  balBefore = usdc.balanceOf(weth_whale)
  swapexecutor.doOptimalSwapWithQuote(weth.address, usdc.address, sell_amount, (1, minOutput, [], []), {'from': weth_whale})
  balAfter = usdc.balanceOf(weth_whale)
  assert (balAfter - balBefore) >= minOutput
  
"""
    test swap in Uniswap V3 from token A to token B directly
"""
def test_swap_in_univ3_single(oneE18, wbtc_whale, wbtc, usdc, pricer, swapexecutor):
  ## 1e8
  sell_amount = 1 * 100000000

  ## minimum quote for WBTC in USDC(1e6)
  p = 1 * 15000 * 1000000 

  ## swap on chain
  slippageTolerance = 0.95 
  wbtc.transfer(swapexecutor.address, sell_amount, {'from': wbtc_whale})
  
  minOutput = p * slippageTolerance   
  balBefore = usdc.balanceOf(wbtc_whale)
  swapexecutor.doOptimalSwapWithQuote(wbtc.address, usdc.address, sell_amount, (3, minOutput, [], [3000]), {'from': wbtc_whale})
  balAfter = usdc.balanceOf(wbtc_whale)
  assert (balAfter - balBefore) >= minOutput
  
"""
    test swap in Uniswap V3 from token A to token B via connectorToken C
"""

def test_swap_in_univ3(oneE18, wbtc_whale, wbtc, weth, usdc, pricer, swapexecutor):  
  ## 1e8
  sell_amount = 1 * 100000000

  ## minimum quote for WBTC in USDC(1e6)
  p = 1 * 15000 * 1000000  

  ## swap on chain
  slippageTolerance = 0.95 
  wbtc.transfer(swapexecutor.address, sell_amount, {'from': wbtc_whale})
  
  minOutput = p * slippageTolerance  
  ## encodedPath = swapexecutor.encodeUniV3TwoHop(wbtc.address, 500, weth.address, 500, usdc.address)   
  balBefore = usdc.balanceOf(wbtc_whale)
  swapexecutor.doOptimalSwapWithQuote(wbtc.address, usdc.address, sell_amount, (4, minOutput, [], [500,500]), {'from': wbtc_whale})
  balAfter = usdc.balanceOf(wbtc_whale)
  assert (balAfter - balBefore) >= minOutput
 
"""
    test swap in Balancer V2 from token A to token B via connectorToken C
"""
def test_swap_in_balancer_batch(oneE18, wbtc_whale, wbtc, weth, usdc, pricer, swapexecutor):  
  ## 1e8
  sell_amount = 1 * 100000000

  ## minimum quote for WBTC in USDC(1e6)
  p = 1 * 15000 * 1000000  

  ## swap on chain
  slippageTolerance = 0.95
  wbtc.transfer(swapexecutor.address, sell_amount, {'from': wbtc_whale})
  
  minOutput = p * slippageTolerance
  wbtc2WETHPoolId = '0xa6f548df93de924d73be7d25dc02554c6bd66db500020000000000000000000e'
  weth2USDCPoolId = '0x96646936b91d6b9d7d0c47c496afbf3d6ec7b6f8000200000000000000000019'   
  balBefore = usdc.balanceOf(wbtc_whale)
  swapexecutor.doOptimalSwapWithQuote(wbtc.address, usdc.address, sell_amount, (6, minOutput, [wbtc2WETHPoolId,weth2USDCPoolId], []), {'from': wbtc_whale})
  balAfter = usdc.balanceOf(wbtc_whale)
  assert (balAfter - balBefore) >= minOutput
 
"""
    test swap in Balancer V2 from token A to token B directly
"""
def test_swap_in_balancer_single(oneE18, weth_whale, weth, usdc, pricer, swapexecutor):  
  ## 1e18
  sell_amount = 1 * oneE18

  ## minimum quote for WETH in USDC(1e6)
  p = 1 * 500 * 1000000  

  ## swap on chain
  slippageTolerance = 0.95  
  weth.transfer(swapexecutor.address, sell_amount, {'from': weth_whale})
  
  minOutput = p * slippageTolerance
  weth2USDCPoolId = '0x96646936b91d6b9d7d0c47c496afbf3d6ec7b6f8000200000000000000000019'   
  balBefore = usdc.balanceOf(weth_whale)
  swapexecutor.doOptimalSwapWithQuote(weth.address, usdc.address, sell_amount, (5, minOutput, [weth2USDCPoolId], []), {'from': weth_whale})
  balAfter = usdc.balanceOf(weth_whale)
  assert (balAfter - balBefore) >= minOutput