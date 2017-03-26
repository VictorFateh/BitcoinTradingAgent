import csv, sys

filename = 'bfx_2017-03-25.csv'

f = open(filename, newline='')
percepts = csv.reader(f)

try:
    for data in percepts:

        #TODO AGENT WILL TAKE A ROW INPUT FROM PERCEPT
        #EACH STATE REPRESENTS A 2-5 SECONDS OF ELAPSED TIME
        print(data) # state is an array
        print("last_price: " + data[0]) # testing array output

except csv.Error as e:
    sys.exit('file {}, line {}: {}'.format(filename, percepts.line_num, e))
