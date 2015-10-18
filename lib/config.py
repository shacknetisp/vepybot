# -*- coding: utf-8 -*-
import bot
from lib import utils
bot.reload(utils)


class Module(bot.Module):

    index = "config"

    def register(self):

        self.addcommand(
            self.config,
            "config",
            ("Act on a config entry, requires admin." +
            " (list, get, reset, set, add, remove)"),
            ["action", "name", "value..."])

        self.addcommand(self.purge, "config purge",
            "Purge a module from the config, requires admin.", ["module"])

    def purge(self, context, args):
        context.exceptrights(["admin"])
        module = args.getstr("module")
        c = self.server.settings.purge(module)
        return "Purged %s (%d entries.)" % (module, c)

    def display(self, v):
        if type(v) in [str, int, float]:
            return str(v)
        elif type(v) is list:
            return ' '.join(v)
        elif type(v) is bool:
            return str(v)
        else:
            return str(v)

    def _core(self, action, name, vname, value,
        get, ignore, toptree, checkuser=True):
        if action == "get":
            if name not in self.server.settings.user and checkuser:
                return "You may not access '%s'" % vname
            try:
                v = get(vname)
            except KeyError:
                return "'%s' does not exist." % vname
            return "%s: %s" % (vname, self.display(v))
        elif action == "list":
            split = name.strip('.').split('.')
            if split[0] in ignore:
                return "You may not access '%s'" % vname
            out = []
            d = toptree
            while split:
                if split[0]:
                    try:
                        if type(d[split[0]]) is not dict:
                            return "'%s' is not a category." % vname
                        if d[split[0]]:
                            d = d[split[0]]
                    except KeyError:
                        return "'%s' is not a category." % vname
                split.pop(0)
            for k, v in sorted(list(d.items()), key=lambda x: x[0]):
                if '=' in k:
                    continue
                if type(v) is bool:
                    out.append('%s' % k)
                else:
                    ok = False
                    for vk in v:
                        if vk.find('=') == -1:
                            ok = True
                    if ok:
                        out.append('@%s' % k)
            if vname:
                return "%s: %s" % (vname, ' '.join(out))
            else:
                return "%s" % (' '.join(out))
        elif action == "reset":
            if name not in self.server.settings.user and checkuser:
                return "You may not access '%s'" % vname
            if name in self.server.settings.defaults:
                self.server.settings.pop(name)
                return "%s reset to: %s" % (vname, self.display(get(vname)))
            else:
                try:
                    try:
                        self.server.settings.pop(name)
                    except KeyError:
                        get(vname)
                    return "%s reset to: %s" % (vname, self.display(get(vname)))
                except KeyError:
                    return "'%s' does not exist." % vname
        elif action == "set":
            if name not in self.server.settings.user and checkuser:
                return "You may not access '%s'" % vname
            try:
                t = type(get(vname))
                if t in [str]:
                    value = str(value)
                elif t in [int, float]:
                    value = t(value)
                elif t in [list]:
                    value = str(value).split(' ')
                elif t in [bool]:
                    value = utils.boolstr(value)
                else:
                    return "Invalid type for %s." % vname
                self.server.settings.set(name, value)
                return "%s set to: %s" % (vname, self.display(get(vname)))
            except KeyError:
                return "'%s' does not exist." % vname
        elif action == "add":
            if name not in self.server.settings.user and checkuser:
                return "You may not access '%s'" % vname
            try:
                t = type(get(vname))
                if t not in [list]:
                    return "Invalid type for %s." % vname
                if value in get(vname):
                    return "Duplicate value already in %s." % vname
                self.server.settings.set(name, get(vname) + [value])
                return "%s set to: %s" % (vname, self.display(get(vname)))
            except KeyError:
                return "'%s' does not exist." % vname
        elif action == "remove":
            if name not in self.server.settings.user and checkuser:
                return "You may not access '%s'" % vname
            try:
                t = type(get(vname))
                if t not in [list]:
                    return "Invalid type for %s." % vname
                if value not in get(vname):
                    return "Value not in %s." % vname
                self.server.settings.set(name, [v for v in get(vname)
                if v != value])
                return "%s set to: %s" % (vname, self.display(get(vname)))
            except KeyError:
                return "'%s' does not exist." % vname
        else:
            return "Invalid action."

    def config(self, context, args):
        action = args.getstr("action")
        args.default("name", "")
        name = args.getstr("name")
        value = ""
        if action in ["set", "add", "remove"]:
            value = args.getstr("value")

        context.exceptrights(["admin"])

        return self._core(action, name, name, value,
            self.server.settings.get,
            self.ignore, self.server.settings.tree)

