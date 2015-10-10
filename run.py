#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import bot
from lib import db
if __name__ == "__main__":
    bot.importmodule("%s/config" % bot.userdata)
    while True:
        for server in bot.runningservers:
            server.dotimers()
            server.run()
        db.saveall()