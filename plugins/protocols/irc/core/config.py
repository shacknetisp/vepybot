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
            ("Act on a channel config entry, requires channel op." +
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

        ct = {
            'channels': {
                args.getstr('channel'): self.server.settings.channeltree
            }
        }

        xname = ('channels.%s.' % args.getstr('channel')) + name
        x = lambda x: self.server.settings.getchannel(
            x, args.getstr('channel'))
        return self._core(action,
                          xname, name, value,
                          x,
                          [],
                          ct, checkuser=False)

bot.register.module(M_Config)
