import brownie
from brownie import *

"""
    swapAuraToBveAuraAndEmit
    Works for both LP and Buy
    Emits event

  emitBadger
    Works
    Emits event
"""

def test_swap_aura_and_emit_with_swap(setup_aura_processor, manager, aura, bve_aura, make_aura_pool_profitable):
  # Make pool swap more proftiable
  
  bve_balance_before = bve_aura.balanceOf(setup_aura_processor.BADGER_TREE())
  assert aura.balanceOf(setup_aura_processor) > 0

  tx = setup_aura_processor.swapAURATobveAURAAndEmit({"from": manager})

  bve_supply = bve_aura.totalSupply()

  assert bve_aura.balanceOf(setup_aura_processor.BADGER_TREE()) > bve_balance_before
  assert aura.balanceOf(setup_aura_processor.BADGER_TREE()) == 0 ## All aura has been emitted

  ## We did not increase supply because we bought instead of minting
  assert bve_supply == bve_aura.totalSupply()


  ## Reverts if called a second time
  with brownie.reverts():
    setup_aura_processor.swapAURATobveAURAAndEmit({"from": manager})


def test_swap_aura_and_emit_with_deposit(setup_aura_processor, manager, aura, bve_aura, make_aura_pool_unprofitable):
  # Make pool swap less profitable
  bve_balance_before = bve_aura.balanceOf(setup_aura_processor.BADGER_TREE())
  assert aura.balanceOf(setup_aura_processor) > 0

  bve_supply = bve_aura.totalSupply()
  
  tx = setup_aura_processor.swapAURATobveAURAAndEmit({"from": manager})

  assert bve_aura.balanceOf(setup_aura_processor.BADGER_TREE()) > bve_balance_before
  assert aura.balanceOf(setup_aura_processor.BADGER_TREE()) == 0 ## All aura has been emitted
  
  ## Because we deposited, totalSupply has increased
  assert bve_aura.totalSupply() > bve_supply

  ## Reverts if called a second time
  with brownie.reverts():
    setup_aura_processor.swapAURATobveAURAAndEmit({"from": manager})


def test_emit_badger(setup_aura_processor, manager, badger):
  badger_balance_before = badger.balanceOf(setup_aura_processor.BADGER_TREE())
  assert badger.balanceOf(setup_aura_processor) > 0

  setup_aura_processor.emitBadger({"from": manager})

  assert badger.balanceOf(setup_aura_processor.BADGER_TREE()) > badger_balance_before
  assert badger.balanceOf(setup_aura_processor) == 0 ## All badger emitted

  ## Reverts if called a second time
  with brownie.reverts():
    setup_aura_processor.emitBadger({"from": manager})