# -*- coding: utf-8 -*-
import bot
import socket
import select

"""
Plain Socket Server
bot.load_server(
    "plainsocket",
    "plainsocket",
    "plains1",
    "shared1",
    {
        'port': 5000,
        'owner': 'host:*',
    })
"""


class Server(bot.Server):

    index = "plainsocket"

    requiredplugins = [
        "generic/rights",
        "generic/alias",
        "generic/config",
        "plainsocket/dispatcher",
    ]

    options = {
        'host': '',
        'backlog': 5,
        'recvsize': 4096,
    }

    def ready(self):
        self.outbuf = []
        self.sockets = []
        self.listener = socket.socket()
        self.listener.bind((self.opt('host'), self.opt('port')))
        self.listener.listen(self.opt('backlog'))

    def run(self):
        readyr, _, _ = select.select(
            self.sockets + [self.listener], [], [], 0.1)
        done = []
        for socket in readyr:
            if socket == self.listener:
                client, addr = socket.accept()
                self.sockets.append(client)
                self.log("CONN OPEN", "%s:%d" % addr)
            else:
                data = socket.recv(self.opt('recvsize'))
                try:
                    data = data.decode()
                except UnicodeDecodeError:
                    continue
                if data:
                    self.log("IN", "%s: %s" % (socket.getpeername()[0],
                        data.strip()))
                    self.dohook('server_recv', socket, data)
                else:
                    done.append(socket)
        for s in done:
            self.sockets.pop(self.sockets.index(s))
            self.log("CONN CLOSE", "%s:%d" % s.getpeername())

bot.register.server(Server)


class M_Settings(bot.Module):

    index = "settings"
    hidden = True

    def register(self):

        self.addhook('prepare_settings', 'sr', self.ready)

    def ready(self):
        pass

bot.register.module(M_Settings)