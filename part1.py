__author__ = 'thomaswatson'

from Dictionary import Dictionary

def pivotDictionary(filename):
    myDictionary = Dictionary.parseFromFile(filename)
    entering = myDictionary.calcEnteringVariable()
    leaving = myDictionary.calcLeavingVariable(entering)
    objectiveValue = myDictionary.pivot(entering, leaving)

    if leaving != -1:
        if entering != -1:
            print entering
            print leaving
            print objectiveValue
        else:
            print "FINALIZED"
    else:
        print "UNBOUNDED"


for i in range(1,11,1):
    print "Dict{0}".format(i)
    pivotDictionary("/users/thomaswatson/code/coursera/linear/LinearSolver/dicts/week2/unitTests/dict{0}.txt".format(i))
