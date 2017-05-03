
from exchange_simulator import *
from ema import *
from naive_bayes import *
from random import randint

# Only does market sell. Limit orders are more difficult to handle because the agent has to keep track of their pending limit orders to cancel?? Maybe?
class Agent_MarketOrdersOnly():
    def __init__(self, ema_short, ema_long, btc_bal=1, usd_bal=0):
        #self.cheat_summaries = { 0: [(936.2413333333333, 21.70424147707626), (936.5120000000001, 21.517075345607992), (5.224297451333333, 7.09834636556952), (935.7746666666666, 21.45970405423239), (3.6622183520000005, 4.816210980636395)], 1: [(938.550909090909, 16.045147213126743), (938.7045454545455, 16.156863782081196), (3.16785915, 2.520631304019733), (938.4018181818182, 16.132811793473472), (3.1402736209090913, 3.621571039635933)]}

        self.counter = 0
        self.training_size = math.floor(10200 * 0.50)

        self.ema_short = ema_short
        self.ema_long = ema_long
        self.btc_bal = btc_bal
        self.usd_bal = usd_bal

        self.Strategy_Algorithm = EMA_Cross_Strategy(ema_short, ema_long)
        self.ML_Naive_Bayes = ML_Naive_Bayes()

    def set_StrategyAlgorithm(self,strategy_algorithm):
        self.Strategy_Algorithm = strategy_algorithm

    def set_MLAlgorithm(self,MLA):
        self.ML_Algorithm = MLA

    def program(self, percept):

        ltp, sp, ss, bp, bs = percept
        last_trade_price = float(ltp)
        sell_price = float(sp)
        sell_size = float(ss)
        buy_price = float(bp)
        buy_size = float(bs)

        signal = self.Strategy_Algorithm.evaluate(last_trade_price)

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
