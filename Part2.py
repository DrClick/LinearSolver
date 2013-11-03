__author__ = 'thomaswatson'
from SimplexDictionary import SimplexDictionary


def pivot_dictionary_until_final(filename):
    my_dictionary = SimplexDictionary.parse_from_file(filename)

    result = "PIVOTING"
    objective_value = None
    iterations = 0

    while result == "PIVOTING":
        entering = my_dictionary.calc_entering_variable()
        if entering == -1:
            result = "FINALIZED"
            break

        leaving = my_dictionary.calc_leaving_variable(entering)

        if __debug__:
            print "Iteration: {0}".format(iterations)
            print my_dictionary
            print "entering: {0} - {1}".format(entering, my_dictionary._nonbasic)
            print "leaving: {0} - {1}".format(leaving, my_dictionary._basic)
            print "\n\n"

        if entering != -1 and leaving != -1:
            objective = my_dictionary.pivot(entering, leaving)
            iterations += 1

            if objective is not None:
                objective_value = objective

        else:
            if leaving == -1:
                result = "UNBOUNDED"
            else:
                result = "FINALIZED"

    if result == "FINALIZED":
        print objective_value
        print iterations
    else:
        print "UNBOUNDED"


#For all the glory, solve the dictionaries
for i in range(1,6):
    print "Dict{0}".format(i)
    pivot_dictionary_until_final("/Users/thomaswatson/code/coursera/linear/LinearSolver/dicts/part2TestCases/assignmentParts/part{0}.dict".format(i))