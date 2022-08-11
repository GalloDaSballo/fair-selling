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



def test_compare_live_to_fix(reverting_contract, fixed_contract, manager, aura, bve_aura):
  """
    Demonstrate revert in old code
    Shows new code won't revert
    Proves math equivalence via exact amount sent to tree
  """
  live_manager = accounts.at(reverting_contract.manager(), force=True)

  ## Setup
  tree = fixed_contract.BADGER_TREE()
  prev_bal = bve_aura.balanceOf(tree)

  bve_sett = interface.ISettV4(fixed_contract.BVE_AURA())

  ## Math for expected number of tokens out from vault
  prev_bal = bve_aura.balanceOf(tree)

  aura_to_process =  aura.balanceOf(fixed_contract)

  assert aura_to_process > 0

  ops_fee = aura_to_process * fixed_contract.OPS_FEE() // fixed_contract.MAX_BPS()

  expected_bve_aura_to_tree = (aura_to_process - ops_fee) * bve_sett.totalSupply() // bve_sett.balance()

  
  ## Show revert on live ## NOTE: This may stop reverting for external reasons
  with brownie.reverts():
    reverting_contract.swapAURATobveAURAAndEmit({"from": live_manager})
  


  ## Run fixed and check
  fixed_contract.swapAURATobveAURAAndEmit({"from": manager})
  after_bal = bve_aura.balanceOf(tree)

  ## Net increase
  assert after_bal > prev_bal

  ## Proper exact math to make sure no value was leaked
  assert after_bal - prev_bal == expected_bve_aura_to_tree
  
