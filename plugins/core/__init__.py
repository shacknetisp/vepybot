# -*- coding: utf-8 -*-
import bot
from . import loader, help, list, echo, net
from . import versions, settings, more, vepy, logger
[bot.reload(x) for x in [loader, help, list, net,
                         echo, versions, settings, more, vepy, logger]]
