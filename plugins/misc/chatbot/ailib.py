# -*- coding: utf-8 -*-
import random
import string


def intorrand(t):
    if type(t) is not int:
        return random.randrange(t[0], t[1])
    else:
        return t


class AI:

    def __init__(self, db):
        self.db = db
        self.lastphrase = None

        def makeentry(n, t={}):
            if n not in self.db or type(self.db[n]) is not type(t):
                self.db[n] = t
        makeentry('phrases', [])

    def keywords(self, text):
        ret = []
        for word in text.split():
            ret.append(word)
        return ret

    def process(self, text, lastphrase=None):
        if lastphrase is not None:
            self.lastphrase = lastphrase
        for c in string.punctuation:
            text.replace(c, '')
        keywords = self.keywords(text)

        def diff(t):
            a = 0
            for kw in keywords:
                if kw in t:
                    a += 1
            return (a / len(t))
        if self.lastphrase:
            x = (self.lastphrase, text, self.keywords(self.lastphrase))
            if x not in self.db['phrases']:
                self.db['phrases'].append(x)
        self.db['phrases'].append([text])
        possible = list(filter(lambda x: len(x) == 3, self.db['phrases']))
        random.shuffle(possible)
        for i in possible:
            if i[0].lower() == text.lower():
                self.lastphrase = i[1]
                return i[1]
        try:
            out = list(reversed(sorted(possible, key=lambda x: diff(x[2]))))[
                0:max(min(round(len(possible) / 7),
                          random.randrange(1, 5)), 1)]
            out = random.choice(out)
            self.lastphrase = out[1]
            return out[1]
        except IndexError:
            pass
        out = random.choice(
            list(filter(lambda x: len(x) == 1, self.db['phrases'])))
        self.lastphrase = out[0]
        return out[0]
