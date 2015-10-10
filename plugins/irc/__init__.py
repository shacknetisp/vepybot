# -*- coding: utf-8 -*-
import bot
import socket
import select
import re


class Server(bot.Server):

    index = "irc"

    requiredplugins = [
        "irc/pinger",
        "irc/dispatcher",
        "irc/channels",
        "irc/rights",
        "irc/alias",
        "irc/users",
    ]

    options = {
        'mode': '*',
        'recv': 16384,
        'plugins': [
            'echo',
            ],
        }

    class Settings(bot.Server.Settings):

        def prefixes(self, context):
            if context.channel:
                return self.get("%s:prefixes" % context.channel,
                    self.get("prefixes"))
            return self.get("prefixes") + [""]

    def settings_ready(self):
        d = {
            'notfoundmsg': '?',
            'prefixes': ['.'],
            'plugins': self.opt('plugins'),
            'channels': [],
        }
        self.settings.default(d)

    def ready(self):
        self.info = {}
        self.outbuf = []
        self.addtimer("output", self.output, 100)
        self.socket = socket.socket()
        self.socket.connect((self.opt('host'), self.opt('port')))
        self.send("NICK %s" % (self.opt('nick')))
        self.send("USER %s %s * %s" % (
            self.opt('nick'),
            self.opt('mode'),
            self.opt('name')))

    def send(self, msg):
        self.outbuf.append(msg)

    def output(self):
        if self.outbuf:
            o = bytes(self.outbuf.pop(0), 'UTF-8')
            if o[-1] != b'\n':
                o += b'\n'
            self.log("OUT", o.decode())
            self.socket.send(o)

    def run(self):
        inr = [self.socket]
        readyr, _, _ = select.select(
            inr, [], [], 0.1)
        if readyr:
            ircmsg = ""
            try:
                ircmsg = self.socket.recv(self.opt('recv')).decode()
            except UnicodeDecodeError:
                pass
            regex = re.compile(
            "\x03(?:\d{1,2}(?:,\d{1,2})?)?", re.UNICODE)
            for ircmsg in ircmsg.strip().split('\n'):
                ircmsg = ircmsg.strip('\r')
                ircmsg = regex.sub("", ircmsg)
                self.log('IN', ircmsg)
                self.dohook("server_recv", ircmsg)

    def ischannel(self, x):
        return x and x[0] in self.info['CHANTYPES']


bot.register.server(Server)


class M_ServerInfo(bot.Module):

    index = "serverinfo"
    hidden = True

    def register(self):
        self.addhook("recv", "recv", self.recv)

    def recv(self, context):
        if context.code("005"):
            t = {
                'MAXCHANNELS': int,
                'PREFIX': lambda x: (x.split(')')[0].strip('()'),
                    x.split(')')[1].strip('()'))
            }
            s = ' '.join(context.rawsplit[3:])
            infos = s[:s.index(" :")].split()
            for e in infos:
                s = e.split('=')
                if len(s) == 1:
                    self.server.info[s[0]] = True
                else:
                    self.server.info[
                        s[0]] = t[s[0]](s[1]) if s[0] in t else s[1]
        elif context.code(376):
            self.server.log('INFO',
                'Now connected to: %s' % self.server.info['NETWORK'])


bot.register.module(M_ServerInfo)