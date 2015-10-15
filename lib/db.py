# -*- coding: utf-8 -*-
import os
import bot
import json
import ast
from threading import Lock

lock = Lock()
dbs = {}
modified = {}


class DB:

    def __init__(self, path, d=None, userdata=True):
        with lock:
            if d is None:
                d = {}
            path = ("%s/%s" % (bot.userdata, path)) if userdata else path
            if path not in dbs:
                if os.path.exists(path):
                    try:
                        dbs[path] = json.load(open(path))
                    except ValueError as e:
                        print(("(%s) Invalid JSON, loading with AST." % path))
                        try:
                            dbs[path] = ast.literal_eval(open(path).read())
                        except SyntaxError as e:
                            raise SyntaxError(
                                "Invalid AST (%s): %s" % (path, e))
                        except ValueError as e:
                            raise ValueError(
                                "Invalid AST (%s): %s" % (path, e))
                else:
                    dbs[path] = d
            self.d = dbs[path]
            self.path = path
            modified[self.path] = True

    def save(self):
        with lock:
            modified[self.path] = True


def saveall():
    for path, d in list(dbs.items()):
        if modified[path]:
            json.dump(d, open(path, 'w'), indent=4, sort_keys=True)
            modified[path] = False
