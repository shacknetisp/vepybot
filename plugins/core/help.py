# -*- coding: utf-8 -*-
import bot


class M_Help(bot.Module):

    index = "help"

    def register(self):

        self.addcommand(
            self.help,
            "help",
            "Get help for a command.",
            ["command..."])

        self.server.gethelp = self.gethelp

    def gethelp(self, command):
        args = []
        for a in command['args']:
            r = a['name']
            if a['full']:
                r += "..."
            if a['kv']:
                r = '-' + r
            else:
                r = "<%s>" % r
            if a['optional']:
                r = "[%s]" % r
            args.append(r)
        return (' '.join(args), command['help'])

    def help(self, context, args):
        split = args.getstr("command").split()
        for k, v in self.server.commands:
            for splitc in [
                    [v[0].plugin] + [v[0].index] + v[1]['name'].split(),
                    [v[0].index] + v[1]['name'].split(),
                    v[1]['name'].split()]:
                    if splitc == split[:len(splitc)]:
                        return "%s %s: %s" % (
                            ' '.join(splitc),
                            self.server.gethelp(v[1])[0],
                            self.server.gethelp(v[1])[1])
        return "That command doesn't exist."

bot.register.module(M_Help)