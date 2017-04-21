import csv, sys, ast
#Constants
MAKER_FEE = 0.001 # 0.1% in decimal form
TAKER_FEE = 0.002 # 0.2% in decimal form


#Constants order_side
SELL = True
BUY = False


#Constants order_type
MARKET = 0
LIMIT = 1
LIMIT_POST = 2
STOP = 3


class Order:
    def __init__(self, order_side=None, order_type=None, target_price=None, amount=0, id=None):
        self.order_side = order_side
        self.order_type = order_type
        self.target_price = target_price
        self.amount = amount
        self.id = id



#End of list has orders closest to the current price.
class OrderStack:
    def __init__(self, order_side):
        self.orders = []
        self.order_side = order_side


    def insertOrderOrNext_check(self, orders_target_price, order_target_price):
        if( self.order_side == BUY):
            if(orders_target_price > order_target_price):
                return False #move to next order
            else:
                return True #insert
        elif( self.order_side == SELL):
            if(orders_target_price < order_target_price):
                return False #move to next order
            else:
                return True #insert
        return True #end of list; insert


    def addOrder(self, order):
        if( self.order_side != order.order_side): #Throw Exception
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
        if len(self.orders) > 0:
            return self.orders[len(self.orders)-1]
        else:
            return None

    def popOrder(self):
        self.orders.pop()


    def cancelOrderByID(self, order_id):
        for i in range(0,len(self.orders)-1):
            if(self.orders[i].id == order_id):
                amount = self.orders[i].amount
                del self.orders[i]
                return True, amount
        return False

    def cancelOrderByType2(self, order_type):
        status = False
        amount = 0;
        for i in range(0,len(self.orders)-1):
            if(self.orders[i].order_type == order_type):
                amount += self.orders[i].amount
                del self.orders[i]
                status = True
        return status, amount

    def printTest(self): #For debugging
        print("Buy Orders") if self.order_side == BUY else print("Sell Orders")
        print("top of stack")
        for order in reversed(self.orders):
            print(order.target_price)

    def size(self):
        return len(self.orders)

"""
        #### EXCHANGE SIMULATOR ####
"""


class ExchangeSimulator:

    def __init__(self, testData = 'bfx_2017-03-25.csv'):
        self.Agent = []

        self.buyOrders = OrderStack(BUY)
        self.sellOrders = OrderStack(SELL)

        self.current_price = None
        self.previous_price = 0 #To avoid compiling error
        self.nearest_buy_price = None
        self.nearest_sell_price = None
        self.nearest_buy_size = None
        self.nearest_sell_size = None
        self.order_id_nonce = 0
        self.deltaP = 0 #Delta Price; Track change in price, used to know which stack to check per STEP

        #temporarily used for simplified development testing
        #self.testData = [5,6,7,8,9,10,9,8,7,6,3,2,1,3,5,7,9,10,10,9,8]
        self.filename = testData
        f = open(self.filename, newline='')
        self.percepts = csv.reader(f)


    def setAgent(self,Agent):
        self.Agent = Agent

    def run(self):
        try:
            next(self.percepts)#skip header in csv
            for percept in self.percepts:
                ltp, sp, ss, bp, bs  = percept
                print("price: ", self.current_price)#For debugging
                self.current_price = float(ltp)
                self.nearest_sell_price = float(sp)
                self.nearest_sell_size = float(ss)
                self.nearest_buy_price = float(bp)
                self.nearest_buy_size = float(bs)
                #self.current_price = percept # set the current price
                #self.nearest_buy_price = self.current_price
                #self.nearest_sell_price = self.current_price

                self.updateDeltaPrice()
                self.handle_QueuedOrders()

                request, info = self.Agent.program(self.current_price)

                response = self.handle_AgentRequest(percept, request, info)

                self.Agent.sees(response)
        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(self.filename, self.percepts.line_num, e))

    def handle_AgentRequest(self, percept, request, info):
        if request == "BUY" or request == "SELL":
            print("EXCHANGE - got it!")#For debugging
            order = info


            if order.order_side == BUY:
                # Check for sufficient funds
                if self.Agent.usd_bal < order.amount:
                    return False, "Insufficient Funds"  # Order Failed

                # Check if limit order can be guaranteed
                if order.order_type == LIMIT_POST and self.current_price >= order.target_price:
                    return False, "Limit Post Failed"  # Order Failed

            elif order.order_side == SELL:
                # Check for sufficient funds
                if self.Agent.btc_bal < order.amount:
                    return False, "Insufficient Funds"  # Order Failed

                # Check if limit order can be guaranteed
                if order.order_type == LIMIT_POST and self.current_price <= order.target_price:
                    return False, "Limit Post Failed" # Order Failed

            #order validation passed, add to queue
            order.id = self.order_id_nonce
            self.order_id_nonce += 1
            self.queueOrder(order)

            if(order.order_type == MARKET):
                return True
            else:
                order_data = {}
                order_data['SIDE'] = order.order_side
                order_data['ID'] = order.id
                order_data['TARGET_PRICE'] = order.target_price
                return True, order_data #Order Queued

        elif request == "CANCEL":
            order_side , order_id= info
            if( order_side == BUY):
                results , amount = self.buyOrders.cancelOrderByID( order_id )
                if(results):
                    self.Agent.usd_bal += amount
            elif( order_side == SELL):
                results, amount = self.sellOrders.cancelOrderByID( order_id )
                if(results):
                    self.Agent.btc_bal += amount
            return results, order_side, order_id;





        return None

    def handle_QueuedOrders(self):
        """
        ### UPTREND TICK ###
        if self.deltaP == 1 and self.sellOrders.size() > 0: # price went up; check sell orders
            order = self.sellOrders.checkOrder()
            if order.order_type == MARKET:
                self.executeSellMarketOrder(order)
                self.sellOrders.popOrder()
                # TODO return status?
            elif order.order_type == LIMIT or order.order_type == LIMIT_POST:
                if self.current_price >= order.target_price:
                    self.executeSellLimitOrder(order)
                    self.sellOrders.popOrder()
                    # TODO return status?

        ### DOWNTREND TICK ###
        elif self.deltaP == -1: # price went down; check buy orders
            order = self.buyOrders.checkOrder()
            if(order):
                if order.order_type == MARKET:
                    self.executeBuyMarketOrder(order)
                    self.buyOrders.popOrder()
                    # TODO return status?
                elif order.order_type == LIMIT or order.order_type == LIMIT_POST:
                    if self.current_price <= order.target_price:
                        self.executeBuyLimitOrder(order)
                        self.buyOrders.popOrder()
                        # TODO return status?
            else:
                return

        ### NO CHANGE IN DELTA PRICE ###
        else:"""
        sellOrder = self.sellOrders.checkOrder()
        if(sellOrder):
            if sellOrder.order_type == MARKET:
                self.executeSellMarketOrder(sellOrder)
                self.sellOrders.popOrder()
                # TODO return status?
            elif sellOrder.order_type == LIMIT or sellOrder.order_type == LIMIT_POST:
                if self.current_price >= sellOrder.target_price:
                    self.executeSellLimitOrder(sellOrder)
                    self.sellOrders.popOrder()
                    # TODO return status?
        buyOrder = self.buyOrders.checkOrder()
        if(buyOrder):
            if buyOrder.order_type == MARKET:
                self.executeBuyMarketOrder(buyOrder)
                self.buyOrders.popOrder()
                # TODO return status?
            elif buyOrder.order_type == LIMIT or buyOrder.order_type == LIMIT_POST:
                if self.current_price <= buyOrder.target_price:
                    self.executeBuyLimitOrder(buyOrder)
                    self.buyOrders.popOrder()
                    # TODO return status?


    def queueOrder(self, order):
        if(order.order_side == BUY):
            self.Agent.usd_bal -= order.amount
            self.buyOrders.addOrder(order)
        elif(order.order_side == SELL):
            self.Agent.btc_bal -= order.amount
            self.sellOrders.addOrder(order)

    """
    def queue_order_request(self, percept, request, info):
        if request == "BUY" or request == "SELL":
            print("BUY/SELL process_order_request")#For debugging
            order = info

            #TODO only calc fee once order is cancelled
            #fee = self.calcFee(order.amount, order.order_type)
            #order.amount -= fee

            if(order.order_type == MARKET):
                btc_bal, usd_bal = self.executeOrderCalcNewBalance( percept, order)
                self.Agent.btc_bal = btc_bal
                self.Agent.usd_bal = usd_bal

        return None
    """
    def printAgentBalance(self):
        print("btc: ", self.Agent.btc_bal)
        print("usd: $", self.Agent.usd_bal)
        print("value: $", round(self.Agent.btc_bal * self.current_price + self.Agent.usd_bal, 8))

    def executeBuyMarketOrder(self, order):
        print("EXCHANGE - executeBuyMarketOrder @ ", self.nearest_buy_price)
        fee = order.amount * TAKER_FEE
        order.amount -= fee
        self.Agent.btc_bal += order.amount / self.nearest_buy_price
        self.Agent.btc_bal = round(self.Agent.btc_bal,8)
        self.printAgentBalance()

    def executeSellMarketOrder(self, order):
        print("EXCHANGE - executeSellMarketOrder @ ", self.nearest_sell_price)
        fee = order.amount * TAKER_FEE
        order.amount -= fee
        self.Agent.usd_bal += order.amount * self.nearest_sell_price
        self.Agent.usd_bal = round(self.Agent.usd_bal, 8)
        self.printAgentBalance()

    def executeBuyLimitOrder(self, order):
        print("EXCHANGE - executeBuyLimitOrder @ ", order.target_price)
        fee = order.amount * MAKER_FEE
        order.amount -= fee
        self.Agent.btc_bal += order.amount / order.target_price
        self.Agent.btc_bal = round(self.Agent.btc_bal, 8)
        self.printAgentBalance()

    def executeSellLimitOrder(self, order):
        print("EXCHANGE - executeSellLimitOrder @ ", order.target_price)
        fee = order.amount * MAKER_FEE
        order.amount -= fee
        self.Agent.usd_bal += order.amount * order.target_price
        self.Agent.usd_bal = round(self.Agent.usd_bal, 8)
        self.printAgentBalance()


    def executeOrderCalcNewBalance(self, percept, order):
        print("calc_new_balance")#For debugging
        last_price = percept
        btc_bal = None
        usd_bal = None
        if order.order_side == BUY:
            btc_bal = order.amount / last_price
            print("btc: ", btc_bal) #For debugging
            usd_bal = 0
            print("usd: ", usd_bal)#For debugging
        elif order.order_side == SELL:
            btc_bal = 0
            print("btc: ", btc_bal)#For debugging
            usd_bal = order.amount * last_price
            print("usd: ", usd_bal)#For debugging

        del order
        return btc_bal, usd_bal


    def calculateFee(self, amount, order_type):
        if order_type == MARKET or order_type == STOP:
            fee = amount * TAKER_FEE
        else: # order_type == LIMIT or order_type == LIMIT_POST
            fee = amount * MAKER_FEE
        return fee

    def updateDeltaPrice(self):
        if (self.current_price > self.previous_price):
            self.previous_price = self.current_price
            if self.deltaP != -1:
                self.deltaP = -1
        elif(self.current_price < self.previous_price):
            self.previous_price = self.current_price
            if self.deltaP != 1:
                self.deltaP = 1
        else:
            if self.deltaP != 0:
                self.deltaP = 0

"""
            /// TestAgent_marketOrdersOnly ///
"""
#Only does market sell. Limit orders are more difficult to handle because the agent has to keep track of their pending limit orders to cancel?? Maybe?
class TestAgent_marketOrdersOnly():

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
                print("AGENT - market buy @ ", last_price)
                o = Order(BUY,MARKET,last_price,self.usd_bal)
                return "BUY", o
        elif prev_deltaP > self.deltaP: # down trend... maybe
            if self.btc_bal != 0:
                print("AGENT - market sell @ ", last_price)
                o = Order(SELL, MARKET, last_price, self.btc_bal)
                return "SELL", o

        return None, None

    def sees(self,response):
        if response:
            print("AGENT - received response: ", response)


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

"""
            /// TestAgent_limitOrdersOnly ///
"""
# stupid agent, doesn't keep track of its own queued orders, testing limit orders
class TestAgent_limitOrdersOnly():

    def __init__(self, btc_bal = 1, usd_bal = 0):
        self.btc_bal = btc_bal
        self.usd_bal = usd_bal
        self.deltaP = 0
        self.previousP = None
        self.previousOrder = {}

    def program(self, percept):
        last_price = percept
        if self.previousP is None:
            self.previousP = last_price

        prev_deltaP = self.deltaP
        self.findNewDelta(last_price)

        if prev_deltaP < self.deltaP: # up trend... maybe
            if self.usd_bal != 0:
                print("AGENT - limit buy @ ", last_price)
                o = Order(BUY,LIMIT,last_price,self.usd_bal)
                return "BUY", o
        elif prev_deltaP > self.deltaP: # down trend... maybe
            if self.btc_bal != 0:
                print("AGENT - limit sell @ ", last_price)
                o = Order(SELL, LIMIT, last_price, self.btc_bal)
                return "SELL", o

        return None, None

    def sees(self,response):
        if response:
            print("AGENT - received response: ", response)
            boolean, order = response
            self.previousOrder = order
            print("AGENT - Saved: ", self.previousOrder)


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
