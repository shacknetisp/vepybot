# -*- coding: utf-8 -*-


class ParserBadCommand(Exception):

    def __init__(self, m):
        Exception.__init__(self, m)
        self.msg = m


class NoPerms(Exception):

    def __init__(self, m):
        Exception.__init__(self, m)
        self.msg = m


class ModuleError(Exception):

    def __init__(self, m):
        Exception.__init__(self, m)
        self.msg = m