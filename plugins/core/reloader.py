# -*- coding: utf-8 -*-
import bot


class M_Reloader(bot.Module):

    index = "reloader"

    def register(self):

        self.protected = ["core", self.server.index]

        self.addcommand(
            self.load,
            "load",
            "Load a plugin, requires admin.",
            ["plugin"])

        self.addcommand(
            self.unload,
            "unload",
            "Unload a plugin, requires admin.",
            ["plugin"])

        self.addcommand(
            self.reload,
            "reload",
            "reload a plugin, requires admin.",
            ["plugin"])

    def unload(self, context, args):
        context.exceptrights('admin')
        plugin = args.getstr("plugin")
        if plugin in self.protected:
            return "You can only reload the server plugin."
        if plugin not in self.server.plugins:
            return "That plugin is not loaded."
        self.server.unloadplugin(plugin)
        return "Unloaded plugin: %s" % (plugin)

    def load(self, context, args):
        context.exceptrights('admin')
        plugin = args.getstr("plugin")
        if plugin in self.server.plugins:
            return "That plugin is already loaded."
        if not self.server.loadplugin(plugin):
            return "Cannot load plugin: %s" % plugin
        return "Loaded plugin: %s" % (plugin)

    def reload(self, context, args):
        context.exceptrights('admin')
        plugin = args.getstr("plugin")
        if plugin not in self.server.plugins:
            return "That plugin is not loaded."
        if not self.server.reloadplugin(plugin):
            return "Cannot load plugin: %s" % plugin
        return "Reloaded plugin: %s" % (plugin)

bot.register.module(M_Reloader)