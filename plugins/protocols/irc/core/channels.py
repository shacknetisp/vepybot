# -*- coding: utf-8 -*-
import bot
from lib import utils
bot.reload(utils)


class Channel:

    def __init__(self, server, name):
        self.server = server
        self.name = name
        self.names = {}


class M_Channels(bot.Module):

    index = "channels"

    def register(self):
        self.addhook("loggedin", "loggedin", self.loggedin)
        self.addhook("recv", "recv", self.recv)
        self.addtimer(self.timer, "timer", 60 * 1000)
        self.channels = {}
        self.server.channels = self.channels

        self.addcommand(
            self.join_c,
            "join",
            "Join a channel, specify -temp to not autojoin.",
            ["-[temp]", "channel"])

        self.addcommand(
            self.part_c,
            "part",
            "Part a channel, specify -temp to not forget the channel.",
            ["-[temp]", "[channel]"])

        self.addcommand(
            self.hop_c,
            "hop",
            "Hop a channel.",
            ["[channel]"])

        self.addcommand(self.get, "channels", "List channels.", [])

        self.addsetting("#kickrejoin", True)
        self.tmp = {}

    def get(self, c, a):
        return ' '.join(list(self.channels.keys())) or 'No channels joined.'

    def timer(self):
        for channel in self.channels:
            self.server.send("WHO %s" % channel)

    def join(self, c, temp=False):
        self.server.send("JOIN %s" % c)
        if temp:
            return
        clist = self.server.settings.get("server.channels")
        if c not in clist:
            clist.append(c)
        self.server.settings.set("server.channels", clist)

    def part(self, c, temp=False):
        self.server.send("PART %s" % c)
        if temp:
            return
        clist = self.server.settings.get("server.channels")
        if c in clist:
            clist.pop(clist.index(c))
        self.server.settings.set("server.channels", clist)

    def join_c(self, context, args):
        if args.getstr('channel') in self.channels:
            return "Already joined %s." % args.getstr('channel')
        context.exceptrights(['admin', args.getstr('channel') + ',op'])
        self.join(args.getstr('channel'), args.getbool('temp'))
        return "Attempted to join %s (%s autojoin)." % (args.getstr('channel'),
            utils.ynstr(args.getstr('channel')
            in self.server.settings.get("server.channels"), "will", "won't"))

    def part_c(self, context, args):
        if context.channel:
            args.default('channel', context.channel)
        if args.getstr('channel') not in self.channels:
            return "Not joined in %s." % args.getstr('channel')
        context.exceptrights(['admin', args.getstr('channel') + ',op'])
        self.part(args.getstr('channel'), args.getbool('temp'))
        ret = "Parted %s (%s autojoin)." % (args.getstr('channel'),
            utils.ynstr(args.getstr('channel')
            in self.server.settings.get("server.channels"), "will", "won't"))
        if context.channel == args.getstr('channel'):
            context.replypriv(ret)
        else:
            context.reply(ret)

    def hop_c(self, context, args):
        if context.channel:
            args.default('channel', context.channel)
        if args.getstr('channel') not in self.channels:
            return "Not joined in %s." % args.getstr('channel')
        context.exceptrights(['admin', args.getstr('channel') + ',op'])
        self.part(args.getstr('channel'), True)
        self.join(args.getstr('channel'), True)
        return "Hopped %s." % args.getstr('channel')

    def loggedin(self):
        for channel in self.server.settings.get("server.channels"):
            self.join(channel)

    def recv(self, context):
        if context.code("kick"):
            self.server.dohook('log', 'kick', context.rawsplit[0],
                (context.rawsplit[2], context.rawsplit[3]))
            if context.rawsplit[3] == self.server.nick:
                if context.rawsplit[2] in self.channels:
                    self.channels.pop(context.rawsplit[2])
                    self.server.log("KICK PARTED", context.rawsplit[2])
                if self.getchannelsetting("kickrejoin", context.reciever):
                    self.join(context.reciever)
        elif context.code("join"):
            if context.user[0] == self.server.nick:
                c = context.rawsplit[2].strip(':')
                self.channels[c] = Channel(self.server, c)
                self.server.send("WHO %s" % c)
                self.server.log("JOINED", c)
        elif context.code("part"):
            if context.user[0] == self.server.nick:
                if context.rawsplit[2] in self.channels:
                    self.channels.pop(context.rawsplit[2])
                    self.server.log("PARTED", context.rawsplit[2])
        elif context.code("352"):
            self.server.dohook('whois.fromtuple', (context.rawsplit[7],
                context.rawsplit[4], context.rawsplit[5]))
            if context.rawsplit[3] not in self.tmp:
                self.tmp[context.rawsplit[3]] = {
                    'names': {},
                    }
            w = self.tmp[context.rawsplit[3]]
            w['names'][context.rawsplit[7]] = [
                            self.server.info['PREFIX'][0][
                            self.server.info['PREFIX'][1].index(m)]
                            for m in context.rawsplit[8]
                            if m in self.server.info['PREFIX'][1]
                            ]
        elif context.code("315"):
            w = self.tmp[context.rawsplit[3]]
            if context.rawsplit[3] not in self.channels:
                self.channels[context.rawsplit[3]] = Channel(
                    self.server, context.rawsplit[3])
            c = self.channels[context.rawsplit[3]]
            c.names = w['names']
            self.server.rget('whois.updatechannels')(list(c.names.keys()))


bot.register.module(M_Channels)