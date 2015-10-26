# -*- coding: utf-8 -*-
import bot


class M_List(bot.Module):

    index = "list"

    def register(self):

        self.addcommand(
            self.list,
            "list",
            "List modules or, if <module> is specified, commands in a module, "
            "<module> can be * for all commands.",
            ["[module]..."])

    def list(self, context, args):
        args.default("module", "")
        m = args.getstr("module")
        if m:
            if m == "*":
                x = []
                for m in self.server.modules:
                    x += [(("%s %s" % (m, x))
                           if len(self.server.numcommands[x]) > 1 else x)
                          for x in self.server.modules[m].commands]
                return "%s" % (', '.join(sorted(x)))
            if m not in self.server.modules:
                return "'%s' is not a loaded module." % m
            return ("%s" % (', '.join(
                self.server.modules[m].commands)) or
                "This module has no commands.")
        else:
            mkeys = sorted(list(self.server.modules.keys()))
            n = []
            for m in mkeys:
                m = self.server.modules[m]
                if not m.hidden:
                    n.append(m.index)
            return "%s" % (', '.join(n))

bot.register.module(M_List)
