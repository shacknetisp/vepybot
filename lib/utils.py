# -*- coding: utf-8 -*-
import re


def boolstr(s):
    if str(s).lower() in ['1', 'yes', 'y', 'true']:
        return True
    return False


def ynstr(b, y="yes", n="no"):
    return y if b else n


def match(t, r):
    return (t == r) or re.match(r, t)


def imatch(t, r):
    return (t == r) or re.match(r, t, re.IGNORECASE)

def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None
