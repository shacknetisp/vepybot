# -*- coding: utf-8 -*-
import bot
from lib import timeutils
bot.reload(timeutils)


class Module(bot.Module):

    index = "restatsdb"

    def register(self):
        self.addcommand(self.main, 'get',
                        'Query a statsdb-interface API.'
                        ' Actions: toprace <map>, game <id>, totals',
                        ['url', 'action', '[query...]'])
        self.addcommand(self.alias, 'alias',
                        'Return the text for a restatsdb alias.', ["url"])

    def alias(self, context, args):
        return "restatsdb get %s $*" % (args.getstr('url'))

    def main(self, context, args):
        action = args.getstr('action')
        http = self.server.rget('http.url')
        actionurl = None
        if action == "toprace":
            actionurl = "/maps/%s" % args.getstr('query')
        elif action == "game":
            actionurl = "/games/%s" % args.getstr('query')
        elif action == "totals":
            try:
                jgames = http.request(
                    args.getstr('url') + '/get/games').json()
                jservers = http.request(
                    args.getstr('url') + '/get/servers').json()
                jmaps = http.request(
                    args.getstr('url') + '/get/maps').json()
                jplayers = http.request(
                    args.getstr('url') + '/get/players').json()
            except http.Error:
                return "Unable to contact API."
            except ValueError:
                return "Invalid API response."
            return "Games: %d, Maps: %d, Servers: %d, Players: %d" % (
                len(jgames),
                len(jmaps),
                len(jservers),
                len(jplayers),
            )
        else:
            return "Invalid action."
        try:
            json = http.request(args.getstr('url') + '/get' + actionurl).json()
        except http.Error:
            return "Unable to contact API."
        except ValueError:
            return "Invalid API response."
        if 'error' in json:
            return json['error']
        if action == 'toprace':
            if 'toprace' not in json:
                return 'No top race results for %s.' % args.getstr('query')
            return "%s by %s" % (
                timeutils.durstr(json['toprace']['time'] / 1000,
                                 dec=True, full=True).strip(),
                ("%s playing as %s" % (
                    json['toprace']['gameplayer']['handle'],
                    json['toprace']['gameplayer']['name'])
                    if json['toprace']['gameplayer']['handle']
                    else
                    "<no auth> playing as %s" % (
                    json['toprace']['gameplayer']['name']))
            )
        elif action == 'game':
            f = {
                'players': len(json['players']),
                'mode': ['Demo', 'Editing', 'DM',
                         'CTF', 'DAC', 'BB', 'Race'][json['mode']],
            }
            return str("Game {g[id]}: {x[mode]} on {g[map]},"
                       " players: {x[players]},"
                       " server: {g[server]}").format(g=json, x=f)

bot.register.module(Module)
