# -*- coding: utf-8 -*-
# Internet utility commands.
import bot
from . import ip, url, safeshare
[bot.reload(x) for x in [ip, url, safeshare]]
