# -*- coding: utf-8 -*-
import bot
import time
import fnmatch


class Context(bot.Context):

    def __init__(self, server, text):
        bot.Context.__init__(self, server)
        stext = text.lstrip(':')
        split = stext.split()
        self.raw = text
        self.rawsplit = split
        self.sender = split[0]
        try:
            self.user = (self.sender.split('!')[0],
                self.sender.split('!')[1].split('@')[0],
                self.sender.split('!')[1].split('@')[1])
        except IndexError:
            self.user = (None, None, None)
        self.auth = ""
        self.rawcode = split[1] if 1 in range(len(split)) else ""
        self.reciever = split[2] if 2 in range(len(split)) else ""
        try:
            self.text = stext[stext.index(':') + 1:]
        except ValueError:
            self.text = ""
        try:
            self.channel = (
                self.reciever
                if self.reciever[0] in server.info['CHANTYPES']
                else
                None
                ) if 'CHANTYPES' in server.info else None
        except IndexError:
            self.channel = ""

    def idstring(self):
        ret = ""
        if self.sender[0]:
            ret = "%s!%s@%s!%s" % (
                self.user[0],
                self.user[1],
                self.user[2],
                self.whois.auth
                )
        return "irc:" + ret

    def code(self, c):
        return self.rawcode.lower() == str(c).lower()

    def reply(self, m):
        sender = self.channel or self.user[0]
        if not sender:
            return
        self.server.send('NOTICE %s :%s' % (sender, m))

    def setting(self, s):
        return "channels.%s.%s" % (self.channel, s)

    def channelidstring(self):
        return "irc#:%s" % self.channel

    def exceptchannelrights(self, rlist, m=None):
        if type(rlist) is str:
            rlist = [rlist]
        rlist = rlist + ['op']
        return self.exceptrights([("%s,%s" % (self.channel, r)) for r in rlist])

    def exceptcancommand(self, module, command):
        if self.channel and not self.checkright(
            "%s,op" % self.channel):
            for r in self.server.getrights(self.channelidstring(), self):
                if fnmatch.fnmatchcase("-%s.%s.%s" % (
                    module.plugin, module.index, command['name']), r):
                        raise bot.NoPerms(
                            "The channel may not use %s" % "%s.%s.%s" % (
                            module.plugin, module.index, command['name']))
                if r == "ignore":
                    raise bot.NoPerms("")

        self._exceptcancommand(module, command)

        if self.channel and not self.checkright(
            "%s,op" % self.channel):
            for r in self.server.getrights(self.idstring(), self):
                if fnmatch.fnmatchcase("%s,-%s.%s.%s" % (self.channel,
                    module.plugin, module.index, command['name']), r):
                        raise bot.NoPerms(
                        "You may not use %s on this channel." % "%s.%s.%s" % (
                        module.plugin, module.index, command['name']))
                if r == "%s,ignore" % self.channel:
                    raise bot.NoPerms("")


class M_Dispatcher(bot.Module):

    index = "dispatcher"
    hidden = False
    whoist = 60

    def register(self):
        self.addhook("server_recv", "s_recv", self.s_recv)
        self.addhook("recv", "recv", self.recv)
        self.addhook("whois", "whois", self.whoised)
        self.buf = {}
        self.whoistime = {}

    def s_recv(self, msg):
        if msg.find(':') == -1:
            return
        try:
            context = Context(self.server, msg)
        except IndexError:
            self.server.log('INVALID IN', msg)
            return
        self.server.dohook("recv", context)

    def recv(self, context):
        if context.code("privmsg"):
            #Find if prefixed
            for prefix in self.server.settings.getchannel(
                "parser.prefixes", context) + (
                    [""] if not context.channel else []) + [
                        self.server.nick + ',',
                        self.server.nick + ':',
                        ]:
                if context.text.startswith(prefix):
                    command = context.text[len(prefix):].strip()
                    #Schedule WHOIS if neccessary
                    if context.user[0] not in self.buf:
                        self.buf[context.user[0]] = []
                    if context.user[0] not in self.whoistime:
                        self.whoistime[context.user[0]] = 0
                    if time.time() - self.whoistime[
                        context.user[0]] > self.whoist or (
                            context.user[0] not in self.server.whois):
                            self.buf[context.user[0]].append((context, command))
                            self.whoistime[context.user[0]] = time.time()
                            self.server.send("WHOIS %s" % context.user[0])
                    else:
                        context.whois = self.server.whois[context.user[0]]
                        self.doinput(context, command)
                    return
        elif context.code(376):
            self.server.dohook('login')
            self.server.dohook('loggedin')

    def whoised(self, user):
        if user in self.buf:
            for context, command in self.buf[user]:
                context.whois = self.server.whois[user]
                self.doinput(context, command)
            del self.buf[user]

    def doinput(self, context, command):
        out, errout = self.server.runcommand(context, command)
        if out or errout:
            context.reply(out if out else errout)
bot.register.module(M_Dispatcher)