# -*- coding: utf-8 -*-
import bot

"""
load irc/auth/vhost
vhost set name myname
vhost set password hunter2
config modules.vhost.enabled true
vhost
"""


class M_Vhost(bot.Module):

    index = "vhost"

    def register(self):
        self.addhook("login", "login", self.login)

        self.addsetting("=name", "")
        self.addsetting("=password", "")
        self.addsetting("enabled", False)
        self.addsetting("auto", True)

        self.addcommand(self.vhost_c, "vhost", "Authenticate with VHOST.", [])

        self.addcommand(self.setp, "set password",
            "Set the VHOST password.", ["password"])

        self.addcommand(self.setn, "set name",
            "Set the VHOST name.", ["[name]"])

    def isset(self):
        return self.getsetting('name') and self.getsetting('password')

    def setn(self, context, args):
        args.default("name", "")
        self.setsetting("name", args.getstr("name"))
        return "Set name to: %s" % self.getsetting('name')

    def setp(self, context, args):
        args.default("password", "")
        self.setsetting("password", args.getstr("password"))
        return "Set password to: %s" % self.getsetting('password')

    def vhost(self):
        self.server.log("AUTH", "Identifying with VHOST.")
        self.server.send("VHOST %s %s" % (
            self.getsetting("name"),
            self.getsetting("password"),
            ))

    def vhost_c(self, context, args):
        context.exceptrights(["admin"])
        if not self.getsetting("enabled"):
            return "VHOST is disabled."
        if not self.isset():
            return "Set the VHOST name and password first."
        self.vhost()
        return "Attempted to VHOST..."

    def login(self):
        if self.getsetting("enabled") and self.getsetting(
            "auto") and self.isset():
                self.vhost()

bot.register.module(M_Vhost)