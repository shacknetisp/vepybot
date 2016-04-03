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

        self.addcommand(
            self.urlshorten,
            "urlshorten",
            "Shorten a url using is.gd",
            ["-shorturl=custom ending", "-service=is.gd or v.gd", "url"]
        )

    def title(self, context, args):
        try:
            r = self.server.rget("http.url").request(args.getstr("url"),
                                                     timeout=4)
        except self.server.rget("http.url").Error:
            return "Error while trying to read that url."
        p = LinksParser()
        p.feed(r.read())
        p.close()
        return p.data[-1] if p.data else "No title found."

    def urlshorten(self, context, args):
        args.default("service", "is.gd")
        args.default("shorturl", "")
        shorturl = args.getstr("shorturl")
        service = args.getstr("service")
        if service in ['v.gd', 'is.gd']:
            params = {
                "url": args.getstr("url"),
                "format": "simple",
                "shorturl": shorturl
            }
            serviceurl = "http://" + service + "/create.php"
            http = self.server.rget("http.url")
            try:
                r = http.request(serviceurl,
                                 timeout=4,
                                 params=params)
            except http.HTTPError as error:
                r = error
            return r.read().decode("utf-8")
        else:
            return "Service must be is.gd or v.gd."


bot.register.module(Module)
