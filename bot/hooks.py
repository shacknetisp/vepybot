# -*- coding: utf-8 -*-
import time


class HookBase:

    def addhook(self, name, uname, function):
        """Add a hook to <name> with the unique id <uname>
        and the function <function>."""
        if name not in self.hooks:
            self.hooks[name] = {}
        self.hooks[name][uname] = function

    def dohook(self, name, *args):
        """Call all functions registered to <name> with <*args>."""
        if name in self.hooks:
            for f in list(self.hooks[name].values()):
                f(*args)

    def addtimer(self, f, n, t):
        """Add a timer with unique name <n>, function <f> and timeout <t>."""
        self.timers[n] = {
            'name': n,
            'function': f,
            'time': t,
            'last': 0,
        }

    def callonce(self, f, t):
        """Call f after <t> ms."""
        self.otimers.append({
            'start': time.time(),
            'function': f,
            'time': t,
        })

    def dotimers(self):
        for timer in list(self.timers.values()):
            if time.time() - timer['last'] > timer['time'] / 1000:
                try:
                    timer['function']()
                except:
                    import traceback
                    traceback.print_exc()
                timer['last'] = time.time()
        self.dootimers()

    def dootimers(self):
        tod = []
        i = 0
        for timer in self.otimers:
            if time.time() - timer['start'] > timer['time'] / 1000:
                try:
                    timer['function']()
                except:
                    import traceback
                    traceback.print_exc()
                tod.append(i)
            i += 1
        tod.reverse()
        for i in tod:
            del self.otimers[i]

    def rset(self, n, v):
        """Register a function or structure to be used by other modules."""
        self.registry[n] = v

    def rget(self, n):
        """Get a value from the registry."""
        return self.registry[n]

    def rhas(self, n):
        """Is a key in the registry?"""
        return n in self.registry