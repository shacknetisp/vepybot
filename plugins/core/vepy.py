# -*- coding: utf-8 -*-
import bot


class Module(bot.Module):

    index = "vepy"

    def register(self):

        self.addcommand(
            self.restart,
            "restart",
            "Completely restart the bot, requires the <bot> right.",
            [])

        self.addcommand(self.reloadall, "reload servers",
            "Reload all plugins.", [])

        self.addcommand(self.reloadall, "stats",
            "Show running information about the bot.", [])

        self.server.addrights({
            "bot": ["owner"],
            })

    def restart(self, context, args):
        context.exceptrights(["bot"])
        bot.run = False

    def reloadall(self, context, args):
        context.exceptrights(["bot"])
        try:
            bot.reloadall()
            return "Reloaded all possible plugins."
        except ValueError as e:
            return str(e)

bot.register.module(Module)