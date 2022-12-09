import os
import re
import sys
import subprocess

import subprocess_tee
from jaraco.functools import pass_none


class Handler:
    def __init__(self):
        self.suppressed = ignored_failures(os.environ.get('SAFETY_TOX_ALLOWED', ''))

    @property
    def runner(self):
        return [subprocess.run, subprocess_tee.run][bool(self.suppressed)]

    @pass_none
    def matches(self, output):
        pattern = f'({"|".join(self.suppressed)})'
        return re.search(
            rf'^Collecting {pattern}$', output, flags=re.MULTILINE | re.IGNORECASE
        )

    def run(self, args):
        cmd = [sys.executable, '-m', 'tox'] + args
        proc = self.runner(cmd)
        if proc.returncode and self.matches(proc.stdout):
            print("safety-tox suppressing return code {proc.returncode}")
            proc.returncode = 0
        return proc.returncode


def ignored_failures(spec):
    """
    >>> ignored_failures('ab-c 123, xyz')
    ['ab-c', '123', 'xyz']
    >>> ignored_failures('')
    []
    """
    return re.findall(r'[-\w]+', spec)


def run(args):
    raise SystemExit(Handler().run(args))


__name__ == '__main__' and run(sys.argv[1:])
