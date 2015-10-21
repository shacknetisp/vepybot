# -*- coding: utf-8 -*-
import bot
import time


class M_Pinger(bot.Module):

    index = "pinger"
    hidden = True

    def register(self):
        self.addhook("recv", "recv", self.recv)
        self.addtimer(self.timer, 'timer', 20 * 1000)

    def recv(self, context):
        if context.sender == "PING":
            self.server.send("PONG :%s" % context.text)
        elif context.code('PONG'):
            self.server.lastpong = time.time()

    def timer(self):
        self.server.send("PING :%s" % self.server.nick)

bot.register.module(M_Pinger)