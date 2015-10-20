# -*- coding: utf-8 -*-
# Internet utility commands.
import bot
from . import ip, url, ddg
[bot.reload(x) for x in [ip, url, ddg]]