import random
import pandas
import csv
import sys
# This is a function that generates permutations for hill climbing search algorithm
# This will permutate next steps in ema short and long values
# This function will initially accept and randomly chosen set of ema values
# It wil then find next permutations and reference our precomputed csv to see if return is maximized
# accepts a list of the two initial parameters
def ema_optimal_parameter_search(ema_period, ema_max=None, df=None):
    #sys.setrecursionlimit(2500)
    ema_short = ema_period[0]
    ema_long = ema_period[1]
    new_ema_short = ema_short
    new_ema_long = ema_long
    # minimum ema period is one we need at least one period
    min_ema_period = 1
    # maximum ema period for now is 200.
    max_ema_period = 200

    if ema_short >= ema_long:
        print("ema short must be less than ema long or a crossover will never happen")
    # Get the return for the currently passed ema parameters
    if df is None:
        df = pandas.read_csv("bruteforced_parameters.csv")
    # 0 = 200 on pandas datframe
    # access with df[long][short]
    #200 - ema value long df[0] gives first row of 200
    #columns start with index value 1 but 1 correlates with 100
    #subtract 99 from all ema short values to get corresonding vaulue
    if ema_short > 199 or ema_short < 100 or ema_long < 101 or ema_long > 200:
        print("we do not have precomputed values for this")
        return

    if ema_max is None:
        ema_max = df.iloc[200-ema_long][ema_short-99]#from csv file

    # take the two randomly chosen ema periods and calculate the return of the algorithm based on those twovalues
    # Using a hill climbing algorithm we will find the optimal, ema short/long periods for which the algorithm to test over
    # For now we are using precomputed values from a csv to save computation time.
    # first generate all permutations
    # For example if 2,5 are passed in for initial short and long ema periods then next possible permutations are
    # 2,6   2,4     1,5     1,4     3,4     1,6     3,6     
    next_emas = {}
    if ema_short > 100:
        #case 1
        next_emas[(ema_short-1, ema_long)] = df.iloc[200-ema_long][ema_short-1-99]
        if ema_short < ema_long - 1:
            #case 2
            next_emas[(ema_short-1, ema_long-1 )] = df.iloc[200-ema_long+1][ema_short-1-99] 
        if ema_long-1 < 200:
            #case 3
            next_emas[(ema_short-1,ema_long-1)] = df.iloc[200-ema_long-1][ema_short-1-99]
    if ema_short + 1 < ema_long:
        #case 4
        next_emas[(ema_short+1, ema_long)] = df.iloc[200-ema_long][ema_short+1-99]
        if ema_long +1 <= 200:
            #case 5
            next_emas[(ema_short+1, ema_long-1)] = df.iloc[200-ema_long-1][ema_short+1-99]
    if ema_long - 1 > ema_short+1:
        next_emas[(ema_short+1, ema_long-1)] = df.iloc[200-ema_long+1][ema_short+1-99]
    if ema_long + 1 <= 200:
        #case 6
        next_emas[(ema_short, ema_long-1)] = df.iloc[200-ema_long-1][ema_short-99]
        if ema_long-1 > ema_short:
            #case 7
            next_emas[(ema_short, ema_long-1)] = df.iloc[200-ema_long+1][ema_short-99]

    #populate dictionary keys with values of return per ema periods
    for key, value in next_emas.items():
        if value > ema_max:
            ema_max = value
            # since key is a tuple, then access short and long accordingly
            new_ema_short = key[0]
            new_ema_long = key[1]

    # if this is the case then a local maximum has been found and is returned in a tuple
    if new_ema_short == ema_short and new_ema_long == ema_long:
        print("::::::final value has been found:::::::")
        print(ema_short,ema_long)
        return (ema_short, ema_long)
    else:
        return ema_optimal_parameter_search((new_ema_short, new_ema_long), ema_max, df)

while True:
    random_short = random.randint(100,199)
    random_long = random.randint(101,200)
    if random_short < random_long:
        break

print(random_short, random_long)
ema_optimal_parameter_search((random_short, random_long))
