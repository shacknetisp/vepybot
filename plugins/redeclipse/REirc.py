# -*- coding: utf-8 -*-
import bot
import fnmatch
import copy
import string
import re


class Module(bot.Module):

    index = "REirc"

    def register(self):
        if self.server.index not in ['irc']:
            self.hidden = True
            return
        self.addsetting('#servers', [])
        self.addsetting('#geoip', False)
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
                if context.channel and self.getchannelsetting('geoip', context):
                    joinregex = (r".* \((\d*\.\d*\.\d*\.\d*)\) has joined " +
                        r"the game \[\d*\.\d*\.\d*-.*\] \(\d* player.\)")
                    if re.match(joinregex, context.text):
                        ip = re.sub(joinregex, r'\1', context.text)
                        info = self.server.rget('ip.lookup')(
                            self.server.rget("http.url"),
                            ip
                            )
                        if info and 'country' in info:
                            context.reply('%s' % (info['country']))
                        else:
                            context.reply('Country not found.')
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
                        if not command.strip(string.punctuation):
                            return
                        if not command.startswith('/'):
                            out, errout = self.server.runcommand(
                                newcontext, command)
                            if out or errout:
                                newcontext.reply(out if out else errout)
                                return
                return

bot.register.module(Module)
