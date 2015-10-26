# -*- coding: utf-8 -*-
import bot
from lib import utils
bot.reload(utils)


def pms(p, m):
    if m:
        return "%s/%s" % (p, m)
    return p


class M_Loader(bot.Module):

    index = "loader"

    def register(self):

        self.addcommand(
            self.load,
            "load",
            "Load a plugin(/module), requires admin.",
            ["[-temp]", "plugin"])

        self.addcommand(
            self.unload,
            "unload",
            "Unload a plugin(/module), requires admin.",
            ["[-temp]", "plugin"])

        self.addcommand(
            self.reload,
            "reload",
            "Reload a plugin, requires admin.",
            ["plugin"])

        self.addcommand(
            self.reloadall,
            "reload all",
            "Reload all plugins, requires admin.",
            [])

    def willautoload(self, name, c=False):
        if not c:
            if name in self.server.settings.get("server.noautoload"):
                return False
            if name.split('/')[0] in self.server.settings.get(
                    "server.noautoload"):
                    return False
        conglomerate = (self.server.requiredplugins +
                        self.server.dautoload + self.server.autoload +
                        self.server.settings.get('server.autoload'))
        for c in conglomerate:
            p = c.split('/')[0]
            if len(c.split('/')) > 1:
                p = p + '/' + c.split('/')[-1]
            if p in [name.split('/')[0], name] or c == name:
                return True
        return False

    def unload(self, context, args):
        context.exceptrights('admin')
        plugin = args.getstr("plugin")
        module = ""
        if len(plugin.split('/')) > 1:
            module = plugin.split('/')[-1]
        if plugin in self.server.protected:
            return "You cannot unload the core plugins."
        plugin = plugin.split('/')[0]
        if pms(plugin, module) in self.server.protected:
            return "You cannot unload the core plugins."
        if plugin not in self.server.plugins:
            return "That plugin is not loaded."
        if module and module not in self.server.plugins[plugin]:
            return "That module is not loaded."
        plist = self.server.settings.get("server.autoload")
        aname = ""
        for p in plist:
            bplugin = p.split('/')[0]
            bmodule = ""
            if len(p.split('/')) > 1:
                bmodule = p.split('/')[-1]
            if plugin == bplugin and module == bmodule:
                aname = p
                if not args.getbool('temp') and p:
                    plist.pop(plist.index(p))
                break
        aname = aname or pms(plugin, module)
        self.server.settings.set("server.autoload", plist)
        self.server.unloadplugin(pms(plugin, module))
        nl = self.server.settings.get("server.noautoload")
        cname = aname
        if len(cname.split('/')) > 1:
            cname = cname.split('/')[0] + '/' + cname.split('/')[-1]
        if cname not in nl and cname.split('/')[0] not in nl:
            nl.append(cname)
        self.server.settings.set("server.noautoload", nl)
        ynstr = utils.ynstr(self.willautoload(aname), "will", "won't")
        return "Unloaded plugin: %s (%s autoload)" % (aname, ynstr)

    def load(self, context, args):
        context.exceptrights('admin')
        plugin = args.getstr("plugin")

        if plugin in self.server.plugins:
            return "That plugin is already loaded."
        try:
            if not self.server.loadplugin(plugin):
                return "Cannot load plugin: %s" % plugin
        except bot.ModuleError as e:
            return str(e)
        if not args.getbool('temp'):
            plist = self.server.settings.get("server.autoload")
            tod = []
            nl = self.server.settings.get("server.noautoload")
            for n in nl:
                for p in [plugin, plugin.split('/')[0]] + [
                        (plugin.split('/')[0] + '/' + x)
                        for x in bot.newmodules
                ]:
                        if n == p or n == p.split('/')[0]:
                            if n not in tod:
                                tod.append(n)
            for n in tod:
                nl.pop(nl.index(n))
            self.server.settings.set("server.noautoload", nl)
            if not self.willautoload(plugin, True):
                plist.append(plugin)
            self.server.settings.set("server.autoload", plist)
        ynstr = utils.ynstr(self.willautoload(plugin), "will", "won't")
        return "Loaded plugin: %s (%s autoload)" % (plugin, ynstr)

    def reload(self, context, args):
        context.exceptrights('admin')
        plugin = args.getstr("plugin")
        module = ""
        if len(plugin.split('/')) > 1:
            module = plugin.split('/')[-1]
        if plugin.split('/')[0] not in self.server.plugins:
            return "That plugin is not loaded."
        if module and module not in self.server.plugins[plugin.split('/')[0]]:
            return "That module is not loaded."
        if not self.server.reloadplugin(plugin):
            return "Cannot load plugin: %s" % plugin
        return "Reloaded plugin: %s" % plugin

    def reloadall(self, context, args):
        context.exceptrights(["admin"])
        try:
            self.server.reloadall()
            return "Reloaded all possible plugins."
        except ValueError as e:
            return str(e)

bot.register.module(M_Loader)
