# -*- coding: utf-8 -*-
import bot
import uuid
import fnmatch
import time


class Module(bot.Module):

    index = "memo"

    def register(self):
        self.db = self.getdb("memo")
        self.addsetting('#inchannel', True)
        self.addcommand(self.memo, 'send',
            'Send a memo to a user. Target can be an idstring or nick glob.',
            ['target', 'message...'])
        self.addcommandalias('send', 'memo')
        self.addcommandalias('send', 'tell')
        self.addcommand(self.delete, 'delete',
            'Delete a memo by ID.', ['id'])
        self.addhook('whois.found', 'whoisfound', self.whoisfound)

    def memo(self, context, args):
        target = args.getstr('target')
        if '!' not in target:
            #An IRC idstring must have !, so this is a nick.
            target = '%s!*' % target
        message = args.getstr('message')
        mid = uuid.uuid4().hex[:12]
        self.db.d[mid] = {
            'from': context.user[0],
            'target': target,
            'message': message,
            'channel': context.channel,
            'time': time.time(),
            }
        self.db.save()
        context.replypriv(
            'You can delete that memo with: memo delete %s' % mid)
        return 'Sent memo to %s: %s' % (target, message)

    def whoisfound(self, nick, idstring, whois):
        tod = []
        for mid in sorted(self.db.d, key=lambda x: self.db.d[x]['time']):
            memo = self.db.d[mid]
            if fnmatch.fnmatch(idstring.lower(), memo['target'].lower()):
                tod.append(mid)
                command = 'NOTICE' if self.server.settings.getchannel(
                        'irc.notice', memo['channel']) else 'PRIVMSG'
                ch = self.getchannelsetting(
                        'inchannel', memo['channel'])
                text = "From %s to you: %s" % (memo['from'], memo['message'])
                if memo['channel'] in whois.channels and ch:
                    text = "From %s to %s: %s" % (
                        memo['from'], nick, memo['message'])
                    self.server.sendto(command, memo['channel'], text)
                else:
                    self.server.sendto(command, nick, text)

        for d in tod:
            self.db.d.pop(d)
            self.db.save()

    def delete(self, context, args):
        mid = args.getstr('id')
        if mid not in self.db.d:
            return 'That memo does not exist.'
        out = "Removed memo to %s: %s" % (
            self.db.d[mid]['target'],
            self.db.d[mid]['message'])
        self.db.d.pop(mid)
        self.db.save()
        return out

bot.register.module(Module)
