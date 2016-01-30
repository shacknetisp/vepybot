# -*- coding: utf-8 -*-
import bot
import subprocess
import shutil


class Module(bot.Module):

    index = "fortune"

    def register(self):

        self.addcommand(
            self.fortune,
            "fortune",
            "Get a fortune from the UNIX fortune program.", [])

    def fortune(self, context, args):
        if not shutil.which("fortune"):
            return "No fortune program here."
        return ' '.join(
            subprocess.check_output(["fortune", "-s"]
            ).decode().strip().replace(
                "\t", " ").replace("\n", " ").split())

bot.register.module(Module)
