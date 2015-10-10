# -*- coding: utf-8 -*-
import bot
import lib.rights
import fnmatch


class M_Rights(lib.rights.Module):

    def register(self):
        lib.rights.Module.register(self)

    def idstring(self, context):
        ret = ""
        if context.sender[0]:
            ret = "%s!%s@%s!%s" % (
                context.user[0],
                context.user[1],
                context.user[2],
                context.whois.auth
                )
        return "irc:" + ret

    def _contextrights(self, idstring, context):
        rights = []
        matches = []
        if context.channel:
            self.server.settings.setifne(context.channel + ":rights", {})
            rightlist = self.server.settings.get(context.channel + ":rights")
            for r in rightlist:
                if fnmatch.fnmatch(idstring, r):
                    matches.append(r)
                    rights += rightlist[r]
        return rights, matches

bot.register.module(M_Rights)