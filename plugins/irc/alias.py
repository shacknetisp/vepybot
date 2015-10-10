# -*- coding: utf-8 -*-
import bot
import lib.alias


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

    def get(self, context, args):
        args.default("channel", "")
        alias = args.getstr('alias')
        if args.getstr("channel"):
            pass
        else:
            return "%s" % (self._get(alias))

    def command(self, context, text, responses):
        if context.channel:
            pass
        responses.append(self._command(context, text,
            self.server.settings.get("aliases")))

    def add(self, context, args):
        args.default("channel", "")
        args.default("content", "")
        alias = args.getstr('alias')
        content = args.getstr('content')
        if args.getstr("channel"):
            context.needchannelrights(['op', 'alias'])
            pass
        else:
            context.needrights(["admin", "alias"])
            return "%s" % (self._add(alias, content))

    def remove(self, context, args):
        args.default("channel", "")
        alias = args.getstr('alias')
        if args.getstr("channel"):
            context.needchannelrights(['op', 'alias'])
            pass
        else:
            context.needrights(["admin", "alias"])
            return "%s" % (self._remove(alias))

bot.register.module(M_Alias)