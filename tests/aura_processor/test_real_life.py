import brownie
from brownie import *
import pytest
from scripts.send_order import get_cowswap_order

LIVE_PROCESSOR = "0x8abd28e4d69bd3953b96dd9ed63533765adb9965"

@pytest.fixture
def reverting_contract():
  return AuraBribesProcessor.at(LIVE_PROCESSOR)


def test_does_it_revert_with_v2_pricer(reverting_contract, manager, weth, usdc, usdc_whale, lenient_contract):
  
  sell_amount = 123000000

  order_details = get_cowswap_order(reverting_contract, usdc, weth, sell_amount)

  usdc.transfer(reverting_contract, sell_amount, {"from": usdc_whale})


  data = order_details.order_data
  uid = order_details.order_uid

  real_manager = accounts.at(reverting_contract.manager(), force=True)

  with brownie.reverts():
    reverting_contract.sellBribeForWeth(data, uid, {"from": real_manager})

  
  ## Deploy new pricer
  new_pricer = lenient_contract

  dev_multi = accounts.at(reverting_contract.DEV_MULTI(), force=True)

  reverting_contract.setPricer(new_pricer, {"from": dev_multi})

  reverting_contract.sellBribeForWeth(data, uid, {"from": real_manager})

    
  
