# -*- coding: utf-8 -*-
# Games & Amusement
import bot
from . import piglatin, chatbot, fortune
[bot.reload(x) for x in [piglatin, chatbot, fortune]]
