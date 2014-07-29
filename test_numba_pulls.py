from __future__ import print_function, absolute_import
import sys
import subprocess
import tempfile
from getpass import getpass
from StringIO import StringIO
from github3 import GitHub, login
platform = sys.argv[1]
print("Platform:", platform)

passed_label = 'passed_' + platform
failed_label = 'failed_' + platform
test_label = 'test_' + platform

ghuser = 'sklam'  # put your user name here
gh = login(ghuser, getpass('enter password for %s > ' % ghuser))

meta_yaml = """
package:
  name: numba
  version: testing

source:
  git_url: %(URL)s
  git_tag: %(TAG)s

requirements:
  build:
    - numpy
    - python
  run:
    - python
    - argparse        [py26]
    - numpy
    - llvmpy
    - cudatoolkit

test:
  requires:
    - unittest2      [py26]
  commands:
    - pycc -h
    - numba -h
"""

def do_testing(stdout):
    PY = '26', '27', '33'
    NP = '17', '18'
    for py, np in itertools.product(PY, NP):
        os.environ['CONDA_PY'] = py
        os.environ['CONDA_NPY'] = np
        subprocess.check_call("conda build --no-binstar-upload numba_template".split(),
                               stdout=stdout, stderr=subprocess.STDOUT)

def run():
    print("=== Run ===")
    # Get all open issues with test labels
    issues = gh.iter_repo_issues('sklam', 'numba-testing', state='open',
                                 labels=test_label)

    # Loop through all labels and get corresponding pull-request
    branches = []
    for iss in issues:
        firstline = iss.body.strip().splitlines()[0]
        prefix = 'https://github.com/numba/numba/pull/'
        if firstline.startswith(prefix):
            prnum = int(firstline[len(prefix):])
            print("PR", prnum)
            # Read Pull Request
            pr = gh.pull_request('numba', 'numba', prnum)
            data = pr.to_json()
            head = data['head']
            branch = head['ref']
            clone_url = head['repo']['clone_url']
            branches.append((iss, branch, clone_url))
    else:
        if not branches:
            print("Nothing to do")


    for iss, branch, url in branches:
        print("==", iss, branch, url, "==")
        with open("numba_template/meta.yaml", 'w') as fyaml:
            fyaml.write(meta_yaml % dict(URL=url, TAG=branch))

        stdout = tempfile.TemporaryFile()
        try:
            do_testing(stdout)
        except:
            print("Failed")
            iss.add_labels(failed_label)
            stdout.flush()
            log = stdout.read()
            iss.create_comment("== %s ==\n%s" % (platform, log))
            raise
        else:
            print("Passed")
        	iss.add_labels(passed_label)
        finally:
            iss.remove_label(test_label)


def main():
    while True:
        run()
        time.sleep(15 * 60)  # every 15 minutes


if __name__ == '__main__':
    main()


