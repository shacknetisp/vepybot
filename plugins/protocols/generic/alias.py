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
            ["alias"])

        self.addcommand(
            self.add,
            "add",
            "Add an alias.",
            ["alias", "content..."])

        self.addcommand(
            self.remove,
            "remove",
            "Remove an alias.",
            ["alias"],)

        self.addcommand(
            self.show,
            "alias list",
            "List aliases.", [])

    def show(self, context, args):
        l = list(self.server.settings.get("server.aliases").keys()) + (
            list(self.server.globalaliases.keys()))
        return ", ".join(l) or "No aliases."

    def get(self, context, args):
        alias = args.getstr('alias')
        return "%s" % (self._get(self.server.settings.get("server.aliases"),
            alias))

    def command(self, context, text, responses, help):
        responses.append(self._command(context, text,
            self.server.settings.get("server.aliases"), help))

    def add(self, context, args):
        args.default("content", "")
        alias = args.getstr('alias')
        content = args.getstr('content')
        context.exceptrights(["admin", "alias"])
        ret = "%s" % (self._add(self.server.settings.get("server.aliases"),
            alias, content))
        self.server.settings.save()
        return ret

    def remove(self, context, args):
        alias = args.getstr('alias')
        context.exceptrights(["admin", "alias"])
        ret = "%s" % (self._remove(
            self.server.settings.get("server.aliases"),
            alias))
        self.server.settings.save()
        return ret

bot.register.module(M_Alias)
