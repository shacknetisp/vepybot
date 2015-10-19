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

        self.protected = [
            "core", self.server.index] + self.server.requiredplugins

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

    def willautoload(self, name):
        if name in self.server.settings.get("server.noautoload"):
            return False
        if name.split('/')[0] in self.server.settings.get("server.noautoload"):
            return False
        return True

    def unload(self, context, args):
        context.exceptrights('admin')
        plugin = args.getstr("plugin")
        module = ""
        if len(plugin.split('/')) > 1:
            module = plugin.split('/')[-1]
        plugin = plugin.split('/')[0]

        if pms(plugin, module) in self.protected:
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
        if aname not in nl and aname.split('/')[0] not in nl:
            nl.append(aname)
        self.server.settings.set("server.noautoload", nl)
        return "Unloaded plugin: %s (%s autoload)" % (aname,
            utils.ynstr(self.willautoload(aname), "will", "won't"))

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
            if plugin not in plist and plugin.split('/')[0] not in plist:
                plist.append(plugin)
            tod = []
            nl = self.server.settings.get("server.noautoload")
            for n in nl:
                if n == plugin or n == plugin.split('/')[0]:
                    tod.append(n)
            for n in tod:
                nl.pop(nl.index(n))
            self.server.settings.set("server.noautoload", nl)
            self.server.settings.set("server.autoload", plist)
        return "Loaded plugin: %s (%s autoload)" % (plugin,
            utils.ynstr(self.willautoload(plugin), "will", "won't"))

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