# -*- coding: utf-8 -*-
from threading import Lock
from .loader import *
from .args import *
from .userdata import *
from .exceptions import *
from .module import *
from .context import *
from .settings import *
from .running import runningservers
from .parser import *
from .hooks import *

threads = True
run = True
restartfromcrash = True

from lib import utils, parser
[reload(x) for x in [utils, parser]]


def make_server(module, kind, name, shared, options):
    global currentplugin
    if kind not in servers:
        loadnamedmodule(module)
    if kind not in servers:
        raise IndexError("%s is not a valid server type!" % kind)
    return servers[kind](name, shared, options)


def load_server(*args):
    server = make_server(*args)
    runningservers.append(server)


class Server(LoaderBase, ParserBase, HookBase):

    """The Server Plugin."""

    """Override with plugins that are required to run the server."""
    requiredplugins = []

    """Default Options."""
    options = {
        'charlimit': 0,
    }

    """Optionally loaded plugins."""
    autoload = []

    dautoload = [
        "misc",
        "internet",
        "games",
    ]

    Settings = Settings

    def __init__(self, name, shared, options):
        self.name = name
        self.shared = shared
        self.hooks = {}
        self.globalaliases = {}
        self.runlock = Lock()
        self.timers = {}
        self.otimers = []
        self.options.update(options)
        self.settings = self.Settings(self)
        self.build_settings()
        self.modules = {}
        self.plugins = {}
        self.protected = []
        self.righttypes = {}
        self.registry = {}
        self.pluginpaths = []
        for k in ["core",
                  self.index] + self.requiredplugins:
                self.loadplugin(k)
                self.protected.append(k)
                for x in newmodules:
                    self.protected.append(k.split('/')[0] + '/%s' % x)
        self.build_lists()
        for k in self.dautoload + self.autoload + self.settings.get(
                "server.autoload"):
                self.loadplugin(k, auto=True)
        self.build_lists()
        self.addhook("server_ready", "sinit", self.ready)
        self.dohook("server_ready")

    def addrights(self, d):
        """Add <d> to the rights hierarchy."""
        self.righttypes.update(d)

    def opt(self, n):
        """Get config.py value <n>."""
        if n not in self.options and n in Server.options:
            return Server.options[n]
        return self.options[n]

    def log(self, category, text):
        """Log <text> under <category>."""
        print(("%s %s: %s" % (self.name, category, text.strip())))
        self.dohook("log", "bot", category, text.strip())

    def build_settings(self):
        """Ready to build settings."""
        pass

    def build_lists(self):
        """Recreate the command and settings lists."""
        self.commands = {}
        self.numcommands = {}
        for m in list(self.modules.values()):
            for k, v in list(m.commands.items()):
                self.commands[(m.plugin, m.index, k)] = (m, v)
                if k not in self.numcommands:
                    self.numcommands[k] = []
                self.numcommands[k].append(m.index)
        self.commands = sorted(list(self.commands.items()),
                               key=lambda x: -len(x[0][2].split()))
        self.settings.user = []
        self.settings.defaults = {}
        self.settings.tree = {}
        self.dohook("core_prepare_settings")
        for m in list(self.modules.values()):
            for k, v in m.serversettings:
                self.settings.add(k, v)

    def checkbuild(self):
        if self.build:
            self.build = False
            self.build_lists()

    def corerun(self):
        self.checkbuild()
        try:
            self.run()
        except Exception as e:
            import traceback
            traceback.print_exc()
            global run
            run = False
            if restartfromcrash:
                raise e

    def parsecommand(self, context, text, v, argtext):
        parsedargs = self.makeargdict(argtext, context, v,
            quote=v[1]['quote'])
        args = Args(parsedargs)
        return v[1]['function'](context, args)

    def getrights(self, *args):
        """Set by modules to get rights."""
        pass

    def modulesetup(self, m):
        """Modify and return <m>, to add attributes to the module class."""
        return m

    def idstring(self, context):
        """Return the rights idstring from <context>.
        Implemented by modules."""
        pass

    def shutdown(self):
        """Called on bot restart."""
        pass

    def commandlist(self):
        """List of commands and names."""
        commands = []
        for k, v in self.commands:
            for splitc in [
                    [v[0].plugin] + [v[0].index] + v[1]['name'].split(),
                    [v[0].index] + v[1]['name'].split(),
                    v[1]['name'].split()]:
                        commands.append((splitc, v))
        return commands

    def runcommand(self, context, text):
        """Run <text> as <context>."""
        commands = self.commandlist()
        split = text.split()
        commands.sort(key=lambda x: -len(x[0]))
        for splitc, v in commands:
            if splitc == split[:len(splitc)]:
                if len(splitc) == 1:
                    if len(self.numcommands[splitc[0]]) > 1:
                        return None, (
                            "Use <module> %s, %s" % (splitc[0], splitc[0]) +
                            " is provided by multiple modules: %s" % (
                                ', '.join(self.numcommands[splitc[0]])
                            ))
                argtext = ' '.join(split[len(splitc):])
                try:
                    context.exceptcancommand(v[0], v[1])
                    return self.parsecommand(context,
                                             text, v, argtext), None
                except ParserBadCommand as e:
                    return None, e
                except NoPerms as e:
                    if not str(e):
                        return None, None
                    return None, e
                except NoArg as e:
                    return None, "%s, Usage: %s %s" % (e,
                                                       ' '.join(splitc),
                                                       self.gethelp(v[1])[0])
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    return None, "Internal Error: %s" % type(e).__name__
        responses = []
        try:
            self.dohook('command', context, text, responses, False)
        except ParserBadCommand as e:
            return None, e
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None, "Internal Error: %s" % type(e).__name__
        for r in responses:
            if r[0] is not None:
                return r[0], None
            elif r[1] is not None:
                return None, r[1]
            else:
                continue

        return None, self.settings.get('messages.notfound')
