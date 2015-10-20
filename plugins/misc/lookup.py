# -*- coding: utf-8 -*-
import bot
import html
import re
tag_re = re.compile(r'<.*?>.*?<\/.*?>')


class Module(bot.Module):

    index = 'lookup'

    def register(self):

        self.addcommand(self.ud, 'ud',
            'Look up a term in Urban Dictionary.', ['term...'])

        self.addcommand(self.ddg, "ddg",
            "Look up something on Duck Duck Go. "
            "http://duckduckgo.com",
            ["query..."])

    def ddg(self, context, args):
        query = args.getstr('query')
        http = self.server.rget('http.url')
        try:
            r = http.request("http://api.duckduckgo.com/", params={
                "q": query,
                "format": 'json',
                "t": bot.version.name.lower(),
                "no_redirect": 1,
                "no_html": 1,
                }).json()
        except http.Error:
            return "Cannot contact the Duck Duck Go API."
        except ValueError:
            return "Invalid response from the Duck Duck Go API."
        if r['AbstractText']:
            if r['Results']:
                return "[%s] %s" % (r['Results'][0]['FirstURL'],
                    html.unescape(r['AbstractText']))
        elif r['AnswerType'] == 'calc':
            return "%s" % tag_re.sub('', r['Answer'])
        elif r['RelatedTopics']:
            return "[%s] %s" % (r['RelatedTopics'][0]['FirstURL'],
                    ' '.join(tag_re.sub('',
                    r['RelatedTopics'][0]['Result']).split()))
        elif r['Redirect']:
            return "%s" % r['Redirect']
        return "No results."

    def ud(self, context, args):
        http = self.server.rget('http.url')
        term = args.getstr('term')
        try:
            r = http.request('http://api.urbandictionary.com/v0/define',
                params={'term': term}, timeout=4).json()
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