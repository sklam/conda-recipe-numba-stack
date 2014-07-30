from __future__ import print_function

import os
import itertools
import subprocess

PY = '26', '27', '33', '34'
NPY = '16', '17', '18',  # forget about npy16 for now

def but_not(py, npy):
	return (py >= '33' and npy <= '16') or (py == '34' and npy <= '17')

subprocess.check_call("conda config --force --add channels https://conda.binstar.org/sklam".split())

try:
	for py, npy in itertools.product(PY, NPY):
		if not but_not(py, npy):
			os.environ['CONDA_PY'] = py
			os.environ['CONDA_NPY'] = npy
			subprocess.check_call(['conda', 'build', 'numba'])
finally:
	subprocess.check_call("conda config --force --remove channels https://conda.binstar.org/sklam".split())
