"""
    temporary prototype to scrape data from exchange to start work on visualizer
    still incomplete, will work on it later
"""


from Api_analyzer import *

import time

def tickerBot(prevMinute, sleepSeconds, updateInterval):
    if(time.time() - prevMinute) < updateInterval:
        data = json.loads(json.dumps(query_ticker()))
        print('last trade: %0.2f' % data['ltp']) # ltp = last traded price
        print('prevMinute: %0.2f' % prevMinute)  # would like to convert time to database timestamp format
        time.sleep( sleepSeconds )  # to be gentle with the bandwidth
        return prevMinute
    else:
        return time.time()







print (query_ticker() )

data = json.loads( json.dumps(query_get_ticker() ) )

print( data['product_code'] )





prevMinute = time.time()

while (True):
    prevMinute = tickerBot(prevMinute, 2, 60)

