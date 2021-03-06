# -*- coding: utf-8 -*-
import bot
import time
import re
from lib import timeutils, utils
bot.reload(timeutils)
bot.reload(utils)


class RedFlare:

    def __init__(self, url, http, timeout=5):
        j = http.request(url, timeout=timeout).json()
        self.time = time.time()
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
                    auth = server['authNames'][index]['plain']
                    serverdata['playerauths'].append([playerName['plain'],
                                                      auth])
                except KeyError:
                    pass
                self.players.append(playerName['plain'])
                try:
                    auth = server['authNames'][index]['plain']
                    self.playerauths.append([playerName['plain'],
                                             auth])
                except KeyError:
                    pass
                index += 1
            self.servers.append(serverdata)


class Module(bot.Module):

    index = "redflare"

    def register(self):
        self.lastseendb = self.getshareddb("redflare", "lastseen")
        self.cache = {}
        self.addsetting('redflares', [])
        self.addtimer(self.docache, 'cachetimer', 60 * 1000)

        self.addcommand(self.search, "search",
                        "See if a player is online.",
                        ["url",
                            "[-auth]",
                            "[-oneline]",
                            "[-regex]",
                            "[search...]"])

        self.addcommand(self.lastseen, "lastseen",
                        "See when a player was last on.",
                        ["url",
                            "[-auth]",
                            "[-regex]",
                            "[-count]",
                            "[search...]"])

        self.addcommand(self.setup, "setup", "Easy redflare setup.",
                        ['url', 'isonalias', 'wasonalias'])

        self.addcommand(self.remove, "remove", "Easy redflare removal.",
                        ['url', 'isonalias', 'wasonalias'])

    def setup(self, context, args):
        context.exceptrights(["admin"])
        url = args.getstr('url')
        ison = args.getstr('isonalias')
        wason = args.getstr('wasonalias')
        try:
            RedFlare(url, self.server.rget('http.url'))
        except Exception as e:
            return "Cannot contact url. (%s)" % (type(e).__name__)
        if url in self.getsetting('redflares'):
            return 'That URL is already registered.'
        aliases = self.server.settings.get('server.aliases')
        if ison in aliases:
            return '%s is already an alias.' % ison
        elif wason in aliases:
            return '%s is already an alias.' % wason
        self.getsetting('redflares').append(url)
        aliases[ison] = "redflare search %s $*" % (url)
        aliases[wason] = "redflare lastseen %s $*" % (url)
        self.server.settings.save()
        return "%s aliased to %s and %s" % (url, ison, wason)

    def remove(self, context, args):
        context.exceptrights(["admin"])
        url = args.getstr('url')
        ison = args.getstr('isonalias')
        wason = args.getstr('wasonalias')
        if url not in self.getsetting('redflares'):
            return 'That URL is not registered.'
        aliases = self.server.settings.get('server.aliases')
        if ison not in aliases or (aliases[ison] !=
                                   "redflare search %s $*" % (url)):
            return '%s is not the alias for this url.' % ison
        elif wason not in aliases or (aliases[ison] !=
                                      "redflare search %s $*" % (url)):
            return '%s is not the alias for this url.' % wason
        self.getsetting('redflares').pop(
            self.getsetting('redflares').index(url))
        aliases.pop(ison)
        aliases.pop(wason)
        self.server.settings.save()
        return "%s removed, with aliases %s and %s" % (url, ison, wason)

    def checkurl(self, url):
        if url not in self.getsetting('redflares'):
            return "That url is not registered."
        if url not in self.cache or url not in self.lastseendb.d:
            self.onecache(url, True)
        if url not in self.cache or url not in self.lastseendb.d:
            return "Unable to contact url."

    def onecache(self, url, ls=False, timeout=3):
        self.server.log('REDFLARE', url)
        try:
            rf = RedFlare(url, self.server.rget('http.url'),
                          timeout=timeout if url in self.cache else 4)
            self.server.log('REDFLARE DONE', url)
        except self.server.rget('http.url').Error:
            return
        except ValueError:
            return
        if url not in self.lastseendb.d:
            self.lastseendb.d[url] = {
                "names": {},
                "auths": {},
            }
        d = self.lastseendb.d[url]
        for player in rf.players:
            if player:
                d['names'][player] = time.time()
        for player in rf.playerauths:
            if player[1]:
                d['auths'][player[1]] = time.time()
        self.cache[url] = rf

    def docache(self):
        for url in self.getsetting('redflares'):
            self.onecache(url, True)
        self.lastseendb.save()

    def search(self, context, args):
        args.default("search", "")
        search = args.getstr("search")
        if not args.getbool("regex"):
            search = ".*" + re.escape(search) + ".*"
        e = self.checkurl(args.getstr('url'))
        if e:
            return e
        if time.time() - self.cache[args.getstr('url')].time > 30:
            self.onecache(args.getstr('url'), timeout=2)
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
                    if utils.imatch(p, search):
                        s.append(p)
            if s:
                d = server['description']
                # d = d[:d.rindex(' [')]
                if args.getbool('oneline'):
                    ret += s
                else:
                    ret.append(("%s: %s" % (d, '; '.join(s)),
                                len(s)))
        if args.getbool('oneline'):
            return '; '.join(sorted(ret))
        ret = '\n'.join([r[0] for r in sorted(ret,
                                              key=lambda x: -x[1])])
        context.reply(ret or "No results.", more=True)
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
        d = d['auths'] if args.getbool('auth') else d['names']
        for p in d:
            v = d[p]
            if utils.imatch(p, search):
                s[p] = v
        if not s:
            return "No results."
        if args.getbool('count'):
            return "The number of entries: %d" % len(s)
        p = sorted(s, key=lambda x: -s[x])[0]
        return "%s: %s -- %s ago." % (p,
                                      time.strftime(
                                      "%Y-%m-%d %H:%M:%S UTC",
                                      time.gmtime(s[p])),
                                      timeutils.agostr(s[p]))
bot.register.module(Module)
