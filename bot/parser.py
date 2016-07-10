# -*- coding: utf-8 -*-
from lib import parser
from .exceptions import *


class ParserBase:

    def splitparse(self, text, context=None, quote=True):
        sections = []
        sectiond = {}
        sectione = {}
        idx = 0
        try:
            cchar = text[idx]
        except IndexError:
            return sections, sectiond
        section = ""
        escaped = False
        quoted = None
        running = False
        runningsection = ""
        rlevel = 0
        while cchar is not None:
            if not escaped and cchar == parser.escape:
                escaped = True
                if not section:
                    sectiond[len(sections)] = "cooked"
            elif escaped:
                section += cchar
                escaped = False
            elif not quoted and cchar == parser.run[0]:
                if not running:
                    runningsection = section
                    section = ""
                    running = True
                else:
                    section += cchar
                rlevel += 1
            elif not quoted and cchar == parser.run[1]:
                rlevel -= 1
                if running and rlevel == 0:
                    c = section
                    section = self.runcommand(context, section)[0]
                    if section is None:
                        raise ParserBadCommand("Failed running: {%s}" % c)
                    section = runningsection + section
                    running = False
                else:
                    section += cchar
            elif (not quoted and cchar in
                parser.quotes and not running and quote):
                quoted = cchar
                if not section:
                    sectiond[len(sections)] = "cooked"
            elif quoted and not running and quote:
                if cchar == quoted:
                    quoted = None
                    if not section:
                        sectione[len(sections)] = True
                else:
                    section += cchar
            else:
                if cchar == ' ' and not running:
                    if section or len(sections) in sectione:
                        sections.append(section)
                    section = ""
                else:
                    section += cchar
            idx += 1
            cchar = text[idx] if idx in range(len(text)) else None
        if section or len(sections) in sectione:
            sections.append(section)
        section = ""
        return sections, sectiond

    def makeargdict(self, argtext, context, v, quote=True):
        sections, sectiond = self.splitparse(argtext, context, quote)
        parsedargs = {}
        args = [a for a in v[1]['args'] if not a['kv']]
        kvargs = [a for a in v[1]['args'] if a['kv']]
        argi = 0
        sectioni = 0
        while sectioni in range(len(sections)):
            st = sections[sectioni]
            sd = sectiond[sectioni] if sectioni in sectiond else ""
            done = False
            if sd != "cooked":
                for prefix in sorted(parser.paramprefixes,
                                    key=lambda x: -len(x)):
                    if st.startswith(prefix):
                        param = st[len(prefix):]
                        name = param.split('=')[0]
                        if name in [a['name'] for a in kvargs]:
                            try:
                                parsedargs[name] = param.split('=')[1]
                            except IndexError:
                                parsedargs[name] = ""
                            done = True
                        break
            if not done and argi in range(len(args)):
                arg = args[argi]
                if arg['optional']:
                    if arg['recognizer'](st):
                        parsedargs[arg['name']] = st
                    else:
                        argi += 1
                        if argi in range(len(args)):
                            arg = args[argi]
                if arg['full']:
                    parsedargs[arg['name']] = ' '.join(
                        sections[sectioni:]
                    )
                    argi = len(args)
                else:
                    parsedargs[arg['name']] = st
                argi += 1
            sectioni += 1
        return parsedargs