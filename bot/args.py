# -*- coding: utf-8 -*-
from lib import utils


class NoArg(Exception):

    def __init__(self, m):
        Exception.__init__(self, m)
        self.msg = m


class Args:

    def __init__(self, d):
        self.d = d
        self.defaults = {}

    def default(self, n, d):
        """Set the default value of arg <n> to <d>"""
        self.defaults[n] = d

    def __contains__(self, n):
        return n in self.d

    def getstr(self, n):
        """Get the arg <n> as a str."""
        try:
            ret = None
            if n not in self.d and n in self.defaults:
                ret = self.defaults[n]
            else:
                ret = self.d[n]
            if ret is not None:
                return str(ret)
            return ret
        except KeyError:
            raise NoArg("Argument not found: %s" % n)

    def getint(self, n):
        """Get the arg <n> as an int."""
        s = self.getstr(n)
        try:
            return int(s)
        except ValueError:
            raise NoArg("Argument must be an integer: %s" % n)

    def getbool(self, n):
        """Get the arg <n> as a bool. For -kv args."""
        if n not in self.d:
            return False
        elif self.d[n] == "":
            return True
        return utils.boolstr(self.d[n])
