# -*- coding: utf-8 -*-
import bot
import os
import time


class Module(bot.Module):

    index = "core_logger"
    hidden = True

    def register(self):

        self.addhook('log', 'log', self.log)
        self.serverset('openlog', self.openlog)
        self.serverset('writelog', self.writelog)
        self.addserversetting("logger.enabled", True)
        self.server.settings.add("logger.enabled", True)
        self.addserversetting("logger.localtime", True)
        self.server.settings.add("logger.localtime", True)
        with self.openlog("bot", 'w'):
            pass

    def openlog(self, path, m='a'):
        fullpath = "%s/servers/%s/logs/%s" % (
            bot.userdata,
            self.server.name,
            path
        )
        os.makedirs(os.path.dirname(fullpath), exist_ok=True)
        return open(fullpath, m)

    def writelog(self, f, text):
        t = (
            time.localtime()
                if self.server.settings.get('logger.localtime')
                else time.gmtime()
        )
        timestr = time.strftime("%Y-%m-%d %H:%M:%S", t)
        f.write("[%s] %s\n" % (timestr, text.strip()))

    def log(self, cat, subcat, text):
        if not self.server.settings.get('logger.enabled'):
            return
        if cat == "bot":
            with self.openlog("bot") as f:
                self.writelog(f, "[%s] %s" % (subcat, text))

bot.register.module(Module)
