import brownie
from brownie import *
from scripts.send_order import get_cowswap_order

"""
  sellBribeForWeth
    Can't sell badger
    Can't sell AURA
    Works for only X to ETH
"""


### Sell Bribes for Weth

def test_sell_bribes_for_weth_cant_sell_badger(setup_aura_processor, badger, weth, manager):
  sell_amount = 10000000000000000000

  order_details = get_cowswap_order(setup_aura_processor, badger, weth, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  with brownie.reverts():
    setup_aura_processor.sellBribeForWeth(data, uid, {"from": manager})

def test_sell_bribes_for_weth_cant_sell_aura(setup_aura_processor, weth, manager, aura):
  sell_amount = 10000000000000000000000

  order_details = get_cowswap_order(setup_aura_processor, aura, weth, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  with brownie.reverts():
    setup_aura_processor.sellBribeForWeth(data, uid, {"from": manager})


def test_sell_bribes_for_weth_works_when_selling_usdc_for_weth(setup_aura_processor, usdc, weth, manager, settlement):
  sell_amount = 1000000000

  order_details = get_cowswap_order(setup_aura_processor, usdc, weth, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  setup_aura_processor.sellBribeForWeth(data, uid, {"from": manager})

  assert settlement.preSignature(uid) > 0

def test_sell_bribes_for_weth_must_buy_weth_cant_sell_weth(setup_aura_processor, usdc, weth, aura, manager, settlement):
  """
    Must buy WETH
    Can't sell WETH
  """
  sell_amount = 100000000000000000000

  order_details = get_cowswap_order(setup_aura_processor, weth, usdc, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid
  
  with brownie.reverts():
    setup_aura_processor.sellBribeForWeth(data, uid, {"from": manager})


  order_details = get_cowswap_order(setup_aura_processor, weth, usdc, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  data[1] = weth.address ## Data.sellToken

  ## Fails because UID is also invalid (Can't get API order of WETH-WETH)
  with brownie.reverts():
    setup_aura_processor.sellBribeForWeth(data, uid, {"from": manager})


