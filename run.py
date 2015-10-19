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
    global run
    run = False
    bot.run = False


def hup_handler(signal, frame):
    bot.run = False


def runserver(server):
    global fatal
    while bot.run:
        try:
            time.sleep(0.05)
            with server.runlock:
                with db.lock:
                    server.dotimers()
            with server.runlock:
                with db.lock:
                    server.corerun()
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
    for s in [
        signal.SIGINT,
        signal.SIGTERM,
        signal.SIGQUIT,
        ]:
            signal.signal(s, signal_handler)
    signal.signal(signal.SIGHUP, hup_handler)
    while run:
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
                bot.httpserver.run()
                with db.lock:
                    db.saveall()
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
                    try:
                        server.dotimers()
                        server.corerun()
                    except InterruptedError:
                        pass
                bot.httpserver.run()
                db.saveall()
            for server in bot.runningservers:
                server.shutdown()
            imp.reload(db)
            imp.reload(bot)