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
