# -*- coding: utf-8 -*-
import bot


class M_Settings(bot.Module):

    index = "core_settings"
    hidden = True

    def register(self):

        self.addhook('core_prepare_settings', 'sr', self.ready)

    def ready(self):
        self.addserversetting("messages.notfound", "?")
        self.addserversetting("parser.prefixes", ['.'])

        self.addserversetting("server.autoload", ['utils'])

bot.register.module(M_Settings)