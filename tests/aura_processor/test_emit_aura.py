import brownie
from brownie import a
from helpers.utils import approx

"""
    swapAuraToBveAuraAndEmit
    Works for both LP and Buy
    Emits event

  emitBadger
    Works
    Emits event
"""

OPS_FEE = 0.05 # Hardcoded in contract

def test_swap_aura_and_emit(setup_aura_processor, manager, aura, bve_aura):
  bve_tree_balance_before = bve_aura.balanceOf(setup_aura_processor.BADGER_TREE())
  bve_processor_balance_before = bve_aura.balanceOf(setup_aura_processor.address) # There could be gravi beforehand
  bve_treasury_balance_before = bve_aura.balanceOf(setup_aura_processor.TREASURY())
  assert aura.balanceOf(setup_aura_processor) > 0

  bve_supply = bve_aura.totalSupply()

  # Only manager can call
  with brownie.reverts():
    setup_aura_processor.swapAURATobveAURAAndEmit({"from": a[9]})

  tx = setup_aura_processor.swapAURATobveAURAAndEmit({"from": manager})

  assert bve_aura.balanceOf(setup_aura_processor.BADGER_TREE()) > bve_tree_balance_before
  assert aura.balanceOf(setup_aura_processor.address) == 0 ## All aura has been emitted

  ## graviAURA supply increased due to deposit
  graviaura_acquird = bve_aura.totalSupply() - bve_supply
  graviaura_total = graviaura_acquird + bve_processor_balance_before
  assert graviaura_acquird > 0

  # Confirm math
  ops_fee = int(graviaura_total) * OPS_FEE
  # 1% approximation due to Brownie rounding
  assert approx(ops_fee, bve_aura.balanceOf(setup_aura_processor.TREASURY()) - bve_treasury_balance_before, 1)

  to_emit = graviaura_total - ops_fee

  # Confirm events
  # Tree Distribution
  assert len(tx.events["TreeDistribution"]) == 1
  event = tx.events["TreeDistribution"][0]
  assert event["token"] == bve_aura.address
  assert approx(event["amount"], to_emit, 1)
  assert event["beneficiary"] == bve_aura.address

  # Performance Fee Governance
  assert len(tx.events["PerformanceFeeGovernance"]) == 1
  event = tx.events["PerformanceFeeGovernance"][0]
  assert event["token"] == bve_aura.address
  assert approx(event["amount"], ops_fee, 1)

  # BribesEmission
  assert len(tx.events["BribeEmission"]) == 1
  event = tx.events["BribeEmission"][0]
  assert event["token"] == bve_aura.address
  assert approx(event["amount"], to_emit, 1)

  ## Reverts if called a second time
  with brownie.reverts():
    setup_aura_processor.swapAURATobveAURAAndEmit({"from": manager})


def test_emit_badger(setup_aura_processor, manager, badger, bve_aura):
  badger_tree_balance_before = badger.balanceOf(setup_aura_processor.BADGER_TREE())
  badger_processor_balance_before = badger.balanceOf(setup_aura_processor)
  badger_treasury_balance_before = badger.balanceOf(setup_aura_processor.TREASURY())
  assert badger_processor_balance_before > 0

  # Only manager can call
  with brownie.reverts():
    setup_aura_processor.emitBadger({"from": a[9]})

  tx = setup_aura_processor.emitBadger({"from": manager})

  assert badger.balanceOf(setup_aura_processor.BADGER_TREE()) > badger_tree_balance_before
  assert badger.balanceOf(setup_aura_processor) == 0 ## All badger emitted

  # Confirm math
  ops_fee = int(badger_processor_balance_before) * OPS_FEE
  # 1% approximation due to Brownie rounding
  assert approx(ops_fee, badger.balanceOf(setup_aura_processor.TREASURY()) - badger_treasury_balance_before, 1)

  to_emit = badger_processor_balance_before - ops_fee

  # Confirm events
  # Tree Distribution
  assert len(tx.events["TreeDistribution"]) == 1
  event = tx.events["TreeDistribution"][0]
  assert event["token"] == badger.address
  assert approx(event["amount"], to_emit, 1)
  assert event["beneficiary"] == bve_aura.address

  # Performance Fee Governance
  assert len(tx.events["PerformanceFeeGovernance"]) == 1
  event = tx.events["PerformanceFeeGovernance"][0]
  assert event["token"] == badger.address
  assert approx(event["amount"], ops_fee, 1)

  # BribesEmission
  assert len(tx.events["BribeEmission"]) == 1
  event = tx.events["BribeEmission"][0]
  assert event["token"] == badger.address
  assert approx(event["amount"], to_emit, 1)

  ## Reverts if called a second time
  with brownie.reverts():
    setup_aura_processor.emitBadger({"from": manager})