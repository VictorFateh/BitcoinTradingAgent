import random
#Constants
MAKER_FEE = 0.001 # 0.1% in decimal form
TAKER_FEE = 0.002 # 0.2% in decimal form


#Constants order_type1
SELL = True
BUY = False


#Constants order_type2
MARKET = 0
LIMIT = 1
LIMIT_POST = 2
STOP = 3


class Order:
    def __init__(self, order_type1=None, order_type2=None, target_price=None, amount=0, id=None):
        self.order_type1 = order_type1
        self.order_type2 = order_type2
        self.target_price = target_price
        self.amount = amount
        self.id = id



#End of list has orders closest to the current price.
class OrderStack:
    def __init__(self, order_type1):
        self.orders = []
        self.order_type1 = order_type1


    def insertOrderOrNext_check(self, orders_target_price, order_target_price):
        if( self.order_type1 == BUY):
            if(orders_target_price > order_target_price):
                return False #move to next order
            else:
                return True #insert
        elif( self.order_type1 == SELL):
            if(orders_target_price < order_target_price):
                return False #move to next order
            else:
                return True #insert
        return True #end of list; insert


    def addOrder(self, order):
        if( self.order_type1 != order.order_type1): #Throw Exception
            raise ValueError("Exception: Trying to add an Order into the wrong OrderStack. Order type1 does NOT match orderStack type1.")


        orders_size = len(self.orders)

        #case 1: empty orders list
        if( orders_size == 0):
            self.orders.append(order)
            return

        #case 2: orders list has 1+ orders
        i = orders_size-1 # zero based indexing
        while i >= -1:
            if self.insertOrderOrNext_check(self.orders[i].target_price, order.target_price):
                self.orders.insert(i+1, order) #insert in next position
                return
            elif i == -1: #case 3: insert at bottom of stack (beginning of list)
                self.orders.insert(i+1, order)
                return
            else:
                i -= 1 #move on to check next


    def checkOrder(self):
        return self.orders[len(self.orders)-1]

    def popOrder(self):
        self.orders.pop()


    def cancelOrderByID(self, order_id):
        for i in range(0,len(self.orders)-1):
            if(self.orders[i].id == order_id):
                amount = self.orders[i].amount
                del self.orders[i]
                return True, amount
        return False

    def cancelOrderByType2(self, order_type2):
        status = False
        amount = 0;
        for i in range(0,len(self.orders)-1):
            if(self.orders[i].order_type2 == order_type2):
                amount += self.orders[i].amount
                del self.orders[i]
                status = True
        return status, amount

    def printTest(self): #For debugging
        print("Buy Orders") if self.order_type1 == BUY else print("Sell Orders")
        print("top of stack")
        for order in reversed(self.orders):
            print(order.target_price)


class ExchangeSimulator:

    def __init__(self):
        self.Agent = []

        self.buyOrders = OrderStack(BUY)
        self.sellOrders = OrderStack(SELL)

        self.current_price = 0 #TODO Set to Initial Value
        self.deltaP = 0 #Delta Price; Track change in price, used to know which stack to check per STEP

        #temporarily used for simplified development testing
        self.testData = [5,6,7,8,9,10,9,8,7,6,3,2,1,3,5,7,9,10,10,5,1]


    def setAgent(self,Agent):
        self.Agent = Agent

    def run(self):
        for percept in self.testData:
            print("price: ", percept)#For debugging
            request, info = self.Agent.program(percept)
            response = self.execute_order(percept, request, info)
            self.Agent.sees(response)

    def execute_order(self, percept, request, info):
        if request == "BUY" or request == "SELL":
            print("execute_order")#For debugging
            order = info

            fee = self.calcFee(order.amount, order.order_type2)
            order.amount -= fee

            if(order.order_type2 == MARKET):
                btc_bal, usd_bal = self.executeOrderCalcNewBalance( percept, order)
                self.Agent.btc_bal = btc_bal
                self.Agent.usd_bal = usd_bal

        return None


    def executeOrderCalcNewBalance(self, percept, order):
        print("calc_new_balance")#For debugging
        last_price = percept
        btc_bal = None
        usd_bal = None
        if order.order_type1 == BUY:
            btc_bal = order.amount / last_price
            print("btc: ", btc_bal) #For debugging
            usd_bal = 0
            print("usd: ", usd_bal)#For debugging
        elif order.order_type1 == SELL:
            btc_bal = 0
            print("btc: ", btc_bal)#For debugging
            usd_bal = order.amount * last_price
            print("usd: ", usd_bal)#For debugging

        del order
        return btc_bal, usd_bal


    def calcFee(self, amount, order_type2):
        if order_type2 == MARKET or order_type2 == STOP:
            fee = amount * TAKER_FEE
        else: # order_type2 == LIMIT or order_type2 == LIMIT_POST
            fee = amount * MAKER_FEE
        return fee





class SimpleTestAgent():

    def __init__(self, btc_bal = 1, usd_bal = 0):
        self.btc_bal = btc_bal
        self.usd_bal = usd_bal
        self.deltaP = 0
        self.previousP = None

    def program(self, percept):
        last_price = percept
        if self.previousP is None:
            self.previousP = last_price

        prev_deltaP = self.deltaP
        self.findNewDelta(last_price)

        if prev_deltaP < self.deltaP: # up trend... maybe
            if self.usd_bal != 0:
                print("buying")
                o = Order(BUY,MARKET,last_price,self.usd_bal)
                self.usd_bal = 0
                return "BUY", o
        elif prev_deltaP > self.deltaP: # down trend... maybe
            if self.btc_bal != 0:
                print("selling")
                o = Order(SELL, MARKET, last_price, self.btc_bal)
                self.btc_bal = 0
                return "SELL", o

        return None, None

    def sees(self,response):
        if response:
            print("got response")


    def findNewDelta(self, currentP):
        if (currentP > self.previousP):
            self.previousP = currentP
            if self.deltaP != 1:
                self.deltaP = 1
        elif(currentP < self.previousP):
            self.previousP = currentP
            if self.deltaP != -1:
                self.deltaP = -1
        else:
            if self.deltaP != 0:
                self.deltaP = 0
