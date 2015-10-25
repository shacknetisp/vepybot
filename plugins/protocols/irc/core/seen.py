# -*- coding: utf-8 -*-
import bot
import time
from lib import timeutils
bot.reload(timeutils)


class Module(bot.Module):

    index = "seen"

    def register(self):
        self.db = self.getdb("seen", {"chat": {}, "all": {}})
        self.addcommand(self.seen, "seen", "Get when a nick was last seen.",
            ["[-chat]", "nick"])
        self.addhook('recv', 'recv', self.recv)

    def recv(self, context):
        if not self.server.settings.get('logger.enabled'):
            return
        if not context.user[0]:
            return
        if context.code('privmsg') or context.code('notice'):
            if context.channel:
                self.db.d['chat'][context.user[0]] = (time.time(),
                    "<%s in %s> %s" % (
                        context.user[0], context.channel, context.text),
                            context.channel)
                self.db.d['all'][context.user[0]] = (time.time(),
                    "<%s in %s> %s" % (
                        context.user[0], context.channel, context.text),
                            context.channel)
                self.db.save()
            else:
                self.db.d['all'][context.user[0]] = (time.time(),
                    "<PMing me>")
                self.db.save()
        elif context.code('JOIN') or context.code('PART'):
            self.db.d['all'][context.user[0]] = (time.time(),
                "%s %s" % (
                    context.rawcode, context.channel),
                        context.channel)
            self.db.save()
        elif context.code('QUIT'):
            self.db.d['all'][context.user[0]] = (time.time(),
                "Quitting IRC")
            self.db.save()

    def seen(self, context, args):
        if not self.server.settings.get('logger.enabled'):
            return "Logger disabled."
        if args.getbool('chat'):
            d = self.db.d['chat']
        else:
            d = self.db.d['all']
        if args.getstr('nick') not in d:
            return "Not found."
        e = d[args.getstr('nick')]
        durstr = "%s (%s ago)" % (
            time.strftime('%D %T', time.gmtime(e[0])),
            timeutils.agostr(e[0]))
        if len(e) == 2:
            return "%s was seen at %s: %s" % (
                args.getstr('nick'), durstr, e[1])
        elif len(e) == 3:
            if context.channel and context.channel != e[2]:
                return "%s was seen at %s in another channel." % (
                    args.getstr('nick'), durstr)
            else:
                if e[2] in context.whois.channels:
                    return "%s was seen at %s: %s" % (
                        args.getstr('nick'), durstr, e[1])
                else:
                    return "%s was seen at %s in a channel you aren't in." % (
                    args.getstr('nick'), durstr)

bot.register.module(Module)
