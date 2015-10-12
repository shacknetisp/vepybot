# -*- coding: utf-8 -*-
import bot
import socket
import select
import re
import copy


class Server(bot.Server):

    index = "irc"

    requiredplugins = [
        "irc/settings",
        "irc/rights",
        "irc/alias",
        "irc/config",
        "irc/pinger",
        "irc/dispatcher",
        "irc/channel",
        "irc/users",
    ]

    options = {
        'mode': '*',
        'recv': 16384,
        }

    class Settings(bot.Server.Settings):

        idents = '.=#'
        mglob = bot.Server.Settings.mglob + ['channels.*.modules.{m}.*']

        channeldefaults = {}
        channeltree = {}

        def getchannel(self, v, context):
            channel = context if type(context) is str else context.channel
            setting = "channels.%s.%s" % (channel, v)
            if channel:
                try:
                    return self.get(setting)
                except KeyError:
                    pass
                if v in self.channeldefaults:
                    self.d[setting] = copy.deepcopy(
                        self.channeldefaults[v])
                    return self.get(setting)
            return self.get(v)

        def addbranch(self, ss, n):
            bot.Server.Settings.addbranch(self, copy.deepcopy(ss), n)
            if '#' in n:
                s = None
                d = self.channeltree
                while ss:
                    s = ss.pop(0)
                    if s not in d:
                        d[s] = {}
                    d = d[s]
                d[n] = True

        def isdefault(self, n, v):
            if n.split('.')[:1] == ['channels']:
                nn = '.'.join(n.split('.')[2:])
                if nn in self.defaults and n in self.d:
                    if self.d[n] == self.defaults[nn]:
                        return True
                elif nn in self.channeldefaults and n in self.d:
                    if self.d[n] == self.channeldefaults[nn]:
                        return True
            return False

        def addchannel(self, n, v):
            self.channeldefaults[n.strip(self.idents)] = v

    def settings_ready(self):
        self.globalaliases = {}

    def modulesetup(self, m):

        def getchannelsetting(self, setting, c):
            return self.server.settings.getchannel(
                "modules.%s.%s" % (self.index, setting), c)

        def addserverchannelsetting(self, n, v):
            self.serverchannelsettings[n] = v

        m.getchannelsetting = getchannelsetting
        m.addserverchannelsetting = addserverchannelsetting
        m.serverchannelsettings = {}
        return m

    def ready(self):
        self.info = {}
        self.outbuf = []
        self.addtimer("output", self.output, 100)
        self.socket = socket.socket()
        self.socket.connect((self.opt('host'), self.opt('port')))
        self.nick = self.settings.get('server.user.nick')
        self.send("NICK %s" % (self.nick))
        self.send("USER %s %s * :%s" % (
            self.settings.get('server.user.ident'),
            self.settings.get('server.user.mode'),
            self.settings.get('server.user.name')))

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

    def build_lists(self):
        bot.Server.build_lists(self)
        self.settings.channeldefaults = {}
        for m in list(self.modules.values()):
            for k, v in list(m.serverchannelsettings.items()):
                self.settings.addchannel(k, v)


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