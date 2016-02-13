# -*- coding: utf-8 -*-
import bot
import fnmatch


class Module(bot.Module):

    index = "autoop"

    def register(self):
        self.w = {}
        self.tmpw = {}
        self.addsetting('#enabled', True)
        self.addhook("join", "join", self.join)
        self.addhook("recv", "recv", self.recv)
        self.addtimer(self.timer, 'timer', 20 * 1000)
        self.addcommand(
            self.auto,
            "autoop",
            "Modify a channel's +w mode list. autoop add/remove o/v *@host",
            ["[channel]", "operation", "mode", "mask"],
            recognizers={'channel': self.server.ischannel})
        self.addcommand(
            self.autolist,
            "autoop list",
            "View a channel's +w list.",
            ["[channel]"],
            recognizers={'channel': self.server.ischannel})

    def autolist(self, context, args):
        if context.channel:
            args.default("channel", context.channel)
        context.exceptrights([args.getstr('channel') + ",op"])
        w = (self.w[args.getstr("channel")]
            if args.getstr("channel") in self.w else [])
        out = []
        for x in w:
            out.append("%s:%s" % (x["level"], x["glob"]))
        return ", ".join(out) or "No results."

    def auto(self, context, args):
        if context.channel:
            args.default("channel", context.channel)
        context.exceptrights([args.getstr('channel') + ",op"])
        insert = {
            "level": args.getstr("mode")[0],
            "glob": args.getstr("mask"),
        }
        if args.getstr("channel") not in self.server.channels:
            return "The bot is not joined there."
        names = self.server.channels[args.getstr("channel")].names
        if self.server.nick not in names or 'o' not in names[self.server.nick]:
            return "The bot does not have sufficient elevation."
        inw = (args.getstr("channel") in self.w and
            insert in self.w[args.getstr("channel")])
        if args.getstr("operation") == "add":
            if inw:
                return "That is already in the +w list."
            else:
                self.server.send("MODE %s +w %s:%s" % (
                    args.getstr("channel"), insert["level"], insert["glob"]))
                return "" if context.channel else "Done."
        elif args.getstr("operation") == "remove":
            if inw:
                self.server.send("MODE %s -w %s:%s" % (
                    args.getstr("channel"), insert["level"], insert["glob"]))
                return "" if context.channel else "Done."
            else:
                return "Cannot find that in the +w list."

        return "The operation must be add or remove."

    def join(self, channel, user):
        if not self.getchannelsetting('enabled', channel):
            return
        self.server.send("MODE %s +w" % channel)

    def timer(self):
        for channel in self.server.channels:
            if not self.getchannelsetting('enabled', channel):
                return
            self.server.send("MODE %s +w" % channel)

    def recv(self, context):
        if context.code(910) or context.code(911):
            channel = context.rawsplit[3]
            if not self.getchannelsetting('enabled', channel):
                return
            if channel not in self.tmpw:
                self.tmpw[channel] = []
            if context.code(910):
                mode = context.rawsplit[4]
                try:
                    self.tmpw[channel].append({
                        "level": mode.split(":", 1)[0],
                        "glob": mode.split(":", 1)[1],
                        })
                except IndexError:
                    pass
            elif context.code(911):
                self.w[channel] = self.tmpw[channel]
                self.tmpw[channel] = []
                channel = self.server.channels[channel]
                for nick in channel.names:
                    if nick not in self.server.whois:
                        continue
                    whois = self.server.whois[nick]
                    hostmask = "%s!%s@%s" % (nick, whois.ident, whois.host)
                    for o in self.w[channel.name]:
                        if fnmatch.fnmatch(hostmask, o["glob"]):
                            if o["level"] not in channel.names[nick]:
                                self.server.send("MODE %s +%s %s" % (
                                    channel.name,
                                    o["level"],
                                    nick
                                ))
        elif context.code("MODE"):
            if not self.getchannelsetting('enabled', context):
                return
            if context.rawsplit[3] in ["+w", "-w"]:
                self.server.send("MODE %s +w" % context.channel)


bot.register.module(Module)
