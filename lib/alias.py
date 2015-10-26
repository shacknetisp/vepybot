# -*- coding: utf-8 -*-
import bot
from lib import parser
bot.reload(parser)
import string


class Module(bot.Module):

    index = "alias"

    def register(self):

        self.addserversetting("server.=aliases", {})

        self.server.addhook("command", "command", self.command)

        self.server.addrights({
            "alias": ["admin"],
        })

    def _add(self, aliases, alias, content):
        if alias in aliases:
            return "That alias already exists."
        aliases[alias] = content
        return "Set alias %s to: %s" % (alias, aliases[alias])

    def _get(self, aliases, alias):
        if alias in aliases:
            return aliases[alias]
        else:
            return "That alias does not exist in the config."

    def _remove(self, aliases, alias):
        if alias in aliases:
            content = aliases[alias]
            del aliases[alias]
            return "Removed %s, contained: %s" % (alias, content)
        else:
            return "That alias does not exist in the config."

    def getalias(self, context, alias, argtext=None):
        if argtext is not None:
            sections, sectiond = self.server.splitparse(argtext, context)
        adata = []
        fullalias = ""
        idx = 0
        escaped = False
        avar = None
        quoted = None
        avari = 0
        try:
            cchar = alias[idx]
        except IndexError:
            cchar = None
        while cchar is not None:
            if not escaped and cchar == parser.escape:
                escaped = True
            elif escaped:
                if cchar in ["%s%s$" % (parser.escape,
                             parser.quotes)]:
                        fullalias += cchar
                        escaped = False
                else:
                    fullalias += cchar
                    escaped = False
            elif avar is None and cchar == '$':
                avar = ""
            elif avar is not None:
                if cchar == '*':
                    if argtext is not None:
                        fullalias += ' '.join(sections[avari:])
                    adata.append('full')
                    avar = None
                elif cchar in string.digits:
                    avar += cchar
                elif cchar == '@':
                    if argtext is not None:
                        try:
                            fullalias += sections[avari - 1] + ' '
                            avari += 1
                        except IndexError:
                            pass
                    adata.append('optional')
                    avar = None
                else:
                    try:
                        num = int(avar)
                    except ValueError:
                        num = 0
                    if num and argtext is not None:
                        try:
                            avari = num
                            fullalias += sections[avari - 1] + ' '
                            avari += 1
                        except IndexError:
                            return "$%d doesn't exist." % num
                    adata.append(num)
                    avar = None
            elif not quoted and cchar in parser.quotes:
                quoted = cchar
            elif quoted:
                if cchar == quoted:
                    quoted = None
                else:
                    fullalias += cchar
            else:
                fullalias += cchar
            idx += 1
            cchar = alias[idx] if idx in range(len(alias)) else None
        return fullalias.strip(), adata

    def _command(self, context, text, aliases, help):
        split = text.split()
        for k, v in list(aliases.items()):
            for splitc in [[k]]:
                if splitc == split[:len(splitc)]:
                    argtext = ' '.join(split[len(splitc):])
                    if help:
                        return "An alias: " + v
                    r = self.getalias(context, v, argtext)
                    if isinstance(r, str):
                        return None, r
                    return self.server.runcommand(context, r[0])
        return None, None
