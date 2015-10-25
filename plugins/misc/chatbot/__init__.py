# -*- coding: utf-8 -*-
import bot
import time
from . import ailib
bot.reload(ailib)


class Module(bot.Module):

    index = "chatbot"

    def register(self):
        self.lastphrase = {}
        self.lasttime = {}
        if self.server.index in ['irc']:
            self.server.rget('addchannelrights')({
                'chatbot': ['op'],
            })
            self.addsetting('#globaldb', True)
        self.addcommand(self.chat, "chat", "Talk to the bot.", ["text..."])
        self.addcommandalias('chat', 'c')
        self.server.addrights({
            'chatbot': ['admin'],
        })

    def chat(self, context, args):
        if self.server.index in ['irc']:
            if context.channel and not self.getchannelsetting(
                    'globaldb', context):
                context.exceptchannelrights(['chatbot'])
            else:
                context.exceptrights(['admin', 'chatbot'])
            cname = ""
            if context.channel:
                cname = self.server.name + '.' + context.channel
            ai = ailib.AI(self.getshareddb('chatbot',
                'global' if self.getchannelsetting(
                    'globaldb', context) else (cname or 'global')).d)
            ids = context.channel or context.idstring()
        else:
            ai = ailib.AI(self.getshareddb('chatbot', 'global').d)
            ids = context.idstring()
        if ids not in self.lastphrase:
            self.lastphrase[ids] = ""
        if ids not in self.lasttime:
            self.lasttime[ids] = 0
        lp = self.lastphrase[ids]
        lt = self.lasttime[ids]
        if time.time() - lt > 180:
            lp = ""
        out = ai.process(args.getstr('text'), lp)
        self.lastphrase[ids] = out
        self.lasttime[ids] = time.time()
        return out

bot.register.module(Module)
