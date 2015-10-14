# -*- coding: utf-8 -*-
import bot
import requests
import socket


def hostinfo(host, l='en'):
    try:
        ip = socket.gethostbyname(host)
        host = socket.gethostbyname_ex(host)[0]
    except socket.gaierror:
        return None
    try:
        geoip = requests.get(
            "http://geoip.nekudo.com/api/%s/full" % ip).json()
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
            'postalcode': geoip['postal']['code'],

            'timezone': geoip['location']['time_zone'],

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
            "Get information about an IP or Hostname. "
            "Values: ip, host, city, region[code], "
            "country[code], continent[code]",
            ["ip", "[values]..."])

    def ip(self, context, args):
        args.default("values", "ip,city,region,country")
        info = hostinfo(args.getstr("ip"))
        if info is None:
            return "Unable to resolve that host."
        out = []
        for v in args.getstr("values").replace(' ', '').split(','):
            if v in info and type(info[v]) in [str, int]:
                out.append("%s: %s" % (v, str(info[v])))
        return ', '.join(out) or "No results."


bot.register.module(M_IP)