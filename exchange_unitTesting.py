
from agents import *

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
a = [[1,2,3],[4,5,6],[7,8,9]]
ar = a

import csv

fl = open('filename.csv', 'w',newline='')
writer = csv.writer(fl)



short = 100
short_reset = short
long = 200
masterList = []
header = ['LongV Short->']+ list( range(100,200))
masterList.append(header)
print(masterList)
exit(1)
writer.writerow(['label1', 'label2', 'label3']) #if needed
for values in ar:
    writer.writerow(values)

fl.close()
"""

import csv

fl = open('bruteforced_parameters.csv', 'w',newline='')
writer = csv.writer(fl)

header = ['LongV Short->']+ list( range(100,200))
print(header)
writer.writerow(header)

# Bruteforce optimal parameters

m = PerformanceTracker()
short = 100
short_reset = short
long = 200
e = ExchangeSimulator('bfx_data/bfx_2017-03-25.csv')
while(long > short_reset):
    print("\ntesting long:",long)
    data = [long]
    while(short < long):

        a = Agent_MarketOrdersOnly(short,long)
        e.setAgent(a)
        e.run()
        x = e.returnPercentageResults()
        m.insert_results( e.returnFinalResults() )

        short+=1
        data.append(x)
    print(data)
    writer.writerow(data)
    long -= 1
    short = short_reset

print("Best EMA Parameters")
m.get_results()
