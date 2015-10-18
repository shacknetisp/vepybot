# -*- coding: utf-8 -*-
import bot
import time


class Whois:

    def __init__(self):
        self.time = time.time()
        self.channels = {}

    ident = ""
    host = ""
    name = ""
    auth = ""
    idle = 0
    signon = 0
    server = ""


class M_Whois(bot.Module):

    index = "whois"
    hidden = False

    def register(self):
        self.addhook("recv", "recv", self.recv)
        self.addhook("whois.fromcontext", "fromcontext", self.fromcontext)
        self.addhook("whois.fromtuple", "fromtuple", self.fromtuple)
        self.addhook("chanmodes", "chanmodes", self.chanmodes)
        self.addtimer(self.timer, "whois", 60 * 1000)
        self.addtimer(self.chantimer, "chantimer", 60 * 1000)
        self.whois = {}
        self.server.whois = self.whois
        self.tmp = {}

        self.addcommand(self.getwhois, "whois",
            "Get information about a nick. Space-delimited values."
            " Values can be: nick, ident, host, channels, or auth/",
            ["nick", "[values...]"])

        self.serverset('whois.updatechannels', self.updatechannels)

    def getwhois(self, context, args):
        args.default('values', 'nick host channels')
        info = {}
        if args.getstr("nick") in self.whois:
            w = self.whois[args.getstr("nick")]
            info['nick'] = args.getstr("nick")
            info['ident'] = w.ident
            info['name'] = w.name
            info['host'] = w.host
            info['channels'] = ' '.join(list(w.channels.keys()))
            info['auth'] = w.auth
        else:
            return "Nick not found."
        out = []
        values = args.getstr("values").split(' ')
        for v in values:
            if v in info and type(info[v]) in [str, int]:
                if len(values) == 1:
                    out.append(str(info[v]))
                else:
                    out.append("%s: %s" % (v, str(info[v])))
        return ', '.join(out) or "No results."

    def updatechannels(self, snick=None):
        nicks = {}
        for chan in self.server.channels:
            v = self.server.channels[chan].names
            for n in v:
                if snick is not None and n not in snick:
                    continue
                if n not in nicks:
                    nicks[n] = {}
                nicks[n][chan] = v[n]
        for nick in nicks:
            if nick in self.whois:
                self.whois[nick].channels = nicks[nick]

    def chantimer(self):
        self.updatechannels()

    def timer(self):
        tod = []
        for w in self.whois:
            if time.time() - self.whois[w].time > 250:
                tod.append(w)
        for d in tod:
            self.whois.pop(d)

    def fromcontext(self, context):
        nicks = [context.user[0]]
        if context.code('nick'):
            nicks.append(context.rawsplit[2])
        for nick in nicks:
            if nick:
                if nick not in self.whois:
                    self.whois[nick] = Whois()
                w = self.whois[nick]
                w.ident = context.user[1]
                w.host = context.user[2]

    def fromtuple(self, t):
        nick = t[0]
        if nick:
            if nick not in self.whois:
                self.whois[nick] = Whois()
            w = self.whois[nick]
            w.ident = t[1]
            w.host = t[2]

    def recv(self, context):
        if context.code("311"):
            self.tmp[context.rawsplit[3]] = Whois()
            w = self.tmp[context.rawsplit[3]]
            w.ident = context.rawsplit[4]
            w.host = context.rawsplit[5]
            w.name = context.text
        elif context.code("312"):
            w = self.tmp[context.rawsplit[3]]
            w.server = context.rawsplit[4]
        elif context.code("317"):
            w = self.tmp[context.rawsplit[3]]
            w.idle = int(context.rawsplit[4])
            w.signon = int(context.rawsplit[5])
        elif context.code("318"):
            self.whois[context.rawsplit[3]] = self.tmp[context.rawsplit[3]]
            self.server.dohook("whois", context.rawsplit[3])
        elif context.code("330"):
            #Freenode
            w = self.tmp[context.rawsplit[3]]
            w.auth = context.rawsplit[4]
        elif context.code("JOIN"):
            self.fromcontext(context)
            w = self.whois[context.user[0]]
            channel = context.rawsplit[2].strip(':')
            if channel not in w.channels:
                w.channels[channel] = []
            self.server.dohook('join', channel, context.user[0])
        elif context.code("PART"):
            self.fromcontext(context)
            w = self.whois[context.user[0]]
            channel = context.rawsplit[2]
            if channel in w.channels:
                w.channels.pop(channel)
        elif context.code("MODE"):
            channel = context.rawsplit[2]
            modes = context.rawsplit[3]
            final = {}
            nicks = context.rawsplit[4:]
            for n in nicks:
                final[n] = []
            now = ''
            idx = 0
            for cchar in modes:
                if cchar in '-+':
                    now = cchar
                elif now and idx in range(len(nicks)):
                    final[nicks[idx]].append(now + cchar)
            self.server.dohook('chanmodes', channel, final)

    def chanmodes(self, channel, modes):
        for target in modes:
            if target not in self.whois:
                continue
            w = self.whois[target]
            if channel not in w.channels:
                w.channels[channel] = []
            for mode in modes[target]:
                if mode == '+o':
                    if 'o' not in w.channels[channel]:
                        w.channels[channel].append('o')
                elif mode == '-o':
                    if 'o' in w.channels[channel]:
                        w.channels[channel].pop(w.channels[channel].index('o'))
                elif mode == '+v':
                    if 'v' not in w.channels[channel]:
                        w.channels[channel].append('v')
                elif mode == '-v':
                    if 'v' in w.channels[channel]:
                        w.channels[channel].pop(w.channels[channel].index('v'))

bot.register.module(M_Whois)