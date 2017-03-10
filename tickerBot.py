"""
    temporary prototype to scrape data from exchange to start work on visualizer
    still incomplete, will work on it later
"""


from Api_analyzer import *

import time, sys

"""
def tickerBot(prevMinute, sleepSeconds, updateInterval):
    if(time.time() - prevMinute) < updateInterval:
        data = json.loads(json.dumps(query_ticker()))
        print('last trade: %0.2f' % data['ltp']) # ltp = last traded price
        print('prevMinute: %0.2f' % prevMinute)  # would like to convert time to database timestamp format
        time.sleep( sleepSeconds )  # to be gentle with the bandwidth
        return prevMinute
    else:
        return time.time()
"""






print (query_ticker() )

data = json.loads( json.dumps(query_get_ticker() ) )

print( data['product_code'] )

def timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())





"""
    TickerBot generates json ticker data for bitFlyer exchange
    Currently tracks price data for minute intervals
    Every minute, it will output a json encoded
    o = opening price of time interval
    h = high price of time interval
    l = low price of time interval
    c = closing price of time interval
    t = timestamp
"""

# TODO Need to implement logic if the bot receives a null response from exchange
# TODO Need to modify IF ELSE logic to work differently as right now there is a drift in seconds per timestamp
def tickerBot(sleepSeconds, verbose = True, updateInterval = 60):

    #is this needed?
    if (updateInterval % sleepSeconds) != 0:
        print("TickerBot: Error Detected!")
        print("updateInterval mod sleepSeconds != 0")
        print('updateInterval = %i' % updateInterval)
        print('sleepSeconds = %i' % sleepSeconds)
        sys.exit(0)

    #synchronize clock
    while (time.strftime("%S", time.gmtime()) != "00"):
        if verbose:
            print("waiting to synchronize")
            print(timestamp())
        time.sleep(1)



    data = json.loads(json.dumps(query_get_ticker()))
    prevMinute = time.time()
    ohlc = {'o': data['ltp'], 'h': data['ltp'], 'l': data['ltp'], 'c': data['ltp'], 't':timestamp()}

    if verbose:
        print ("tickerBot initialized.")

    while (True):

        if(time.time() - prevMinute) < updateInterval:
            data = json.loads(json.dumps(query_ticker()))

            if data['ltp'] > ohlc['h']:
                ohlc['h'] = data['ltp']

            if data['ltp'] < ohlc['l']:
                ohlc['l'] = data['ltp']


            ohlc['c'] = data['ltp']

            time.sleep( sleepSeconds )  # to be gentle with the bandwidth
        else:
            print( json.dumps( ohlc ) )
            ohlc = {'o': data['ltp'], 'h': data['ltp'], 'l': data['ltp'], 'c': data['ltp'], 't':timestamp()}
            prevMinute = time.time()

tickerBot(2)


#TODO implement a different tickerBot that tracks the current price and the amount of time it took till the price changed. This will be more effective for backtesting?

