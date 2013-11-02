from array import array
from numpy import *
import scipy as Sci
import scipy.linalg
import Watson


class Dictionary:
    # Represents a linear programming problem in standard form Max. cTx S.T. Ax <= b
    _basic = None
    _nonbasic = None
    _A = None
    _B = None
    _C = None
    _z = None

    def __init__(self, m, n):
        _basic = array('i')
        _nonbasic = array('i')
        _A = mat()
        _B = array('f')
        _C = array('f')

    def __str__(self):
        sb = Watson.StringBuilder()


        #basic and A matrix
        for i in range(self._basic.Length):
            sb.Append("X{0}\t| {1}\t ".format(self._basic[i], self._B[i]))
            sb.AppendLine(self._A[i, :])

        #last row
        sb.AppendLine("--------------------------");
        lastRow = []
        for i in range(len(self._C)):
            lastRow.append("{0}X{1}".format(self._C[i], self._nonbasic[i]))

        sb.AppendLine("z\t| {0}\t {1}".format(self._z, '\t'.join(lastRow)))

        return sb.__str__()

    def calcEnteringVariable(self):
        candidateVar = sys.maxint
        for i in range(len(self._C)):
            if self._C[i] > 0.0:
                if self._nonbasic[i] < candidateVar:
                    candidateVar = self._nonbasic[i]

        if candidateVar < int.MaxValue:
            return candidateVar  #not finalized
        return -1  #Finalized

    def calcLeavingVariable(self, entering):

        enterIndex = self.__getEnteringIndex(entering)
        smallestContraint = float("inf")
        indexOfSmallest = -1


        #find the smallest contraint where A[?,entering] is negative
        for i in range(len(self._A)):
            a = self._A[i, enterIndex]
            constraint = math.abs(self._B[i] / a)

            if a < 0 and constraint <= smallestContraint:
                if indexOfSmallest == -1 \
                    or constraint == smallestContraint and self._basic[i] < self._basic[indexOfSmallest] \
                    or constraint < smallestContraint:
                    smallestContraint = constraint
                    indexOfSmallest = i

        return self._basic[indexOfSmallest] if indexOfSmallest >= 0 else -1

    def __getEnteringIndex(self, entering):

        indexOfEnteringVariable = -1
        for i in range(len(self._nonbasic)):
            if (self._nonbasic[i] == entering):
                indexOfEnteringVariable = i
                break

        return indexOfEnteringVariable

    def __getLeavingIndex(self, leaving):
        indexOfLeavingVariable = -1

        for i in range(len(self._basic)):
            if self._basic[i] == leaving:
                indexOfLeavingVariable = i
                break

        return indexOfLeavingVariable

    def pivot(self, entering, leaving):
        enterIndex = self.__getEnteringIndex(entering)
        leaveIndex = self.__getLeavingIndex(leaving)

        if enterIndex == -1 or leaveIndex == -1:
            return None

        #swap the basic value
        self._basic[leaveIndex] = entering
        self._nonbasic[enterIndex] = leaving

        #divide row by the A value (solves for the new entering variable
        coeffEntering = self._A[leaveIndex, enterIndex] * -1
        self._A[leaveIndex, enterIndex] = -1

        #fix up the B value
        self._B[leaveIndex] /= coeffEntering

        #fix up the A Matrix
        for i in range(shape(self._A)[1]):
            self._A[leaveIndex, i] /= coeffEntering

        #add this row to each other row and C multiplied by the coefficient
        for i in range(len(self._A)):
            #skip this row if it is the leaving row
            if i != leaveIndex:
                multiplier = self._A[i, enterIndex]
                self._B[i] = self._B[i] + multiplier * self._B[leaveIndex]
                for j in range(shape(self._A)[1]):
                    self._A[i, j] = self._A[i, j] + multiplier * self._A[leaveIndex, j]

        #substitute C
        finalMultipler = self._C[enterIndex]
        for i in range(len(self._C)):
            self._C[i] = self._C[i] + finalMultipler * self._A[leaveIndex, i]

        #calculate new z
        self._z = self._z + finalMultipler * self._B[leaveIndex]

        return self._

    def parseFromFile(self, filename):
        data = open(filename, "r").readlines()
        mn = data[0].split()
        m = int(mn[0])
        n = int(mn[1])
        basic = [int(x) for x in data[1].split()]
        nonbasic = [int(x) for x in data[2].split()]
        B = [float(x) for x in data[3].split()]
        A = mat(m, n)
        C = [float(x) for x in data[4 + m].split()[1:]]
        z = float(data[4 + m].split()[0])

        #loop through and add data to matrix
        for i in range(m):
            row = [float(x) for x in data[4 + i].split()]
            for j in range(len(row)):
                A[i, j] = row[j]

        d = Dictionary(m, n)
        d._A = A
        d._B = B
        d._C = C
        d._basic = basic
        d._nonbasic = nonbasic
        d._z = z

        return dict