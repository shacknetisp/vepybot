# -*- coding: utf-8 -*-
import os
import sys
import importlib
import time
import fnmatch
import copy
import platform
import textwrap
from threading import Lock

threads = True
run = True

version = "0.1.6"
versionname = "Vepybot"
versionstring = "%s %s" % (versionname, version)
versiontuple = (versionname, version, "Python %s on %s (%s)" % (
    platform.python_version(),
    platform.system(),
    platform.release()
    ))
source = "https://github.com/shacknetisp/vepybot"

userdata = 'userdata'


def createuserdata():
    for d in [
            'servers',
            'shared',
            'plugins',
        ]:
            os.makedirs(userdata + '/' + d, exist_ok=True)
    open('%s/plugins/__init__.py' % userdata, 'w')


def reload(m):
    importlib.reload(m)

from lib import db, utils, parser
[reload(x) for x in [utils, parser]]


def importmodule(path, r=False):
    sys.path = [os.path.dirname(path)] + sys.path
    module = importlib.import_module(
        os.path.basename(os.path.splitext(path)[0]))
    if r:
        reload(module)
    sys.path.pop(0)
    return module

modlock = Lock()
servers = {}
runningservers = []
plugins = {}
pluginfiles = {}
currentplugin = ""
newmodules = []


class register:

    def server(c):
        servers[c.index] = c

    def module(c):
        plugins[currentplugin][c.index] = c
        if c.index not in newmodules:
            newmodules.append(c.index)


def reloadall():
    for server in runningservers:
        server.reloadall()


def loadnamedmodule(n, p=""):
    global currentplugin
    global newmodules
    newmodules = []
    for directory in ["plugins", userdata + "/plugins"]:
        sys.path = sys.path + [directory]
        if (os.path.exists("%s/%s/__init__.py" % (directory, n)) or
            os.path.exists("%s/%s.py" % (directory, n))):
                currentplugin = p or n
                if currentplugin not in plugins:
                    plugins[currentplugin] = {}
                importmodule("%s/%s" % (directory, n), r=True)
                currentplugin = ""
                return True
        sys.path.pop(sys.path.index(directory))
    return False


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


class NoArg(Exception):

    def __init__(self, m):
        Exception.__init__(self, m)
        self.msg = m


class Args:

    def __init__(self, d):
        self.d = d

    def default(self, n, d):
        """Set the default value of arg <n> to <d>"""
        if n not in self.d:
            self.d[n] = d

    def getstr(self, n):
        """Get the arg <n> as a str."""
        try:
            return str(self.d[n])
        except KeyError:
            raise NoArg("Argument not found: %s" % n)

    def getbool(self, n):
        """Get the arg <n> as a bool. For -kv args."""
        if n not in self.d:
            return False
        elif self.d[n] == "":
            return True
        return utils.boolstr(self.d[n])


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


class Server:
    """The Server Plugin."""

    """Override with plugins that are required to run the server."""
    requiredplugins = []

    """Default Options."""
    options = {
        'charlimit': 0,
        }

    class Settings:

        """Indicator Characters."""
        idents = '.=~'
        """Module search glob, {m} is replaced with the module name."""
        mglob = ['modules.{m}.*']

        def __init__(self, server):
            os.makedirs("%s/servers/%s" % (userdata, server.name),
                exist_ok=True)
            os.makedirs("%s/shared/%s" % (userdata, server.shared),
                exist_ok=True)
            self.db = db.DB("servers/%s/settings.json" % server.name)
            self.d = self.db.d
            self.defaults = {}
            self.user = []
            self.tree = {}

        def isdefault(self, n, v):
            """Determine if a setting <n> with value <v>
            is set to it's default."""
            pass

        def purge(self, m):
            """Purge module <m> from the settings DB."""
            c = 0
            tod = []
            for v in self.d:
                for g in self.mglob:
                    if fnmatch.fnmatch(v, g.format(m=m)):
                        c += 1
                        tod.append(v)
                        break
            for d in tod:
                self.d.pop(d)
            self.save()
            return c

        def pop(self, n):
            """Pop <n> from the DB."""
            r = self.d.pop(n)
            self.save()
            return r

        def get(self, n, pop=False):
            """Return the setting <n> or it's default."""
            if n not in self.d:
                self.d[n] = copy.deepcopy(self.defaults[n])
                ret = self.d[n]
                if type(ret) not in [list, dict] or pop:
                    self.d.pop(n)
                return ret
            return self.d[n]

        def addbranch(self, ss, n, rm=False):
            """Add <ss> to the tree with name <n>."""
            ss = copy.deepcopy(ss)
            s = None
            d = self.tree
            while ss:
                s = ss.pop(0)
                if s not in d:
                    d[s] = {}
                d = d[s]
            if n.strip(self.idents) in d and rm:
                d.pop(n.strip(self.idents))
            d[n] = True

        def set(self, n, v):
            """Set <n> to <v>, adding it to the tree if neccessary."""
            split = n.split('.')
            sections = split[:-1]
            basen = split[-1]
            truename = '.'.join(sections + [basen.strip(self.idents)])
            self.d[truename] = v
            self.addbranch(sections, basen)
            self.save()

        def save(self):
            """Save the database, removing values set to their defaults."""
            tod = []
            for k in self.d:
                if k in self.defaults:
                    if self.d[k] == self.defaults[k]:
                        tod.append(k)
                else:
                    if self.isdefault(k, self.d[k]):
                        tod.append(k)
            for t in tod:
                self.d.pop(t)
            self.db.save()

        def add(self, n, v):
            """Add a default setting <n> with a value of <v>."""
            split = n.split('.')
            sections = split[:-1]
            basen = split[-1]
            truename = '.'.join(sections + [basen.strip(self.idents)])
            self.defaults[truename] = copy.deepcopy(v)
            if '=' not in basen and '~' not in basen:
                self.user.append(truename)
            self.addbranch(sections, basen)
            self.save()

    def __init__(self, name, shared, options):
        self.name = name
        self.shared = shared
        self.hooks = {}
        self.globalaliases = {}
        self.timers = {}
        self.otimers = []
        self.options.update(options)
        self.settings = self.Settings(self)
        self.build_settings()
        self.modules = {}
        self.plugins = {}
        self.righttypes = {}
        self.registry = {}
        self.pluginpaths = []
        for k in ["core",
            self.index] + self.requiredplugins:
                self.loadplugin(k)
        self.build_lists()
        for k in self.settings.get(
            "server.autoload"):
                self.loadplugin(k)
        self.build_lists()
        self.addhook("server_ready", "sinit", self.ready)
        self.dohook("server_ready")

    def loadplugin(self, k):
        """Load the plugin/module <k>."""
        with modlock:
            plugin = k.split('/')[0]
            loadnamedmodule(k, plugin)
            if plugin not in plugins:
                return False
            modules = plugins[plugin]
            n = 0
            for index in modules:
                if index not in newmodules:
                    continue
                v = modules[index]
                if index in self.modules:
                    raise ModuleError(
                        "Module %s already registered from plugin: %s" % (
                        index,
                        self.modules[index].plugin
                        ))
                v = self.modulesetup(v)
                self.modules[index] = v(self)
                self.modules[index].plugin = plugin
                self.log('LOAD', "%s/%s" % (plugin, index))
                n += 1
            if n == 0:
                return False
            self.plugins[plugin] = modules
            self.pluginpaths.append(k)
            self.build = True
            return True

    def unloadplugin(self, plugin):
        """Unload the plugin/module <plugin>."""
        with modlock:
            module = ""
            if len(plugin.split('/')) > 1:
                module = plugin.split('/')[-1]
            plugin = plugin.split('/')[0]
            if module:
                self.log('UNLOAD', "%s/%s" % (plugin, module))
                self.modules[module].unload()
                del self.modules[module]
                del self.plugins[plugin][module]
                if not self.plugins[plugin]:
                    del self.plugins[plugin]
                self.build_lists()
                return
            for m in self.plugins[plugin]:
                if m in self.modules:
                    self.log('UNLOAD', "%s/%s" % (plugin, m))
                    self.modules[m].unload()
                    del self.modules[m]
            self.pluginpaths = [x for x in self.pluginpaths
                if x.split('/')[0] != plugin]
            del self.plugins[plugin]
            self.build = True

    def reloadplugin(self, plugin):
        """Reload the plugin/module <plugin>."""
        module = ""
        if len(plugin.split('/')) > 1:
            module = plugin.split('/')[-1]
        if module:
            try:
                if not self.loadplugin(plugin):
                    return False
            except SyntaxError:
                return False
            except:
                pass
            self.unloadplugin(plugin)
            for pp in self.pluginpaths:
                if fnmatch.fnmatch(pp, "%s/*/%s" % (
                        plugin.split('/')[0], module)):
                    plugin = pp
                    break
                elif fnmatch.fnmatch(pp, "%s/%s" % (
                        plugin.split('/')[0], module)):
                    plugin = pp
                    break
            if not self.loadplugin(plugin):
                return False
            self.build_lists()
            return True
        with modlock:
            oldpaths = copy.deepcopy(self.pluginpaths)
        try:
            for pp in oldpaths:
                if pp.split('/')[0] == plugin:
                    self.loadplugin(pp)
        except SyntaxError:
            return False
        except:
            pass
        self.unloadplugin(plugin)
        for pp in oldpaths:
            if pp.split('/')[0] == plugin:
                self.loadplugin(pp)
        self.log('RELOAD', plugin)
        self.build = True
        return True

    def reloadall(self):
        toreload = []
        for plugin in self.plugins:
            toreload.append(plugin)
        for r in toreload:
            if not self.reloadplugin(r):
                raise ValueError("Cannot reload %s." % r)

    def addrights(self, d):
        """Add <d> to the rights hierarchy."""
        self.righttypes.update(d)

    def opt(self, n):
        """Get config.py value <n>."""
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
                timer['function']()
                timer['last'] = time.time()
        tod = []
        i = 0
        for timer in self.otimers:
            if time.time() - timer['start'] > timer['time'] / 1000:
                timer['function']()
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
        self.run()

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

    def runcommand(self, context, text):
        """Run <text> as <context>."""
        commands = []
        split = text.split()
        for k, v in self.commands:
            for splitc in [
                    [v[0].plugin] + [v[0].index] + v[1]['name'].split(),
                    [v[0].index] + v[1]['name'].split(),
                    v[1]['name'].split()]:
                        commands.append((splitc, v))
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
            recognizers=None):
        """Add a command to the module."""
        if recognizers is None:
            recognizers = {}
        c = {
            'name': name,
            'help': helptext,
            'args': [],
            'function': function,
            'alias': None,
            }
        for arg in arguments:
            a = {
                'name': arg.strip('-.[]'),
                'recognizer': lambda x: False,
                }
            a['kv'] = (arg.strip('[')[0] == '-')
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

    def unload(self):
        for timer in self.timers:
            self.server.timers.pop(timer)
        for hook in self.hooks:
            self.server.hooks[hook[0]].pop(hook[1])
        for sset in self.ssets:
            self.server.registry.pop(sset)


class Context:
    """Server Specific Context, implement the core functions at least."""

    moretemplate = "[{n} more message{s}]"

    def __init__(self, server):
        self.server = server

    def reply(self, m):
        """Reply with <m>."""

    def replypriv(self, m):
        """Reply privately with <m>."""
        self.reply(m)

    def idstring(self):
        """Return the idstring of the context."""
        return self.server.idstring(self)

    def checkright(self, r):
        """Check if the context has the right <r>."""
        return r in self.server.getrights(self.idstring(), self)

    def exceptrights(self, rlist, m=None):
        """Raise NoPerms exception if this context has none of the
        rights in <r>, <m> is an optional exception message."""
        if type(rlist) is str:
            rlist = [rlist]
        rlist = rlist + ['owner']
        for r in rlist:
            if r in self.server.getrights(self.idstring(), self):
                return True
        raise NoPerms(m or "You must have %s: %s" % (
            "this right" if len(rlist) == 1 else "one of these rights",
            '; '.join(rlist)))

    def exceptcancommand(self, module, command):
        """Call _exceptcancommand, raise NoPerms if cannot execute <command>."""
        self._exceptcancommand(module, command)

    def _exceptcancommand(self, module, command):
        if not self.checkright("admin"):
            for r in self.server.getrights(self.idstring(), self):
                if fnmatch.fnmatchcase("-%s.%s.%s" % (
                    module.plugin, module.index, command['name']), r):
                        raise NoPerms("You may not use %s" % "%s.%s.%s" % (
                            module.plugin, module.index, command['name']))
                if r == "ignore":
                    raise NoPerms("")

    def domore(self, message):
        if not self.server.opt('charlimit'):
            return message
        messages = textwrap.wrap(message, self.server.opt('charlimit') - len(
            " " + self.moretemplate,
            ))
        message = messages[0]
        if len(messages) > 1:
            self.server.more[self.idstring()] = messages[1:]
            try:
                if self.server.more[self.idstring()]:
                    l = len(self.server.more[self.idstring()])
                    message += (' ' +
                        self.moretemplate.format(n=l,
                        s=('s' if l != 1 else '')))
            except KeyError:
                pass
        return message

    def replydriver(self, f, message, more):
        if more and message.count('\n') == 0:
            message = self.domore(message)
        for message in message.split('\n'):
            messages = textwrap.wrap(message, self.server.opt('charlimit')
                - len('...'))
            f(messages[0] + ('...' if len(messages) > 1 else ''))
