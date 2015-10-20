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


def hostinfo(http, inhost, l='en', rdns=False):
    ip = inhost
    host = inhost
    try:
        if not is_valid_ipv6_address(ip) and not is_valid_ipv4_address(ip):
            r = http.request(
                "http://api.statdns.com/%s/a" % inhost, timeout=2).json()
            if 'error' not in r and r['answer']:
                ip = r['answer'][0]['rdata']
        if rdns:
            r = http.request(
                "http://api.statdns.com/x/%s" % ip, timeout=2).json()
            if 'error' not in r and r['answer']:
                host = r['answer'][0]['rdata'].rstrip('.')
    except ValueError:
        pass
    except http.Error:
        pass
    try:
        geoip = http.request(
            "http://geoip.nekudo.com/api/%s/full" % ip, timeout=2).json()
    except http.Error:
        geoip = {}
    except ValueError:
        geoip = {}
    ret = {
        'ip': ip,
        'host': host,
        }
    if geoip:
        subdivisions = []
        for sd in geoip['subdivisions']:
            subdivisions.append({
                'code': sd['iso_code'],
                'name': sd['names'][l],
                })
        ret.update({
            'continent': geoip['continent']['names'][l],
            'continentcode': geoip['continent']['code'],

            'country': geoip['country']['names'][l],
            'countrycode': geoip['country']['iso_code'],

            'city': geoip['city']['names'][l],

            'timezone': geoip['location']['time_zone'],

            'regions': subdivisions,
            })
        try:
            ret.update({
                'postalcode': geoip['postal']['code'],
                })
        except KeyError:
            pass
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
            "Values: ip, host, city, region[code], "
            "country[code], continent[code]",
            ["ip", "[values]..."])
        self.addcommandalias("ip", "geoip")

    def ip(self, context, args):
        args.default("values", "ip city region country")
        info = hostinfo(self.server.rget("http.url"), args.getstr("ip"),
            rdns='host' in args.getstr("values").split())
        if info is None:
            return "Unable to resolve that host."
        out = []
        values = args.getstr("values").split()
        for v in values:
            if v in info and type(info[v]) in [str, int]:
                if len(values) == 1:
                    out.append(str(info[v]))
                else:
                    out.append("%s: %s" % (v, str(info[v])))
        return ', '.join(out) or "No results."


bot.register.module(M_IP)