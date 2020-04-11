import re

import discord

from cogs.utils.paginators import Pages


class UrbanDictionaryPages(Pages):
    BRACKETED = re.compile(r'(\[(.+?)\])')

    def __init__(self, ctx, data):
        super().__init__(ctx, entries=data, per_page=1)

    def get_page(self, page):
        return self.entries[page - 1]

    @staticmethod
    def cleanup_definition(definition, *, regex=BRACKETED):
        def repl(m):
            word = m.group(2)
            return f'[{word}](http://{word.replace(" ", "-")}.urbanup.com)'

        ret = regex.sub(repl, definition)
        if len(ret) >= 2048:
            return ret[0:2000] + ' [...]'
        return ret

    def prepare_embed(self, entry, page, *, first=False):
        if self.maximum_pages > 1:
            title = f'{entry["word"]}: {page} out of {self.maximum_pages}'
        else:
            title = entry['word']

        self.embed = e = discord.Embed(colour=0xE86222, title=title, url=entry['permalink'])
        e.set_footer(text=f'by {entry["author"]}')
        e.description = self.cleanup_definition(entry['definition'])
        e.add_field(name="Example", value=entry.get('example', 'No example given.'))

        try:
            up, down = entry['thumbs_up'], entry['thumbs_down']
        except KeyError:
            pass
        else:
            e.add_field(name='Votes', value=f'\N{THUMBS UP SIGN} {up} \N{THUMBS DOWN SIGN} {down}', inline=False)

        try:
            date = discord.utils.parse_time(entry['written_on'][0:-1])
        except (ValueError, KeyError):
            pass
        else:
            e.timestamp = date
