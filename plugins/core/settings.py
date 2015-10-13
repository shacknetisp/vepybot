# -*- coding: utf-8 -*-
import bot


class M_Settings(bot.Module):

    index = "core_settings"
    hidden = True

    def register(self):

        self.addhook('core_prepare_settings', 'sr', self.ready)

    def ready(self):
        self.server.settings.add("messages.notfound", "?")
        self.server.settings.add("parser.prefixes", ['.'])

        self.server.settings.add("server.autoload", [])

        self.server.dohook("prepare_settings")

bot.register.module(M_Settings)