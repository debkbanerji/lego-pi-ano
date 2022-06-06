import time
import numpy as np
cimport cython
def hello_world():
    print("hello world")

def set_array(size):
    arr = np.zeros((size,), dtype=int)
    i = 0
    while i < arr.size:
        arr[i] = i
        i += 1

@cython.wraparound(False)
cpdef set_array_optimized(int size):
    arr = np.zeros((size,), dtype=int)
    cdef int[:] arr_view = arr
    cdef int i = 0
    while i < arr_view.shape[0]:
        arr_view[i] = i
        i += 1
