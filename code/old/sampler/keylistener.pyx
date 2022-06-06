import keyboard
from sampler import Sampler
import numpy as np
cimport cython

cdef class KeyListener():
    cdef public object sampler

    def __init__(self, sampler):
        self.sampler = sampler

    #Sampler must be initialized and loaded!
    @cython.wraparound(False)
    @cython.boundscheck(False)
    cpdef start_listening(self):
        cdef short[:] key_arr = self.sampler.generate_key_press_array()
        codes = self.sampler.key_arr
        print("codes:", codes)
        cdef int i
        while not keyboard.is_pressed('q'):
            for i in range(key_arr.shape[0]):
                if keyboard.is_pressed(chr(codes[i])):
                    key_arr[i] = 1
                else:
                    key_arr[i] = 0
            self.sampler.update_optimized_v2(key_arr)