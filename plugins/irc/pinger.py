# -*- coding: utf-8 -*-
import bot


class M_Pinger(bot.Module):

    index = "pinger"
    hidden = True

    def register(self):
        self.addhook("recv", "recv", self.recv)

    def recv(self, context):
        if context.sender == "PING":
            self.server.send("PONG :%s" % context.text)

bot.register.module(M_Pinger)