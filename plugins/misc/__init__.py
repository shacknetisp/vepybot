# -*- coding: utf-8 -*-
# Various utility commands.
import bot
from . import calc, lookup
[bot.reload(x) for x in [calc, lookup]]
