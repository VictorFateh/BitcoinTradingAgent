#
# Naive Bayes
# http://machinelearningmastery.com/naive-bayes-classifier-scratch-python/
#

import csv
import random
import math

def loadCsv(filename, skip_header=False):
    f = open(filename, newline='')
    lines = csv.reader(f)
    if(skip_header == True):
        next(lines)
    dataset = list(lines)
    for i in range(len(dataset)):
        dataset[i] = [float(x) for x in dataset[i]]
    return dataset

def splitDataset(dataset, splitRatio):
    trainSize = int(len(dataset) * splitRatio)
    trainSet = []
    copy = list(dataset)
    while len(trainSet) < trainSize:
        index = random.randrange(len(copy))
        trainSet.append(copy.pop(index))
    return [trainSet, copy]


def separateByClass(dataset):
    separated = {}
    for i in range(len(dataset)):
        vector = dataset[i]
        if (vector[-1] not in separated):
            separated[vector[-1]] = []
        separated[vector[-1]].append(vector)
    return separated


def mean(numbers):
    return sum(numbers) / float(len(numbers))


def stdev(numbers):
    avg = mean(numbers)
    variance = sum([pow(x - avg, 2) for x in numbers]) / float(len(numbers) - 1)
    return math.sqrt(variance)


def summarize(dataset):
    summaries = [(mean(attribute), stdev(attribute)) for attribute in zip(*dataset)]
    del summaries[-1]
    return summaries


def summarizeByClass(dataset):
    separated = separateByClass(dataset)
    summaries = {}
    for classValue, instances in separated.items():
        summaries[classValue] = summarize(instances)
    return summaries


def calculateProbability(x, mean, stdev):
    exponent = math.exp(-(math.pow(x - mean, 2) / (2 * math.pow(stdev, 2))))
    return (1 / (math.sqrt(2 * math.pi) * stdev)) * exponent


def calculateClassProbabilities(summaries, inputVector):
    probabilities = {}
    for classValue, classSummaries in summaries.items():
        probabilities[classValue] = 1
        for i in range(len(classSummaries)):
            mean, stdev = classSummaries[i]
            x = inputVector[i]
            probabilities[classValue] *= calculateProbability(x, mean, stdev)
    return probabilities


def predict(summaries, inputVector):
    probabilities = calculateClassProbabilities(summaries, inputVector)
    bestLabel, bestProb = None, -1
    for classValue, probability in probabilities.items():
        if bestLabel is None or probability > bestProb:
            bestProb = probability
            bestLabel = classValue
    return bestLabel


def getPredictions(summaries, testSet):
    predictions = []
    for i in range(len(testSet)):
        result = predict(summaries, testSet[i])
        predictions.append(result)
    return predictions


def getAccuracy(testSet, predictions):
    correct = 0
    for i in range(len(testSet)):
        if testSet[i][-1] == predictions[i]:
            correct += 1
    return (correct / float(len(testSet))) * 100.0


def main():
    filename = 'pima-indians-diabetes.csv'
    splitRatio = 0.67
    dataset = loadCsv(filename)
    trainingSet, testSet = splitDataset(dataset, splitRatio)
    #print('Split {0} rows into train={1} and test={2} rows').format(len(dataset), len(trainingSet), len(testSet))
    # prepare model
    summaries = summarizeByClass(trainingSet)
    # test model
    predictions = getPredictions(summaries, testSet)
    accuracy = getAccuracy(testSet, predictions)
    #print('Accuracy: {0}%').format(accuracy)


#main()

#
# calculate rolling stats on live data
# https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance
#

class rollingStat():
    def __init__(self,data_type=""):
        self.data_type = data_type
        self.K = 0
        self.n = 0
        self.ex = 0
        self.ex2 = 0

    def add_variable(self,x):
        if (self.n == 0):
            self.K = x
        self.n = self.n + 1
        self.ex += x - self.K
        self.ex2 += (x - self.K) * (x - self.K)

    def remove_variable(self,x):
        self.n = self.n - 1
        self.ex -= (x - self.K)
        self.ex2 -= (x - self.K) * (x - self.K)

    def get_meanvalue(self):
        return self.K + self.ex / self.n

    def get_variance(self):
        return (self.ex2 - (self.ex * self.ex) / self.n) / (self.n - 1)

    def get_stdev(self):
        return math.sqrt( self.get_variance() )

    def print(self):
        print(self.data_type)
        print('mean:', self.get_meanvalue())
        print('stdv:', self.get_stdev())


# test if both methods give the same results
"""
data = [5,6,7,8,9]
print("testing first functions")
m = mean(data)
print('mean:',m)
sd = stdev(data)
print('sd:',sd)


r2 = rollingStat()
for i in data:
    r2.add_variable(i)
print('testing rolling stats; same data')
print('mean:',r2.get_meanvalue())
print('sd:',math.sqrt(r2.get_variance()))

# test to see what our data looks like
print("test to see what our data looks like")
filename = 'bfx_2017-03-25.csv'
f = open(filename, newline='')
percepts = csv.reader(f)

price = rollingStat("\nprice")
sell_price = rollingStat("\nsell_price")
buy_price = rollingStat("\nbuy_price")
sell_size = rollingStat("\nsell_size")
buy_size = rollingStat("\nbuy_size")
next(percepts)  # skip header in csv


for percept in percepts:
    ltp, sp, ss, bp, bs = percept
    # print("price: ", self.current_price)#For debugging
    price.add_variable( float(ltp) )
    sell_price.add_variable(  float(sp) )
    sell_size.add_variable(  float(ss) )
    buy_price.add_variable(  float(bp) )
    buy_size.add_variable(  float(bs) )

price.print()
sell_price.print()
sell_size.print()
buy_price.print()
buy_size.print()

# see different price probabilities

print()
p = 980
sum = 0
while(p >= 900):
    pp = calculateProbability(p,price.get_meanvalue(),price.get_stdev())
    sum += pp
    print("probability of ${}: {}".format(p, pp))
    p -= 1
print("probability sum:",sum)


dataset = [[1,20,1], [2,21,0], [3,22,1]]
separated = separateByClass(dataset)
print('Separated instances: ',separated)
"""