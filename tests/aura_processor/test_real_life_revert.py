import brownie
from brownie import *
import pytest

LIVE_PROCESSOR = "0xC66C9F87d847dDc964724B789D3113885b08efCF"

@pytest.fixture
def reverting_contract():
  return AuraBribesProcessor.at(LIVE_PROCESSOR)


@pytest.fixture
def live_pricer(reverting_contract):
  return reverting_contract.pricer()

@pytest.fixture
def fixed_contract(live_pricer, reverting_contract, manager, aura, aura_whale):
  
  ## Deploy
  p = AuraBribesProcessor.deploy(live_pricer, {"from": manager})


  amount_to_test = aura.balanceOf(reverting_contract)

  ## Send some aura
  aura.transfer(p, amount_to_test, {"from": aura_whale})

  return p



def test_compare_live_to_fix(reverting_contract, fixed_contract, manager, aura, bve_aura, aura_whale):
  live_manager = accounts.at(reverting_contract.manager(), force=True)

  with brownie.reverts():
    reverting_contract.swapAURATobveAURAAndEmit({"from": live_manager})

  tree = fixed_contract.BADGER_TREE()
  prev_bal = bve_aura.balanceOf(tree)

  assert aura.balanceOf(fixed_contract) > 0

  fixed_contract.swapAURATobveAURAAndEmit({"from": manager})
  after_bal = bve_aura.balanceOf(tree)

  ## Net increase
  assert after_bal > prev_bal

  ## TODO: Proper exact math to make sure no value was leaked
  
