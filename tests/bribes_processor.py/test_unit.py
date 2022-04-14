import brownie
from brownie import *
from scripts.send_order import get_cowswap_order

"""
  Unit tests for all functions
  
  Ragequit
    Anytime from manager
    After 28 days from anyone

  sellBribeForWeth
    Can't sell badger
    Can't sell CVX
    Works for only X to ETH

  swapWethForBadger
    Works
    Reverts if not weth -> badger
  
  swapWethForCVX
    Works
    Reverts if not weth -> CVX
    
  swapCVXTobveCVXAndEmit
    Works for both LP and Buy
    Emits event

  emitBadger
    Works
    Emits event
"""


### Ragequit

def test_ragequit_permission(setup_processor, manager, usdc):
  balance_before = usdc.balanceOf(setup_processor.BADGER_TREE())

  ## The manager can RQ at any time
  setup_processor.ragequit(usdc, False, {"from": manager})

  assert usdc.balanceOf(setup_processor.BADGER_TREE()) > balance_before


def test_ragequit_anyone_after_time(setup_processor, manager, usdc):
  rando = accounts[2]

  ## Reverts if rando calls immediately
  with brownie.reverts():
    setup_processor.ragequit(usdc, False, {"from": rando})

  chain.sleep(setup_processor.MAX_MANAGER_IDLE_TIME() + 1)
  chain.mine()

  balance_before = usdc.balanceOf(setup_processor.BADGER_TREE())

  ## Rando can call after time has passed
  setup_processor.ragequit(usdc, False, {"from": rando})

  assert usdc.balanceOf(setup_processor.BADGER_TREE()) > balance_before


### Sell Bribes for Weth

def test_sell_bribes_for_weth_cant_sell_badger(setup_processor, badger, weth, manager):
  sell_amount = 10000000000000000000

  order_details = get_cowswap_order(setup_processor, badger, weth, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  with brownie.reverts():
    setup_processor.sellBribeForWeth(data, uid, {"from": manager})

def test_sell_bribes_for_weth_cant_sell_cvx(setup_processor, cvx, weth, manager):
  sell_amount = 10000000000000000000

  order_details = get_cowswap_order(setup_processor, cvx, weth, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  with brownie.reverts():
    setup_processor.sellBribeForWeth(data, uid, {"from": manager})


def test_sell_bribes_for_weth_works_when_selling_usdc_for_weth(setup_processor, usdc, weth, manager, settlement):
  sell_amount = 1000000000

  order_details = get_cowswap_order(setup_processor, usdc, weth, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  setup_processor.sellBribeForWeth(data, uid, {"from": manager})

  assert settlement.preSignature(uid) > 0

## TODO: must buy WETH

## TODO: Can't sell WETH



### Swap Weth for Badger

def test_swap_weth_for_badger(setup_processor, weth, badger, manager, settlement):
  sell_amount = 10000000000000000000

  order_details = get_cowswap_order(setup_processor, weth, badger, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  setup_processor.swapWethForBadger(data, uid, {"from": manager})

  assert settlement.preSignature(uid) > 0


## TODO: check that it must be WETH -> BADGER


### Swap Weth for CVX

def test_swap_weth_for_cvx(setup_processor, weth, cvx, manager, settlement):
  sell_amount = 10000000000000000000

  order_details = get_cowswap_order(setup_processor, weth, cvx, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  setup_processor.swapWethForCVX(data, uid, {"from": manager})

  assert settlement.preSignature(uid) > 0

## TODO: check that it must be WETH -> CVX


## swapCVXTobveCVXAndEmit