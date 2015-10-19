# -*- coding: utf-8 -*-
import bot
from html.parser import HTMLParser


class LinksParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.recording = 0
        self.data = []

    def handle_starttag(self, tag, attributes):
        if tag != 'title':
            return
        if self.recording:
            self.recording += 1
            return
        self.recording = 1

    def handle_endtag(self, tag):
        if tag == 'title' and self.recording:
            self.recording -= 1

    def handle_data(self, data):
        if self.recording:
            self.data.append(data)


class Module(bot.Module):

    index = "url"

    def register(self):

        self.addcommand(
            self.title,
            "title",
            "Get the title of a url.",
            ["url"])

    def title(self, context, args):
        try:
            r = self.server.rget("http.url").request(args.getstr("url"))
        except self.server.rget("http.url").Error:
            return "Error while trying to read that url."
        p = LinksParser()
        p.feed(r.read())
        p.close()
        return p.data[-1] if p.data else "No title found."


bot.register.module(Module)