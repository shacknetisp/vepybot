# -*- coding: utf-8 -*-
import bot
from . import loader, help, list, echo, versions, settings
[bot.reload(x) for x in [loader, help, list, echo, versions, settings]]