#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import bot
import sys
from lib import db
from threading import Thread
import time
import imp
import signal

fatal = False
run = True
threads = []


def signal_handler(signal, frame):
    print("Caught signal, exiting.")
    global run
    run = False
    bot.run = False


def hup_handler(signal, frame):
    print('Reloading from HUP.')
    bot.run = False


def runserver(server):
    global fatal
    while bot.run:
        try:
            time.sleep(0.01)
            with server.runlock:
                with db.lock:
                    server.corerun()
            with server.runlock:
                with db.lock:
                    server.dotimers()
        except:
            print("Fatal Exception!")
            import traceback
            traceback.print_exc()
            fatal = True
    server.shutdown()

if __name__ == "__main__":
    initial = True
    for s in [
        signal.SIGINT,
        signal.SIGTERM,
    ]:
        signal.signal(s, signal_handler)
    if hasattr(signal, "SIGHUP"):
        signal.signal(signal.SIGHUP, hup_handler)
    while run:
        if len(sys.argv) > 1:
            bot.userdata = sys.argv[1]
        bot.createuserdata()
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
                    bot.run = False
                    run = False
                with db.lock:
                    db.saveall()
                time.sleep(0.01)
                if not bot.run:
                    for thread in threads:
                        thread.join()
                    imp.reload(db)
                    imp.reload(bot)
                    break
        else:
            print("Running unthreaded...")
            while bot.run:
                for server in bot.runningservers:
                    server.corerun()
                    server.dotimers()
                db.saveall()
                time.sleep(0.01)
            for server in bot.runningservers:
                server.shutdown()
            imp.reload(db)
            imp.reload(bot)
