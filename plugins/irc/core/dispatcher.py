# -*- coding: utf-8 -*-
import bot
import time
import fnmatch


class Context(bot.Context):

    def __init__(self, server, text):
        self.moretemplate = "%s[{n} more message{s}]%s" % (
            server.codes.bold, server.codes.bold)
        bot.Context.__init__(self, server)
        stext = text.lstrip(':')
        split = stext.split()
        self.raw = text
        self.rawsplit = split
        self.sender = split[0]
        try:
            self.user = [self.sender.split('!')[0],
                self.sender.split('!')[1].split('@')[0],
                self.sender.split('!')[1].split('@')[1]]
        except IndexError:
            self.user = [None, None, None]
        self.displayname = self.user[0]
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
        self.ctcp = ""
        if self.text.startswith('\1'):
            self.ctcp = self.text.strip('\1')

    def idstring(self):
        ret = ""
        if self.sender[0]:
            ret = "%s!%s@%s!%s" % (
                self.user[0],
                self.user[1],
                self.user[2],
                self.whois.auth if hasattr(self, 'whois') else ''
                )
        return "irc:" + ret

    def code(self, c):
        return self.rawcode.lower() == str(c).lower()

    def reply(self, m, more=True, command=None, priv=False):
        if command is None:
            command = 'NOTICE' if self.server.settings.getchannel(
                'irc.notice', self) else 'PRIVMSG'
        m = str(m).strip()
        if not m:
            return
        if priv:
            target = self.user[0]
        else:
            target = self.channel or self.user[0]
        if not target:
            return
        sendf = lambda message: self.server.send(
            '%s %s :%s' % (command, target, message))
        self.replydriver(sendf, m, more)

    def replypriv(self, *args):
        self.reply(*args, priv=True)

    def replyctcp(self, m):
        self.reply("\1%s\1" % m, more=False, command='NOTICE')

    def setting(self, s):
        return "channels.%s.%s" % (self.channel, s)

    def channelidstring(self):
        return "irc#:%s" % self.channel

    def exceptchannelrights(self, rlist, m=None):
        if type(rlist) is str:
            rlist = [rlist]
        rlist = rlist + ['op']
        return self.exceptrights([("%s,%s" % (self.channel, r)) for r in rlist])

    def getrights(self):
        return self.server.getrights(self.idstring(), self)

    def exceptcancommand(self, module, command):
        if self.channel:
            for r in self.server.getrights(self.channelidstring(), self):
                if fnmatch.fnmatchcase("-%s.%s.%s" % (
                    module.plugin, module.index, command['name']), r):
                        if not self.checkright(
                            "%s,op" % self.channel):
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
    hidden = True
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
            if context.user[0]:
                if context.user[0] not in self.server.whois:
                    self.server.dohook(
                        "whois.fromcontext", context)
                context.whois = self.server.whois[
                    context.user[0]]
        except IndexError:
            self.server.log('INVALID IN', msg)
            return
        self.server.dohook("recv", context)

    def recv(self, context):
        self.server.dohook("whois.fromcontext", context)
        if context.code("privmsg"):
            if context.ctcp:
                split = context.ctcp.split()
                if split[0]:
                    self.server.dohook('ctcp.%s' % split[0].lower(),
                        context, split[1:])
            else:
                responses = []
                self.server.dohook("dispatcher.ignore", context, responses)
                if responses:
                    return
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
                                self.buf[context.user[0]].append(
                                    (context, command))
                                self.whoistime[context.user[0]] = time.time()
                                if self.server.settings.get('server.whois'):
                                    self.server.send(
                                        "WHOIS %s" % context.user[0])
                                else:
                                    self.server.dohook(
                                        "whois.fromcontext", context)
                                    context.whois = self.server.whois[
                                        context.user[0]]
                                    self.doinput(context, command)
                        else:
                            context.whois = self.server.whois[context.user[0]]
                            self.doinput(context, command)
                        return
        elif context.code(376):
            self.server.dohook('login')
            self.server.loggedin = True
            self.server.dohook('loggedin')

    def whoised(self, user):
        if user in self.buf:
            for context, command in self.buf[user]:
                context.whois = self.server.whois[user]
                self.doinput(context, command)
            del self.buf[user]

    def doinput(self, context, command):
        import string
        if not command.strip(string.punctuation):
            return
        out, errout = self.server.runcommand(context, command)
        if out or errout:
            context.reply(out if out else errout)
bot.register.module(M_Dispatcher)