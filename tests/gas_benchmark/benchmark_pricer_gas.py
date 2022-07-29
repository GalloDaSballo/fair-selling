import brownie
from brownie import *
import pytest

"""
    Benchmark test for gas cost in findOptimalSwap on various conditions
    This file is ok to be exclcuded in test suite due to its underluying functionality should be covered by other tests
    Rename the file to test_benchmark_pricer_gas.py to make this part of the testing suite if required
"""

def test_gas_only_uniswap_v2(oneE18, weth, pricer):
  token = "0xBC7250C8c3eCA1DfC1728620aF835FCa489bFdf3" # some swap (GM-WETH) only in Uniswap V2  
  ## 1e18
  sell_count = 100000000
  sell_amount = sell_count * 1000000000 ## 1e9
    
  tx = pricer.findOptimalSwap(token, weth.address, sell_amount)
  assert tx.return_value[0] == 1 ## UNIV2  
  assert tx.return_value[1] > 0  
  assert tx.gas_used <= 80000 ## 73925 in test simulation

def test_gas_uniswap_v2_sushi(oneE18, weth, pricer):
  token = "0x2e9d63788249371f1DFC918a52f8d799F4a38C94" # some swap (TOKE-WETH) only in Uniswap V2 & SushiSwap
  ## 1e18
  sell_count = 5000
  sell_amount = sell_count * oneE18 ## 1e18
    
  tx = pricer.findOptimalSwap(token, weth.address, sell_amount)
  assert (tx.return_value[0] == 1 or tx.return_value[0] == 2) ## UNIV2 or SUSHI
  assert tx.return_value[1] > 0  
  assert tx.gas_used <= 90000 ## 83158 in test simulation

def test_gas_only_balancer_v2(oneE18, weth, aura, pricer):
  token = aura # some swap (AURA-WETH) only in Balancer V2
  ## 1e18
  sell_count = 100
  sell_amount = sell_count * oneE18 ## 1e18
    
  tx = pricer.findOptimalSwap(token, weth.address, sell_amount)
  assert tx.return_value[0] == 5 ## BALANCER  
  assert tx.return_value[1] > 0  
  assert tx.gas_used <= 110000 ## 101190 in test simulation

def test_gas_only_balancer_v2_with_weth(oneE18, wbtc, aura, pricer):
  token = aura # some swap (AURA-WETH-WBTC) only in Balancer V2 via WETH in between as connector
  ## 1e18
  sell_count = 100
  sell_amount = sell_count * oneE18 ## 1e18
    
  tx = pricer.findOptimalSwap(token, wbtc.address, sell_amount)
  assert tx.return_value[0] == 6 ## BALANCERWITHWETH  
  assert tx.return_value[1] > 0  
  assert tx.gas_used <= 170000 ## 161690 in test simulation

def test_gas_only_uniswap_v3(oneE18, weth, pricer):
  token = "0xf4d2888d29D722226FafA5d9B24F9164c092421E" # some swap (LOOKS-WETH) only in Uniswap V3
  ## 1e18
  sell_count = 600000
  sell_amount = sell_count * oneE18 ## 1e18
    
  tx = pricer.findOptimalSwap(token, weth.address, sell_amount)
  assert tx.return_value[0] == 3 ## UNIV3  
  assert tx.return_value[1] > 0  
  assert tx.gas_used <= 160000 ## 158204 in test simulation

def test_gas_only_uniswap_v3_with_weth(oneE18, wbtc, pricer):
  token = "0xf4d2888d29D722226FafA5d9B24F9164c092421E" # some swap (LOOKS-WETH-WBTC) only in Uniswap V3 via WETH in between as connector
  ## 1e18
  sell_count = 600000
  sell_amount = sell_count * oneE18 ## 1e18
    
  tx = pricer.findOptimalSwap(token, wbtc.address, sell_amount)
  assert tx.return_value[0] == 4 ## UNIV3WITHWETH  
  assert tx.return_value[1] > 0  
  assert tx.gas_used <= 230000 ## 227498 in test simulation

def test_gas_almost_everything(oneE18, wbtc, weth, pricer):
  token = weth # some swap (WETH-WBTC) almost in every DEX, the most gas-consuming scenario
  ## 1e18
  sell_count = 10
  sell_amount = sell_count * oneE18 ## 1e18
    
  tx = pricer.findOptimalSwap(token, wbtc.address, sell_amount)
  assert (tx.return_value[0] <= 3 or tx.return_value[0] == 5) ## CURVE or UNIV2 or SUSHI or UNIV3 or BALANCER  
  assert tx.return_value[1] > 0  
  assert tx.gas_used <= 210000 ## 200229 in test simulation
  