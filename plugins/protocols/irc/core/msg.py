# -*- coding: utf-8 -*-
import bot


class Module(bot.Module):

    index = "msg"

    def register(self):

        self.addcommand(self.say, "say", "Send a message to a channel.",
                        ["[-notice]", "channel", "message..."])

        self.addcommand(self.do, "do", "Send a /me message to a channel.",
                        ["channel", "message..."])

    def say(self, context, args):
        if args.getstr("channel") not in self.server.channels:
            return "That channel has not been joined."
        context.exceptrights(["admin", "%s,op" % args.getstr("channel")])
        command = "NOTICE" if args.getbool('notice') else "PRIVMSG"
        self.server.sendto(command, args.getstr("channel"),
                           args.getstr("message"))

    def do(self, context, args):
        if args.getstr("channel") not in self.server.channels:
            return "That channel has not been joined."
        context.exceptrights(["admin", "%s,op" % args.getstr("channel")])
        self.server.sendto("PRIVMSG", args.getstr("channel"),
                           "\1ACTION %s\1" % args.getstr("message"))

bot.register.module(Module)
