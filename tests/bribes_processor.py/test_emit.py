import brownie
import pytest


"""
    swapCVXTobveCVXAndEmit
    Works for both LP and Buy
    Emits event

  emitBadger
    Works
    Sets new emissions schedule
    Emits event
"""

def test_swap_cvx_and_emit(rewards, setup_processor, manager, bve_cvx, cvx):
  bve_balance_before = bve_cvx.balanceOf(setup_processor.BADGER_TREE())
  assert cvx.balanceOf(setup_processor) > 0

  schedules_length_before = len(rewards.getUnlockSchedulesFor(bve_cvx, bve_cvx))

  assert rewards.hasRole(rewards.MANAGER_ROLE(), setup_processor)

  setup_processor.swapCVXTobveCVXAndEmit({"from": manager})

  assert bve_cvx.balanceOf(setup_processor.BADGER_TREE()) > bve_balance_before
  assert cvx.balanceOf(setup_processor.BADGER_TREE()) == 0 ## All CVX has been emitted
  assert len(rewards.getUnlockSchedulesFor(bve_cvx, bve_cvx)) > schedules_length_before
  assert rewards.getUnlockSchedulesFor(bve_cvx, bve_cvx)[-1][-1] <= 60 * 60 * 24 * 14

  ## Reverts if called a second time
  with brownie.reverts():
    setup_processor.swapCVXTobveCVXAndEmit({"from": manager})


def test_emit_badger(rewards, setup_processor, manager, badger, bve_cvx):
  badger_balance_before = badger.balanceOf(setup_processor.BADGER_TREE())
  assert badger.balanceOf(setup_processor) > 0

  schedules_length_before = len(rewards.getUnlockSchedulesFor(bve_cvx, badger))

  assert rewards.hasRole(rewards.MANAGER_ROLE(), setup_processor)

  setup_processor.emitBadger({"from": manager})

  assert badger.balanceOf(setup_processor.BADGER_TREE()) > badger_balance_before
  assert badger.balanceOf(setup_processor) == 0 ## All badger emitted
  assert len(rewards.getUnlockSchedulesFor(bve_cvx, badger)) > schedules_length_before
  assert rewards.getUnlockSchedulesFor(bve_cvx, badger)[-1][-1] <= 60 * 60 * 24 * 14

  ## Reverts if called a second time
  with brownie.reverts():
    setup_processor.emitBadger({"from": manager})


# note: currently does not work; needs a way to fake badger tree memory slot
@pytest.mark.xfail
def test_emit_badger_after_schedule_deadline(rewards, manager, bve_cvx, badger, badger_whale, setup_processor, bool_true):
  last_ending_time = rewards.getUnlockSchedulesFor(bve_cvx, badger)[-1][-2]

  # fast fwd chain to 1 day after last ending time
  now = brownie.chain.time()
  delta = last_ending_time - now
  assert delta > 0
  brownie.chain.sleep(delta + 60 * 60 * 24)

  # fast fwd badger tree last published timestamp
  # TODO: somehow fake BadgerTree.lastPublishTimestamp() to delta + 60 * 60 * 24

  # do another badger emissions, but now after schedule has ended already
  assert badger.balanceOf(setup_processor) > 0
  badger.transfer(setup_processor, 6e22, {"from": badger_whale})
  test_emit_badger(rewards, setup_processor, manager, badger, bve_cvx, bool_true)

  # assert schedule set is indeed shorter than 14 days
  assert rewards.getUnlockSchedulesFor(bve_cvx, badger)[-1][-1] < 60 * 60 * 24 * 14
