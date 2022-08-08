import brownie
from brownie import *
from scripts.send_order import get_cowswap_order

"""
  swapWethForBadger
    Works
    Reverts if not weth -> badger
  
  swapWethForAURA
    Works
    Reverts if not weth -> AURA
"""


### Swap Weth for Badger

def test_swap_weth_for_badger(setup_aura_processor, weth, badger, manager, settlement):
  sell_amount = 10000000000000000000

  order_details = get_cowswap_order(setup_aura_processor, weth, badger, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  setup_aura_processor.swapWethForBadger(data, uid, {"from": manager})

  assert settlement.preSignature(uid) > 0


def test_swap_weth_for_badger_must_be_weth_badger(setup_aura_processor, weth, badger, usdc, aura, manager, settlement):
  ## Fail if opposite swap
  sell_amount = 10000000000000000000

  order_details = get_cowswap_order(setup_aura_processor, badger, weth, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  with brownie.reverts():
    setup_aura_processor.swapWethForBadger(data, uid, {"from": manager})

  ## Fail if selling non weth
  order_details = get_cowswap_order(setup_aura_processor, usdc, badger, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  with brownie.reverts():
    setup_aura_processor.swapWethForBadger(data, uid, {"from": manager})

  ## Fail if random token combo
  order_details = get_cowswap_order(setup_aura_processor, usdc, aura, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  with brownie.reverts():
    setup_aura_processor.swapWethForBadger(data, uid, {"from": manager})



### Swap Weth for AURA or graviAURA

def test_swap_weth_for_aura(setup_aura_processor, weth, aura, manager, settlement):
  sell_amount = 100000000000000000000

  order_details = get_cowswap_order(setup_aura_processor, weth, aura, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  setup_aura_processor.swapWethForAURA(data, uid, {"from": manager})

  assert settlement.preSignature(uid) > 0

def test_swap_weth_for_graviaura(setup_aura_processor, weth, bve_aura, manager, settlement):
  sell_amount = 10000000000000000000 # 10 wETH since there is lower liquidity for graviAURA (fails with 100 wETH)

  order_details = get_cowswap_order(setup_aura_processor, weth, bve_aura, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  setup_aura_processor.swapWethForAURA(data, uid, {"from": manager})

  assert settlement.preSignature(uid) > 0

def test_swap_weth_for_aura_must_be_weth_aura(setup_aura_processor, weth, badger, usdc, aura, manager):
  ## Fail if opposite swap
  sell_amount = 100000000000000000000

  order_details = get_cowswap_order(setup_aura_processor, aura, weth, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  with brownie.reverts():
    setup_aura_processor.swapWethForAURA(data, uid, {"from": manager})

  ## Fail if selling non weth
  order_details = get_cowswap_order(setup_aura_processor, usdc, aura, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  with brownie.reverts():
    setup_aura_processor.swapWethForAURA(data, uid, {"from": manager})

  ## Fail if random token combo
  order_details = get_cowswap_order(setup_aura_processor, usdc, badger, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  with brownie.reverts():
    setup_aura_processor.swapWethForAURA(data, uid, {"from": manager})
