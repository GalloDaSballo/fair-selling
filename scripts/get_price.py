import requests
from brownie import *

import json

"""
    Get quote for token by given id(/coin/list) from coingecko api https://www.coingecko.com/en/api/documentation
"""
def get_coingecko_price(coinID):
    quote_denomination = 'usd'
    
    quote = "https://api.coingecko.com/api/v3/simple/price"
    get_params = {
        "ids": coinID,
        "vs_currencies": quote_denomination
    }
    r = requests.get(quote, params=get_params)
    assert r.ok and r.status_code == 200

    price = float(r.json()[coinID][quote_denomination])
    assert price > 0
    
    return price
    
"""
    Get quote for token by given id(from metadata) from coinmarketcap api https://coinmarketcap.com/api/documentation
"""
def get_coinmarketcap_price(coinID, apiKey):
    quote_denomination = 'USD'
    
    quote = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
    get_params = {
        "id": coinID,
        "convert": quote_denomination
    }    
    get_headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': apiKey,
    }

    r = requests.get(quote, params=get_params, headers=get_headers)
    assert r.ok and r.status_code == 200

    price = float(r.json()['data'][coinID]['quote'][quote_denomination]['price'])
    assert price > 0
    
    return price
    
"""
    Get quote for token by given slug(/coin/list) from coinmarketcap api https://coinmarketcap.com/api/documentation
"""
def get_coinmarketcap_metadata(coinSlug, apiKey):    
    quote = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/info"
    get_params = {
        "slug": coinSlug
    }    
    get_headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': apiKey,
    }

    r = requests.get(quote, params=get_params, headers=get_headers)
    print(json.dumps(json.loads(r.text), indent = 2))
    assert r.ok and r.status_code == 200
    
    return r.text