# -*- coding: utf-8 -*-
import bot


class Module(bot.Module):

    index = "logger"
    hidden = True

    def register(self):

        self.addhook('log', 'log', self.log)
        self.openlog = self.server.rget('openlog')
        self.writelog = self.server.rget('writelog')

    def log(self, cat, subcat, text):
        if cat == "join":
            with self.openlog("channels/%s" % text) as f:
                self.writelog(f, "--> %s!%s@%s has joined %s" % (
                    subcat[0], subcat[1], subcat[2],
                    text
                    ))
        elif cat == "part":
            with self.openlog("channels/%s" % text[0]) as f:
                self.writelog(f, "<-- %s!%s@%s has parted %s%s" % (
                    subcat[0], subcat[1], subcat[2],
                    text[0], (": " + text[1]) if text[1] else ''
                    ))
        elif cat == "mode":
            p = (("channels/%s" % text[0])
                if self.server.ischannel(text[0]) else
                ("users/%s" % text[0]))
            with self.openlog(p) as f:
                self.writelog(f, "-- %s MODE %s %s %s" % (
                    subcat,
                    text[0],
                    text[1],
                    text[2]
                    ))
        elif cat == "kick":
            with self.openlog("channels/%s" % text[0]) as f:
                self.writelog(f, "<-- %s KICK %s %s" % (
                    subcat,
                    text[0],
                    text[1]
                    ))
        elif cat == "quit":
            for channel in text[0]:
                with self.openlog("channels/%s" % channel) as f:
                    self.writelog(f, "<-- %s QUIT: %s" % (
                        subcat[0],
                        text[1]
                        ))
            with self.openlog("users/%s" % subcat[1][0]) as f:
                    self.writelog(f, "<-- %s QUIT: %s" % (
                        subcat[0],
                        text[1]
                        ))
        elif cat == "sendto":
            p = (("channels/%s" % text[0])
                if self.server.ischannel(text[0]) else
                ("users/%s" % text[0]))
            r = "<>" if subcat == "PRIVMSG" else "--"
            with self.openlog(p) as f:
                self.writelog(f, "%s%s%s %s" % (
                    r[0], self.server.nick, r[1], text[1]
                    ))
        elif cat == "chat":
            if not text[1][0]:
                return
            p = (("channels/%s" % text[0])
                if self.server.ischannel(text[0]) else
                ("users/%s" % text[1][0]))
            r = "<>" if subcat == "PRIVMSG" else "--"
            with self.openlog(p) as f:
                self.writelog(f, "%s%s%s %s" % (
                    r[0], text[1][0], r[1], text[2]
                    ))

bot.register.module(Module)