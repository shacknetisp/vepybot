# -*- coding: utf-8 -*-


def boolstr(s):
    if str(s).lower() in ['1', 'yes', 'y', 'true']:
        return True
    return False


def ynstr(b, y="yes", n="no"):
    return y if b else n