import brownie
from brownie import *
from scripts.send_order import get_cowswap_order


"""
    swapAuraToBveAuraAndEmit
    Works for both LP and Buy
    Emits event

  emitBadger
    Works
    Emits event
"""

def test_swap_cvx_and_emit(setup_aura_processor, manager, aura, bve_aura):
  bve_balance_before = bve_aura.balanceOf(setup_aura_processor.BADGER_TREE())
  assert aura.balanceOf(setup_aura_processor) > 0

  setup_aura_processor.swapAURAtobveAURAAndEmit({"from": manager})

  assert bve_aura.balanceOf(setup_aura_processor.BADGER_TREE()) > bve_balance_before
  assert aura.balanceOf(setup_aura_processor.BADGER_TREE()) == 0 ## All CVX has been emitted


  ## Reverts if called a second time
  with brownie.reverts():
    setup_aura_processor.swapAURAtobveAURAAndEmit({"from": manager})

def test_emit_badger(setup_aura_processor, manager, badger):
  badger_balance_before = badger.balanceOf(setup_aura_processor.BADGER_TREE())
  assert badger.balanceOf(setup_aura_processor) > 0

  setup_aura_processor.emitBadger({"from": manager})

  assert badger.balanceOf(setup_aura_processor.BADGER_TREE()) > badger_balance_before
  assert badger.balanceOf(setup_aura_processor) == 0 ## All badger emitted

  ## Reverts if called a second time
  with brownie.reverts():
    setup_aura_processor.emitBadger({"from": manager})