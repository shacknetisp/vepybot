# -*- coding: utf-8 -*-
import bot
import fnmatch
import time


class Module(bot.Module):

    index = "automode"

    def register(self):
        self.lasttime = {}
        self.modes = {
            "op": "o",
            "voice": "v",
            }
        for mode in self.modes:
            self.addsetting("~#%slist" % mode, [])
        self.addtimer(self.timer, "timer", 20 * 1000)
        self.addhook("join", "join", self.join)

    def join(self, channel, nick):
        self.server.callonce(lambda: self.checkmode(channel, nick), 1000)
        self.lasttime[(channel, nick)] = time.time()

    def checkmode(self, channel, nick):
        if nick in self.server.whois:
            w = self.server.whois[nick]
            idstring = "irc:%s!%s@%s!%s" % (
                nick, w.ident, w.host, w.auth)
            if channel not in w.channels:
                return
            for mode in self.modes:
                if self.modes[mode] in w.channels[channel]:
                    continue
                for i in self.getchannelsetting("%slist" % mode,
                    channel):
                        if fnmatch.fnmatch(idstring, i):
                            self.server.send("MODE %s +%s %s" % (
                                channel,
                                self.modes[mode],
                                nick
                                ))
                            break

    def timer(self):
        for channel in self.server.channels:
            channel = self.server.channels[channel]
            for nick in channel.names:
                if (channel.name, nick) in self.lasttime:
                    if time.time() - self.lasttime[(channel.name, nick)] < 1:
                        continue
                self.checkmode(channel.name, nick)

bot.register.module(Module)