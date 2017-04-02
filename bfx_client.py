"""
REQUIRED PYTHON PACKAGES: websocket-client-py3

Bitfinex Ticker Data Collector implemented using web sockets.

Useful references

    https://bitfinex.readme.io/v2/reference#rest-public-tickers

    https://bitfinex.readme.io/v2/docs/ws-general


"""
import time
import ast  # used to convert string to array
import csv


import json
import hashlib
import hmac
import itertools

from websocket import create_connection

# TODO Clean up code and break up into a class with parameter options


# code to output tick data to a csv file
"""
fileName = "bfx_" + time.strftime("%Y-%m-%d", time.gmtime()) + ".csv"
csvfile = open(fileName, 'w', 1, newline='')
fieldnames = ['last_price', 'ask', 'ask_size', 'bid', 'bid_size']
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()


#code was used to run collector overnight and display if it was still alive while not displaying ticker data
currentHour = time.strftime("%H", time.gmtime()) #remove
print("Time: " + currentHour + " hr") #remove
"""

class BFXclient():

    def __init__(self):
        try:
            # establish web socket object
            self.ws = create_connection("wss://api.bitfinex.com/ws/2/")

            print("Initializing...")
            result = self.ws.recv()
            print("First Response -> %s" % result)

            print("\nSending Ping...")
            self.ws.send('{ "event": "ping" }')
            result = self.ws.recv()
            print("Response -> %s" % result)

        except:
            print("Something went wrong")



    def start_collector(self):

        print("\nSending Event Subscription...")
        input = '{"event": "subscribe","channel": "ticker","symbol": "tBTCUSD"}'
        self.ws.send(input)
        result = self.ws.recv()
        print("Response -> %s" % result)

        print("\nStarting Data Feed...\n")

        data = {}

        while (self.ws.connected):
            result = self.ws.recv()
            result2array = ast.literal_eval(result)  # convert string to array

            print("Response -> %s" % result)  # verbose

            if (result2array[1] != "hb"):  # hb = Heartbeat message
                tickDataArray = result2array[1]
                data['bid'] = tickDataArray[0]
                data['bid_size'] = tickDataArray[1]
                data['ask'] = tickDataArray[2]
                data['ask_size'] = tickDataArray[3]
                # data['daily_change'] = tickData[4]
                # data['daily_change_p'] = tickDataArray[5]
                data['last_price'] = tickDataArray[6]
                # data['vol'] = tickData[7]
                # data['high'] = tickDataArray[8]
                # data['low'] = tickDataArray[9]

                print(data)  # verbose
                print(" Time (GMT): " + time.strftime("%H:%M:%S", time.gmtime()))  # Time elapsed

                # Write ticker data to csv file
                # writer.writerow({'last_price': data['last_price'], 'ask': data['ask'], 'ask_size': data['ask_size'], 'bid': data['bid'], 'bid_size': data['bid_size']})

                """
                #code was used to run collector overnight and display if it was still alive while not displaying ticker data
                if (time.strftime("%H", time.gmtime()) != currentHour):
                    currentHour = time.strftime("%H", time.gmtime())
                    print("Time: " + currentHour + " hr")
                """

    def end(self):
        self.ws.close()
        print("closing socket connection")

    """
    @param AUTH_DATA is a String
    formatted: API_KEY::API_SECRET
    """
    def authenticate(self, AUTH_DATA=None):

        if(AUTH_DATA):
            self.API_KEY, self.API_SECRET = AUTH_DATA.split('::')
            print("\nAuthenticating...")

            self.ws.send(self.authenticate_json())
            for _ in itertools.repeat(None, 14):
                result = self.ws.recv()
                print("Response -> %s" % result)
        else:
            print("Please input your API KEY and API SECRET using the format")
            print('*.authenticate("API_KEY::API_SECRET")')


    def authenticate_json(self):
        nonce = int(time.time() * 1000000)
        auth_payload = 'AUTH{}'.format(nonce)
        signature = hmac.new(
            self.API_SECRET.encode(),
            msg=auth_payload.encode(),
            digestmod=hashlib.sha384
        ).hexdigest()

        payload = {
            'apiKey': self.API_KEY,
            'event': 'auth',
            'authPayload': auth_payload,
            'authNonce': nonce,
            'authSig': signature
        }
        return json.dumps(payload)

    def unauth(self):
        payload = {
            'event': 'unauth'
        }
        self.ws.send(json.dumps(payload))
        result = self.ws.recv()
        print("Response -> %s" % result)

    def recv(self):
        result = self.ws.recv()
        print("Response -> %s" % result)

x = BFXclient()
x.authenticate()
x.end()

#Sample Output
"""
Initializing...
First Response -> {"event":"info","version":2}

Sending Ping...
Response -> {"event":"pong"}

Authenticating...
Response -> {"event":"auth","status":"OK","chanId":0,"userId":123456,"auth_id":"o8741qn9-32q5-470n-no75-052pps2rs202","caps":{"orders":{"read":1,"write":1},"account":{"read":1,"write":0},"funding":{"read":0,"write":0},"history":{"read":1,"write":0},"wallets":{"read":0,"write":0},"withdraw":{"read":0,"write":0},"positions":{"read":0,"write":0}}}
Response -> [0,"ps",[]]
Response -> [0,"ws",[["exchange","BTC",0.21600383,0,0]]]
Response -> [0,"os",[[2211468553,null,28895134784,"tBTCUSD",1491033695179,1491033695179,-0.21600383,-0.21600383,"EXCHANGE LIMIT",null,null,null,0,"ACTIVE",null,null,1256.8,0,0,0,null,null,null,0,0,0]]]
Response -> [0,"hos",[[2154167111,null,80939082057,"tBTCUSD",1490394539157,1490394539157,-0.216,-0.216,"EXCHANGE LIMIT",null,null,null,0,"CANCELED",null,null,1249.8,0,0,0,null,null,null,0,0,0]]]
Response -> [0,"fos",[]]
Response -> [0,"fcs",[]]
Response -> [0,"fls",[]]
Response -> [0,"hts",[]]
Response -> [0,"hfts",[]]
Response -> [0,"ats",[]]
Response -> [0,"bs",[238.16582296,238.16582296]]
Response -> [0,"mis",[0,0,[["tBTCUSD",[0,0,0,0,null,null,null,null]],["tLTCUSD",[0,0,0,0,null,null,null,null]],["tLTCBTC",[0,0,0,0,null,null,null,null]],["tETHUSD",[0,0,0,0,null,null,null,null]],["tETHBTC",[0,0,0,0,null,null,null,null]],["tETCBTC",[0,0,0,0,null,null,null,null]],["tETCUSD",[0,0,0,0,null,null,null,null]],["tBFXUSD",[0,0,0,0,null,null,null,null]],["tBFXBTC",[0,0,0,0,null,null,null,null]],["tRRTUSD",[0,0,0,0,null,null,null,null]],["tRRTBTC",[0,0,0,0,null,null,null,null]],["tZECUSD",[0,0,0,0,null,null,null,null]],["tZECBTC",[0,0,0,0,null,null,null,null]],["tXMRUSD",[0,0,0,0,null,null,null,null]],["tXMRBTC",[0,0,0,0,null,null,null,null]],["tDSHUSD",[0,0,0,0,null,null,null,null]],["tDSHBTC",[0,0,0,0,null,null,null,null]],["tBCCBTC",[0,0,0,0,null,null,null,null]],["tBCUBTC",[0,0,0,0,null,null,null,null]],["tBCCUSD",[0,0,0,0,null,null,null,null]],["tBCUUSD",[0,0,0,0,null,null,null,null]]],0,0]]
Response -> [0,"fis",[null,null,[["fUSD",[0,0,0,0]],["fBTC",[0,0,0,0]],["fLTC",[0,0,0,0]],["fETH",[0,0,0,0]],["fETC",[0,0,0,0]],["fBFX",[0,0,0,0]],["fZEC",[0,0,0,0]],["fXMR",[0,0,0,0]],["fDSH",[0,0,0,0]]]]]
closing socket connection
"""