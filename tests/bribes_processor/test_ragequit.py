import brownie
from brownie import *

"""
  Unit tests for all functions
  
  Ragequit
    Anytime from manager
    After 28 days from anyone
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