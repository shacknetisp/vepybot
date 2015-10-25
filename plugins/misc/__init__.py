# -*- coding: utf-8 -*-
# Various utility commands.
import bot
from . import calc, chatbot, lookup
[bot.reload(x) for x in [calc, chatbot, lookup]]
