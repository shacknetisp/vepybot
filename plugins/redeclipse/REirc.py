# -*- coding: utf-8 -*-
import bot
import fnmatch
import copy


class Module(bot.Module):

    index = "REirc"

    def register(self):
        if self.server.index not in ['irc']:
            self.hidden = True
            return
        self.addsetting('#servers', [])
        self.addhook('dispatcher.ignore', 'dr', self.dr)
        self.addhook('recv', 'recv', self.recv)

    def dr(self, context, responses):
        if context.code('privmsg'):
            for idstring in self.getchannelsetting('servers', context, True):
                if fnmatch.fnmatch(context.idstring(), idstring):
                    responses.append(True)
                    return

    def recv(self, context):
        for idstring in self.getchannelsetting('servers', context, True):
            if fnmatch.fnmatch(context.idstring(), idstring):
                s = context.text
                try:
                    name = s[s.index('<') + 1:s.index('> ')]
                    text = s[s.index('> ') + 2:]
                except ValueError:
                    return
                newcontext = copy.copy(context)
                newcontext.displayname = name
                newcontext.replypriv = newcontext.reply
                oldidstring = newcontext.idstring()
                newcontext.idstring = lambda: "re:%s" % (
                    oldidstring.replace('irc:', ''),
                    )
                self.server.log('REIRC', newcontext.idstring() + " :" + text)
                for prefix in self.server.settings.getchannel(
                    "parser.prefixes", context):
                    if text.startswith(prefix):
                        command = text[len(prefix):].strip()
                        out, errout = self.server.runcommand(
                            newcontext, command)
                        if out or errout:
                            newcontext.reply(out if out else errout)
                return

bot.register.module(Module)