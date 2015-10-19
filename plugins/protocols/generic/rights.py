# -*- coding: utf-8 -*-
import bot
import lib.rights
bot.reload(lib.rights)


class M_Rights(lib.rights.Module):

    def register(self):
        lib.rights.Module.register(self)

    def _contextrights(self, idstring, context):
        """Rights from a context."""
        rights = []
        matches = []
        return rights, matches

bot.register.module(M_Rights)