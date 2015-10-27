[![Code Climate](https://codeclimate.com/github/shacknetisp/vepybot/badges/gpa.svg)](https://codeclimate.com/github/shacknetisp/vepybot)

## Vepybot

Vepybot is independent of protocol, with most functionality added by plugins.
By default it includes an IRC plugin, as well as a minimal `plainsocket` plugin for basing other protocol plugins on.

### Quick Start
Copy config.py.example in userdata to config.py and run with `python3 run.py`.

### [Guide](doc/guide.md)
There is an introduction to Vepybot [here](doc/guide.md).

### Proxy Support
Vepybot's IRC protocol can connect via a SOCKS5 proxy (i.e. Tor), and all it's HTTP functions can also have a SOCKS5 proxy applied.

### Red Eclipse
Vepybot comes with a `redeclipse` plugin that adds support for [Red Eclipse](http://redeclipse.net) IRC relays, as well as reading from [Redflare](https://github.com/stainsby/redflare), a server list for Red Eclipse master servers.
