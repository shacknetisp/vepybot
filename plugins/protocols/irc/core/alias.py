# -*- coding: utf-8 -*-
import bot
import lib.alias
bot.reload(lib.alias)


class M_Alias(lib.alias.Module):

    def register(self):
        lib.alias.Module.register(self)

        self.addcommand(
            self.get,
            "get",
            "Get an alias.",
            ["[channel]", "alias"],
            recognizers={'channel': self.server.ischannel})

        self.addcommand(
            self.add,
            "add",
            "Add an alias.",
            ["[channel]", "alias", "content..."],
            recognizers={'channel': self.server.ischannel})

        self.addcommand(
            self.remove,
            "remove",
            "Remove an alias.",
            ["[channel]", "alias"],
            recognizers={'channel': self.server.ischannel})

        self.addcommand(
            self.show,
            "list",
            "List aliases.",
            ["[channel]"],
            recognizers={'channel': self.server.ischannel})

        self.addserversetting("server.=#aliases", {})
        self.addserverchannelsetting("aliases", {})

    def show(self, context, args):
        args.default("channel", "")
        l = list(self.server.settings.get("server.aliases").keys()) + (
            list(self.server.globalaliases.keys()))
        if args.getstr("channel"):
            l = list(self.server.settings.getchannel(
                    "aliases", args.getstr("channel")).keys())
        return ", ".join(l) or "No aliases."

    def get(self, context, args):
        args.default("channel", "")
        alias = args.getstr('alias')
        if args.getstr("channel"):
            return "[%s] %s" % (args.getstr("channel"),
                self._get(self.server.settings.getchannel(
                "aliases", args.getstr("channel")),
                alias))
        else:
            return "%s" % (self._get(self.server.settings.get("server.aliases"),
                alias))

    def command(self, context, text, responses, help):
        if context.channel:
            r = self._command(context, text,
                self.server.settings.getchannel("server.aliases", context),
                help)
            if r[0] is not None or r[1] is not None:
                responses.append(r)
                return
        responses.append(self._command(context, text,
            self.server.settings.get("server.aliases"), help))
        responses.append(self._command(context, text,
            self.server.globalaliases, help))

    def add(self, context, args):
        args.default("channel", "")
        args.default("content", "")
        alias = args.getstr('alias')
        content = args.getstr('content')
        if args.getstr("channel"):
            context.exceptchannelrights(['alias'])
            ret = "[%s] %s" % (args.getstr("channel"),
                self._add(
                self.server.settings.getchannel('server.aliases',
                    args.getstr("channel")),
                alias, content))
            return ret
        else:
            context.exceptrights(["admin", "alias"])
            ret = "%s" % (self._add(self.server.settings.get("server.aliases"),
                alias, content))
            self.server.settings.save()
            return ret

    def remove(self, context, args):
        args.default("channel", "")
        alias = args.getstr('alias')
        if args.getstr("channel"):
            context.exceptchannelrights(['op', 'alias'])
            ret = "[%s] %s" % (args.getstr("channel"),
                self._remove(
                self.server.settings.getchannel("server.aliases",
                    args.getstr("channel")),
                alias))
            self.server.settings.save()
            return ret
        else:
            context.exceptrights(["admin", "alias"])
            ret = "%s" % (self._remove(
                self.server.settings.get("server.aliases"),
                alias))
            self.server.settings.save()
            return ret

bot.register.module(M_Alias)