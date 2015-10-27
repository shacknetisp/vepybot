# -*- coding: utf-8 -*-
import bot
from lib import utils
bot.reload(utils)


class M_Channels(bot.Module):

    index = "channels"

    def register(self):
        self.addhook("loggedin", "loggedin", self.loggedin)
        self.addhook("recv", "recv", self.recv)
        self.addtimer(self.timer, "timer", 60 * 1000)
        self.addcommand(
            self.join_c, "join",
            "Join a channel, specify -temp to not autojoin.",
            ["-[temp]", "channel"])
        self.addcommand(
            self.part_c, "part",
            "Part a channel, specify -temp to not forget the channel.",
            ["-[temp]", "[channel]"])
        self.addcommand(
            self.hop_c, "cycle",
            "Cycle on a channel.",
            ["[channel]"])
        self.addcommandalias('cycle', 'hop')
        self.addcommand(self.get, "channels", "List channels.", [])
        self.addsetting("#kickrejoin", True)
        self.tmp = {}

    def get(self, c, a):
        return ' '.join(list(
            self.server.channels.keys())) or 'No channels joined.'

    def timer(self):
        for channel in self.server.channels:
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

    def ynchannelauto(self, channel):
        return utils.ynstr(channel
                             in self.server.settings.get("server.channels"),
                             "will",
                             "won't")

    def join_c(self, context, args):
        if args.getstr('channel') in self.server.channels:
            return "Already joined %s." % args.getstr('channel')
        context.exceptrights(['admin', args.getstr('channel') + ',op'])
        self.join(args.getstr('channel'), args.getbool('temp'))
        ynstr = self.ynchannelauto(args.getstr('channel'))
        return "Attempted to join %s (%s autojoin)." % (args.getstr('channel'),
                                                        ynstr)

    def part_c(self, context, args):
        if context.channel:
            args.default('channel', context.channel)
        if args.getstr('channel') not in self.server.channels:
            return "Not joined in %s." % args.getstr('channel')
        context.exceptrights(['admin', args.getstr('channel') + ',op'])
        self.part(args.getstr('channel'), args.getbool('temp'))
        ynstr = self.ynchannelauto(args.getstr('channel'))
        ret = "Parted %s (%s autojoin)." % (args.getstr('channel'),
                                            ynstr)
        if context.channel == args.getstr('channel'):
            context.replypriv(ret)
        else:
            context.reply(ret)

    def hop_c(self, context, args):
        if context.channel:
            args.default('channel', context.channel)
        if args.getstr('channel') not in self.server.channels:
            return "Not joined in %s." % args.getstr('channel')
        context.exceptrights(['admin', args.getstr('channel') + ',op'])
        self.part(args.getstr('channel'), True)
        self.join(args.getstr('channel'), True)
        return "Cycled %s." % args.getstr('channel')

    def loggedin(self):
        for channel in self.server.settings.get("server.channels"):
            self.join(channel)

    def checkpart(self, channel, reason):
        if channel in self.server.channels:
            self.server.channels.pop(channel)
            self.server.log("KICK PARTED", channel)

    def handlekick(self, context):
        self.server.dohook('log', 'kick', context.rawsplit[0],
                           (context.rawsplit[2], context.rawsplit[3]))
        if context.rawsplit[3] == self.server.nick:
            self.checkpart(context.rawsplit[2], 'KICK PARTED')
            if self.getchannelsetting("kickrejoin", context.reciever):
                self.join(context.reciever)

    def handlejoin(self, context):
        if context.user[0] == self.server.nick:
            c = context.rawsplit[2].strip(':')
            self.server.channels[c] = self.server.Channel(self.server, c)
            self.server.send("WHO %s" % c)
            self.server.log("JOINED", c)

    def handlepart(self, context):
        if context.user[0] == self.server.nick:
            self.checkpart(context.rawsplit[2], 'PARTED')

    def handle352(self, context):
        self.server.dohook('whois.fromtuple', (context.rawsplit[7],
                                                   context.rawsplit[4],
                                                   context.rawsplit[5]))
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

    def handle315(self, context):
        w = self.tmp[context.rawsplit[3]]
        if context.rawsplit[3] not in self.server.channels:
            self.server.channels[context.rawsplit[3]] = self.server.Channel(
                self.server, context.rawsplit[3])
        c = self.server.channels[context.rawsplit[3]]
        c.names = w['names']
        self.server.rget('whois.updatechannels')(list(c.names.keys()))

    def recv(self, context):
        if context.code("kick"):
            self.handlekick(context)
        elif context.code("join"):
            self.handlejoin(context)
        elif context.code("part"):
            self.handlepart(context)
        elif context.code("352"):
            self.handle352(context)
        elif context.code("315"):
            self.handle315(context)


bot.register.module(M_Channels)
