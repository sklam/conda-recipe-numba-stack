from __future__ import print_function, absolute_import
import sys
import tempfile
from getpass import getpass
import subprocess
from github3 import login


class PRTesting(object):
    def __init__(self, platform, ghuser, user, repo, pr_user, pr_repo,
                 templatedir, templates):
        self.platform = platform
        self.gh = login(ghuser, getpass())
        self.user = user
        self.repo = repo
        self.pullrepo = 'https://github.com/%s/%s/pull/' % (pr_user, pr_repo)
        self.pr_user = pr_user
        self.pr_repo = pr_repo
        self.templatedir = templatedir
        self.templates = templates
        self.labels = {
            'passed': 'passed_' + platform,
            'failed': 'failed_' + platform,
            'test': 'test_' + platform,
        }

    def test(self):
        self.runtest(sys.stdout)

    def configure(self, url, branch):
        get_master = "git clone https://github.com/%s/%s.git %s" % \
                        (self.pr_user, self.pr_repo, self.pr_repo)
        change_dir = "cd %s" % self.pr_repo
        pull_remote = "git pull %s %s" % (url, branch)
        cmds = '\n'.join([get_master, change_dir, pull_remote])
        with open("%s/build.sh" % self.templatedir, 'w') as fscript:
            fscript.write(self.templates['build.sh'] % cmds)
        with open("%s/bld.bat" % self.templatedir, 'w') as fscript:
            fscript.write(self.templates['bld.bat'] % cmds)

    def run(self):
        print("=== Run ===")
        # Get all open issues with test labels
        issues = self.gh.iter_repo_issues(self.user, self.repo, state='open',
                                          labels=self.labels['test'])

        # Loop through all labels and get corresponding pull-request
        branches = []
        for iss in issues:
            print("checking issue", iss)
            lines = iss.body.strip().splitlines()
            if not lines:
                continue
            firstline = lines[0]
            prefix = self.pullrepo
            if firstline.startswith(prefix):
                prnum = int(firstline[len(prefix):])
                print("PR", prnum)
                # Read Pull Request
                pr = self.gh.pull_request(self.pr_user, self.pr_user, prnum)
                data = pr.to_json()
                head = data['head']
                branch = head['ref']
                clone_url = head['repo']['clone_url']
                if data['mergeable']:
                    branches.append((iss, branch, clone_url))
                else:
                    print("not mergeable'")
            else:
                print('no prefix', prefix)
        else:
            if not branches:
                print("Nothing to do")

        for iss, branch, url in branches:
            print("==", iss, branch, url, "==")

            self.configure(url, branch)
            stdout = tempfile.TemporaryFile()
            try:
                self.runtest(stdout)
            except subprocess.CalledProcessError:
                print("Failed")
                stdout.flush()
                stdout.seek(0)  # reset read position
                log = stdout.read()

                iss.remove_label(self.labels['test'])
                iss.remove_label(self.labels['passed'])
                iss.add_labels(self.labels['failed'])

                files = {
                    '%s.txt' % self.repo: {
                        'content': log,
                    }
                }

                gist = self.gh.create_gist("error log %s" % self.platform,
                                           files)
                iss.create_comment("%s test failed! see log at: %s" %
                                   (self.platform, gist.html_url))
            else:
                print("Passed")
                iss.add_labels(self.labels['passed'])
                iss.remove_label(self.labels['failed'])
                iss.remove_label(self.labels['test'])

    def runtest(self):
        raise NotImplementedError
