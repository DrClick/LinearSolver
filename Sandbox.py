from array import array
from numpy import *
import scipy as Sci
import scipy.linalg
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



pivotDictionary("/users/thomaswatson/code/coursera/linear/LinearSolver/dicts/week2/unitTests/dict1.txt")

