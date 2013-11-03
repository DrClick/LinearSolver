__author__ = 'thomaswatson'

from SimplexDictionary import SimplexDictionary

def pivotDictionary(filename):
    myDictionary = SimplexDictionary.parse_from_file(filename)
    entering = myDictionary.calc_entering_variable()
    leaving = myDictionary.calc_leaving_variable(entering)
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
