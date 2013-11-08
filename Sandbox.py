from array import array
import numpy as np
import scipy as Sci
import scipy.linalg
from SimplexDictionary import SimplexDictionary

test = np.mat([[1,2,3,4,5,6],[1,1,1,1,1,1]])
update = [1,8,9,-1,1,2]

test[1, :] += update

test = np.c_[test, np.ones(2)]

print test







