# -*- coding: utf-8 -*-
from threading import Lock


class lock:

    def __init__(self, module, sock):
        self.module = module
        self.sock = sock

    def __enter__(self):
        import socks
        if not hasattr(self.module, '_vepy_socklock'):
            self.module._vepy_socklock = Lock()
        self.module._vepy_socklock.acquire()
        if self.sock:
            socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5,
                self.sock[0], self.sock[1])
        else:
            socks.setdefaultproxy()
        socks.wrapmodule(self.module)

    def __exit__(self, _1, _2, _3):
        import socks
        socks.setdefaultproxy()
        socks.wrapmodule(self.module)
        self.module._vepy_socklock.release()