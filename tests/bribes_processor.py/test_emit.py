import brownie


"""
    swapCVXTobveCVXAndEmit
    Works for both LP and Buy
    Emits event

  emitBadger
    Works
    Emits event
"""

# def test_swap_cvx_and_emit(setup_processor, manager, bve_cvx, cvx):
#   bve_balance_before = bve_cvx.balanceOf(setup_processor.BADGER_TREE())
#   assert cvx.balanceOf(setup_processor) > 0

#   setup_processor.swapCVXTobveCVXAndEmit({"from": manager})

#   assert bve_cvx.balanceOf(setup_processor.BADGER_TREE()) > bve_balance_before
#   assert cvx.balanceOf(setup_processor.BADGER_TREE()) == 0 ## All CVX has been emitted


#   ## Reverts if called a second time
#   with brownie.reverts():
#     setup_processor.swapCVXTobveCVXAndEmit({"from": manager})

def test_emit_badger(rewards, setup_processor, manager, badger, bve_cvx):
  badger_balance_before = badger.balanceOf(setup_processor.BADGER_TREE())
  assert badger.balanceOf(setup_processor) > 0

  schedules_length_before = len(rewards.getUnlockSchedulesFor(bve_cvx, badger))

  assert rewards.hasRole(rewards.MANAGER_ROLE(), setup_processor)

  setup_processor.emitBadger({"from": manager})

  assert badger.balanceOf(setup_processor.BADGER_TREE()) > badger_balance_before
  assert badger.balanceOf(setup_processor) == 0 ## All badger emitted
  assert len(rewards.getUnlockSchedulesFor(bve_cvx, badger)) > schedules_length_before

  ## Reverts if called a second time
  with brownie.reverts():
    setup_processor.emitBadger({"from": manager})
