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

        self.addcommand(
            self.source,
            "source",
            "Get the bot source.",
            [])

    def version(self, context, args):
        return "%s" % (bot.version.namever)

    def source(self, context, args):
        return "%s" % (bot.version.source)

bot.register.module(M_Versions)
