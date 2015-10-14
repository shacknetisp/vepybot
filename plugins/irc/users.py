# -*- coding: utf-8 -*-
import bot
import time


class Whois:

    def __init__(self):
        self.time = time.time()

    ident = ""
    host = ""
    name = ""
    channels = {}
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
        self.addtimer("whois", self.timer, 10 * 1000)
        self.whois = {}
        self.server.whois = self.whois
        self.tmp = {}

    def timer(self):
        tod = []
        for w in self.whois:
            if time.time() - self.whois[w].time > 60:
                tod.append(w)
        for d in tod:
            self.whois.pop(d)

    def fromcontext(self, context):
        nick = context.user[0]
        if context.code('nick'):
            nick = context.rawsplit[2]
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
        elif context.code("319"):
            w = self.tmp[context.rawsplit[3]]
            for e in context.text.split():
                for ct in self.server.info['CHANTYPES']:
                    split = e.split(ct)
                    if len(split) == 2:
                        w.channels[ct + split[1]] = [
                            self.server.info['PREFIX'][0][
                            self.server.info['PREFIX'][1].index(m)]
                            for m in split[0]
                            ]
                        break
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

bot.register.module(M_Whois)