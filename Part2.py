__author__ = 'thomaswatson'
from Dictionary import Dictionary

def pivotDictionaryUntilFinal(filename):
    myDictionary = Dictionary.parseFromFile(filename)

    result = "PIVOTING"
    objectiveValue = None
    iterations = 0

    while result == "PIVOTING":
        entering = myDictionary.calcEnteringVariable()
        leaving = myDictionary.calcLeavingVariable(entering)

        #print "Iteration: {0}".format(iterations)
        #print myDictionary
        #print "entering: {0} - {1}".format(entering, myDictionary._nonbasic)
        #print "leaving: {0} - {1}".format(leaving, myDictionary._basic)
        #print "\n\n"

        if entering != -1 and leaving != -1:
            objective = myDictionary.pivot(entering, leaving)
            iterations += 1


            if objective is not None:
                objectiveValue = objective

        else:
            if leaving == -1:
                result = "UNBOUNDED"
            else:
                result = "FINALIZED"

    if result == "FINALIZED":
        print objectiveValue
        print iterations
    else:
        print "UNBOUNDED"


#For all the glory, solve the dictionaries
for i in range(1,6,1):
    print "Dict{0}".format(i)
    pivotDictionaryUntilFinal("/Users/thomaswatson/code/coursera/linear/LinearSolver/dicts/part2TestCases/assignmentParts/part{0}.dict".format(i))