from setuptools import setup
from Cython.Build import cythonize

setup(
    name='Hello world app',
    ext_modules=cythonize(["*.pyx"]),
    zip_safe=False,
)

#to build, run:
#python setup.py build_ext --inplace