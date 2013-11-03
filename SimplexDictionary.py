from numpy import *
import sys
import Watson

"""
Rudimentary implementation of simplex algorithm of Linear Programming. The following LaTex will show what a dictionary
looks like

\begin{array}{c| c c c c c }
x_{B1} & b_1 & + a_{11} x_{N1} & + \cdots + & a_{1n} x_{Nn} \\
\vdots & \vdots &  & \ddots & \\
x_{Bj} & b_j & + a_{j1} x_{N1} & + \cdots + & a_{jn} x_{Nn}\\
\vdots & \\
x_{Bm} & b_m & + a_{m1} x_{N1} & + \cdots + & a_{mn} x_{Nn} \\
\hline
z & z_0 & + c_1 x_{N1} & + \cdots + & c_n x_{Nn} \\
\end{array}

"""
class SimplexDictionary:
    # Represents a linear programming problem in standard form Max. cTx S.T. Ax = b (slack variables added)
    _basic = None
    _nonbasic = None
    _A = None
    _B = None
    _C = None
    _z = None

    def __init__(self, m, n, debug=None):
        self.__debug = debug
        _basic = array('i')
        _nonbasic = array('i')
        _A = empty(shape=(m, n))
        _B = array('f')
        _C = array('f')

    def __str__(self):
        sb = Watson.StringBuilder()

        #basic and A matrix
        for i, b in enumerate(self._basic):
            sb.append("X{0}\t| {1}\t ".format(b, self._B[i]))
            sb.appendLine(self._A[i, :])

        #last row`
        sb.appendLine("--------------------------")
        last_row = []
        for i, c in enumerate(self._C):
            last_row.append("{0}X{1}".format(c, self._nonbasic[i]))

        sb.appendLine("z\t| {0}\t {1}".format(self._z, '\t'.join(last_row)))

        return sb.__str__()

    """
    Determines what variable should enter for the pivot, -1 if dictionary is final. Uses Bland's Rule for breaking ties
    """
    def calc_entering_variable(self):
        #find the lowest index positive coefficient of C (Blands Rule)
        candidate_var = sys.maxint
        for i, c in enumerate(self._C):
            if c > 0.0:  # found a positive coefficient
                if self._nonbasic[i] < candidate_var:
                    candidate_var = self._nonbasic[i]

        return candidate_var if candidate_var < sys.maxint else -1

    """
    Determines the leaving variable given the entering variable. Returns -1 if unbounded. Uses Bland's Rule for breaking
    ties
    """
    def calc_leaving_variable(self, entering):

        enter_index = self.__get_entering_index(entering)
        smallest_constraint = float("inf")
        index_of_smallest = -1

        #find the smallest constraint where A[?,entering] is negative
        for i, a in enumerate(self._A[:, enter_index]):
            if a < 0:
                constraint = abs(self._B[i] / a)

                if constraint <= smallest_constraint:
                    if (index_of_smallest == -1
                        or constraint == smallest_constraint and self._basic[i] < self._basic[index_of_smallest]
                        or constraint < smallest_constraint):
                        smallest_constraint = constraint
                        index_of_smallest = i

        return self._basic[index_of_smallest] if index_of_smallest >= 0 else -1

    def __get_entering_index(self, entering):
        return self._nonbasic.index(entering)

    def __get_leaving_index(self, leaving):
        return self._basic.index(leaving)

    """
    Pivots the dictionary. See https://class.coursera.org/linearprogramming-001/lecture/45 for an explanation of the
    logic. Basically, enter the dictionary, solve for the new leaving variable, and finally do
    algebraic substitution to find the new dictionary.
    """
    def pivot(self, entering, leaving):
        enter_index = self.__get_entering_index(entering)
        leave_index = self.__get_leaving_index(leaving)

        if enter_index == -1 or leave_index == -1:
            return None

        #swap the basic value
        self._basic[leave_index] = entering
        self._nonbasic[enter_index] = leaving

        #divide row by the coefficient of A[leave,enter] (solves for the new entering variable
        coeff_entering = self._A[leave_index, enter_index] * -1
        self._A[leave_index, enter_index] = -1

        #fix up the B value
        self._B[leave_index] /= coeff_entering

        #fix up the entering row
        self._A[leave_index, :] /= coeff_entering

        #add the entering row to each other row of A, B and C multiplied by the coefficient
        rows_in_a = shape(self._A)[0]
        for i in xrange(rows_in_a):
            #skip this row if it is the leaving row
            if i != leave_index:
                multiplier = self._A[i, enter_index]  # this is the var being replaced
                self._A[i, enter_index] = 0  # zero it out !IMPORTANT after finding the coefficient
                self._B[i] = self._B[i] + multiplier * self._B[leave_index]
                self._A[i, :] += multiplier * self._A[leave_index, :]

        #substitute C
        final_multiplier = self._C[enter_index]
        self._C[enter_index] = 0
        self._C += final_multiplier * self._A[leave_index, :]

        #calculate new z
        self._z = self._z + final_multiplier * self._B[leave_index]

        return self._z

    """
    Reads in dictionary from file with the following format:

    [Line 1] m n
    [Line 2] B1 B2 ... Bm [the list of basic indices m integers]
    [Line 3] N1 N2 ... Nn [the list of non-basic indices n integers]
    [Line 4] b1 .. bm (m floating point numbers)
    [Line 5] a11 ... a1n (first row coefficients. See dictionary notation above.)
    ....
    [Line m+4] am1 ... amn (mth row coefficients. See dictionary notation above.)
    [Line m+5] z0 c1 .. cn (objective coefficients (n+1 floating point numbers))
    """
    @staticmethod
    def parse_from_file(filename):
        data = open(filename, "r").readlines()

        mn = data[0].split()
        m = int(mn[0])
        n = int(mn[1])
        basic = [int(x) for x in data[1].split()]
        nonbasic = [int(x) for x in data[2].split()]

        B = [float(x) for x in data[3].split()]
        A = empty(shape=(m, n))
        C = [float(x) for x in data[4 + m].split()[1:]]
        z = float(data[4 + m].split()[0])

        #loop through and add data to matrix
        for i in xrange(m):
            row = [float(x) for x in data[4 + i].split()]
            for j, r in enumerate(row):
                A[i, j] = r

        d = SimplexDictionary(m, n)
        d._A = A
        d._B = B
        d._C = C
        d._basic = basic
        d._nonbasic = nonbasic
        d._z = z

        return d