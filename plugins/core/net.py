# -*- coding: utf-8 -*-
import bot
import httplib2
import json
from lib import socklock
import socket
import urllib.parse


class HTTPURL:

    def __init__(self, module):
        self.module = module
        self.server = module.server

    class Response:

        def __init__(self, content):
            self.headers = content[0]
            self.content = content[1]

        def raw(self):
            return self.content

        def read(self):
            return self.raw().decode()

        def json(self):
            return json.loads(self.read())

    def socks(self):
        try:
            s = self.server.settings.get('net.socksproxy').split(':')
            return (s[0], int(s[1]))
        except:
            return None

    def request(self, url, code="GET", params={},
        body="", headers={}, timeout=None):
            if params:
                if code == "GET":
                    url += '?' + urllib.parse.urlencode(params)
                elif code == "POST":
                    body = urllib.parse.urlencode(params)
            with socklock.lock(httplib2, self.socks()):
                try:
                    http = httplib2.Http(timeout=timeout)
                    try:
                        return self.Response(http.request(url,
                            code, body=body, headers=headers))
                    except httplib2.RelativeURIError:
                        url = "http://%s" % url
                        return self.Response(http.request(url,
                            code, body=body, headers=headers))
                except socket.timeout:
                    raise self.TimeoutError()
                except httplib2.ServerNotFoundError:
                    raise self.ResolveError()

    class Error(Exception):
        pass

    class TimeoutError(Error):
        pass

    class ResolveError(Error):
        pass


class Module(bot.Module):

    index = "core_net"
    hidden = True

    def register(self):

        self.addserversetting('net.socksproxy', '')
        self.serverset("http.url", HTTPURL(self))

bot.register.module(Module)