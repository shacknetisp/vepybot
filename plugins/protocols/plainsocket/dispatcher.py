# -*- coding: utf-8 -*-
import bot


class Context(bot.Context):

    def __init__(self, server, socket, text):
        bot.Context.__init__(self, server)
        self.socket = socket
        self.text = text

    def idstring(self):
        return "host:" + str(self.socket.getpeername()[0])

    def reply(self, m, more=True, command=None, priv=False):
        m = m.strip()
        if not m:
            return
        if more:
            m = self.domore(m)
        sendf = lambda message: self.socket.send(message.encode() + b'\n')
        self.replydriver(sendf, m, more)
        self.server.log('OUT', '%s: %s' % (self.socket.getpeername()[0],
            m.strip()))


class M_Dispatcher(bot.Module):

    index = "dispatcher"
    hidden = True

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