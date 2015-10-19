# -*- coding: utf-8 -*-
from datetime import datetime
from wsgiref.simple_server import make_server, WSGIRequestHandler
import time
import sys
import urllib.parse
import bot
import select


class httpd:

    def __init__(self):
        pass

    def __call__(self, environ, start_response):
        sys.stdout.write(((datetime.now().strftime('%D %T')
        + ': ' + environ['REMOTE_ADDR']
        + ': ' + environ['PATH_INFO'] + '?' + environ['QUERY_STRING']).strip()
        + '...'))
        result = b"404 Not Found"
        headers = [('Content-type', 'text/plain')]
        status = "404 Not Found"
        t = time.time()
        paths = environ['PATH_INFO'].split('/')
        params = urllib.parse.parse_qs(environ['QUERY_STRING'], True)
        try:
            for server in bot.runningservers:
                if paths and paths[0] == server.name:
                    with server.runlock:
                        responses = []
                        server.dohook('corehttp',
                            paths[1:], params, environ, responses)
                        if responses:
                            start_response(responses[0][0], responses[0][1])
                            sys.stdout.write('...done [%f]\n' % (
                                time.time() - t))
                            return [responses[0][2]]
        except:
            import traceback
            status = "500 Internal Error"
            headers = [('Content-type', 'text/plain')]
            result = b"500 Internal Error"
            print((traceback.format_exc()))
        sys.stdout.write('...done [%f]\n' % (time.time() - t))
        start_response(status, headers)
        return [result]


class httphandler (WSGIRequestHandler):

    def log_message(self, format, *args):
        pass


server = None


def start(host, port):
    global server
    server = make_server(host, port, httpd(), handler_class=httphandler)


def run():
    if select.select([server], [], [], 0.1)[0]:
        server.handle_request()