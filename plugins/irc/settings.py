# -*- coding: utf-8 -*-
import bot


class M_Settings(bot.Module):

    index = "settings"
    hidden = True

    def register(self):

        self.addhook('prepare_settings', 'sr', self.ready)

    def ready(self):
        self.addserversetting("parser.#prefixes", ['.'])

        self.addserversetting("server.channels", [])
        for n in ['nick', 'mode']:
            self.addserversetting("server.user.%s" % n, self.server.opt(n))
        self.addserversetting("server.user.name", bot.versionstring)
        self.addserversetting("server.user.ident", self.server.opt('nick'))

bot.register.module(M_Settings)