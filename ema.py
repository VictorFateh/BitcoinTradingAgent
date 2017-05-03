import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
#style.use('fivethirtyeight')
style.use('ggplot')
#style.use('dark_background')


df = pd.read_csv('bfx_data/bfx_2017-03-25.csv')
#df["mean"] = df["last_price"]



class Ema():
    def __init__(self,period):
        self.period = period
        self.counter = 1
        self.multiplier = (2/(period+1))
        ##print("multiplier: ",self.multiplier)
        self.previousEMA = 0
        self.average = 0

    def avg(self,current): #used to seed EMA once counter == period
        if (self.counter < self.period):
            self.average += current #not really average, just keeping a running total
            self.counter +=1
        elif(self.counter == self.period): #calculate average for period
            self.average += current
            self.average = self.average / self.period
            self.counter += 1
            ##print("average: ",self.average)
            self.previousEMA = self.average

    def ema(self,current):

        if(self.counter <= self.period):
            self.avg(current)

        output = ( self.multiplier * (current - self.previousEMA) + self.previousEMA)
        self.previousEMA = output
        return output


class Diff:
    def __init__(self,short,long):
        self.short = Ema(short)
        self.long = Ema(long)
        self.prev = None

    def alert(self,current):
        if(self.prev == None):
            self.prev = current

        if(current < self.prev):
            print('\nsell at ', current)
        elif(current > self.prev):
            print('\nbuy at ', current)
        self.prev = current

    def diff(self,current):
        self.alert(current)
        return self.short.ema(current) - self.long.ema(current)

class EMA_Cross_Strategy:
    def __init__(self,short,long):
        self.short = Ema(short)
        self.long = Ema(long)
        self.prev = None
        self.init_counter = 1
        self.start_counter = long
        self.start_evaluate = False

    def calculate(self,current):
        if(self.prev == None):
            self.prev = current

        areaDiff = self.short.ema(current) - self.long.ema(current)
        if(self.start_evaluate == False and self.init_counter <= self.start_counter):
            self.init_counter += 1
            if(self.init_counter == self.start_counter):
                self.start_evaluate = True

        signal = None

        if( self.start_evaluate ):
            if(self.prev < 0 and areaDiff > 0):
                signal = 'BUY'
            elif(self.prev > 0 and areaDiff < 0):
                signal = 'SELL'
            self.prev = areaDiff

        return signal





    def evaluate(self,current):
        signal = self.calculate(current)
        return signal




class EMA_MinMax_Strategy:
    def __init__(self,short,long):
        self.short = Ema(short)
        self.long = Ema(long)
        self.prev_areaDiff = None
        self.prev_state = None
        self.init_counter = 1
        self.start_counter = long
        self.start_evaluate = False

    def calculate(self,current):
        if(self.prev_areaDiff == None):
            self.prev_areaDiff = current

        current_areaDiff = self.short.ema(current) - self.long.ema(current)
        if(self.start_evaluate == False and self.init_counter <= self.start_counter):
            self.init_counter += 1
            if(self.init_counter == self.start_counter):
                self.start_evaluate = True

        signal = None

        if( self.start_evaluate ):
            #check for new min max
            if(self.prev_state == 1 and self.prev_areaDiff > current_areaDiff):
                signal = 'SELL'
            elif(self.prev_state == -1 and self.prev_areaDiff < current_areaDiff):
                signal = 'BUY'

            #keep track of previous state slope
            if(self.prev_areaDiff < current_areaDiff):
                self.prev_state = 1
            elif(self.prev_areaDiff > current_areaDiff):
                self.prev_state = -1
            else:
                self.prev_state = 0
            self.prev_areaDiff = current_areaDiff


        return signal





    def evaluate(self,current):
        signal = self.calculate(current)
        return signal






def apple():
    data = [22.27,22.19,22.08,22.17,22.18,22.13,22.23,22.43,22.24,22.29,22.15,22.39,22.38,22.61,23.36,24.05,23.75,23.83,23.95,23.63,23.82,23.87,23.65,23.19,23.10,23.33,22.68,23.10,22.40,22.17]



    d = Diff(5,10)
    i=3
    for v in data:
        print("%d data: %f Diff: %f" % (i, v, d.diff(v)))
        i+=1

def show_partitioned_example():
    fig = plt.figure()
    ax1 = plt.subplot2grid((2, 1), (0, 0))
    ax2 = plt.subplot2grid((2, 1), (1, 0), sharex=ax1)

    df['last_price'].plot(ax=ax1)
    df['ask'].plot(ax=ax1)
    df['bid'].plot(ax=ax1)

    df['ask_size'].plot(ax=ax2)
    df['bid_size'].plot(ax=ax2)

    plt.legend().remove()
    plt.show()

def show_ema_example():
    df['ema10'] = df['last_price'].ewm(span=10).mean()
    df['ema21'] = df['last_price'].ewm(span=21).mean()
    df['last_price'].plot(color='black')
    df['ema10'].plot(color='blue')
    df['ema21'].plot(color='red')

    #plt.legend().remove()
    plt.show()

def show_ema_v2():
    fig = plt.figure()
    ax1 = plt.subplot2grid((2, 1), (0, 0))

    ax2 = plt.subplot2grid((2, 1), (1, 0), sharex=ax1)

    df['ema100'] = df['last_price'].ewm(span=100).mean()
    df['ema200'] = df['last_price'].ewm(span=200).mean()

    df['diff'] = df['ema100']-df['ema200']
    df['last_price'].plot(color='black',ax=ax1)
    df['ema100'].plot(color='blue',ax=ax1)
    df['ema200'].plot(color='red',ax=ax1)
    ax1.legend(loc=4)
    df['index'] = range(1, len(df) + 1)

    df['diff'].plot(ax=ax2, color='black', label='ema_diff')
    ax2.legend(loc=4)

    df['prev'] = df['diff'].shift(1)
    ax2.fill_between(df['index'], 0, df['diff'], where=(df['diff'] > df['prev']), facecolor='g', alpha=0.5)
    ax2.fill_between(df['index'], 0, df['diff'], where=(df['diff'] <= df['prev']), facecolor='r', alpha=0.5)

    print(df.tail())
    #plt.legend().remove()
    plt.show()

#show_partitioned_example()
#show_ema_example()
#show_ema_v2()
#apple()

