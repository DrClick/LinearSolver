__author__ = 'thomaswatson'
"""
This module is no longer relevant. This was an interim step in the solver
"""

import sys
from SimplexDictionary import SimplexDictionary


def init_dict(filename, debug):
    """
    Pivots the dictionary until it is final and reports the final objective value and number of pivots
    used to find the final dictionary
    """
    my_dictionary = SimplexDictionary.parse_from_file(filename, debug)

    print my_dictionary.initialize()


#For all the glory, solve the dictionaries

def main():
    """
    Will pivot all the dictionaries in the assignment
    """
    for i in xrange(1,7):
        print "Dict{0}".format(i)
        init_dict("/Users/thomaswatson/code/coursera/linear/LinearSolver/dicts/initializationTests/assignmentTests/part{0}.dict".format(i), False)

    return 0

if __name__ == '__main__':
    sys.exit(main())
