# -*- coding: utf-8 -*-
import time
from threading import Lock
from .loader import *
from .args import *
from .userdata import *
from .exceptions import *
from .module import *
from .context import *
from .settings import *
from .running import runningservers

threads = True
run = True

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


class Server(LoaderBase):

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

    def corerun(self):
        if self.build:
            self.build = False
            self.build_lists()
        try:
            self.run()
        except:
            import traceback
            traceback.print_exc()
            global run
            run = False

    def splitparse(self, text, context=None):
        sections = []
        sectiond = {}
        sectione = {}
        idx = 0
        try:
            cchar = text[idx]
        except IndexError:
            return sections, sectiond
        section = ""
        escaped = False
        quoted = None
        running = False
        runningsection = ""
        rlevel = 0
        while cchar is not None:
            if not escaped and cchar == parser.escape:
                escaped = True
                if not section:
                    sectiond[len(sections)] = "cooked"
            elif escaped:
                if cchar in ["%s%s" % (parser.escape, parser.quotes)]:
                    section += cchar
                    escaped = False
                else:
                    section += cchar
                    escaped = False
            elif not quoted and cchar == parser.run[0]:
                if not running:
                    runningsection = section
                    section = ""
                    running = True
                else:
                    section += cchar
                rlevel += 1
            elif not quoted and cchar == parser.run[1]:
                rlevel -= 1
                if running and rlevel == 0:
                    c = section
                    section = self.runcommand(context, section)[0]
                    if section is None:
                        raise ParserBadCommand("Failed running: {%s}" % c)
                    section = runningsection + section
                    running = False
                else:
                    section += cchar
            elif not quoted and cchar in parser.quotes and not running:
                quoted = cchar
                if not section:
                    sectiond[len(sections)] = "cooked"
            elif quoted and not running:
                if cchar == quoted:
                    quoted = None
                    if not section:
                        sectione[len(sections)] = True
                else:
                    section += cchar
            else:
                if cchar == ' ' and not running:
                    if section or len(sections) in sectione:
                        sections.append(section)
                    section = ""
                else:
                    section += cchar
            idx += 1
            cchar = text[idx] if idx in range(len(text)) else None
        if section or len(sections) in sectione:
            sections.append(section)
        section = ""
        return sections, sectiond

    def makeargdict(self, argtext, context, v):
        sections, sectiond = self.splitparse(argtext, context)
        parsedargs = {}
        args = [a for a in v[1]['args'] if not a['kv']]
        kvargs = [a for a in v[1]['args'] if a['kv']]
        argi = 0
        sectioni = 0
        while sectioni in range(len(sections)):
            st = sections[sectioni]
            sd = sectiond[sectioni] if sectioni in sectiond else ""
            done = False
            if sd != "cooked":
                for prefix in ['--', '-']:
                    if st.startswith(prefix):
                        param = st[len(prefix):]
                        name = param.split('=')[0]
                        if name in [a['name'] for a in kvargs]:
                            try:
                                parsedargs[name] = param.split('=')[1]
                            except IndexError:
                                parsedargs[name] = ""
                            done = True
                        break
            if not done:
                if argi in range(len(args)):
                    arg = args[argi]
                    if arg['optional']:
                        if arg['recognizer'](st):
                            parsedargs[arg['name']] = st
                        else:
                            argi += 1
                            if argi in range(len(args)):
                                arg = args[argi]
                    if arg['full']:
                        parsedargs[arg['name']] = ' '.join(
                            sections[sectioni:]
                        )
                        argi = len(args)
                    else:
                        parsedargs[arg['name']] = st
                    argi += 1
            sectioni += 1
        return parsedargs

    def parsecommand(self, context, text, v, argtext):
        parsedargs = self.makeargdict(argtext, context, v)
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
        self.dohook('command', context, text, responses, False)
        for r in responses:
            if r[0] is not None:
                return r[0], None
            elif r[1] is not None:
                return None, r[1]
            else:
                continue

        return None, self.settings.get('messages.notfound')
