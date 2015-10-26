import bot


class Module(bot.Module):

    index = 'safeshare'

    def register(self):

        self.addcommand(
            self.safeshare,
            "safeshare",
            "Generate safeshare.tv link for YouTube and Vimeo videos.",
            ["[-description=description]", "[-title=title]", "[-end=end]",
             "[-start=start]", "url"]
        )

    def safeshare(self, context, args):

        payload = {
            'url': args.getstr('url'),
        }
        if 'title' in args:
            payload['title'] = args.getstr('title')
        if 'description' in args:
            payload['description'] = args.getstr('description')
        if 'start' in args:
            payload['start'] = int(args.getstr('start'))
        if 'end' in args:
            payload['end'] = int(args.getstr('end'))
        http = self.server.rget('http.url')
        response = http.request('http://safeshare.tv/api/generate',
                                code="GET", params=payload, body=None,
                                headers={}, timeout=None).json()
        return "%s" % ("http://safeshare.tv/v/" +
                       response['data'][0]['safeshare_id'])
