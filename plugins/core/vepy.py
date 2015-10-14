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

        self.server.addrights({
            "bot": ["owner"],
            })

    def restart(self, context, args):
        context.exceptrights(["bot"])
        bot.run = False

bot.register.module(Module)