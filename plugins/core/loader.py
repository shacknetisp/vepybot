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
            "reload a plugin, requires admin.",
            ["plugin"])

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
        self.server.unloadplugin(pms(plugin, module))

        plist = self.server.settings.get("server.autoload")
        aname = ""
        for p in plist:
            bplugin = p.split('/')[0]
            bmodule = ""
            if len(p.split('/')) > 1:
                bmodule = p.split('/')[-1]
            if plugin == bplugin and module == bmodule:
                if args.getbool('temp'):
                    return
                aname = p
                plist.pop(plist.index(p))
                break
        self.server.settings.set("server.autoload", plist)
        return "Unloaded plugin: %s (%s autoload)" % (aname,
            utils.ynstr(aname
            in self.server.settings.get("server.autoload"), "will", "won't"))

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
        if args.getbool('temp'):
            return
        plist = self.server.settings.get("server.autoload")
        if plugin not in plist:
            plist.append(plugin)
        self.server.settings.set("server.autoload", plist)
        return "Loaded plugin: %s (%s autoload)" % (plugin,
            utils.ynstr(plugin
            in self.server.settings.get("server.autoload"), "will", "won't"))

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

bot.register.module(M_Loader)