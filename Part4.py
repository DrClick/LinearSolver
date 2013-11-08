__author__ = 'thomaswatson'
import sys
from SimplexDictionary import SimplexDictionary



def solve_dict(filename, debug):
    """
    Pivots the dictionary until it is final and reports the final objective value and number of pivots
    used to find the final dictionary
    """
    my_dictionary = SimplexDictionary.parse_from_file(filename, "INTEGER", debug)

    print my_dictionary.solve()
    print my_dictionary


def main():
    """
    Will solve all the dictionaries in the assignment
    """

    for i in xrange(1,2):
        print "Dict{0}".format(i)
        solve_dict("/Users/thomaswatson/code/coursera/linear/LinearSolver/dicts/ilpTests/unitTests/ilpTest{0}".format(i), False)

    return 0

if __name__ == '__main__':
    sys.exit(main())