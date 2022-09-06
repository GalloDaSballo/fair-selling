from time import time
import requests
from brownie import *
import click
from rich.console import Console
from dotmap import DotMap

console = Console()

DEV_MULTI = "0xB65cef03b9B89f99517643226d76e286ee999e77"
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

SLIPPAGE = 0.98 ## 2%

def main():
    """
        DEMO ORDER
        Customize to use it for real life usage
    """
    dev  = connect_account()

    seller = CowSwapDemoSeller.at("0x75547825A99283379e0E812B7c10F832813326d6")

    usdc = interface.ERC20(USDC)
    weth = interface.ERC20(WETH)

    amount = usdc.balanceOf(seller)

    order_data = get_cowswap_order(seller, usdc, weth, amount)

    data = order_data.order_data
    uid = order_data.order_uid

    seller.initiateCowswapOrder(data, uid, {"from": dev})


def get_cowswap_order(contract, sell_token, buy_token, amount_in):
    """
        Get quote, place order and return orderData as well as orderUid
    """
    amount =    amount_in

    # get the fee + the buy amount after fee
    ## TODO: Refactor to new, better endpoint: https://discord.com/channels/869166959739170836/935460632818516048/953702376345309254
    fee_and_quote = "https://api.cow.fi/mainnet/api/v1/feeAndQuote/sell"
    get_params = {
        "sellToken": sell_token.address,
        "buyToken": buy_token.address,
        "sellAmountBeforeFee": amount_in
    }
    r = requests.get(fee_and_quote, params=get_params)
    assert r.ok and r.status_code == 200

    # These two values are needed to create an order
    fee_amount = int(r.json()['fee']['amount'])
    buy_amount_after_fee = int(r.json()['buyAmountAfterFee'])
    assert fee_amount > 0
    assert buy_amount_after_fee > 0

    deadline = chain.time() + 60*60*1 # 1 hour

    # Submit order
    order_payload = {
        "sellToken": sell_token.address,
        "buyToken": buy_token.address,
        "sellAmount": str(amount-fee_amount), # amount that we have minus the fee we have to pay
        "buyAmount": str(buy_amount_after_fee), # buy amount fetched from the previous call
        "validTo": deadline,
        "appData": "0x2B8694ED30082129598720860E8E972F07AA10D9B81CAE16CA0E2CFB24743E24", # maps to https://bafybeiblq2ko2maieeuvtbzaqyhi5fzpa6vbbwnydsxbnsqoft5si5b6eq.ipfs.dweb.link
        "feeAmount": str(fee_amount),
        "kind": "sell",
        "partiallyFillable": False,
        "receiver": contract.address,
        "signature": contract.address,
        "from": contract.address,
        "sellTokenBalance": "erc20",
        "buyTokenBalance": "erc20",
        "signingScheme": "presign" # Very important. this tells the api you are going to sign on chain
    }
    orders_url = f"https://api.cow.fi/mainnet/api/v1/orders"
    r = requests.post(orders_url, json=order_payload)
    assert r.ok and r.status_code == 201
    order_uid = r.json()
    print(f"Payload: {order_payload}")
    print(f"Order uid: {order_uid}")
    
    order_data = [
        sell_token.address, 
        buy_token.address, 
        contract.address, 
        amount-fee_amount,
        buy_amount_after_fee,
        deadline,
        "0x2B8694ED30082129598720860E8E972F07AA10D9B81CAE16CA0E2CFB24743E24",
        fee_amount,
        contract.KIND_SELL(),
        False,
        contract.BALANCE_ERC20(),
        contract.BALANCE_ERC20()
    ]

    return DotMap(
        order_data=order_data,
        order_uid=order_uid,
        sellToken=sell_token.address,
        buyToken=buy_token.address,
        receiver=contract.address,
        sellAmount=amount-fee_amount,
        buyAmount=buy_amount_after_fee,
        validTo=deadline,
        appData="0x2B8694ED30082129598720860E8E972F07AA10D9B81CAE16CA0E2CFB24743E24",
        feeAmount=fee_amount,
        kind=contract.KIND_SELL(),
        partiallyFillable=False,
        sellTokenBalance=contract.BALANCE_ERC20(),
        buyTokenBalance=contract.BALANCE_ERC20()
    )


def cowswap_sell_demo(contract, sell_token, buy_token, amount_in):
    """
        Demo of placing order and verifying it
    """
    amount = amount_in
    
    # get the fee + the buy amount after fee
    ## TODO: Refactor to new, better endpoint: https://discord.com/channels/869166959739170836/935460632818516048/953702376345309254
    fee_and_quote = "https://api.cow.fi/mainnet/api/v1/feeAndQuote/sell"
    get_params = {
        "sellToken": sell_token.address,
        "buyToken": buy_token.address,
        "sellAmountBeforeFee": amount
    }
    r = requests.get(fee_and_quote, params=get_params)
    assert r.ok and r.status_code == 200

    # These two values are needed to create an order
    fee_amount = int(r.json()['fee']['amount'])
    buy_amount_after_fee = int(r.json()['buyAmountAfterFee'])
    assert fee_amount > 0
    assert buy_amount_after_fee > 0

    # Pretty random order deadline :shrug:
    deadline = chain.time() + 60*60*1 # 1 hour

    # Submit order
    order_payload = {
        "sellToken": sell_token.address,
        "buyToken": buy_token.address,
        "sellAmount": str(amount-fee_amount), # amount that we have minus the fee we have to pay
        "buyAmount": str(buy_amount_after_fee * SLIPPAGE), # buy amount fetched from the previous call
        "validTo": deadline,
        "appData": "0x2B8694ED30082129598720860E8E972F07AA10D9B81CAE16CA0E2CFB24743E24", # maps to https://bafybeiblq2ko2maieeuvtbzaqyhi5fzpa6vbbwnydsxbnsqoft5si5b6eq.ipfs.dweb.link
        "feeAmount": str(fee_amount),
        "kind": "sell",
        "partiallyFillable": False,
        "receiver": contract.address,
        "signature": contract.address,
        "from": contract.address,
        "sellTokenBalance": "erc20",
        "buyTokenBalance": "erc20",
        "signingScheme": "presign" # Very important. this tells the api you are going to sign on chain
    }
    orders_url = f"https://api.cow.fi/mainnet/api/v1/orders"
    r = requests.post(orders_url, json=order_payload)
    assert r.ok and r.status_code == 201
    order_uid = r.json()
    print(f"Payload: {order_payload}")
    print(f"Order uid: {order_uid}")
    
    # IERC20 sellToken;
    # IERC20 buyToken;
    # address receiver;
    # uint256 sellAmount;
    # uint256 buyAmount;
    # uint32 validTo;
    # bytes32 appData;
    # uint256 feeAmount;
    # bytes32 kind;
    # bool partiallyFillable;
    # bytes32 sellTokenBalance;
    # bytes32 buyTokenBalance;
    order_data = [
        sell_token.address, 
        buy_token.address, 
        contract.address, 
        amount-fee_amount,
        buy_amount_after_fee,
        deadline,
        "0x2B8694ED30082129598720860E8E972F07AA10D9B81CAE16CA0E2CFB24743E24",
        fee_amount,
        contract.KIND_SELL(),
        False,
        contract.BALANCE_ERC20(),
        contract.BALANCE_ERC20()
    ]

    hashFromContract = contract.getHash(order_data, contract.domainSeparator())
    print(f"Hash from Contract: {hashFromContract}")
    fromContract = contract.getOrderID(order_data)
    print(f"Order uid from Contract: {fromContract}")

    contract.checkCowswapOrder(order_data, order_uid)
    return order_uid

    ## TODO Refactor to return hash map with all the fields


def connect_account():
    click.echo(f"You are using the '{network.show_active()}' network")
    dev = accounts.load(click.prompt("Account", type=click.Choice(accounts.load())))
    click.echo(f"You are using: 'dev' [{dev.address}]")
    return dev
