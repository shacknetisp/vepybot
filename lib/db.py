# -*- coding: utf-8 -*-
import os
import bot
import json
import ast
from threading import Lock

lock = Lock()
dbs = {}
modified = {}


def literal_eval(node_or_string):
    if isinstance(node_or_string, str):
        node_or_string = ast.parse(node_or_string, mode='eval')
    if isinstance(node_or_string, ast.Expression):
        node_or_string = node_or_string.body

    def _convert(node):
        if isinstance(node, (ast.Str, ast.Bytes)):
            return node.s
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Tuple):
            return tuple(map(_convert, node.elts))
        elif isinstance(node, ast.List):
            return list(map(_convert, node.elts))
        elif isinstance(node, ast.Set):
            return set(map(_convert, node.elts))
        elif isinstance(node, ast.Dict):
            return dict((_convert(k), _convert(v)) for k, v
                        in zip(node.keys, node.values))
        elif isinstance(node, ast.NameConstant):
            return node.value
        elif isinstance(node, ast.UnaryOp) and \
            isinstance(node.op, (ast.UAdd, ast.USub)) and \
                isinstance(node.operand, (ast.Num, ast.UnaryOp, ast.BinOp)):
            operand = _convert(node.operand)
            if isinstance(node.op, ast.UAdd):
                return + operand
            else:
                return - operand
        elif isinstance(node, ast.BinOp) and \
            isinstance(node.op, (ast.Add, ast.Sub)) and \
            isinstance(node.right, (ast.Num, ast.UnaryOp, ast.BinOp)) and \
                isinstance(node.left, (ast.Num, ast.UnaryOp, ast.BinOp)):
            left = _convert(node.left)
            right = _convert(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            else:
                return left - right
        elif node.id in ['true', 'false']:
            return node.id == 'true'
        raise ValueError('malformed node or string: ' + repr(node))
    return _convert(node_or_string)


class DB:

    clear = lambda: None

    def __init__(self, path, d=None, userdata=True):
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
                        dbs[path] = literal_eval(open(path).read())
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
        modified[self.path] = True


def saveall():
    for path, d in list(dbs.items()):
        if modified[path]:
            json.dump(d, open(path, 'w'), indent=4, sort_keys=True)
            modified[path] = False
