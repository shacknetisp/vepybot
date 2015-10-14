#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import bot
import sys
from lib import db
from threading import Thread
import time

fatal = False


def runserver(server):
    global fatal
    while True:
        try:
            time.sleep(0.05)
            server.dotimers()
            server.run()
        except:
            print("Fatal Exception!")
            import traceback
            traceback.print_exc()
            fatal = True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        bot.userdata = sys.argv[1]
    bot.createuserdata()
    bot.importmodule("%s/config.py" % bot.userdata)
    if bot.threads:
        print("Starting threads...")
        for server in bot.runningservers:
            t = Thread(target=runserver, args=(server,))
            t.daemon = True
            t.start()
        while True:
            if fatal:
                sys.exit(1)
            time.sleep(0.05)
            with db.lock:
                db.saveall()
    else:
        print("Running unthreaded...")
        while True:
            for server in bot.runningservers:
                server.dotimers()
                server.run()
            db.saveall()