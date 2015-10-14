# -*- coding: utf-8 -*-
import bot


class M_NickServ(bot.Module):

    index = "nickserv"

    def register(self):
        self.addhook("recv", "recv", self.recv)
        self.addhook("login", "login", self.login)
        self.addhook("nickinuse", "433", self.nickinuse)

        self.addsetting("name", "")
        self.addsetting("password", "")
        self.addsetting("enabled", False)
        self.addsetting("ghost", True)

        self.lastns = ""

        self.addcommand(self.register_c, "register",
            "Register with NickServ.", ["email"])

        self.addcommand(self.verify_c, "verify register",
            "Verify with NickServ.", ["account", "code"])

        self.addcommand(self.identify_c, "identify",
            "Identify with NickServ.", [])

    def recv(self, context):
        if context.user[0]:
            if context.code('notice') and context.user[0].lower() == 'nickserv':
                if context.reciever == self.server.nick:
                    if self.lastns:
                        self.server.send("PRIVMSG %s :NickServ -- %s" % (
                        self.lastns,
                        context.text,
                        ))

    def nickinuse(self, r):
        if (self.getsetting("enabled") and
        self.getsetting("password") and self.getsetting("ghost")):
            self.server.setnick(self.server.nick + "_")
            self.server.send("PRIVMSG nickserv :GHOST %s %s" % (
                self.getsetting("name"),
                self.getsetting("password"),
                ))
            r.append(True)

    def identify(self):
        self.server.log("AUTH", "Identifying with NickServ.")
        self.server.send("PRIVMSG nickserv :IDENTIFY %s %s" % (
            self.getsetting("name"),
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

    def register_c(self, context, args):
        if not self.getsetting("enabled"):
            return "NickServ is disabled."
        if not self.getsetting("password"):
            return "There is no password set."
        self.server.send("PRIVMSG nickserv :REGISTER %s %s" % (
            self.getsetting("password"),
            args.getstr('email'),
            ))
        self.lastns = context.user[0]

    def verify_c(self, context, args):
        if not self.getsetting("enabled"):
            return "NickServ is disabled."
        if not self.getsetting("password"):
            return "There is no password set."
        self.server.send("PRIVMSG nickserv :VERIFY REGISTER %s %s" % (
            args.getstr('account'),
            args.getstr('code'),
            ))
        self.lastns = context.user[0]

    def login(self):
        if self.getsetting("enabled") and self.getsetting("password"):
            self.identify()

bot.register.module(M_NickServ)