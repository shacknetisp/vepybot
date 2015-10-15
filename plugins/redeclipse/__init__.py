# -*- coding: utf-8 -*-
import bot
from . import REirc, redflare
[bot.reload(x) for x in [REirc, redflare]]


class Module(bot.Module):

    index = "redeclipse"
    hidden = True

    def register(self):
        pass


bot.register.module(Module)