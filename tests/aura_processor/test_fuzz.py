import brownie
from brownie import *
from brownie.test import given, strategy
import pytest

"""
  Fuzz
    Fuzz any random address and amount
    To ensure no revert will happen
"""
LIVE_PROCESSOR = "0x8abd28e4d69bd3953b96dd9ed63533765adb9965"

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


### Sell Bribes for Weth
@given(amount=strategy("uint256"), sell_token_num=strategy("uint256"))
def test_fuzz_processing(sell_token_num, amount):

  sell_token = interface.ERC20(BRIBES_TOKEN_CLAIMABLE[sell_token_num % len(BRIBES_TOKEN_CLAIMABLE)][0])
  
  ## Skip if amt = 0
  if amount == 0:
    return True

  if str(web3.eth.getCode(str(sell_token.address))) == "b''":
    return True


  ## NOTE: Put all the fixtures here cause I keep getting reverts
  #### FIXTURES ###
  ## NOTE: We have 5% slippage on this one
  univ3simulator = UniV3SwapSimulator.deploy({"from": accounts[0]})
  balancerV2Simulator = BalancerSwapSimulator.deploy({"from": accounts[0]})
  lenient_pricer_fuzz = OnChainPricingMainnetLenient.deploy(univ3simulator.address, balancerV2Simulator.address, {"from": accounts[0]})
  lenient_pricer_fuzz.setSlippage(499, {"from": accounts.at(lenient_pricer_fuzz.TECH_OPS(), force=True)})

  setup_processor = AuraBribesProcessor.at(LIVE_PROCESSOR)

  dev_multi = accounts.at(setup_processor.DEV_MULTI(), force=True)
  setup_processor.setPricer(lenient_pricer_fuzz, {"from": dev_multi})

  
  settlement_fuzz = interface.ICowSettlement(setup_processor.SETTLEMENT())

  fee_amount = amount * 0.01
  data = [
        sell_token, 
        setup_processor.WETH(),  ## Can only buy WETH here
        setup_processor.address, 
        amount-fee_amount,
        1.1579209e76, ## 2^256-1 / 10 so it passes
        4294967294,
        "0x2B8694ED30082129598720860E8E972F07AA10D9B81CAE16CA0E2CFB24743E24",
        fee_amount,
        setup_processor.KIND_SELL(),
        False,
        setup_processor.BALANCE_ERC20(),
        setup_processor.BALANCE_ERC20()
    ]

  """
    SKIP to avoid revert on these cases

    require(orderData.sellToken != AURA); // Can't sell AURA;
    require(orderData.sellToken != BADGER); // Can't sell BADGER either;
    require(orderData.sellToken != WETH); // Can't sell WETH
    require(orderData.buyToken == WETH); // Gotta Buy WETH;
  """

  if sell_token == setup_processor.AURA():
    return True
  if sell_token == setup_processor.BADGER():
    return True
  if sell_token == setup_processor.WETH():
    return True
  if sell_token == setup_processor.AURA():
    return True

  
  uid = setup_processor.getOrderID(data)


  tx = setup_processor.sellBribeForWeth(data, uid, {"from": accounts.at(setup_processor.manager(), force=True)})

  print("real test")

  assert settlement_fuzz.preSignature(uid) > 0