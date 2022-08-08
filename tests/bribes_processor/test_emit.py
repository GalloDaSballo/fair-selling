import brownie
from brownie import *

"""
    swapCVXTobveCVXAndEmit
    Works for both LP and Buy
    Emits event

  emitBadger
    Works
    Emits event
"""

def test_swap_cvx_and_emit_with_purchase(setup_processor, manager, bve_cvx, cvx, make_cvx_pool_profitable):
  bve_balance_before = bve_cvx.balanceOf(setup_processor.BADGER_TREE())
  assert cvx.balanceOf(setup_processor) > 0

  tx = setup_processor.swapCVXTobveCVXAndEmit({"from": manager})

  assert bve_cvx.balanceOf(setup_processor.BADGER_TREE()) > bve_balance_before
  assert cvx.balanceOf(setup_processor.BADGER_TREE()) == 0 ## All CVX has been emitted


  ## Reverts if called a second time
  with brownie.reverts():
    setup_processor.swapCVXTobveCVXAndEmit({"from": manager})
    
def test_swap_cvx_and_emit_with_deposit(setup_processor, manager, bve_cvx, cvx, make_cvx_pool_unprofitable):
  bve_balance_before = bve_cvx.balanceOf(setup_processor.BADGER_TREE())
  assert cvx.balanceOf(setup_processor) > 0

  tx = setup_processor.swapCVXTobveCVXAndEmit({"from": manager})

  assert bve_cvx.balanceOf(setup_processor.BADGER_TREE()) > bve_balance_before
  assert cvx.balanceOf(setup_processor.BADGER_TREE()) == 0 ## All CVX has been emitted


  ## Reverts if called a second time
  with brownie.reverts():
    setup_processor.swapCVXTobveCVXAndEmit({"from": manager})

def test_emit_badger(setup_processor, manager, badger,):
  badger_balance_before = badger.balanceOf(setup_processor.BADGER_TREE())
  assert badger.balanceOf(setup_processor) > 0

  setup_processor.emitBadger({"from": manager})

  assert badger.balanceOf(setup_processor.BADGER_TREE()) > badger_balance_before
  assert badger.balanceOf(setup_processor) == 0 ## All badger emitted

  ## Reverts if called a second time
  with brownie.reverts():
    setup_processor.emitBadger({"from": manager})