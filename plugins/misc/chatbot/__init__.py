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
            self.addsetting('#db', 'global')
        else:
            self.addsetting('db', 'global')
        self.addcommand(self.chat, "chat", "Talk to the bot.", ["text..."])

    def chat(self, context, args):
        if self.server.index in ['irc']:
            ai = ailib.AI(self.getshareddb('chatbot', self.getsetting('db')).d)
            ids = context.channel or context.idstring()
        else:
            ai = ailib.AI(self.getshareddb('chatbot',
                self.getchannelsetting('db', context)).d)
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