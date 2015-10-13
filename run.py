#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import bot
import sys
from lib import db
if __name__ == "__main__":
    if len(sys.argv) > 1:
        bot.userdata = sys.argv[1]
    bot.createuserdata()
    bot.importmodule("%s/config.py" % bot.userdata)
    while True:
        for server in bot.runningservers:
            server.dotimers()
            server.run()
        db.saveall()