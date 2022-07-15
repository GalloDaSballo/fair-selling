import brownie
from brownie import *
import pytest

from scripts.send_order import get_cowswap_order, get_cowswap_order_with_receiver_deadline_appdata

"""
    Verify order
    Place order
"""
## @pytest.mark.skip(reason="VERIFYANDPLACEORDER")
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

"""
    CowSwapProcessor: request and submit order
"""
## @pytest.mark.skip(reason="REQUESTANDSUBMITORDER")
def test_processor_request_and_submit(cowprocessor, usdc, wbtc, manager, wbtc_whale):
  sell_amount = 100000000
   
  ## approve token to CowSwapProcessor in advance
  wbtc.approve(cowprocessor.address, sell_amount * 10000, {'from': wbtc_whale})
  cowprocessor.setRequesters(wbtc_whale.address, True, {"from": manager})
  
  ## enqueue order request which will transfer token from requester to CowSwapProcessor
  requestTx = cowprocessor.requestCowSwapOrder(wbtc.address, usdc.address, sell_amount, {'from': wbtc_whale})
  requestAppData = requestTx.return_value[0]
  requestDeadline = requestTx.return_value[1]

  ## submit off-chain order to cowswap
  assert cowprocessor.queuedRequestCount() > 0
  order_details = get_cowswap_order_with_receiver_deadline_appdata(cowprocessor, wbtc, usdc, sell_amount, wbtc_whale.address, requestDeadline, str(requestAppData))

  data = order_details.order_data
  uid = order_details.order_uid  
  
  receiver = order_details.receiver
  assert receiver == wbtc_whale.address
  
  appData = order_details.appData
  assert appData == requestAppData

  ## finalize the order signing on-chain
  ## notice this may take a while,
  ## to avoid timeout, increase the timeout parameter of fork network:
  ## brownie networks modify mainnet-fork timeout=240
  cowprocessor.submitCowSwapOrder(data, uid, {"from": manager})
  assert cowprocessor.queuedRequestCount() == 0

  ## ensure the order submitted successfully to CowSwap solver
  settlement = interface.ICowSettlement('0x9008D19f58AAbD9eD0D60971565AA8510560ab41')
  assert settlement.preSignature(uid) > 0
    
"""
    CowSwapProcessor: in case order request failed to execute, we need to return the fund
"""
## @pytest.mark.skip(reason="RETURNFUND")
def test_processor_return_fund(cowprocessor, usdc, wbtc, manager, wbtc_whale):
  sell_amount = 100000000
   
  ## approve token to CowSwapProcessor in advance
  wbtc.approve(cowprocessor.address, sell_amount * 10000, {'from': wbtc_whale})
  cowprocessor.setRequesters(wbtc_whale.address, True, {"from": manager})
  
  ## enqueue order request which will transfer token from requester to CowSwapProcessor
  requestTx = cowprocessor.requestCowSwapOrder(wbtc.address, usdc.address, sell_amount, {'from': wbtc_whale})
  requestAppData = requestTx.return_value[0]
  
  ## move chain time to make the order request expire
  now = chain.time()
  assert cowprocessor.queuedRequestCount() > 0
  chain.mine(1, now + 7200)
  
  ## return the fund to requester
  balBefore = wbtc.balanceOf(wbtc_whale.address)
  cowprocessor.incaseOrderExpired(requestAppData, {'from': manager})
  balAfter = wbtc.balanceOf(wbtc_whale.address)
  assert cowprocessor.queuedRequestCount() == 0
  assert (balAfter - balBefore) == sell_amount

  


