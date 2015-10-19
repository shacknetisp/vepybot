# -*- coding: utf-8 -*-
import bot
import requests


class Module(bot.Module):

    index = 'define'

    def register(self):
        self.addcommand(self.ud, 'urbandictionary',
            'Look up a term in Urban Dictionary.', ['term...'])
        self.addcommandalias('urbandictionary', 'ud')

    def ud(self, context, args):
        term = args.getstr('term')
        try:
            r = requests.get('http://api.urbandictionary.com/v0/define',
                params={'term': term}).json()
        except:
            return "Unable to contact the urbandictionary.com api."
        possible = []
        first = ""
        final = ""
        for entry in r['list']:
            definition = entry['definition']
            if not first:
                first = definition
            if entry['example']:
                definition += " | %s" % entry['example']
            if entry['thumbs_up'] / max(entry['thumbs_down'], 1) > 5:
                possible.append(definition)
        if not possible:
            final = first
        else:
            for p in sorted(possible, key=lambda x: len(x)):
                if len(p) < self.server.opt('charlimit') - 40:
                    final = p
                    break
            if not final:
                final = first
        final = ' '.join(final.split())
        return final or "No definition found."

bot.register.module(Module)