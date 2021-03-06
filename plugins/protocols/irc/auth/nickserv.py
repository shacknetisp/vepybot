# -*- coding: utf-8 -*-
import bot
import time

"""
load irc/auth/nickserv
nickserv set password hunter2
config set modules.nickserv.enabled True
config set modules.nickserv.ghost True
nickserv register email@do.main
nickserv verify register myaccount c0d3numb3r
nickserv identify
"""


class M_NickServ(bot.Module):

    index = "nickserv"

    def register(self):
        self.addhook("recv", "recv", self.recv)
        self.addhook("login", "login", self.login)
        self.addhook("nickinuse", "433", self.nickinuse)

        self.addsetting("=name", "")
        self.addsetting("=password", "")
        self.addsetting("enabled", False)
        self.addsetting("auto", True)
        self.addsetting("ghost", True)

        self.lastns = ""
        self.lastnstime = time.time()
        self.ghosting = True

        self.addcommand(self.register_c, "register",
                        "Register with NickServ.",
                        ["[-name=account name]", "email"])

        self.addcommand(self.verify_c, "verify register",
                        "Verify with NickServ.", ["account", "code"])

        self.addcommand(self.identify_c, "identify",
                        "Identify with NickServ.", [])

        self.addcommand(self.setp, "set password",
                        "Set the NickServ password.", ["password"])

        self.addcommand(self.setn, "set name",
                        "Set the NickServ name.", ["[name]"])

    def setn(self, context, args):
        args.default("name", "")
        self.setsetting("name", args.getstr("name"))
        return "Set name to: %s" % self.getsetting('name')

    def setp(self, context, args):
        args.default("password", "")
        self.setsetting("password", args.getstr("password"))
        return "Set password to: %s" % self.getsetting('password')

    def name(self):
        return self.getsetting("name") or self.server.settings.get(
            'server.user.nick')

    def recv(self, context):
        if context.user[0]:
            if context.code('notice') and context.user[0].lower() == 'nickserv':
                if context.reciever == self.server.nick:
                    if self.lastns and time.time() - self.lastnstime < 30:
                        self.server.sendto("NOTICE", self.lastns,
                                           "NickServ -- %s" % (
                                               context.text,
                                           ))
                    if self.ghosting:
                        self.server.setnick(self.server.wantnick)
                        self.ghosting = False

    def nickinuse(self, r):
        if (self.getsetting("enabled") and
           self.getsetting("password") and self.getsetting("ghost")):
            self.server.setnick(self.server.nick + "_")
            self.server.sendto("PRIVMSG", "nickserv", "GHOST %s %s" % (
                self.server.wantnick,
                self.getsetting("password"),
            ))
            self.ghosting = True
            r.append(True)

    def identify(self):
        self.server.log("AUTH", "Identifying with NickServ.")
        self.server.sendto("PRIVMSG", "nickserv", "IDENTIFY %s %s" % (
            self.name(),
            self.getsetting("password"),
        ))

    def identify_c(self, context, args):
        context.exceptrights(["admin"])
        if not self.getsetting("enabled"):
            return "NickServ is disabled."
        if not self.getsetting("password"):
            return "There is no password set."
        self.identify()
        self.lastns = context.user[0]
        self.lastnstime = time.time()

    def register_c(self, context, args):
        if not self.getsetting("enabled"):
            return "NickServ is disabled."
        if not self.getsetting("password"):
            return "There is no password set."
        self.server.sendto("PRIVMSG", "nickserv", "REGISTER %s %s %s" % (
            self.name() if args.getbool('name') else '',
            self.getsetting("password"),
            args.getstr('email'),
        ))
        self.lastns = context.user[0]
        self.lastnstime = time.time()

    def verify_c(self, context, args):
        if not self.getsetting("enabled"):
            return "NickServ is disabled."
        if not self.getsetting("password"):
            return "There is no password set."
        self.server.sendto("PRIVMSG", "nickserv", "VERIFY REGISTER %s %s" % (
            args.getstr('account'),
            args.getstr('code'),
        ))
        self.lastns = context.user[0]
        self.lastnstime = time.time()

    def login(self):
        if self.getsetting("enabled") and self.getsetting("password"):
            if self.getsetting("auto"):
                self.identify()

bot.register.module(M_NickServ)
