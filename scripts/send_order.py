from time import time
import requests
from brownie import *
import click
from rich.console import Console

console = Console()

DEV_MULTI = "0xB65cef03b9B89f99517643226d76e286ee999e77"
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

def main():
    c = CowSwapSeller.deploy(a[0], {"from": a[0]})

    usdc = interface.ERC20(USDC)
    weth = interface.ERC20(WETH)

    amount = 1000000000000000000

    cowswap_sell(c, weth, usdc, amount, a[0])

def cowswap_sell(contract, sell_token, buy_token, amount_in, dev):
    amount = amount_in
    
    # get the fee + the buy amount after fee
    fee_and_quote = "https://protocol-mainnet.gnosis.io/api/v1/feeAndQuote/sell"
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
    deadline = chain.time() + 60*60*24*100 # 100 days

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
    orders_url = f"https://protocol-mainnet.gnosis.io/api/v1/orders"
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
        str(amount-fee_amount),
        str(buy_amount_after_fee),
        deadline,
        "0x2B8694ED30082129598720860E8E972F07AA10D9B81CAE16CA0E2CFB24743E24",
        str(fee_amount),
        contract.stringToBytes32("sell"),
        False,
        contract.stringToBytes32("erc20"),
        contract.stringToBytes32("erc20")
    ]

    fromContract = contract.getOrderID(order_data)
    print(f"Order uid from Contract: {fromContract}")


    return order_uid


def connect_account():
    click.echo(f"You are using the '{network.show_active()}' network")
    dev = accounts.load(click.prompt("Account", type=click.Choice(accounts.load())))
    click.echo(f"You are using: 'dev' [{dev.address}]")
    return dev
