# -*- coding: utf-8 -*-
import bot


class M_Vhost(bot.Module):

    index = "vhost"

    def register(self):
        self.addhook("login", "login", self.login)

        self.addsetting("name", "")
        self.addsetting("password", "")
        self.addsetting("enabled", False)

        self.addcommand(self.vhost_c, "vhost", "Authenticate with VHOST.", [])

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
        self.vhost()
        return "Attempted to VHOST..."

    def login(self):
        if self.getsetting("enabled"):
            self.vhost()

bot.register.module(M_Vhost)