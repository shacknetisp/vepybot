# -*- coding: utf-8 -*-
import textwrap
from .exceptions import *
import fnmatch


class Context:

    """Server Specific Context, implement the core functions at least."""

    moretemplate = "[{n} more message{s}]"

    def __init__(self, server):
        self.server = server

    def reply(self, m):
        """Reply with <m>."""

    def replypriv(self, m):
        """Reply privately with <m>."""
        self.reply(m)

    def idstring(self):
        """Return the idstring of the context."""
        return self.server.idstring(self)

    def checkright(self, r):
        """Check if the context has the right <r>."""
        return r in self.server.getrights(self.idstring(), self)

    def exceptrights(self, rlist, m=None):
        """Raise NoPerms exception if this context has none of the
        rights in <r>, <m> is an optional exception message."""
        if isinstance(rlist, str):
            rlist = [rlist]
        rlist = rlist + ['owner']
        for r in rlist:
            if r in self.server.getrights(self.idstring(), self):
                return True
        raise NoPerms(m or "You must have %s: %s" % (
            "this right" if len(rlist) == 1 else "one of these rights",
            '; '.join(rlist)))

    def exceptcancommand(self, module, command):
        """Call _exceptcancommand, raise NoPerms if cannot execute <command>."""
        self._exceptcancommand(module, command)

    def _exceptcancommand(self, module, command):
        if not self.checkright("admin"):
            for r in self.server.getrights(self.idstring(), self):
                if module and command:
                    if fnmatch.fnmatchcase("-%s.%s.%s" % (
                                           module.plugin,
                                           module.index, command['name']), r):
                            raise NoPerms("You may not use %s" % "%s.%s.%s" % (
                                module.plugin, module.index, command['name']))
                if r == "ignore":
                    raise NoPerms("")

    def domore(self, message):
        if not self.server.opt('charlimit'):
            return message
        messages = textwrap.wrap(message, self.server.opt('charlimit') - len(
            " " + self.moretemplate,
        ))
        message = messages[0]
        if len(messages) > 1:
            self.server.more[self.idstring()] = messages[1:]
            try:
                if self.server.more[self.idstring()]:
                    l = len(self.server.more[self.idstring()])
                    message += (' ' +
                                self.moretemplate.format(n=l,
                                                         s=('s'
                                                            if l != 1
                                                            else '')))
            except KeyError:
                pass
        return message

    def replydriver(self, f, message, more):
        if more and message.count('\n') == 0:
            message = self.domore(message)
        for message in message.split('\n'):
            messages = textwrap.wrap(message, self.server.opt('charlimit')
                                     - len('...'))
            f(messages[0] + ('...' if len(messages) > 1 else ''))
