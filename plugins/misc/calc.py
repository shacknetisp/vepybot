# -*- coding: utf-8 -*-
import bot
import ast
import operator
import math
import random

_operations = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.BitXor: operator.xor,
}


def _safe_eval(node, variables, functions):
        if isinstance(node, ast.Num):
                return node.n
        elif isinstance(node, ast.Name):
                return variables[node.id]
        elif isinstance(node, ast.BinOp):
                op = _operations[node.op.__class__]
                left = _safe_eval(node.left, variables, functions)
                right = _safe_eval(node.right, variables, functions)
                if isinstance(node.op, ast.Pow):
                        assert right < 100, 'pow operator too large.'
                        assert right < 1000000000, 'pow operator too large.'
                return op(left, right)
        elif isinstance(node, ast.Call):
                assert (not node.keywords and not
                        node.starargs and not node.kwargs)
                assert isinstance(node.func,
                                  ast.Name), 'Unsafe function derivation.'
                func = functions[node.func.id]
                args = [_safe_eval(arg, variables, functions)
                        for arg in node.args]
                return func(*args)

        assert False, 'Unsupported operation.'


def safe_eval(expr, variables={}, functions={}):
        node = ast.parse(expr, '<string>', 'eval').body
        return _safe_eval(node, variables, functions)


class Module(bot.Module):

    index = "calc"

    def register(self):

        self.addcommand(self.calc, "calc", "Evaluate an expression.",
                        ['expr...'])

    def calc(self, context, args):
        expr = args.getstr('expr')
        v = {}
        f = {}
        s = {}
        for k in math.__dict__:
            if not k.startswith('_'):
                s[k] = math.__dict__[k]
        for x in ['uniform', 'random', 'randrange', 'normalvariate']:
            s[x] = random.__dict__[x]
        for k in s:
            if hasattr(s[k], '__call__'):
                f[k] = s[k]
            else:
                v[k] = s[k]
        try:
            return str(safe_eval(expr, v, f)) or 'Invalid expression.'
        except AssertionError as e:
            return e
        except Exception as e:
            return 'Unable to evaluate: %s' % e

bot.register.module(Module)
