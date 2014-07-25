from __future__ import print_function

import os
import subprocess

PY = '26', '27', '33', '34'
for pyver in PY:
	os.environ['CONDA_PY'] = pyver
	subprocess.check_call(['conda', 'build', 'llvmpy'])
