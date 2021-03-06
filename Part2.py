__author__ = 'thomaswatson'
from SimplexDictionary import SimplexDictionary
import sys

def pivot_dictionary_until_final(filename):
    """
    Pivots the dictionary until it is final and reports the final objective value and number of pivots
    used to find the final dictionary
    """
    my_dictionary = SimplexDictionary.parse_from_file(filename)

    print my_dictionary.pivot_until_final()


#For all the glory, solve the dictionaries

def main():
    """
    Will pivot all the dictionaries in the assignment
    """
    for i in range(1,6):
        print "Dict{0}".format(i)
        pivot_dictionary_until_final("/Users/thomaswatson/code/coursera/linear/LinearSolver/dicts/part2TestCases/assignmentParts/part{0}.dict".format(i))

    return 0

if __name__ == '__main__':
    sys.exit(main())