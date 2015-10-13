# -*- coding: utf-8 -*-
import bot


class Context(bot.Context):

    def __init__(self, server, socket, text):
        bot.Context.__init__(self, server)
        self.socket = socket
        self.text = text

    def idstring(self):
        return "host:" + str(self.socket.getpeername()[0])

    def reply(self, m):
        self.socket.send(m.strip().encode() + b'\n')
        self.server.log('OUT', '%s: %s' % (self.socket.getpeername()[0],
            m.strip()))


class M_Dispatcher(bot.Module):

    index = "dispatcher"
    hidden = False
    whoist = 60

    def register(self):
        self.addhook("server_recv", "s_recv", self.s_recv)
        self.addhook("recv", "recv", self.recv)

    def s_recv(self, socket, msg):
        context = Context(self.server, socket, msg)
        self.server.dohook("recv", context)

    def recv(self, context):
        self.doinput(context, context.text)

    def doinput(self, context, command):
        out, errout = self.server.runcommand(context, command)
        if out or errout:
            context.reply(out if out else errout)

bot.register.module(M_Dispatcher)