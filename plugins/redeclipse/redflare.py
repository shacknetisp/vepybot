# -*- coding: utf-8 -*-
import bot
import requests
import time
import re
from lib import timeutils
bot.reload(timeutils)


class RedFlare:

    def __init__(self, url, timeout=5):
        j = requests.get(url, timeout=timeout).json()
        self.servers = []
        self.players = []
        self.playerauths = []
        for serverkey in j:
            server = j[serverkey]
            serverdata = {
                'id': serverkey,
                'host': server['host'],
                'port': server['port'],
                'mode': server['gameMode'],
                'mutators': server['mutators'],
                'time': server['timeLeft'],
                'map': server['mapName'],
                'version': server['gameVersion'],
                'description': server['description'],
                'players': [],
                'playerauths': [],
                }
            index = 0
            for playerName in server['playerNames']:
                serverdata['players'].append(playerName['plain'])
                try:
                    serverdata['playerauths'].append([playerName['plain'],
                        server['authNames'][index]['plain']])
                except KeyError:
                    pass
                self.players.append(playerName['plain'])
                try:
                    self.playerauths.append([playerName['plain'],
                            server['authNames'][index]['plain']])
                except KeyError:
                    pass
                index += 1
            self.servers.append(serverdata)


class Module(bot.Module):

    index = "redflare"

    def register(self):
        self.lastseendb = self.getdb("lastseen")
        self.cache = {}
        self.addsetting('redflares', [])
        self.addtimer(self.docache, 'cachetimer', 60 * 1000)

        self.addcommand(self.search, "search",
            "See if a player is online.",
            ["url", "[-auth]", "[-regex]", "[search...]"])

        self.addcommand(self.lastseen, "lastseen",
            "See when a player was last on.",
            ["url", "[-auth]", "[-regex]", "[search...]"])

    def checkurl(self, url):
        if url not in self.getsetting('redflares'):
            return "That url is not registered."
        if url not in self.cache or url not in self.lastseendb.d:
            self.docache()
        if url not in self.cache or url not in self.lastseendb.d:
            return "Unable to contact url."

    def docache(self):
        for url in self.getsetting('redflares'):
            self.server.log('REDFLARE', url)
            rf = RedFlare(url, timeout=3 if url in self.cache else 8)
            if url not in self.lastseendb.d:
                self.lastseendb.d[url] = {}
            d = self.lastseendb.d[url]
            for player in rf.players:
                if player:
                    d['=' + player] = time.time()
            for player in rf.playerauths:
                if player[1]:
                    d['+' + player[1]] = time.time()
            self.cache[url] = rf
        self.lastseendb.save()

    def search(self, context, args):
        args.default("search", "")
        search = args.getstr("search")
        if not args.getbool("regex"):
            search = ".*" + re.escape(search) + ".*"
        e = self.checkurl(args.getstr('url'))
        if e:
            return e
        rf = self.cache[args.getstr('url')]
        ret = []
        for server in rf.servers:
            s = []
            l = (server['playerauths']
                if args.getbool('auth')
                else server['players'])
            for p in l:
                if type(p) in (tuple, list):
                    p = p[1]
                if p:
                    if re.match(search, p,
                        re.IGNORECASE) is not None or p == args.getstr(
                            "search"):
                                s.append(p)
            if s:
                d = server['description']
                d = d[:d.rindex(' [')]
                ret.append(("%s: %s" % (d, '; '.join(s)),
                    len(s)))
        context.reply('\n'.join([r[0] for r in sorted(ret,
            key=lambda x: -x[1])]) or "No results.", more=True)
        return ""

    def lastseen(self, context, args):
        args.default("search", "")
        search = args.getstr("search")
        if not args.getbool("regex"):
            search = ".*" + re.escape(search) + ".*"
        e = self.checkurl(args.getstr('url'))
        if e:
            return e
        d = self.lastseendb.d[args.getstr('url')]
        s = {}
        for p in d:
            v = d[p]
            if ((args.getbool('auth') and p[0] == '+')
                or (not args.getbool('auth') and p[0] == '=')):
                    p = p[1:]
                    if p:
                        if re.match(search, p,
                            re.IGNORECASE) is not None or p == args.getstr(
                                "search"):
                                    s[p] = v
        if not s:
            return "No results."
        p = sorted(s, key=lambda x: -s[x])[0]
        return "%s: %s -- %s ago." % (p,
            time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(s[p])),
            timeutils.agostr(s[p]))
bot.register.module(Module)