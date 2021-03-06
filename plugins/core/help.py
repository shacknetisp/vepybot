# -*- coding: utf-8 -*-
import bot


class M_Help(bot.Module):

    index = "help"

    def register(self):

        self.addcommand(
            self.help,
            "help",
            "Get help for a command.",
            ["[command...]"])

        self.server.gethelp = self.gethelp

    def gethelp(self, command):
        args = []
        for a in command['args']:
            r = a['name']
            if a['full']:
                r += "..."
            if a['kv']:
                r = '-' + r
                if 'kvtext' in a:
                    r += '=<' + a['kvtext'] + '>'
            else:
                r = "<%s>" % r
            if a['optional']:
                r = "[%s]" % r
            args.append(r)
        return (' '.join(args), command['help'])

    def help(self, context, args):
        if "command" not in args:
            return ("Use 'help <command>' for command usage, " +
                "'list <module>' to find commands, and " +
                "'list' to find modules. " +
                "For more information: 'help list'")
        split = args.getstr("command").split()
        commands = self.server.commandlist()
        commands.sort(key=lambda x: -len(x[0]))

        #Return function, add note about modules if they match.
        def ret(s):
            if args.getstr("command") in self.server.modules:
                return "%s (Use 'list %s' if you want the module.)" % (
                    s,
                    args.getstr("command"),
                    )
            return s

        #Find command, return help.
        for splitc, v in commands:
            if splitc == split[:len(splitc)]:
                if len(splitc) == 1:
                    if len(self.server.numcommands[splitc[0]]) > 1:
                        return ret(
                            "Use <module> %s, %s" % (
                                splitc[0], splitc[0]) +
                            " is provided by multiple modules: %s" % (
                                ', '.join(self.server.numcommands[splitc[0]])
                            ))
                if self.server.gethelp(v[1])[0]:
                    return ret("%s %s: %s" % (
                        ' '.join(splitc),
                        self.server.gethelp(v[1])[0],
                        self.server.gethelp(v[1])[1]))
                else:
                    return ret("%s: %s" % (
                        ' '.join(splitc),
                        self.server.gethelp(v[1])[1]))
        #Handle "commands" registered by modules (like aliases).
        responses = []
        self.server.dohook('command', context, args.getstr("command"),
                           responses, True)
        for r in responses:
            if r and isinstance(r, str):
                return ret(r)
        return ret("That command doesn't exist.")

bot.register.module(M_Help)
