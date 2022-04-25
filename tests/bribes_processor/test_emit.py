import brownie
from brownie import *
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

@pytest.fixture
def proposer():
  return accounts.at("0x1a6d6d120a7e3f71b084b4023a518c72f1a93ee9", force=True)

@pytest.fixture
def approver():
  return accounts.at("0x1318d5c0c24830d86cc27db13ced0ced31412438", force=True)

@pytest.fixture
def tree(setup_processor):
  return BadgerTreeV2.at(setup_processor.BADGER_TREE())

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
def test_emit_badger_after_schedule_deadline(tree, proposer, approver, rewards, manager, bve_cvx, badger, badger_whale, setup_processor):
  last_ending_time = rewards.getUnlockSchedulesFor(bve_cvx, badger)[-1][-2]

  # fast fwd chain to 1 day after last ending time
  now = brownie.chain.time()
  delta = last_ending_time - now
  assert delta > 0
  brownie.chain.sleep(delta + 60 * 60 * 24)

  # fast fwd badger tree last published timestamp
  # TODO: somehow fake BadgerTree.lastPublishTimestamp() to delta + 60 * 60 * 24
  root = tree.merkleRoot()
  contentHash = tree.merkleContentHash()
  cycle = tree.currentCycle() + 1
  startBlock = tree.lastPublishStartBlock() + 1
  endBlock = tree.lastPublishEndBlock() + 500 ## About 500 blocks

  tree.proposeRoot(
    root,
    contentHash,
    cycle,
    startBlock,
    endBlock,
    {"from": proposer}
  )

  tree.approveRoot(
    root,
    contentHash,
    cycle,
    startBlock,
    endBlock,
    {"from": approver}
  )
  

  # do another badger emissions, but now after schedule has ended already
  assert badger.balanceOf(setup_processor) > 0
  badger.transfer(setup_processor, 6e22, {"from": badger_whale})
  test_emit_badger(rewards, setup_processor, manager, badger, bve_cvx)

  # assert schedule set is indeed shorter than 14 days
  assert rewards.getUnlockSchedulesFor(bve_cvx, badger)[-1][-1] < 60 * 60 * 24 * 14
