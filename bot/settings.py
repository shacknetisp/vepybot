# -*- coding: utf-8 -*-
from lib import db
from .userdata import userdata
import os
import copy
import fnmatch


class Settings:

        """Indicator Characters."""
        idents = '.=~'
        """Module search glob, {m} is replaced with the module name."""
        mglob = ['modules.{m}.*']

        def __init__(self, server):
            os.makedirs("%s/servers/%s" % (userdata, server.name),
                        exist_ok=True)
            os.makedirs("%s/shared/%s" % (userdata, server.shared),
                        exist_ok=True)
            self.db = db.DB("servers/%s/settings.json" % server.name)
            self.d = self.db.d
            self.defaults = {}
            self.user = []
            self.tree = {}

        def isdefault(self, n, v):
            """Determine if a setting <n> with value <v>
            is set to it's default."""
            pass

        def purge(self, m):
            """Purge module <m> from the settings DB."""
            c = 0
            tod = []
            for v in self.d:
                for g in self.mglob:
                    if fnmatch.fnmatch(v, g.format(m=m)):
                        c += 1
                        tod.append(v)
                        break
            for d in tod:
                self.d.pop(d)
            self.save()
            return c

        def pop(self, n):
            """Pop <n> from the DB."""
            r = self.d.pop(n)
            self.save()
            return r

        def get(self, n, pop=False):
            """Return the setting <n> or it's default."""
            if n not in self.d:
                self.d[n] = copy.deepcopy(self.defaults[n])
                ret = self.d[n]
                if type(ret) not in [list, dict] or pop:
                    self.d.pop(n)
                return ret
            return self.d[n]

        def branchdict(self, d, ss):
            s = None
            while ss:
                s = ss.pop(0)
                if s not in d:
                    d[s] = {}
                d = d[s]
            return d

        def addbranch(self, ss, n, rm=False):
            """Add <ss> to the tree with name <n>."""
            ss = copy.deepcopy(ss)
            d = self.tree
            d = self.branchdict(d, ss)
            if n.strip(self.idents) in d and rm:
                d.pop(n.strip(self.idents))
            d[n] = True

        def set(self, n, v):
            """Set <n> to <v>, adding it to the tree if neccessary."""
            split = n.split('.')
            sections = split[:-1]
            basen = split[-1]
            truename = '.'.join(sections + [basen.strip(self.idents)])
            self.d[truename] = v
            self.addbranch(sections, basen)
            self.save()

        def save(self):
            """Save the database, removing values set to their defaults."""
            tod = []
            for k in self.d:
                if k in self.defaults:
                    if self.d[k] == self.defaults[k]:
                        tod.append(k)
                else:
                    if self.isdefault(k, self.d[k]):
                        tod.append(k)
            for t in tod:
                self.d.pop(t)
            self.db.save()

        def add(self, n, v):
            """Add a default setting <n> with a value of <v>."""
            split = n.split('.')
            sections = split[:-1]
            basen = split[-1]
            truename = '.'.join(sections + [basen.strip(self.idents)])
            self.defaults[truename] = copy.deepcopy(v)
            if '=' not in basen and '~' not in basen:
                self.user.append(truename)
            self.addbranch(sections, basen)
            self.save()