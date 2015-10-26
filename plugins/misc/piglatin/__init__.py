# -*- coding: utf-8 -*-
import bot
from . import piglatin

class Module(bot.Module):

    index = "piglatin"

    def register(self):

        self.addcommand(
            self.piglatin,
            "piglatin",
            "Translate text into pig latin. ",
            ["[text]..."])

    def piglatin(self, context, args):
        args.default("text", "")
        return "%s" % (piglatin.translate(args.getstr("text")))
                
bot.register.module(Module)
