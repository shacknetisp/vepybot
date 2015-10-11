# -*- coding: utf-8 -*-
import bot
import lib.config
bot.reload(lib.config)


class M_Config(lib.config.Module):

    ignore = ["channels"]

    def register(self):
        lib.config.Module.register(self)

bot.register.module(M_Config)