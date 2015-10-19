# -*- coding: utf-8 -*-
import bot


class Module(bot.Module):

    index = "moderator"

    def register(self):

        self.addsetting('#enabled', False)
        self.addhook('recv', 'recv', self.recv)
        self.addsetting('#tolerance', 9)
        self.addhook('dispatcher.ignore', 'dr', self.dr)
        self.addtimer(self.timer, 'timer', 1 * 1000)
        self.d = {}
        self.b = set()

    def dr(self, context, responses):
        if context.code('privmsg'):
            if context.user[0] in self.b:
                responses.append(True)

    def timer(self):
        for channel in self.d:
            tol = self.getchannelsetting('tolerance', channel)
            for user in self.d[channel]:
                self.d[channel][user][0] = max(0,
                    self.d[channel][user][0] - 1)
                self.d[channel][user][1] = max(0,
                    self.d[channel][user][1] - (0.5 / tol))

    def recv(self, context):
        if not context.channel:
            return
        if not (context.code('privmsg') or context.code('notice')):
            return
        if not self.getchannelsetting('enabled', context):
            return
        responses = []
        self.server.dohook("dispatcher.ignore", context, responses)
        if responses:
            return
        tol = self.getchannelsetting('tolerance', context)
        if context.channel not in self.d:
            self.d[context.channel] = {}
        d = self.d[context.channel]
        if not context.user[0]:
            return
        if context.user[0] not in d:
            d[context.user[0]] = [0, 0]
        d = d[context.user[0]]
        priv = 0
        if ('%s,op' % context.channel) in context.getrights():
            return
        if ('%s,v' % context.channel) in context.getrights():
            priv += 1
        avgcount = (len(context.text) / len(set(context.text)))
        d[0] += max((
            1 +
            avgcount) -
            priv, 0)
        if d[0] >= tol:
            d[0] /= 1.5
            d[1] += 1
            if d[1] <= 1:
                context.reply("%s: Don't spam." % context.user[0])
            elif d[1] <= 2:
                self.server.send("KICK %s %s :%s" % (
                    context.channel,
                    context.user[0],
                    "Don't spam.",
                    ))
            else:
                d[0] = 0
                d[1] = 0
                self.server.send("MODE %s +b %s!*@*" % (
                    context.channel,
                    context.user[0],
                    ))
                self.b.add(context.user[0])
                self.server.callonce(lambda: self.server.send(
                        "MODE %s -b %s!*@*" % (
                        context.channel,
                        context.user[0],
                    )), 10 * 1000)
                self.server.callonce(lambda: self.b.discard(
                    context.user[0]), 10 * 1000)
                self.server.send(
                    "KICK %s %s: The ban will lift in 10 seconds." % (
                    context.channel,
                    context.user[0],
                    ))

bot.register.module(Module)