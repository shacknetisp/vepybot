# -*- coding: utf-8 -*-
import bot
import fnmatch
import copy


class Module(bot.Module):

    index = "irchub"

    def register(self):
        if self.server.index not in ['irc']:
            self.hidden = True
            return
        self.addsetting('#hubs', [])
        self.addhook('dispatcher.ignore', 'dr', self.dr)
        self.addhook('recv', 'recv', self.recv)

    def dr(self, context, responses):
        for idstring in self.getchannelsetting('hubs', context):
            if fnmatch.fnmatch(context.idstring(), idstring):
                responses.append(True)
                return

    def recv(self, context):
        for idstring in self.getchannelsetting('hubs', context):
            if fnmatch.fnmatch(context.idstring(), idstring):
                s = context.text
                try:
                    name = s[:s.index('> ')]
                    text = s[s.index('> ') + 2:]
                except ValueError:
                    return
                newcontext = copy.copy(context)
                newcontext.replypriv = newcontext.reply
                newcontext.displayname = name
                newcontext.text = text
                oldidstring = newcontext.idstring()
                newcontext.idstring = lambda: "irchub:%s!%s" % (
                    name,
                    oldidstring.replace('irc:', ''),
                )
                self.server.dohook('recv', newcontext)
                return

bot.register.module(Module)