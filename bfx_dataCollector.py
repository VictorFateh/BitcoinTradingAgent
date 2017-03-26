"""
REQUIRED PYTHON PACKAGES: websocket-client-py3

Bitfinex Ticker Data Collector implemented using web sockets.

Useful references

    https://bitfinex.readme.io/v2/reference#rest-public-tickers
    
    https://bitfinex.readme.io/v2/docs/ws-general


"""


import time
import ast #used to convert string to array
import csv

from websocket import create_connection

#TODO Clean up code and break up into a class with parameter options


#code to output tick data to a csv file
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

try:
    # establish web socket object
    ws = create_connection("wss://api.bitfinex.com/ws/2/")


    print ("Initializing...")
    result =  ws.recv()
    print ("First Response -> %s" % result)


    print("\nSending Ping...")
    ws.send('{ "event": "ping" }')
    result =  ws.recv()
    print ("Response -> %s" % result)


    print("\nSending Event Subscription...")
    input = '{"event": "subscribe","channel": "ticker","symbol": "tBTCUSD"}'
    ws.send(input)
    result =  ws.recv()
    print ("Response -> %s" % result)


    print ("\nStarting Data Feed...\n")

    data = {}

    while(1):
        result =  ws.recv()
        result2array = ast.literal_eval(result) # convert string to array

        print ("Response -> %s" % result) # verbose

        if(result2array[1] != "hb"): # hb = Heartbeat message
            tickDataArray = result2array[1]
            data['bid'] = tickDataArray[0]
            data['bid_size'] = tickDataArray[1]
            data['ask'] = tickDataArray[2]
            data['ask_size'] = tickDataArray[3]
            #data['daily_change'] = tickData[4]
            #data['daily_change_p'] = tickDataArray[5]
            data['last_price'] = tickDataArray[6]
            #data['vol'] = tickData[7]
            #data['high'] = tickDataArray[8]
            #data['low'] = tickDataArray[9]

            print(data) # verbose
            print(" Time (GMT): " + time.strftime("%H:%M:%S", time.gmtime())) # Time elapsed

            # Write ticker data to csv file
            #writer.writerow({'last_price': data['last_price'], 'ask': data['ask'], 'ask_size': data['ask_size'], 'bid': data['bid'], 'bid_size': data['bid_size']})

            """
            #code was used to run collector overnight and display if it was still alive while not displaying ticker data
            if (time.strftime("%H", time.gmtime()) != currentHour):
                currentHour = time.strftime("%H", time.gmtime())
                print("Time: " + currentHour + " hr")
            """



except:
    ws.close()
    print("Something went wrong Captain...")

ws.close()
print("Web Socket connection closed...")