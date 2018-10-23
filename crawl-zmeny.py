import scrapy
from functools import partial
from operator import methodcaller


strip_all = partial(map, methodcaller('strip'))


class Zmeny:
    def set_possible_validity(self, val):
        split_val = val.split('.')
        if len(split_val) != 3:
            return
        self.validity = '{2}-{1:0>2}-{0:0>2}'.format(*map(int, split_val))

    possible_validity = property(None, set_possible_validity)

    def __init__(self):
        self.validity = None
        self.zmeny = []
        self.last_trida = None

    def add(self, trida, hodina, predmet, skupina, mistnost, akce, ucitel, pozn):
        if trida:
            self.last_trida = trida
        else:
            trida = self.last_trida
        hodina = int(hodina.split('.')[0])
        o = dict(locals())
        del o['self']
        self.zmeny.append(o)

    def add_ucitel(self, ucitel, hodina, akce, predmet, trida, mistnost, comment):
        self.add(ucitel, hodina, trida, '', mistnost, akce, predmet, comment)



class ZmenySpider(scrapy.Spider):
    name = '1VT-zmeny-crawler'
    custom_settings = {
        'USER_AGENT': '1VT-zmeny-crawler',
        'DOWNLOAD_DELAY': 3}
    start_urls = ['https://www.spseol.cz/data/rozvrhy/suplobec.htm']

    def parse(self, response):
        all_zmeny = [Zmeny()]
        for val in response.css('body > p.textlarge_3::text'):
            all_zmeny[-1].possible_validity = val.extract().split()[-1]
            if all_zmeny[-1].validity:
                all_zmeny.append(Zmeny())

        for i, supltrid in enumerate(response.css('table.tb_supltrid_3')):
            for tr in supltrid.css('tr:not(:first-child)'):
                all_zmeny[i].add(*strip_all(tr.css('td ::text').extract()))

        for i, suplucit in enumerate(response.css('table.tb_suplucit_3')):
            for tr in suplucit.css('tr:not(:first-child)'):
                all_zmeny[i].add_ucitel(*strip_all(tr.css('td ::text').extract()))

        for zmeny in all_zmeny:
            if zmeny.validity:
                yield {
                    'valid': zmeny.validity,
                    'zmeny': zmeny.zmeny}
