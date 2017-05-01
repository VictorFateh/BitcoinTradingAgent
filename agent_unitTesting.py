from agent_exchangeSim import *

"""" ORDER TESTING
d = Order(BUY,LIMIT_POST,14,100)
a = Order(BUY,LIMIT_POST,11,100)
c = Order(BUY,LIMIT_POST,9,100)
b = Order(BUY,LIMIT_POST,13,100)

x = Order(SELL,LIMIT_POST,13,100,4)
y = Order(SELL,LIMIT_POST,9,100,3)
z = Order(SELL,LIMIT_POST,11,100,2)
w = Order(SELL,LIMIT_POST,14,100,1)

stackB = OrderStack(BUY)
stackB.addOrder(a)
stackB.addOrder(c)
stackB.addOrder(b)
stackB.addOrder(d)
stackB.printTest()

stackS = OrderStack(SELL)
stackS.addOrder(x)
stackS.addOrder(y)
stackS.addOrder(z)
stackS.addOrder(w)
stackS.printTest()

#Expected Output

Buy Orders
top of stack
14
13
11
9
Sell Orders
top of stack
9
11
13
14

print("\nDeleting 14 with order_id 1")
stackS.cancelOrderByID(1)
stackS.printTest()
print("\nPopping from top of stack, should delete 9")
stackS.popOrder()
stackS.printTest()
"""
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
short = 134
long = 191
a = EMAAgent_marketOrdersOnly(short, long)
e = ExchangeSimulator('bfx_2017-03-25.csv')
e.setAgent(a)
e.run()
x = e.returnFinalResults()
m.insert_results(x)
m.get_results()


# Bruteforce optimal parameters
"""
m = PerformanceTracker()
short = 100
short_reset = short
long = 200
e = ExchangeSimulator('bfx_2017-03-25.csv')
while(long >= 2):
    print("\ntesting long:",long)
    while(short < long):
        a = EMAAgent_marketOrdersOnly(short,long)
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