# -*- coding: utf-8 -*-
from .userdata import userdata
import os
from lib import db


class Module:

    """A Module Object."""

    """Display the module in lists?"""
    hidden = False

    def __init__(self, server):
        self.server = server
        self.commands = {}
        self.serversettings = []
        self.timers = []
        self.hooks = []
        self.ssets = []
        self.register()

    def addserversetting(self, n, v):
        """Add setting <n> with default value <v>."""
        self.serversettings.append((n, v))

    def addcommand(self, function, name, helptext, arguments,
                   recognizers=None, quote=True):
        """Add a command to the module."""
        if recognizers is None:
            recognizers = {}
        c = {
            'name': name,
            'help': helptext,
            'args': [],
            'function': function,
            'alias': None,
            'quote': quote,
        }
        for arg in arguments:
            a = {
                'name': arg.strip('-.[]').split('=')[0],
                'recognizer': lambda x: False,
                'kv': False,
            }
            a['kv'] = (arg.strip('[')[0] == '-')
            try:
                a['kvtext'] = arg.strip('[-]').split('=')[1]
            except IndexError:
                pass
            a['optional'] = (arg.strip('-')[0] == '[')
            a['full'] = (arg.strip(']')[-1] == '.')
            if a['name'] in recognizers:
                a['recognizer'] = recognizers[a['name']]
            c['args'].append(a)
        self.commands[c['name']] = c

    def addcommandalias(self, name, newname):
        self.commands[newname] = self.commands[name].copy()
        self.commands[newname]['name'] = newname
        self.commands[newname]['alias'] = name

    def addhook(self, name, uname, function):
        """Add a server hook, prefixing the name with the module index."""
        self.server.addhook(name, "%s:%s" % (self.index, uname), function)
        self.hooks.append((name, "%s:%s" % (self.index, uname)))

    def addtimer(self, function, name, timeout):
        """Add a timer hook, prefixing the name with the module index."""
        self.server.addtimer(function, "%s:%s" % (self.index, name), timeout)
        self.timers.append("%s:%s" % (self.index, name))

    def addsetting(self, setting, value):
        """Add a module-specific <setting> with a default value of <value>."""
        self.addserversetting("modules.%s.%s" % (self.index, setting), value)

    def getsetting(self, setting):
        """Get a module-specific <setting>."""
        return self.server.settings.get("modules.%s.%s" % (self.index, setting))

    def setsetting(self, setting, value):
        """Set a module-specific <setting>."""
        return self.server.settings.set(
            "modules.%s.%s" % (self.index, setting), value)

    def serverset(self, name, value):
        """Add <name> as <value> to the server registry."""
        self.server.rset(name, value)
        self.ssets.append(name)

    def getdb(self, name, d=None):
        """Get a database <name> with default <d>."""
        os.makedirs("%s/servers/%s/%s" % (
            userdata, self.server.name, self.index), exist_ok=True)
        return db.DB("servers/%s/%s/%s.json" % (
            self.server.name,
            self.index, name), d)

    def getshareddb(self, index, name, d=None):
        """Get a shared database <name> with default <d>."""
        os.makedirs("%s/shared/%s/%s" % (
            userdata, self.server.shared, index), exist_ok=True)
        return db.DB("shared/%s/%s/%s.json" % (
            self.server.shared,
            index, name), d)

    def _unload(self):
        for timer in self.timers:
            self.server.timers.pop(timer)
        for hook in self.hooks:
            self.server.hooks[hook[0]].pop(hook[1])
        for sset in self.ssets:
            self.server.registry.pop(sset)
