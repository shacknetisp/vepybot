# -*- coding: utf-8 -*-
import bot


class M_Versions(bot.Module):

    index = "versions"

    def register(self):

        self.addcommand(
            self.version,
            "version",
            "Get the bot version.",
            [])

    def version(self, context, args):
        return "%s" % (bot.versionstring)

bot.register.module(M_Versions)