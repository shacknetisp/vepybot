#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import bot
import sys
from lib import db
from threading import Thread
import time
import imp

fatal = False
threads = []


def runserver(server):
    global fatal
    while bot.run:
        try:
            time.sleep(0.05)
            server.dotimers()
            server.run()
        except:
            print("Fatal Exception!")
            import traceback
            traceback.print_exc()
            fatal = True
    server.shutdown()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        bot.userdata = sys.argv[1]
    bot.createuserdata()
    initial = True
    while True:
        bot.importmodule("%s/config.py" % bot.userdata, r=not initial)
        initial = False
        bot.run = True
        if bot.threads:
            print("Starting threads...")
            for server in bot.runningservers:
                t = Thread(target=runserver, args=(server,))
                t.daemon = True
                t.start()
                threads.append(t)
            while True:
                if fatal:
                    sys.exit(1)
                time.sleep(0.05)
                with db.lock:
                    db.saveall()
                if not bot.run:
                    for thread in threads:
                        thread.join()
                    imp.reload(db)
                    imp.reload(bot)
                    print('Restarting...')
                    break
        else:
            print("Running unthreaded...")
            while bot.run:
                for server in bot.runningservers:
                    server.dotimers()
                    server.run()
                db.saveall()
            imp.reload(db)
            imp.reload(bot)
            print('Restarting...')