from __future__ import print_function, absolute_import
import sys
import subprocess
import time
import os
import itertools
from pullutils import PRTesting

ghuser = 'sklam'  # put your user name here

platform = sys.argv[1]
print("Platform:", platform)

build_sh_template = """#!/bin/bash
%s
$PYTHON setup.py install
"""

bld_bat_template = """%s
%%PYTHON%% setup.py install
"""

templates = {
    'build.sh': build_sh_template,
    'bld.bat': bld_bat_template,
}


class NumbaPRTesting(PRTesting):
    def runtest(self, stdout):
        PY = ['26', '27', '33']
        NP = ['17', '18']
        for py, np in itertools.product(PY, NP):
            os.environ['CONDA_PY'] = py
            os.environ['CONDA_NPY'] = np
            print("==", py, np)
            cmd = "conda build --no-binstar-upload %s" % self.templatedir
            subprocess.check_call(cmd.split(), stdout=stdout,
                                  stderr=subprocess.STDOUT)


prtesting = NumbaPRTesting(platform, 'sklam', 'sklam', 'numba-testing',
                           'numba', 'numba', 'numba_template', templates)


def main():
    while True:
        prtesting.run()
        print("Waiting")
        time.sleep(15 * 60)  # every 15 minutes


if __name__ == '__main__':
    if '--test' in sys.argv[1:]:
        prtesting.test()
    else:
        main()

