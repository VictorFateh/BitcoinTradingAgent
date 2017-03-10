#A utiliy file to provide api query functionality

import json
from urllib.request import urlopen

api_urls = {    'ticker' : "http://api.bitflyer.jp/v1/ticker",
                'get_ticker' : "http://api.bitflyer.jp/v1/getticker"}

product_codes = ["BTC_JPY", "FX_BTC_JPY", "ETH_BTC"]
get_query = "?product_code="


# Accepts a string for the URL of the API 
# Returns a json reponse in the format of a dictionary
def query_api(api):
    response = urlopen(api).read().decode('utf-8')
    response_json = json.loads(response)
    return response_json


def query_ticker(product_code="FX_BTC_JPY"):
    api = api_urls['ticker'] + get_query + product_code
    return query_api(api)

def query_get_ticker(product_code="FX_BTC_JPY"):
    api = api_urls['get_ticker'] + get_query + product_code
    return query_api(api_urls['get_ticker'])

#Sample code to test functionality of query 
while(True):
    print(query_ticker())
    
