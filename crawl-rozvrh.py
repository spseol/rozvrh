import scrapy
from itertools import takewhile
from operator import eq, methodcaller
from functools import partial
from pprint import pprint
from typing import Union

str_empty = partial(eq, '')
strip = methodcaller('strip', '\xa0 ')

def prep_time(t: str) -> str:
    return t.split('|')[-1].center(11)
def prep_sub(s: str) -> str:
    return s.replace('|', ' ').center(11)

def struct_sub(s: Union[str, list]) -> Union[dict, list]:
    if type(s) is list:
        return list(map(struct_sub, s))
    if '|' not in s:
        return None
    parts = s.split('|')
    if len(parts) < 4:
        parts.insert(1, None)
    return {
        'subject': parts[0],
        'group': parts[1],
        'teacher': parts[2],
        'room': parts[3]}

class Rozvrh:
    SEQ = 'times', 'mon', 'tue', 'wed', 'thu', 'fri'

    @property
    def skip(self):
        empty = takewhile(str_empty, self.times)
        return sum(1 for _ in empty)

    def __init__(self, trida = ''):
        self.trida = trida
        for key in self.SEQ:
            setattr(self, key, None)

    def add(self, line):
        if not line:
            return
        for key in self.SEQ:
            if getattr(self, key) is None:
                setattr(self, key, line)
                return

    @property
    def structured(self) -> dict:
        d = dict()
        d['trida'] = self.trida
        d['times'] = [t.split('|')[-1] for t in self.times[self.skip:]]
        for day in self.SEQ[1:]:
            d[day] = list(map(struct_sub, getattr(self, day)[self.skip:]))
        return d

    def __str__(self):
        out = []
        out.append(' '.join(map(prep_time, self.times[self.skip:])))
        for day in self.SEQ[1:]:
            out.append(' '.join(map(prep_sub, getattr(self, day)[self.skip:])))
        return '\n'.join(out)



class RowspanMerger:
    def __init__(self):
        self.rowspans = [0]
        self.final = []

    def register_rowspan(self, rs: int):
        self.rowspans.insert(0, rs)

    def add_line(self, line: list):
        if self.rowspans[-1] <= 0:
            self.rowspans.pop()
            self.final.append(line)
        else:
            self.final[-1] = list(self._merge(self.final[-1], line))
        self.rowspans[-1] -= 1

    def _merge(self, final, add):
        for i in range(min(len(final), len(add))):
            fi, ai = final[i], add[i]
            if ai in fi:
                yield final[i]
                continue
            yield [fi, ai] if type(fi) is str else [*fi, ai]


class RozvrhSpider(scrapy.Spider):
    name = '1VT-rozvrh-crawler'
    custom_settings = {
        'USER_AGENT': '1VT-rozvrh-crawler',
        'DOWNLOAD_DELAY': 3}
    start_urls = [
        'https://www.spseol.cz/data/rozvrhy/trvj.htm',
        'https://www.spseol.cz/data/rozvrhy/trvk.htm',
        'https://www.spseol.cz/data/rozvrhy/trvl.htm',
        'https://www.spseol.cz/data/rozvrhy/trvd.htm',
        'https://www.spseol.cz/data/rozvrhy/trve.htm',
        'https://www.spseol.cz/data/rozvrhy/trvf.htm',
        'https://www.spseol.cz/data/rozvrhy/trv8.htm',
        'https://www.spseol.cz/data/rozvrhy/trv9.htm',
        'https://www.spseol.cz/data/rozvrhy/trva.htm',
        'https://www.spseol.cz/data/rozvrhy/trv3.htm',
        'https://www.spseol.cz/data/rozvrhy/trv4.htm',
        'https://www.spseol.cz/data/rozvrhy/trv5.htm',
        'https://www.spseol.cz/data/rozvrhy/trvm.htm',
        'https://www.spseol.cz/data/rozvrhy/trvn.htm',
        'https://www.spseol.cz/data/rozvrhy/trvg.htm',
        'https://www.spseol.cz/data/rozvrhy/trvi.htm',
        'https://www.spseol.cz/data/rozvrhy/trvb.htm',
        'https://www.spseol.cz/data/rozvrhy/ucukfxp.htm',
        'https://www.spseol.cz/data/rozvrhy/ucul8sn.htm',
        'https://www.spseol.cz/data/rozvrhy/ucu30j8.htm',
        'https://www.spseol.cz/data/rozvrhy/ucu2fo1.htm',
        'https://www.spseol.cz/data/rozvrhy/ucuynv0.htm',
        'https://www.spseol.cz/data/rozvrhy/ucund0n.htm',
        'https://www.spseol.cz/data/rozvrhy/ucuzbn3.htm',
        'https://www.spseol.cz/data/rozvrhy/ucuzbn6.htm',
        'https://www.spseol.cz/data/rozvrhy/ucule5k.htm',
        'https://www.spseol.cz/data/rozvrhy/ucuvz3t.htm',
        'https://www.spseol.cz/data/rozvrhy/ucumcdl.htm',
        'https://www.spseol.cz/data/rozvrhy/ucuzbnp.htm',
        'https://www.spseol.cz/data/rozvrhy/ucuzbnn.htm',
        'https://www.spseol.cz/data/rozvrhy/ucuiuic.htm',
        'https://www.spseol.cz/data/rozvrhy/ucuzbne.htm',
        'https://www.spseol.cz/data/rozvrhy/ucuu1gt.htm',
        'https://www.spseol.cz/data/rozvrhy/ucuejce.htm',
        'https://www.spseol.cz/data/rozvrhy/uculdy5.htm',
        'https://www.spseol.cz/data/rozvrhy/ucud37o.htm',
        'https://www.spseol.cz/data/rozvrhy/ucun35r.htm',
        'https://www.spseol.cz/data/rozvrhy/ucuxxsn.htm',
        'https://www.spseol.cz/data/rozvrhy/ucuzbno.htm',
        'https://www.spseol.cz/data/rozvrhy/ucu8b7i.htm',
        'https://www.spseol.cz/data/rozvrhy/ucuxf4l.htm',
        'https://www.spseol.cz/data/rozvrhy/ucuxtun.htm',
        'https://www.spseol.cz/data/rozvrhy/ucut9a2.htm',
        'https://www.spseol.cz/data/rozvrhy/ucu2kch.htm',
        'https://www.spseol.cz/data/rozvrhy/ucu4ll8.htm',
        'https://www.spseol.cz/data/rozvrhy/ucu797t.htm',
        'https://www.spseol.cz/data/rozvrhy/ucuka6i.htm',
        'https://www.spseol.cz/data/rozvrhy/ucuzbnm.htm',
        'https://www.spseol.cz/data/rozvrhy/ucuptpi.htm',
        'https://www.spseol.cz/data/rozvrhy/ucuzbn8.htm',
        'https://www.spseol.cz/data/rozvrhy/ucusn2k.htm',
        'https://www.spseol.cz/data/rozvrhy/ucuy5hv.htm',
        'https://www.spseol.cz/data/rozvrhy/ucujysc.htm',
        'https://www.spseol.cz/data/rozvrhy/ucuzbni.htm',
        'https://www.spseol.cz/data/rozvrhy/ucuzbnb.htm']

    TRIDA_SELECTOR = 'table.tb_rozvrh_1 tr > td.td_titulek_1 > p > span.textlargebold_1::text'
    UCITEL_SELECTOR = 'table.tb_rozvrh_2 tr > td.td_titulek_2 > p > span.textlargebold_2::text'
    def get_trida(self, response) -> str:
        trida = response.css(self.TRIDA_SELECTOR).extract_first()
        if not trida:
            trida = response.css(self.UCITEL_SELECTOR).extract_first()
        return trida.strip()

    def get_rowspan(self, td) -> int:
        rs = td.css('::attr(rowspan)').extract_first()
        if rs is not None:
            return int(rs)
        return 1

    def get_text(self, td) -> str:
        got = td.css('::text').extract()
        if len(got) > 1:
            return '|'.join(map(strip, got))
        return ''

    def prefill(self, raw_table, n):
        for _ in range(n):
            raw_table.append([None] * 10)

    def parse(self, response):
        merger = RowspanMerger()
        raw_table = self.parse_raw_table(response, merger.register_rowspan)
        pprint(raw_table)
        for row in raw_table:
            merger.add_line(row)
        pprint(merger.final)
        rozvrh = Rozvrh(self.get_trida(response))
        for line in merger.final:
            rozvrh.add(line)
        yield rozvrh.structured

    def parse_raw_table(self, response, rowspan_cb) -> list:
        raw_table = []
        table = response.css('table.tb_rozvrh_1, table.tb_rozvrh_2')
        y = 0
        rs_left = 0
        for tr in table.css('tr'):
            tds = iter(tr.css('td.td_1, td.td_2'))
            if not rs_left:
                try:
                    rs_left = self.get_rowspan(next(tds))
                except StopIteration:
                    continue
                self.prefill(raw_table, rs_left)
                rowspan_cb(rs_left)
            x = 0
            for td in tds:
                td_txt = self.get_text(td)
                while raw_table[y][x] is not None:
                    x += 1
                for rs_add in range(self.get_rowspan(td)):
                    raw_table[y + rs_add][x] = td_txt
            rs_left -= 1
            y += 1
        return raw_table
