# -*- coding: utf-8 -*-
import bot
from . import loader, help, list, echo, versions, settings, more, vepy
[bot.reload(x) for x in [loader, help, list,
    echo, versions, settings, more, vepy]]