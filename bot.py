# -*- coding: utf-8 -*-
import os
import sys
import importlib
import time
from lib import db, utils, parser

userdata = 'userdata'
for d in [
        'servers',
        'shared',
    ]:
        os.makedirs(userdata + '/' + d, exist_ok=True)


def importmodule(path):
    osp = sys.path
    sys.path.append(os.path.dirname(path))
    module = importlib.import_module(
        os.path.splitext(os.path.basename(path))[0])
    sys.path = osp
    return module


def listmodules(directory):
    ret = []
    for module in os.listdir(directory):
        if module[0] == '_':
            continue
        ret.append(os.path.splitext(module)[0])
    return ret

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
        if currentplugin not in plugins:
            plugins[currentplugin] = {}
        plugins[currentplugin][c.index] = c
        if c.index not in newmodules:
            newmodules.append(c.index)


def loadnamedmodule(n, p=""):
    global currentplugin
    global newmodules
    newmodules = []
    for directory in ["plugins", userdata + "/plugins"]:
        if (os.path.exists("%s/%s/__init__.py" % (directory, n)) or
            os.path.exists("%s/%s.py" % (directory, n))):
                currentplugin = p or n
                m = importmodule("%s/%s" % (directory, n))
                importlib.reload(m)
                currentplugin = ""
                return True
    return False


def make_server(module, kind, name, shared, options):
    global currentplugin
    currentplugin = kind
    loadnamedmodule(module)
    currentplugin = ""
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
        if n not in self.d:
            self.d[n] = d

    def getstr(self, n):
        try:
            return self.d[n]
        except KeyError:
            raise NoArg("Argument not found: %s" % n)

    def getbool(self, n):
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


class Server:

    class Settings:

        def __init__(self, server):
            os.makedirs("%s/servers/%s" % (userdata, server.name),
                exist_ok=True)
            os.makedirs("%s/shared/%s" % (userdata, server.shared),
                exist_ok=True)
            self.db = db.DB("servers/%s/settings.json" % server.name)
            self.d = self.db.d

        def get(self, n, d=None):
            if n not in self.d and d is not None:
                return d
            return self.d[n]

        def set(self, n, v):
            self.d[n] = v
            self.db.save()

        def setifne(self, n, v):
            if n not in self.d:
                self.set(n, v)

        def default(self, d):
            tmp = dict(list(d.items()) + list(self.d.items()))
            self.d.update(tmp)
            self.db.save()

    def __init__(self, name, shared, options):
        self.name = name
        self.shared = shared
        self.hooks = {}
        self.timers = []
        self.options.update(options)
        self.settings = self.Settings(self)
        self.build_settings()
        self.modules = {}
        self.plugins = {}
        self.righttypes = {}
        self.pluginpaths = []
        for k in ["core",
            self.index] + self.requiredplugins + self.settings.get(
            "plugins"):
                self.loadplugin(k)
        self.addhook("server_ready", "sinit", self.ready)
        self.dohook("server_ready")

    def loadplugin(self, k):
        plugin = k.split('/')[0]
        loadnamedmodule(k, plugin)
        modules = plugins[plugin]
        for index in modules:
            if index not in newmodules:
                continue
            v = modules[index]
            self.modules[index] = v(self)
            self.modules[index].plugin = plugin
            self.log('LOAD', "%s/%s" % (plugin, index))
        self.plugins[plugin] = modules
        self.pluginpaths.append(k)
        self.build_lists()
        return True

    def unloadplugin(self, plugin):
        for module in self.plugins[plugin]:
            self.log('UNLOAD', "%s/%s" % (plugin, module))
            del self.modules[module]
        self.pluginpaths = [x for x in self.pluginpaths
            if x.split('/')[0] != plugin]
        del self.plugins[plugin]
        self.build_lists()

    def reloadplugin(self, plugin):
        plugin = plugin.split('/')[0]
        oldpaths = self.pluginpaths
        self.unloadplugin(plugin)
        for pp in oldpaths:
            if pp.split('/')[0] == plugin:
                self.loadplugin(pp)
        self.log('RELOAD', plugin)
        self.build_lists()
        return True

    def addrights(self, d):
        self.righttypes.update(d)

    def opt(self, n):
        return self.options[n]

    def log(self, category, text):
        print(("%s %s: %s" % (self.name, category, text.strip())))

    def build_settings(self):
        self.settings_ready()

    def build_lists(self):
        self.commands = {}
        for m in list(self.modules.values()):
            for k, v in list(m.commands.items()):
                self.commands[(m.plugin, m.index, k)] = (m, v)
        self.commands = sorted(list(self.commands.items()),
            key=lambda x: -len(x[0][2].split()))

    def addhook(self, name, uname, function):
        if name not in self.hooks:
            self.hooks[name] = {}
        self.hooks[name][uname] = function

    def dohook(self, name, *args):
        if name in self.hooks:
            for f in list(self.hooks[name].values()):
                f(*args)

    def addtimer(self, n, f, t):
        self.timers.append({
            'name': n,
            'function': f,
            'time': t,
            'last': 0,
            })

    def dotimers(self):
        for timer in self.timers:
            if time.time() - timer['last'] > timer['time'] / 1000:
                timer['function']()
                timer['last'] = time.time()

    def splitparse(self, text, context=None):
        sections = []
        sectiond = {}
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
            elif not quoted and cchar in parser.quotes:
                quoted = cchar
                if not section:
                    sectiond[len(sections)] = "cooked"
            elif quoted:
                if cchar == quoted:
                    quoted = None
                else:
                    section += cchar
            else:
                if cchar == ' ' and not running:
                    if section:
                        sections.append(section)
                    section = ""
                else:
                    section += cchar
            idx += 1
            cchar = text[idx] if idx in range(len(text)) else None
        if section:
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
        pass

    def runcommand(self, context, text):
        split = text.split()
        for k, v in self.commands:
            for splitc in [[v[0].index] + v[1]['name'].split(),
                    v[1]['name'].split()]:
                    if splitc == split[:len(splitc)]:
                        argtext = ' '.join(split[len(splitc):])
                        try:
                            return self.parsecommand(context,
                                text, v, argtext), None
                        except ParserBadCommand as e:
                            return None, e
                        except NoPerms as e:
                            return None, e
                        except NoArg as e:
                            return None, e
                        except Exception as e:
                            import traceback
                            traceback.print_exc()
                            return None, "Internal Error: %s" % type(e).__name__
        responses = []
        self.dohook('command', context, text, responses)
        for r in responses:
            if r[0] is not None:
                return r[0], None
            elif r[1] is not None:
                return None, r[1]

        return None, self.settings.get('notfoundmsg').format(
            command=split[0])


class Module:

    hidden = False

    def __init__(self, server):
        self.server = server
        self.commands = {}
        self.register()

    def addcommand(self, function, name, helptext, arguments,
            recognizers=None):
        if recognizers is None:
            recognizers = {}
        c = {
            'name': name,
            'help': helptext,
            'args': [],
            'function': function,
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

    def addhook(self, name, uname, function):
        self.server.addhook(name, "%s:%s" % (self.index, uname), function)


class Context:

    def __init__(self, server):
        self.server = server

    def idstring(self):
        return self.server.idstring(self)

    def checkright(self, r):
        return r in self.server.getrights(self.idstring(), self)

    def needrights(self, rlist, m=None):
        if type(rlist) is str:
            rlist = [rlist]
        rlist = rlist + ['owner']
        for r in rlist:
            if r in self.server.getrights(self.idstring(), self):
                return True
        raise NoPerms(m or "You must have %s: %s" % (
            "this right" if len(rlist) == 1 else "one of these rights",
            ', '.join(rlist)))
