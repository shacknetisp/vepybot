# -*- coding: utf-8 -*-
import bot
import lib.rights
bot.reload(lib.rights)
import fnmatch


class M_Rights(lib.rights.Module):

    def register(self):
        lib.rights.Module.register(self)

        self.addserverchannelsetting("=crights", {})

        self.addcommand(
            self.setcright,
            "set channel",
            "Set a channel right on user.",
            ["[channel]", "idstring", "right"],
            recognizers={'channel': self.server.ischannel})

        self.addcommand(
            self.unsetcright,
            "unset channel",
            "Unset a channel right on user.",
            ["[channel]", "idstring", "right"],
            recognizers={'channel': self.server.ischannel})

        self.righttypes = {
            'op': ['op'],
            'v': ['op'],
            '-': ['op'],
            'ignore': ['op'],
        }
        self.serverset('addchannelrights',
                       lambda r: self.righttypes.update(r))
        self.server.globalaliases.update({
            'idhost': 'echo irc:*@$*!*',
            'idauth': 'echo irc:*!$*',
        })

    def _contextrights(self, idstring, context):
        rights = []
        matches = []
        if context.channel:
            rightlist = self.server.settings.getchannel("crights", context)
            for r in rightlist:
                if fnmatch.fnmatch(idstring, r):
                    if rightlist[r]:
                        matches.append(r)
                    rights += [context.channel + "," + r for r in rightlist[r]]
        for c in context.whois.channels:
            modes = context.whois.channels[c]
            if 'o' in modes:
                rights += [c + ',' + 'op']
            elif 'v' in modes:
                rights += [c + ',' + 'v']
        return rights, matches

    def channelgetrequired(self, r):
        required = []
        if r.startswith('-'):
            required = self.righttypes['-'] + ['op']
        else:
            required = self.righttypes[r] + ['op']
        return required

    def setcright(self, context, args):
        args.default("channel", context.channel)
        channel = args.getstr("channel")
        if not channel:
            return "That channel does not exist."
        ids = args.getstr("idstring")
        r = args.getstr("right")
        rightlist = self.server.settings.getchannel("crights", channel)
        if ids not in rightlist:
            rightlist[ids] = []
        if r in rightlist[ids]:
            return "%s already has %s." % (ids, r)
        if r not in self.righttypes and not r.startswith('-'):
            return "%s is not a valid right." % r
        required = self.channelgetrequired(r)
        for required in required:
            required = channel + ',' + required
            if context.checkright(required) or context.checkright("owner"):
                rightlist[ids].append(r)
                self.server.settings.save()
                return "Set %s on %s" % (r, ids)
        return "You do not have the rights to do that."

    def unsetcright(self, context, args):
        args.default("channel", context.channel)
        channel = args.getstr("channel")
        if not channel:
            return "That channel does not exist."
        ids = args.getstr("idstring")
        r = args.getstr("right")
        rightlist = self.server.settings.getchannel("crights", channel)
        if ids not in rightlist:
            rightlist[ids] = []
        if r not in rightlist[ids]:
            return "%s does not have that right." % (ids)
        required = self.channelgetrequired(r)
        for required in required:
            required = channel + ',' + required
            if context.checkright(required) or context.checkright("owner"):
                rightlist[ids] = [x for x in rightlist[ids] if x != r]
                if not rightlist[ids]:
                    rightlist.pop(ids)
                self.server.settings.save()
                return "Unset %s from %s" % (r, ids)
        return "You do not have the rights to do that."

bot.register.module(M_Rights)
