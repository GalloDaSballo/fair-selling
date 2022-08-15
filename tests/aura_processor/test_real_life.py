from time import sleep
import brownie
from brownie import *
import pytest
from scripts.send_order import get_cowswap_order

LIVE_PROCESSOR = "0x8abd28e4d69bd3953b96dd9ed63533765adb9965"

EXPECT_REVERT = True

"""
  NOTE: 
  Neutrino
  T
  Worhmhole UST
  All fail at the Cowswap level
  TODO: Ack / Remove or leave as failing
"""

@pytest.fixture
def reverting_contract():
  return AuraBribesProcessor.at(LIVE_PROCESSOR)



def test_does_it_revert_with_v2_pricer(reverting_contract, weth, usdc, usdc_whale, lenient_contract):
  """
    Basic revert check to proove that V2 Pricer breaks V3 Processor
  """
  sell_amount = 123000000

  order_details = get_cowswap_order(reverting_contract, usdc, weth, sell_amount)

  usdc.transfer(reverting_contract, sell_amount, {"from": usdc_whale})


  data = order_details.order_data
  uid = order_details.order_uid

  real_manager = accounts.at(reverting_contract.manager(), force=True)

  ## Change this after governance has fixed
  if EXPECT_REVERT:
    with brownie.reverts():
      reverting_contract.sellBribeForWeth(data, uid, {"from": real_manager})

  
  ## Deploy new pricer
  new_pricer = lenient_contract

  dev_multi = accounts.at(reverting_contract.DEV_MULTI(), force=True)

  reverting_contract.setPricer(new_pricer, {"from": dev_multi})

  reverting_contract.sellBribeForWeth(data, uid, {"from": real_manager})


BRIBES_TOKEN_CLAIMABLE = [
  ("0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B", 18), ## CVX
  ("0x6B175474E89094C44Da98b954EedeAC495271d0F", 18), ## DAI
  ("0x090185f2135308bad17527004364ebcc2d37e5f6", 22), ## SPELL ## NOTE: Using 22 to adjust as spell is super high supply
  ("0xdbdb4d16eda451d0503b854cf79d55697f90c8df", 18), ## ALCX
  ("0x9D79d5B61De59D882ce90125b18F74af650acB93", 8), ## NSBT ## NOTE: Using 6 + 2 decimals to make it more
  ("0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0", 18), ## MATIC
  ("0x3432b6a60d23ca0dfca7761b7ab56459d9c964d0", 18), ## FXS
  ("0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32", 18), ## LDO
  ("0xc7283b66Eb1EB5FB86327f08e1B5816b0720212B", 18),  ## TRIBE
  ("0x8207c1FfC5B6804F6024322CcF34F29c3541Ae26", 18), ## OGN
  ("0xa3BeD4E1c75D00fa6f4E5E6922DB7261B5E9AcD2", 18), ## MTA
  ("0x31429d1856aD1377A8A0079410B297e1a9e214c2", 22), ## ANGLE ## NOTE Using 18 + 4 to raise the value
  ("0xCdF7028ceAB81fA0C6971208e83fa7872994beE5", 22), ## T ## NOTE Using 18 + 4 to raise the value
  ("0xa693B19d2931d498c5B318dF961919BB4aee87a5", 6), # UST
  ("0xB620Be8a1949AA9532e6a3510132864EF9Bc3F82", 22), ## LFT ## NOTE Using 18 + 4 to raise the value
  ("0x6243d8CEA23066d098a15582d81a598b4e8391F4", 18), ## FLX
  ("0x3Ec8798B81485A254928B70CDA1cf0A2BB0B74D7", 18), ## GRO
  ("0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6", 18), ## STG
  ("0xdB25f211AB05b1c97D595516F45794528a807ad8", 2), ## EURS
  ("0x674C6Ad92Fd080e4004b2312b45f796a192D27a0", 18), ## USDN
  ("0xFEEf77d3f69374f66429C91d732A244f074bdf74", 18), ## cvxFXS
  ("0x41D5D79431A913C4aE7d69a668ecdfE5fF9DFB68", 18)## INV
]


@pytest.fixture
def fixed_contract(lenient_contract, reverting_contract):
  new_pricer = lenient_contract

  dev_multi = accounts.at(reverting_contract.DEV_MULTI(), force=True)

  reverting_contract.setPricer(new_pricer, {"from": dev_multi})

  return reverting_contract


@pytest.mark.parametrize("token, decimals", BRIBES_TOKEN_CLAIMABLE)
def test_fixed_with_v3_pricer_token_check(fixed_contract, token, decimals, weth):
  """
    Prove that V3 Processor with V3 Pricer works for all the bribes mentioned above
  """

  real_manager = accounts.at(fixed_contract.manager(), force=True)

  sell_amount = 1000 * 10 ** decimals

  token = interface.ERC20(token)

  sleep(1) ## Wait 1 second to avoid getting timed out

  order_details = get_cowswap_order(fixed_contract, token, weth, sell_amount)
  data = order_details.order_data
  uid = order_details.order_uid

  fixed_contract.sellBribeForWeth(data, uid, {"from": real_manager})


