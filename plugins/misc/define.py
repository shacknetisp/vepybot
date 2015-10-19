# -*- coding: utf-8 -*-
import bot


class Module(bot.Module):

    index = 'define'

    def register(self):
        self.addcommand(self.ud, 'urbandictionary',
            'Look up a term in Urban Dictionary.', ['term...'])
        self.addcommandalias('urbandictionary', 'ud')

    def ud(self, context, args):
        http = self.server.rget('http.url')
        term = args.getstr('term')
        try:
            r = http.request('http://api.urbandictionary.com/v0/define',
                params={'term': term}).json()
        except http.Error:
            return "Unable to contact the urbandictionary.com api."
        except ValueError:
            return "Invalid response from the urbandictionary.com api."
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