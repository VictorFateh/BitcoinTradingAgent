#A utiliy file to 

import json
from urllib.request import urlopen

ticker_api_url = "http://api.bitflyer.jp/v1/ticker"
get_ticket_api_url = "http://api.bitflyer.jp/v1/getticker"

def get_ticket_data():
    response = urlopen(ticker_api_url).read().decode('utf-8')
    response_json = json.loads(response)
    return response_json

