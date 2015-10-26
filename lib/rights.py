# -*- coding: utf-8 -*-
import bot
import fnmatch


class Module(bot.Module):

    index = "rights"

    def register(self):

        self.addcommand(
            self.getrights_c,
            "get",
            "Get the rights of a user, defaults to yourself.",
            ["[-matches]", "[idstring]"])

        self.addcommand(
            self.setright,
            "set",
            "Set a right on user.",
            ["idstring", "right"])

        self.addcommand(
            self.unsetright,
            "unset",
            "Unset a right on user.",
            ["idstring", "right"])

        self.server.getrights = self.getrights
        self.addserversetting("server.=rights", {})

        self.server.addrights({
            "owner": [""],
            "admin": ["owner"],
            "-": ["owner"],
            "ignore": ["owner"],
        })

    def _getrights(self, idstring, context=None):
        rightlist = self.server.settings.get("server.rights")
        rights = (["owner"]
                  if fnmatch.fnmatch(idstring,
                                     self.server.opt('owner')) else [])
        matches = []
        for r in rightlist:
            if fnmatch.fnmatch(idstring, r):
                if rightlist[r]:
                    matches.append(r)
                rights += rightlist[r]
        if context:
            cr = self._contextrights(idstring, context)
            rights += cr[0]
            matches += cr[1]
        return rights, matches

    def getrights(self, *args):
        return self._getrights(*args)[0]

    def setright(self, context, args):
        ids = args.getstr("idstring")
        r = args.getstr("right")
        rightlist = self.server.settings.get("server.rights")
        if ids not in rightlist:
            rightlist[ids] = []
        if r in rightlist[ids]:
            return "%s already has %s." % (ids, r)
        if r not in self.server.righttypes and not r.startswith('-'):
            return "%s is not a valid right." % r
        if r.startswith('-'):
            required = self.server.righttypes['-'] + ['owner']
        else:
            required = self.server.righttypes[r] + ['owner']
        for required in required:
            if context.checkright(required):
                rightlist[ids].append(r)
                self.server.settings.set("server.rights", rightlist)
                return "Set %s on %s" % (r, ids)
        return "You do not have the rights to do that."

    def unsetright(self, context, args):
        ids = args.getstr("idstring")
        r = args.getstr("right")
        rightlist = self.server.settings.get("server.rights")
        if ids not in rightlist:
            rightlist[ids] = []
        if r not in rightlist[ids]:
            return "%s does not have that right." % (ids)
        if r.startswith('-'):
            required = self.server.righttypes['-'] + ['owner']
        else:
            required = self.server.righttypes[r] + ['owner']
        for required in required:
            if context.checkright(required):
                rightlist[ids] = [x for x in rightlist[ids] if x != r]
                if not rightlist[ids]:
                    rightlist.pop(ids)
                self.server.settings.set("server.rights", rightlist)
                return "Unset %s from %s" % (r, ids)
        return "You do not have the rights to do that."

    def getrights_c(self, context, args):
        gcontext = context if "idstring" not in args.d else None
        args.default("idstring", context.idstring())
        if args.getbool("matches"):
            return "%s (%s): %s" % (args.getstr("idstring"),
                                    ' '.join(
                                        self._getrights(
                                            args.getstr(
                                                "idstring"), gcontext)[1]),
                                    ' '.join(self.server.getrights(args.getstr("idstring"), gcontext)))
        return "%s: %s" % (args.getstr("idstring"), ' '.join(
            self.server.getrights(args.getstr("idstring"), gcontext)))
