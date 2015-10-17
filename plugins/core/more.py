# -*- coding: utf-8 -*-
import bot


class M_More(bot.Module):

    index = "more"

    def register(self):

        self.server.more = {}

        self.addcommand(
            self.clear,
            "clear",
            "Clear your more queue.", [])

        self.addcommand(
            self.more,
            "more",
            "Get the next message in your more queue.", [])

    def more(self, context, args):
        if context.idstring() in self.server.more:
            try:
                m = (self.server.more[context.idstring()].pop(0))
                if self.server.more[context.idstring()]:
                    l = len(self.server.more[context.idstring()])
                    m += (' ' +
                    context.moretemplate.format(n=l,
                    s=('s' if l != 1 else '')))
                context.reply(m, more=False)
                return ''
            except IndexError:
                pass
        return 'No more messages.'

    def clear(self, context, args):
        if context.idstring() in self.server.more:
            self.server.more.pop(context.idstring())
        return 'Cleared all messages.'

bot.register.module(M_More)