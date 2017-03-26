import csv, sys



filename = 'bfx_2017-03-25.csv'



f = open(filename, newline='')
test_environment = csv.reader(f)

try:
    for state in test_environment:

        #TODO AGENT WILL TAKE A ROW INPUT FROM THE ENVIRONMENT AS ITS PERCEPT
        #EACH STATE REPRESENTS A 2-5 SECONDS OF ELAPSED TIME
        print(state) # state is an array
        print("last_price: " + state[0]) # testing array output



except csv.Error as e:
    sys.exit('file {}, line {}: {}'.format(filename, test_environment.line_num, e))