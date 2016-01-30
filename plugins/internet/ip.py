# -*- coding: utf-8 -*-
import bot
import socket


def is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False

    return True


def is_valid_ipv6_address(address):
    try:
        socket.inet_pton(socket.AF_INET6, address)
    except socket.error:  # not a valid address
        return False
    return True


def getiphost(http, inhost):
    ip = inhost
    try:
        if not is_valid_ipv6_address(ip) and not is_valid_ipv4_address(ip):
            ip = ""
            r = http.request(
                "https://dns-api.org/A/%s" % inhost, timeout=2).json()[0]
            if 'error' not in r and r['value']:
                ip = r['value']
    except ValueError:
        pass
    except http.Error:
        pass
    return ip


def hostinfo(http, inhost, l='en'):
    ip = getiphost(http, inhost)
    if not ip:
        return {}
    try:
        geoip = http.request(
            "http://geoip.nekudo.com/api/%s/full" % ip, timeout=2).json()
    except http.Error:
        geoip = {}
    except ValueError:
        geoip = {}
    ret = {
        'ip': ip,
    }
    if geoip:
        subdivisions = []
        if 'subdivisions' in geoip:
            for sd in geoip['subdivisions']:
                subdivisions.append({
                    'code': sd['iso_code'],
                    'name': sd['names'][l],
                })

        def add(k, k2):
            d = geoip
            try:
                for kv in k2:
                    d = d[kv]
                ret[k] = d
            except KeyError:
                pass
        add('timezone', ['location', 'time_zone'])

        add('city', ['city', 'names', l])
        add('postalcode', ['postal', 'code'])

        add('country', ['country', 'names', l])
        add('countrycode', ['country', 'iso_code'])

        add('continent', ['continent', 'names', l])
        add('continentcode', ['continent', 'code'])
        ret.update({
            'regions': subdivisions,
        })
        if subdivisions:
            ret['region'] = subdivisions[0]['name']
            ret['regioncode'] = subdivisions[0]['code']
    return ret


class M_IP(bot.Module):

    index = "ip"

    def register(self):

        self.addcommand(
            self.ip,
            "ip",
            "Get information about an IP or Hostname. Space-delimited values."
            "Lookup Values: ip, city, region[code], "
            "country[code], continent[code]",
            ["ip", "[lookups]..."])
        self.addcommandalias("ip", "geoip")
        self.serverset('ip.lookup', hostinfo)

    def ip(self, context, args):
        args.default("lookups", "ip city region country")
        info = hostinfo(self.server.rget("http.url"), args.getstr("ip"))
        if info is None:
            return "Unable to resolve that host."
        out = []
        lookups = args.getstr("lookups").split()
        for l in lookups:
            if l in info and type(info[l]) in [str, int]:
                if len(lookups) == 1:
                    out.append(str(info[l]))
                else:
                    out.append("%s: %s" % (l, str(info[l])))
        return ', '.join(out) or "No results."


bot.register.module(M_IP)
