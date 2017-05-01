import csv, sys, ast
from ema import *
from naive_bayes import *
from random import randint
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

        self.initial = None

        #temporarily used for simplified development testing
        #self.testData = [5,6,7,8,9,10,9,8,7,6,3,2,1,3,5,7,9,10,10,9,8]
        self.filename = testData
        f = open(self.filename, newline='')
        self.percepts = loadCsv(self.filename, skip_header=True)#csv.reader(f)


    def setAgent(self,Agent):
        self.Agent = Agent

    def run(self):
        try:

            for percept in self.percepts:

                ltp, sp, ss, bp, bs  = percept

                self.current_price = float(ltp)
                self.nearest_sell_price = float(sp)
                self.nearest_sell_size = float(ss)
                self.nearest_buy_price = float(bp)
                self.nearest_buy_size = float(bs)

                if(self.initial == None):
                    self.initial = self.current_price

                #self.updateDeltaPrice()
                self.handle_QueuedOrders()

                request, info = self.Agent.program(percept)

                response = self.handle_AgentRequest(request, info)

                self.Agent.sees(response)


        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(self.filename, self.percepts.line_num, e))

    def handle_AgentRequest(self, request, info):
        if request == "BUY" or request == "SELL":
            ##print("EXCHANGE - got it!")#For debugging
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
    def returnFinalResults(self):
        finalValue = round(self.Agent.btc_bal * self.current_price + self.Agent.usd_bal, 8)
        results = finalValue / self.initial
        a = [round(results*100-100,2),self.Agent.ema_short,self.Agent.ema_long,self.initial,round(finalValue,2)]
        return a

    def printFinalResults(self):
        finalValue = round(self.Agent.btc_bal * self.current_price + self.Agent.usd_bal, 8)
        results = finalValue / self.initial
        print("EMA Short:", self.Agent.ema_short)
        print("EMA Long:", self.Agent.ema_long)
        print("Result %:", round(results*100-100,2))
        print("Start Balance: $",self.initial)
        print("Final Balance: $",round(finalValue,2))

    def printAgentBalance(self):
        print("btc: ", self.Agent.btc_bal)
        print("usd: $", self.Agent.usd_bal)
        print("value: $", round(self.Agent.btc_bal * self.current_price + self.Agent.usd_bal, 8))

    def executeBuyMarketOrder(self, order):
        ##print("EXCHANGE - executeBuyMarketOrder @ ", self.nearest_buy_price)
        fee = order.amount * TAKER_FEE
        order.amount -= fee
        self.Agent.btc_bal += order.amount / self.nearest_buy_price
        self.Agent.btc_bal = round(self.Agent.btc_bal,8)
        ##self.printAgentBalance()

    def executeSellMarketOrder(self, order):
        ##print("EXCHANGE - executeSellMarketOrder @ ", self.nearest_sell_price)
        fee = order.amount * TAKER_FEE
        order.amount -= fee
        self.Agent.usd_bal += order.amount * self.nearest_sell_price
        self.Agent.usd_bal = round(self.Agent.usd_bal, 8)
        ##self.printAgentBalance()

    def executeBuyLimitOrder(self, order):
       ##print("EXCHANGE - executeBuyLimitOrder @ ", order.target_price)
        fee = order.amount * MAKER_FEE
        order.amount -= fee
        self.Agent.btc_bal += order.amount / order.target_price
        self.Agent.btc_bal = round(self.Agent.btc_bal, 8)
        ##self.printAgentBalance()

    def executeSellLimitOrder(self, order):
        ##print("EXCHANGE - executeSellLimitOrder @ ", order.target_price)
        fee = order.amount * MAKER_FEE
        order.amount -= fee
        self.Agent.usd_bal += order.amount * order.target_price
        self.Agent.usd_bal = round(self.Agent.usd_bal, 8)
        ##self.printAgentBalance()


    def executeOrderCalcNewBalance(self, percept, order):
        ##print("calc_new_balance")#For debugging
        last_price = percept
        btc_bal = None
        usd_bal = None
        if order.order_side == BUY:
            btc_bal = order.amount / last_price
            ##print("btc: ", btc_bal) #For debugging
            usd_bal = 0
            ##print("usd: ", usd_bal)#For debugging
        elif order.order_side == SELL:
            btc_bal = 0
            ##print("btc: ", btc_bal)#For debugging
            usd_bal = order.amount * last_price
            ##print("usd: ", usd_bal)#For debugging

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


"""
            /// MACHINE LEARNING NAIVE BAYES ///
        Currently customized for EMA Crossover Strategy
"""
class ML_Naive_Bayes():
    def __init__(self):
        self.summaries = None
        self.testing_mode = False

        self.prev_order_side = None
        self.prev_percept = None
        self.dataset = []

    def add_dataset(self,current_order_side, percept):

        current_percept = list(percept)

        if( self.prev_order_side == BUY and current_order_side == SELL):
            if(self.prev_percept[3] < current_percept[1]):
                self.prev_percept.append(1) # decision successful
            else:
                self.prev_percept.append(0) # decision failed
            self.dataset.append(self.prev_percept)
        elif( self.prev_order_side == SELL and current_order_side == BUY):
            if(self.prev_percept[1] > current_percept[3]):
                self.prev_percept.append(1) # decision successful
            else:
                self.prev_percept.append(0) # decision failed
            self.dataset.append(self.prev_percept)

        self.prev_order_side = current_order_side
        self.prev_percept = current_percept


    def print_dataset(self):
        print(self.dataset)

    def get_dataset(self):
        return self.dataset

    def start_testing(self):

        self.summaries = summarizeByClass(self.dataset)
        self.testing_mode = True

    def testing_mode_active(self):
        return self.testing_mode

    def get_prediction(self, percept):
        result = predict(self.summaries, percept)
        return result


# Only does market sell. Limit orders are more difficult to handle because the agent has to keep track of their pending limit orders to cancel?? Maybe?
class EMAAgent_marketOrdersOnly():
    def __init__(self, ema_short, ema_long, btc_bal=1, usd_bal=0):
        #self.cheat_summaries = {0: [(936.2413333333333, 21.70424147707626), (936.5120000000001, 21.517075345607992), (5.224297451333333, 7.09834636556952), (935.7746666666666, 21.45970405423239), (3.6622183520000005, 4.816210980636395)], 1: [(938.550909090909, 16.045147213126743), (938.7045454545455, 16.156863782081196), (3.16785915, 2.520631304019733), (938.4018181818182, 16.132811793473472), (3.1402736209090913, 3.621571039635933)]}

        self.counter = 0
        self.training_size = math.floor(10200 * 0.50)


        self.ema_short = ema_short
        self.ema_long = ema_long
        self.btc_bal = btc_bal
        self.usd_bal = usd_bal

        self.EmaX = EMA_Cross_Strategy(ema_short, ema_long)
        self.ML_Naive_Bayes = ML_Naive_Bayes()

    def program(self, percept):

        ltp, sp, ss, bp, bs = percept
        last_trade_price = float(ltp)
        sell_price = float(sp)
        sell_size = float(ss)
        buy_price = float(bp)
        buy_size = float(bs)

        signal = self.EmaX.evaluate(last_trade_price)

        ##print("price: ", last_trade_price)#For debugging
        if(self.counter < self.training_size):
            self.counter += 1
        elif(self.counter == self.training_size):
            self.ML_Naive_Bayes.start_testing()

        prediction = 1
        if(signal and self.ML_Naive_Bayes.testing_mode_active()):
            prediction = self.ML_Naive_Bayes.get_prediction(percept)
            #prediction = randint(0,1) #debugging; also baseline test with random prediction
        if (signal == 'BUY' and prediction == 1):  # up trend... maybe
            if self.usd_bal != 0:
                ##print("AGENT - market buy @ ", last_trade_price) #debugging
                self.ML_Naive_Bayes.add_dataset(BUY, percept)
                o = Order(BUY, MARKET, last_trade_price, self.usd_bal)
                return "BUY", o
        elif (signal == 'SELL' and prediction == 1):  # down trend... maybe
            if self.btc_bal != 0:
                ##print("AGENT - market sell @ ", last_trade_price) #debugging
                self.ML_Naive_Bayes.add_dataset(SELL, percept)
                o = Order(SELL, MARKET, last_trade_price, self.btc_bal)
                return "SELL", o

        return None, None

    def sees(self, response):
        pass


class PerformanceTracker:
    def __init__(self):
        self.percentage = -100
        self.ema_short = None
        self.ema_long = None
        self.start_bal = None
        self.end_bal = None

    def insert_results(self,input_array):

        percentage, ema_short, ema_long, start_bal, end_bal = input_array


        if(percentage > self.percentage):
            self.percentage = percentage
            self.ema_short = ema_short
            self.ema_long = ema_long
            self.start_bal = start_bal
            self.end_bal = end_bal
            self.get_results()


    def get_results(self):
        print()
        print("EMA Short:", self.ema_short)
        print("EMA Long:", self.ema_long)
        print("Result %:", self.percentage)
        print("Start Balance: $",self.start_bal)
        print("Final Balance: $",self.end_bal)