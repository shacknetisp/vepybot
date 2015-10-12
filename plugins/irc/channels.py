# -*- coding: utf-8 -*-
import bot
from lib import utils


class Channel:

    def __init__(self, server, name):
        self.server = server
        self.name = name


class M_Channels(bot.Module):

    index = "channels"

    def register(self):
        self.addhook("loggedin", "loggedin", self.loggedin)
        self.addhook("recv", "recv", self.recv)
        self.channels = {}

        self.addcommand(
            self.join_c,
            "join",
            "Join a channel, specify -temp to not autojoin.",
            ["-[temp]", "channel"])

        self.addcommand(
            self.part_c,
            "part",
            "Part a channel, specify -temp to not forget the channel.",
            ["-[temp]", "channel"])

        self.addcommand(
            self.hop_c,
            "hop",
            "Hop a channel.",
            ["channel"])

        self.addsetting("#kickrejoin", True)

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
        context.exceptrights(['admin', args.getstr('channel') + ',op'])
        self.join(args.getstr('channel'), args.getbool('temp'))
        return "Joined %s (%s autojoin)." % (args.getstr('channel'),
            utils.ynstr(args.getstr('channel')
            in self.server.settings.get("server.channels"), "will", "won't"))

    def part_c(self, context, args):
        if context.channel:
            args.default('channel', context.channel)
        context.exceptrights(['admin', args.getstr('channel') + ',op'])
        self.part(args.getstr('channel'), args.getbool('temp'))
        return "Parted %s (%s autojoin)." % (args.getstr('channel'),
            utils.ynstr(args.getstr('channel')
            in self.server.settings.get("server.channels"), "will", "won't"))

    def hop_c(self, context, args):
        if context.channel:
            args.default('channel', context.channel)
        context.exceptrights(['admin', args.getstr('channel') + ',op'])
        self.part(args.getstr('channel'), True)
        self.join(args.getstr('channel'), True)

    def loggedin(self):
        for channel in self.server.settings.get("server.channels"):
            self.join(channel)

    def recv(self, context):
        if context.code("kick"):
            if self.getchannelsetting("kickrejoin", context.reciever):
                self.join(context.reciever)


bot.register.module(M_Channels)