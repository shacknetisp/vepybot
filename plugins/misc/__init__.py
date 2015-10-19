# -*- coding: utf-8 -*-
# Various utility commands.
import bot
from . import calc, chatbot, define
[bot.reload(x) for x in [calc, chatbot, define]]