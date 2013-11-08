import numpy as np
import sys
import Watson



class SimplexDictionary:
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
    # Represents a linear programming problem in standard form Max. cTx S.T. Ax = b (slack variables added)
    _basic = None
    _nonbasic = None
    _A = None
    _B = None
    _C = None
    _z = None
    _isInDualMode = False
    _mode = None

    _status = {'FINALIZED': 0, 'PIVOTING': 1, 'UNBOUNDED': 2, 'UNFEASIBLE': 3}
    _modes = {'INTEGER': 0, 'LINEAR': 1}


    def __init__(self, m, n, mode, debug=None):
        self.__debug = debug
        self._basic = np.array('i')
        self._nonbasic = np.array('i')
        self._A = np.empty(shape=(m, n))
        self._B = np.array('f')
        self._C = np.array('f')
        self._mode = self._modes[mode]

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

    def calc_entering_variable(self):
        """
        Determines what variable should enter for the pivot, -1 if dictionary is final. Uses Bland's Rule for breaking ties
        """
        #find the lowest index positive coefficient of C (Blands Rule)
        candidate_var = sys.maxint
        for i, c in enumerate(self._C):
            if c > 0.0:  # found a positive coefficient
                if self._nonbasic[i] < candidate_var:
                    candidate_var = self._nonbasic[i]

        return candidate_var if candidate_var < sys.maxint else -1

    def calc_leaving_variable(self, entering):
        """
        Determines the leaving variable given the entering variable. Returns -1 if unbounded. Uses Bland's Rule for breaking
        ties
        """
        enter_index = self.__get_entering_index(entering)
        smallest_constraint = float("inf")
        index_of_smallest = -1

        #find the smallest constraint where A[?,entering] is negative
        for i, a in enumerate(self._A[:, enter_index]):
            if a < 0 or entering == 0:
                constraint = self._B[i] / abs(a)

                if constraint <= smallest_constraint:
                    if (index_of_smallest == -1
                        or constraint == smallest_constraint and self._basic[i] < self._basic[index_of_smallest]
                        or constraint < smallest_constraint):
                        smallest_constraint = constraint
                        index_of_smallest = i

        return self._basic[index_of_smallest] if index_of_smallest >= 0 else -1

    def __get_entering_index(self, entering):
        return np.nonzero(self._nonbasic == entering)[0][0]

    def __get_leaving_index(self, leaving):
        return np.nonzero(self._basic == leaving)[0][0]

    def pivot(self, entering, leaving):
        """
        Pivots the dictionary. See https://class.coursera.org/linearprogramming-001/lecture/45 for an explanation of the
        logic. Basically, enter the dictionary, solve for the new leaving variable, and finally do
        algebraic substitution to find the new dictionary.
        """
        if entering == -1 or leaving == -1:
            return None

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
        rows_in_a = np.shape(self._A)[0]
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

    def solve(self):
        """
        Solves the linear program by first determine if the dictionary is feasible, if not, then it converts the problem
        to the dual and then solves.

        If dual, the problem is converted back to the original problem when finalized

        If this is integer ILP, then the solution uses Gomory/Chvatal cutting planes to reduce the feasible space to
        the integer hull.
        """

        #determine if feasible
        if not all([i >= 0 for i in self._B]):
            self.toggle_dual_problem()

        result = self.pivot_until_final()

        #if the dictionary was finalized in the dual, switch it back to the primal mode
        if result["status"] == self._status["FINALIZED"] and self._isInDualMode:
            self.toggle_dual_problem()

        #check for integers if in integer mode
        if result["status"] == self._status["FINALIZED"] and self._mode == self._modes["INTEGER"]:
            if not all([i == int(i) for i in self._B]):
                self.add_cutting_plane()
                result["status"] = self._status["PIVOTING"]
                self.solve()

        return result

    def add_cutting_plane(self):
        """
        Adds a Gomory/Chvatal cutting plane constraint
        """

        #find the first partial B
        cutting_var_index = np.nonzero(self._B != [int(i) for i in self._B])[0][0]
        b = -(self._B[cutting_var_index] - np.floor(self._B[cutting_var_index]))
        a = -self._A[cutting_var_index, :] - np.floor(-self._A[cutting_var_index, :])
        basic = max(max(self._nonbasic), max(self._basic)) + 1  # gets the next available var for the new constraint

        self._A = np.vstack((self._A, a))
        self._B = np.hstack((self._B, b))
        self._basic = np.hstack((self._basic, basic))

        if self.__debug:
            print "dictionary after dded cutting plane"
            print self

    def toggle_dual_problem(self):
        """
        Toggles the problem between being in the dual form or primal
        The dual given the dictionary is in the form:
            max c^{T}
            S.T Ax <= b

            is

            max -b^{T}y
            S.T. -A^{T}y <= c
        """
        self._isInDualMode = not self._isInDualMode

        #change the variables
        (self._basic, self._nonbasic) = self._nonbasic, self._basic
        #convert their values
        (self._B, self._C) = self._C * -1, self._B * -1
        #negate the objective
        self._z = -self._z
        #transponse and negate A
        self._A = -1 * np.transpose(self._A)

    def pivot_until_final(self):
        """
        Pivots the dictionary until it is final and reports the final objective value and number of pivots
        used to find the final dictionary
        """

        result = self._status["PIVOTING"]
        objective_value = None
        iterations = 0

        while result == self._status["PIVOTING"]:
            entering = self.calc_entering_variable()
            if entering == -1:
                result = self._status["FINALIZED"]
                break

            leaving = self.calc_leaving_variable(entering)

            if self.__debug:
                print "Iteration: {0}".format(iterations)
                print self
                print "entering: {0} - {1}".format(entering, self._nonbasic)
                print "leaving: {0} - {1}".format(leaving, self._basic)
                print "\n\n"

            if entering != -1 and leaving != -1:
                objective = self.pivot(entering, leaving)
                iterations += 1

                if objective is not None:
                    objective_value = objective

            else:
                if leaving == -1:
                    result = self._status["UNBOUNDED"]
                else:
                    result = self._status["FINALIZED"]

        return {"status": result, "objective_value": objective_value, "num_iterations": iterations}

    @staticmethod
    def parse_from_file(filename, mode="LINEAR", debug=False):
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
        data = None
        with open(filename, "r") as file_handle:
            data = file_handle.readlines()

        mn = data[0].split()
        m = int(mn[0])
        n = int(mn[1])
        basic = [int(x) for x in data[1].split()]
        nonbasic = [int(x) for x in data[2].split()]

        B = [float(x) for x in data[3].split()]
        A = np.empty(shape=(m, n))
        C = [float(x) for x in data[4 + m].split()[1:]]
        z = float(data[4 + m].split()[0])

        #loop through and add data to matrix
        for i in xrange(m):
            row = [float(x) for x in data[4 + i].split()]
            for j, r in enumerate(row):
                A[i, j] = r

        d = SimplexDictionary(m, n, mode, debug)
        d._A = A
        d._B = np.array(B)
        d._C = np.array(C)
        d._basic = np.array(basic)
        d._nonbasic = np.array(nonbasic)
        d._z = z

        return d