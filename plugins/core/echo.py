# -*- coding: utf-8 -*-
import bot


class M_Echo(bot.Module):

    index = "echo"

    def register(self):

        self.addcommand(
            self.echo,
            "echo",
            "Echo text.",
            ["[text]..."])

    def echo(self, context, args):
        args.default("text", "")
        return "%s" % (args.getstr("text"))

bot.register.module(M_Echo)
