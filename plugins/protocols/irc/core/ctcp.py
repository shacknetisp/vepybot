# -*- coding: utf-8 -*-
import bot
import time


class M_CTCP(bot.Module):

    index = "ctcp"
    hidden = False

    def register(self):
        self.addsetting("userinfo", "")
        self.addhook("ctcp.version", "ctcp.version", self.ctcp_version)
        self.addhook("ctcp.ping", "ctcp.ping", self.ctcp_ping)
        self.addhook("ctcp.time", "ctcp.time", self.ctcp_time)
        self.addhook("ctcp.errmsg", "ctcp.errmsg", self.ctcp_errmsg)
        self.addhook("ctcp.userinfo", "ctcp.userinfo", self.ctcp_userinfo)
        self.addhook("ctcp.clientinfo", "ctcp.clientinfo", self.ctcp_clientinfo)
        self.addhook("ctcp.source", "ctcp.source", self.ctcp_source)

    def ctcp_version(self, context, args):
        context.replyctcp("VERSION %s %s -- %s" % (bot.version.platformtuple))

    def ctcp_ping(self, context, args):
        if args:
            context.replyctcp("PING %s" % args[0])

    def ctcp_time(self, context, args):
        context.replyctcp("TIME %s" % time.ctime())

    def ctcp_source(self, context, args):
        context.replyctcp("SOURCE %s" % bot.source)

    def ctcp_errmsg(self, context, args):
        context.replyctcp("ERRMSG An error has occurred.")

    def ctcp_userinfo(self, context, args):
        if self.getsetting('userinfo'):
            context.replyctcp("USERINFO %s" % self.getsetting('userinfo'))

    def ctcp_clientinfo(self, context, args):
        l = []
        for hook in self.server.hooks:
            if hook.split('.')[0] == 'ctcp':
                l.append(hook.split('.')[1].upper())
        context.replyctcp('CLIENTINFO %s' % ' '.join(l))

bot.register.module(M_CTCP)