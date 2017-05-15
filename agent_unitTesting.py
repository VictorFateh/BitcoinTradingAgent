
from agents import *

"""
a_m = TestAgent_marketOrdersOnly()
e = ExchangeSimulator()
e.setAgent(a_m)
print("\nRunning Exchange Simulation Testbench")
print("\nTesting Market Orders Test Agent")
print("Agent starts out with 1 btc and 0 usd")
print("btc:", 1)
print("usd:",0)
e.run()
"""

"""
a_l = TestAgent_limitOrdersOnly()
e_ = ExchangeSimulator()
e.setAgent(a_l)
print("\nRunning Exchange Simulation Testbench")
print("\nTesting Limit Orders Test Agent")
print("Agent starts out with 1 btc and 0 usd")
print("btc:", 1)
print("usd:",0)
e.run()
"""




m = PerformanceTracker()
short = 225
long = 231
a = Agent_MarketOrdersOnly(short, long)
e = ExchangeSimulator('bfx_data/bfx_2017-03-25.csv')
e.setAgent(a)
e.run()
x = e.returnFinalResults()
m.insert_results(x)
m.get_results()

# Bruteforce optimal parameters
"""
print("Uptrend_Results")
m = PerformanceTracker()
short = 100
short_reset = short
long = 250
e = ExchangeSimulator('bfx_data/bfx_2017-03-25.csv')
while(long >= short_reset):
    print("\ntesting long:",long)
    while(short < long):
        a = Agent_MarketOrdersOnly(short,long)
        #e = ExchangeSimulator()
        e.setAgent(a)
        #print("\nRunning Exchange Simulation Testbench")
        e.run()
        x = e.returnFinalResults()
        m.insert_results( x )
        short+=1
    long -= 1
    short = short_reset

print("Best EMA Parameters")
m.get_results()

print("Downtrend_Results")
m = PerformanceTracker()
short = 100
short_reset = short
long = 250
e = ExchangeSimulator('bfx_data/bfx_2017-03-25_reversed.csv')
while(long >= short_reset):
    print("\ntesting long:",long)
    while(short < long):
        a = Agent_MarketOrdersOnly(short,long)
        #e = ExchangeSimulator()
        e.setAgent(a)
        #print("\nRunning Exchange Simulation Testbench")
        e.run()
        x = e.returnFinalResults()
        m.insert_results( x )
        short+=1
    long -= 1
    short = short_reset

print("Best EMA Parameters")
m.get_results()
"""