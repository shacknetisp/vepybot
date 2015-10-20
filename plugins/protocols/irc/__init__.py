# -*- coding: utf-8 -*-
import bot
import select
import re
import copy
import time
from lib import utils
bot.reload(utils)
from deps import socks
import socket


def ircsocket(proxy):
    if proxy:
        s = socks.socksocket()
        s.setproxy(socks.PROXY_TYPE_SOCKS5, proxy[0], proxy[1])
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return s
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
        #'proxy': ('127.0.0.1', 9050),
        #'ssl': True,
    })
"""


class Server(bot.Server):

    index = "irc"

    requiredplugins = [
        "irc/serverinfo",
        "irc/settings",

        "irc/core/rights",
        "irc/core/alias",
        "irc/core/config",
        "irc/core/automode",

        "irc/core/pinger",
        "irc/core/dispatcher",
        "irc/core/channels",
        "irc/core/users",

        "irc/core/ctcp",
        "irc/core/msg",
        "irc/core/nick",
        "irc/core/logger",
        "irc/core/seen",
    ]

    options = {
        'mode': '*',
        'recv': 1024,
        'charlimit': 440,
        'proxy': None,
        'ssl': False,
        }

    autoload = [
        "irc/moderator"
    ]

    class Settings(bot.Server.Settings):

        idents = bot.Server.Settings.idents + '#'
        mglob = bot.Server.Settings.mglob + ['channels.*.modules.{m}.*']

        channeldefaults = {}
        channeltree = {}

        def getchannel(self, v, context, pop=False):
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
                    ret = self.d[setting]
                    if type(ret) not in [list, dict] or pop:
                        self.d.pop(setting)
                    return ret
            return self.get(v, pop=pop)

        def addbranch(self, ss, n):
            if '~' not in n:
                bot.Server.Settings.addbranch(
                    self, copy.deepcopy(ss), n, rm=True)
            n = n.replace('~', '')
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

        def getchannelsetting(self, setting, c, pop=False):
            return self.server.settings.getchannel(
                "modules.%s.%s" % (self.index, setting), c, pop)

        def addserverchannelsetting(self, n, v):
            self.serverchannelsettings[n] = v

        m.getchannelsetting = getchannelsetting
        m.addserverchannelsetting = addserverchannelsetting
        m.serverchannelsettings = {}
        return m

    def setnick(self, nick):
        self.nick = nick
        self.send("NICK %s" % (nick))

    def connect(self):
        self.log("SOCK CONN", "Starting.")
        self.socket = ircsocket(self.opt('proxy'))
        self.socket.connect((self.opt('host'), self.opt('port')))
        if self.opt('ssl'):
            import ssl
            self.socket = ssl.wrap_socket(self.socket)
        self.log("SOCK CONN", "Done.")

    class Channel:

        def __init__(self, server, name):
            self.server = server
            self.name = name
            self.names = {}

    def ready(self):
        self.socket = None
        self.loggedin = False
        self.info = {}
        self.channels = {}
        self.inbuf = bytes()
        self.outbuf = []
        self.addtimer(self.output, "output", 100)
        self.wantnick = self.settings.get("server.user.nick")
        self.setnick(self.wantnick)
        self.send("USER %s %s * :%s" % (
            self.settings.get('server.user.ident'),
            self.settings.get('server.user.mode'),
            self.settings.get('server.user.name')))

    def send(self, msg):
        self.outbuf.append(msg)

    def sendto(self, command, target, msg):
        self.send("%s %s :%s" % (command, target, msg))
        self.dohook('log', 'sendto', command.upper(), (target.lower(), msg))

    def output(self):
        if not self.socket:
            self.connect()
        if self.outbuf:
            o = bytes(self.outbuf.pop(0), 'UTF-8')
            if o[-1] != b'\n':
                o += b'\n'
            self.log("OUT", o.decode())
            self.socket.send(o)

    def run(self):
        if not self.socket:
            self.connect()
        inr = [self.socket]
        try:
            readyr, _, _ = select.select(
                inr, [], [], 0.1)
        except InterruptedError:
            return
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
        if 'CHANTYPES' not in self.info:
            return x and True
        return x and x[0] in self.info['CHANTYPES']

    def build_lists(self):
        bot.Server.build_lists(self)
        self.settings.channeldefaults = {}
        for m in list(self.modules.values()):
            for k, v in list(m.serverchannelsettings.items()):
                self.settings.addchannel(k, v)

    def shutdown(self):
        self.socket.send(('QUIT :%s\n' % (bot.versionstring)).encode())
        time.sleep(0.1)
        self.socket.shutdown(socket.SHUT_RDWR)
        time.sleep(0.1)
        self.socket.close()

    #References:
    #http://stackoverflow.com/a/13382032
    #https://www.codeux.com/textual/help/Text-Formatting.kb
    class codes:

        reset = '\x0f'
        bold = '\x02'
        italic = '\x1d'
        reverse = '\x16'
        underline = '\x1f'
        strike = '\x13'
        color = '\x03'

        white = 0
        black = 1
        darkblue = 2
        darkgreen = 3
        red = 4
        darkred = 5
        darkviolet = 6
        orange = 7
        yellow = 8
        lightgreen = 9
        cyan = 10
        lightcyan = 11
        blue = 12
        violet = 13
        darkgray = 14
        lightgray = 15

        def buildcolor(foreground=-1, background=-1):
            """Build a color string from <foreground> and <background>."""
            out = ""
            if foreground >= 0:
                out += Server.codes.color + '%d' % foreground
            if background >= 0:
                out += ',%d' % background
            return out


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
        if 'ident' not in self.server.options:
            self.server.options['ident'] = self.server.settings.get(
                'server.user.nick')
        self.server.settings.add("server.user.ident", self.server.opt('ident'))

bot.register.module(M_Settings)


class M_Nick(bot.Module):

    index = "nick"
    hidden = True

    def register(self):

        self.addhook('recv', 'recv', self.recv)
        self.addsetting('poll', True)
        self.addtimer(self.poll, 'poll', 120 * 1000)
        self.addcommand(
            self.setnick, 'nick',
            'Set the bot nick. Use login nick if omitted.',
            ['[-temp]', '[nick]'])
        self.npending = None

    def setnick(self, context, args):
        context.exceptrights(["admin"])
        args.default('nick', self.server.settings.get('server.user.nick'))
        if args.getstr('nick') == self.server.nick:
            return "%s is already the nick." % self.server.nick
        self.server.wantnick = args.getstr('nick')
        self.server.setnick(self.server.wantnick)
        ret = "Set nick to %s ({w} set at login)." % (args.getstr('nick'))
        self.npending = (lambda server: context.reply(ret.format(w=(
            utils.ynstr(args.getstr('nick')
            == server.settings.get("server.user.nick"), "will", "won't")
            ))),
            lambda: context.reply(
                "Cannot set nick to %s" % args.getstr('nick')),
                    args.getstr('nick') if not args.getbool('temp') else '')

    def recv(self, context):
        if context.code(433):
            if self.npending:
                self.npending[1]()
            if context.reciever != '*':
                self.server.nick = context.reciever
            responses = []
            self.server.dohook('nickinuse', responses)
            if not responses and not self.server.loggedin:
                self.server.setnick(self.server.nick + "_")
        elif context.code('NICK'):
            if context.reciever.strip(':') == self.server.wantnick:
                if self.npending:
                    if self.npending[2]:
                        self.server.settings.set("server.user.nick",
                            self.npending[2])
                    self.npending[0](self.server)

    def poll(self):
        if self.getsetting("poll"):
            if self.server.wantnick != self.server.nick:
                self.server.setnick(self.server.wantnick)

bot.register.module(M_Nick)