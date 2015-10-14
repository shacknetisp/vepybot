# -*- coding: utf-8 -*-
import bot


class M_IP(bot.Module):

    index = "ip"

    def register(self):

        self.addcommand(
            self.ip,
            "ip",
            "Get information about an IP.",
            ["ip", "[values]..."])

    def ip(self, context, args):
        import time
        time.sleep(10)
        return "Done!"

bot.register.module(M_IP)