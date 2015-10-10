# -*- coding: utf-8 -*-
import bot


class Channel:

    def __init__(self, server, name):
        self.server = server
        self.name = name


class M_Channels(bot.Module):

    index = "channels"

    def register(self):
        self.addhook("recv", "recv", self.recv)
        self.channels = {}

    def join(self, c):
        self.server.send("JOIN %s" % c)

    def recv(self, context):
        if context.code(376):
            for channel in self.server.settings.get("channels"):
                self.join(channel)

bot.register.module(M_Channels)