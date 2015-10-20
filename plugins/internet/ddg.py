# -*- coding: utf-8 -*-
import bot
import html
import re
tag_re = re.compile(r'<.*?>.*?<\/.*?>')


class Module(bot.Module):

    index = "ddg"

    def register(self):
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
                "t": bot.versionname.lower(),
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

bot.register.module(Module)