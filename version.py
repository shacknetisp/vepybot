# -*- coding: utf-8 -*-
import platform
version = "0.2.17"
name = "Vepybot"
namever = "%s %s" % (name, version)
platformtuple = (name, version, "Python %s on %s (%s)" % (
    platform.python_version(),
    platform.system(),
    platform.release()
))
source = "https://github.com/shacknetisp/vepybot"
