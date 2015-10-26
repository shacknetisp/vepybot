# -*- coding: utf-8 -*-
import bot
import urllib.request
import json
from deps import socks
from deps.sockshandler import SocksiPyHandler
import urllib.parse
import socket


class HTTPURL:

    def __init__(self, module):
        self.module = module
        self.server = module.server

    class Response:

        def __init__(self, content):
            self.headers = dict(content.headers)
            self.content = content.read()

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
                body=None, headers={}, timeout=None):
            if params:
                if code == "GET":
                    url += '?' + urllib.parse.urlencode(params)
                elif code == "POST":
                    if body is None:
                        body = urllib.parse.urlencode(params).encode()
                    else:
                        url += '?' + urllib.parse.urlencode(params)

            def maker():
                req = urllib.request.Request(url)
                if 'User-agent' not in headers:
                    req.add_header('User-agent',
                        'python-vepybot-net/%s' % bot.version.version)
                for r in headers:
                    req.add_header(r, headers[r])
                try:
                    if self.socks():
                        o = urllib.request.build_opener(
                            SocksiPyHandler(socks.SOCKS5,
                                            self.socks()[0], self.socks()[1]))
                        return self.Response(o.open(req, data=body,
                                                    timeout=timeout))
                    else:
                        return self.Response(urllib.request.urlopen(
                            req, data=body, timeout=timeout))
                except socket.timeout:
                    raise self.TimeoutError()
                except urllib.error.URLError:
                    raise self.ResolveError()
            try:
                return maker()
            except ValueError:
                url = "http://%s" % url
                return maker()

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
