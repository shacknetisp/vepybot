# -*- coding: utf-8 -*-
# Various utility commands.
import bot
from . import ip, calc, chatbot
[bot.reload(x) for x in [ip, calc, chatbot]]