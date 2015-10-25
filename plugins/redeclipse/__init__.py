# -*- coding: utf-8 -*-
# Red Eclipse (http://redeclipse.net) support.
import bot
from . import REirc, redflare, restatsdb
[bot.reload(x) for x in [REirc, redflare, restatsdb]]
