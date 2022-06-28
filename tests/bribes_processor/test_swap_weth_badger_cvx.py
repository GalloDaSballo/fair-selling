import brownie
from brownie import *
from scripts.send_order import get_cowswap_order

"""
  swapWethForBadger
    Works
    Reverts if not weth -> badger
  
  swapWethForCVX
    Works
    Reverts if not weth -> CVX
"""


### Swap Weth for Badger

def test_swap_weth_for_badger(setup_processor, weth, badger, manager, settlement):
  sell_amount = 10000000000000000000

  order_details = get_cowswap_order(setup_processor, weth, badger, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  setup_processor.swapWethForBadger(data, uid, {"from": manager})

  assert settlement.preSignature(uid) > 0


def test_swap_weth_for_badger_must_be_weth_badger(setup_processor, weth, badger, usdc, cvx, manager, settlement):
  ## Fail if opposite swap
  sell_amount = 10000000000000000000

  order_details = get_cowswap_order(setup_processor, badger, weth, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  with brownie.reverts():
    setup_processor.swapWethForBadger(data, uid, {"from": manager})

  ## Fail if selling non weth
  order_details = get_cowswap_order(setup_processor, usdc, badger, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  with brownie.reverts():
    setup_processor.swapWethForBadger(data, uid, {"from": manager})

  ## Fail if random token combo
  order_details = get_cowswap_order(setup_processor, usdc, cvx, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  with brownie.reverts():
    setup_processor.swapWethForBadger(data, uid, {"from": manager})



### Swap Weth for CVX

def test_swap_weth_for_cvx(setup_processor, weth, cvx, manager, settlement):
  sell_amount = 100000000000000000000

  order_details = get_cowswap_order(setup_processor, weth, cvx, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  setup_processor.swapWethForCVX(data, uid, {"from": manager})

  assert settlement.preSignature(uid) > 0

def test_swap_weth_for_cvx_must_be_weth_cvx(setup_processor, weth, badger, usdc, cvx, manager, settlement):
  ## Fail if opposite swap
  sell_amount = 100000000000000000000

  order_details = get_cowswap_order(setup_processor, cvx, weth, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  with brownie.reverts():
    setup_processor.swapWethForCVX(data, uid, {"from": manager})

  ## Fail if selling non weth
  order_details = get_cowswap_order(setup_processor, usdc, cvx, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  with brownie.reverts():
    setup_processor.swapWethForCVX(data, uid, {"from": manager})

  ## Fail if random token combo
  order_details = get_cowswap_order(setup_processor, usdc, badger, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  with brownie.reverts():
    setup_processor.swapWethForCVX(data, uid, {"from": manager})
