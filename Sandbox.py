from array import array
from numpy import *
import scipy as Sci
import scipy.linalg
from SimplexDictionary import SimplexDictionary

test = mat([[1,2,3,4,5,6],[1,1,1,1,1,1]])
update = [6,8,9,0,1,2]

test[1, :] += update

print test

print shape(test)[0]




