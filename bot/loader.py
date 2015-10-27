# -*- coding: utf-8 -*-
import fnmatch
import copy
import version
import importlib
from threading import Lock
import os
import sys
from .userdata import userdata
from .running import runningservers


def reload(m):
    importlib.reload(m)


def importmodule(path, r=False):
    sys.path = [os.path.dirname(path)] + sys.path
    module = importlib.import_module(
        os.path.basename(os.path.splitext(path)[0]))
    if r:
        reload(module)
    sys.path.pop(0)
    return module


modlock = Lock()
plugins = {}
pluginfiles = {}
currentplugin = ""
newmodules = []
servers = {}


class register:

    def server(c):
        servers[c.index] = c

    def module(c):
        plugins[currentplugin][c.index] = c
        if c.index not in newmodules:
            newmodules.append(c.index)


def reloadall():
    reload(version)
    for server in runningservers:
        server.reloadall()


def loadnamedmodule(n, p=""):
    global currentplugin
    global newmodules
    newmodules = []
    paths = [
        "",
        "protocols",
    ]
    d = []
    for f in paths:
        d.append("plugins/" + f)
        d.append(userdata + "/plugins/" + f)
    for directory in d:
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


class LoaderBase:

    def loadplugin(self, k, auto=False, can=False):
        """Load the plugin/module <k>."""
        with modlock:
            plugin = k.split('/')[0]
            if auto and plugin in self.settings.get("server.noautoload"):
                return False
            loadnamedmodule(k, plugin)
            if plugin not in plugins:
                return False
            modules = plugins[plugin]
            n = 0
            for index in modules:
                if index not in newmodules:
                    continue
                if auto and (plugin + "/" + index
                             ) in self.settings.get("server.noautoload"):
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
            if n == 0 and not can:
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
                self.modules[module]._unload()
                del self.modules[module]
                del self.plugins[plugin][module]
                if not self.plugins[plugin]:
                    del self.plugins[plugin]
                self.build_lists()
                return
            for m in self.plugins[plugin]:
                if m in self.modules:
                    self.log('UNLOAD', "%s/%s" % (plugin, m))
                    self.modules[m]._unload()
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
                if not self.loadplugin(plugin, can=True):
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

        def loadfrompaths(oldpaths):
            for pp in oldpaths:
                if pp.split('/')[0] == plugin:
                    self.loadplugin(pp)
        try:
            loadfrompaths(oldpaths)
        except SyntaxError:
            return False
        except:
            pass
        self.unloadplugin(plugin)
        loadfrompaths(oldpaths)
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