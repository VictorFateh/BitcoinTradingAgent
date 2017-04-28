from agent_exchangeSim import *

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
"""
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
"""
print("\nDeleting 14 with order_id 1")
stackS.cancelOrderByID(1)
stackS.printTest()
print("\nPopping from top of stack, should delete 9")
stackS.popOrder()
stackS.printTest()

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

class emaMax:
    def __init__(self):
        self.percentage = 0
        self.ema_short = None
        self.ema_long = None
        self.start_bal = None
        self.end_bal = None

    def apple(self,input_array):

        percentage, ema_short, ema_long, start_bal, end_bal = input_array

        if(percentage > self.percentage):
            self.percentage = percentage
            self.ema_short = ema_short
            self.ema_long = ema_long
            self.start_bal = start_bal
            self.end_bal = end_bal

    def results(self):
        print("EMA Short:", self.ema_short)
        print("EMA Long:", self.ema_long)
        print("Result %:", self.percentage)
        print("Start Balance: $",self.start_bal)
        print("Final Balance: $",self.end_bal)


m = emaMax()
short = 1
long = 200
while(long >= 2):
    while(short < long):
        a = EMAAgent_marketOrdersOnly(short,long)
        e = ExchangeSimulator()
        e.setAgent(a)
        #print("\nRunning Exchange Simulation Testbench")
        e.run()
        x = e.returnFinalResults()
        m.apple( x )
        short+=1
    print("long: ",long)
    long -= 1
    short = 1

print("emaMAX")
m.results()