# -*- coding: utf-8 -*-
import bot
import socket
import select
import re
import copy
import time

"""
IRC Client
bot.load_server(
    "irc",
    "irc",
    "freenode1",
    "shared1",
    {
        'host': 'irc.freenode.net',
        'port': 6667,
        'nick': 'vepybot',
        'owner': 'irc:*',
    })
"""


class Server(bot.Server):

    index = "irc"

    requiredplugins = [
        "irc/serverinfo",
        "irc/settings",

        "irc/rights",
        "irc/alias",
        "irc/config",

        "irc/pinger",
        "irc/dispatcher",
        "irc/channels",
        "irc/users",

        "irc/ctcp",
        "irc/msg",
        "irc/nicktrouble"
    ]

    options = {
        'mode': '*',
        'recv': 1024,
        'charlimit': 440,
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
            bot.Server.Settings.addbranch(self, copy.deepcopy(ss), n, rm=True)
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

    def setnick(self, nick):
        self.nick = nick
        self.send("NICK %s" % (nick))

    def ready(self):
        self.loggedin = False
        self.info = {}
        self.inbuf = bytes()
        self.outbuf = []
        self.addtimer("output", self.output, 100)
        self.socket = socket.socket()
        self.socket.connect((self.opt('host'), self.opt('port')))
        self.setnick(self.settings.get('server.user.nick'))
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
            self.inbuf += self.socket.recv(self.opt('recv'))
            while b'\n' in self.inbuf:
                ircmsg = self.inbuf[:self.inbuf.index(b'\n')].decode()
                self.inbuf = self.inbuf[self.inbuf.index(b'\n') + 1:]
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

    def shutdown(self):
        self.socket.send(('QUIT :%s\n' % (bot.versionstring)).encode())
        time.sleep(0.25)
        self.socket.close()


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


class M_Settings(bot.Module):

    index = "settings"
    hidden = True

    def register(self):

        self.addhook('prepare_settings', 'sr', self.ready)

    def ready(self):
        self.server.settings.add("parser.#prefixes", ['.'])

        self.server.settings.add("irc.#notice", True)

        self.server.settings.add("server.channels", [])
        self.server.settings.add("server.whois", True)
        for n in ['nick', 'mode']:
            self.server.settings.add("server.user.%s" % n, self.server.opt(n))
        self.server.settings.add("server.user.name", bot.versionstring)
        self.server.settings.add("server.user.ident", self.server.opt('nick'))

bot.register.module(M_Settings)


class M_433(bot.Module):

    index = "nicktrouble"
    hidden = True

    def register(self):

        self.addhook('recv', 'recv', self.recv)
        self.addsetting('poll', True)
        self.addtimer('poll', self.poll, 120 * 1000)

    def recv(self, context):
        if context.code(433):
            if context.reciever != '*':
                self.server.nick = context.reciever
            responses = []
            self.server.dohook('nickinuse', responses)
            if not responses and not self.server.loggedin:
                self.server.setnick(self.server.nick + "_")

    def poll(self):
        if self.getsetting("poll"):
            if self.server.settings.get("server.user.nick") != self.server.nick:
                self.server.setnick(
                    self.server.settings.get("server.user.nick"))

bot.register.module(M_433)