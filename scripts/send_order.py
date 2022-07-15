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

## keccak256("sell")
KIND_KILL = '0xf3b277728b3fee749481eb3e0b3b48980dbbab78658fc419025cb16eee346775'
## keccak256("erc20")
BALANCE_ERC20 = '0x5a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc9'

def main():
    pricer = OnChainPricingMainnet.deploy({"from": a[0]})

    c = CowSwapDemoSeller.deploy(pricer, {"from": a[0]})

    usdc = interface.ERC20(USDC)
    weth = interface.ERC20(WETH)

    amount = 1000000000000000000

    cowswap_sell_demo(c, weth, usdc, amount, a[0])
    
def get_cowswap_order(contract, sell_token, buy_token, amount_in):
    """
        Get quote, place order and return orderData as well as orderUid
    """
    receiver = contract.address
    validTo = chain.time()
    appData = "0x2B8694ED30082129598720860E8E972F07AA10D9B81CAE16CA0E2CFB24743E24" # maps to https://bafybeiblq2ko2maieeuvtbzaqyhi5fzpa6vbbwnydsxbnsqoft5si5b6eq.ipfs.dweb.link
    return get_cowswap_order_with_receiver_deadline_appdata(contract, sell_token, buy_token, amount_in, receiver, validTo, appData)

def get_cowswap_order_with_receiver_deadline_appdata(contract, sell_token, buy_token, amount_in, receiver, validTo, appData):
    """
        Get quote with specific receiver/deadline/appData, place order and return orderData as well as orderUid
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

    deadline = validTo + 60*60*1 # plus 1 hour

    # Submit order
    order_payload = {
        "sellToken": sell_token.address,
        "buyToken": buy_token.address,
        "sellAmount": str(amount-fee_amount), # amount that we have minus the fee we have to pay
        "buyAmount": str(buy_amount_after_fee), # buy amount fetched from the previous call
        "validTo": deadline,
        "appData": appData,
        "feeAmount": str(fee_amount),
        "kind": "sell",
        "partiallyFillable": False,
        "receiver": receiver,
        "signature": contract.address,
        "from": contract.address,
        "sellTokenBalance": "erc20",
        "buyTokenBalance": "erc20",
        "signingScheme": "presign" # Very important. this tells the api you are going to sign on chain
    }
    orders_url = f"https://api.cow.fi/mainnet/api/v1/orders"
    r = requests.post(orders_url, json=order_payload)
    print(f"Response: {r} and Payload: {order_payload}")
    assert r.ok and r.status_code == 201
    order_uid = r.json()
    print(f"Order uid: {order_uid}")
    
    order_data = [
        sell_token.address, 
        buy_token.address, 
        receiver, 
        amount-fee_amount,
        buy_amount_after_fee,
        deadline,
        appData,
        fee_amount,
        KIND_KILL,
        False,
        BALANCE_ERC20,
        BALANCE_ERC20
    ]

    return DotMap(
        order_data=order_data,
        order_uid=order_uid,
        sellToken=sell_token.address,
        buyToken=buy_token.address,
        receiver=receiver,
        sellAmount=amount-fee_amount,
        buyAmount=buy_amount_after_fee,
        validTo=deadline,
        appData=appData,
        feeAmount=fee_amount,
        kind=KIND_KILL,
        partiallyFillable=False,
        sellTokenBalance=BALANCE_ERC20,
        buyTokenBalance=BALANCE_ERC20
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
