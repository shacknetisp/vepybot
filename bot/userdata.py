# -*- coding: utf-8 -*-
import os
userdata = 'userdata'


def createuserdata():
    for d in [
            'servers',
            'shared',
            'plugins',
    ]:
            os.makedirs(userdata + '/' + d, exist_ok=True)
    open('%s/plugins/__init__.py' % userdata, 'w')