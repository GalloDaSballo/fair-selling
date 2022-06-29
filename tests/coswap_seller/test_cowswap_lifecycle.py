import brownie
from brownie import *
from scripts.send_order import get_cowswap_order

"""
    Verify order
    Place order
"""

def test_verify_and_add_order(seller, usdc, weth, manager, pricer):
  sell_amount = 1000000000000000000

  ## TODO Use the Hash Map here to verify it
  order_details = get_cowswap_order(seller, weth, usdc, sell_amount)

  data = order_details.order_data
  uid = order_details.order_uid

  ## Verify that the ID Matches
  assert uid == seller.getOrderID(data)

  ## Verify that the quote is better than what we could do
  assert seller.checkCowswapOrder(data, uid)

  ## Place the order
  ## Get settlement here and check
  seller.initiateCowswapOrder(data, uid, {"from": manager})

  settlement = interface.ICowSettlement(seller.SETTLEMENT())

  assert settlement.preSignature(uid) > 0



