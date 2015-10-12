# -*- coding: utf-8 -*-
import bot
import lib.config
bot.reload(lib.config)


class M_Config(lib.config.Module):

    ignore = ["channels"]

    def register(self):
        lib.config.Module.register(self)

        self.addcommand(
            self.channelconfig,
            "channel config",
            ("Act on a channel config entry." +
            " (list, get, reset, set, add, remove)"),
            ["[channel]", "action", "name", "value..."],
            recognizers={'channel': self.server.ischannel})

    def channelconfig(self, context, args):
        if context.channel:
            args.default("channel", context.channel)

        action = args.getstr("action")
        args.default("name", "")
        name = args.getstr("name")
        value = ""
        if action in ["set", "add", "remove"]:
            value = args.getstr("value")

        context.exceptrights([args.getstr('channel') + ",op"])

        d = {}
        try:
            d = self.server.settings.tree['channels']
            [args.getstr('channel')]
        except KeyError:
            pass

        ct = {
            'channels': {
                    args.getstr('channel'): self.server.settings.channeltree
                }
            }

        xname = ('channels.%s.' % args.getstr('channel')) + name

        return self._core(action,
            xname, name, value,
            lambda x: self.server.settings.getchannel(x,
                args.getstr('channel')),
            [],
            dict(list(d.items()) + list(
            ct.items())))

bot.register.module(M_Config)