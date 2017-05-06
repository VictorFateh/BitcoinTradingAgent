# This is a function that generates permutations for hill climbing search algorithm
# This will permutate next steps in ema short and long values
# This function will initially accept and randomly chosen set of ema values
# It wil then find next permutations and reference our precomputed csv to see if return is maximized
# accepts a list of the two initial parameters
def ema_optimal_parameter_search(ema_period):
    ema_short = ema_period[0]
    ema_long = ema_period[1]

    if ema_short >= ema_long:
        print("ema short must be less than ema long or a crossover will never happen")

    
