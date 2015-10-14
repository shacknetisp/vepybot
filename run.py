#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import bot
import sys
from lib import db
from threading import Thread
import time


def runserver(server):
    while True:
        time.sleep(0.05)
        server.dotimers()
        server.run()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        bot.userdata = sys.argv[1]
    bot.createuserdata()
    bot.importmodule("%s/config.py" % bot.userdata)
    print("Starting threads...")
    for server in bot.runningservers:
        t = Thread(target=runserver, args=(server,))
        t.daemon = True
        t.start()
    while True:
        time.sleep(0.05)
        with db.lock:
            db.saveall()