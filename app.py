from flask import g, Flask, render_template, request
from datetime import date, timedelta
from collections import defaultdict
from operator import methodcaller
import json


isoformat = methodcaller('isoformat')

class AutoescapingFlask(Flask):
    def select_jinja_autoescape(self, filename):
        return True


app = AutoescapingFlask(__name__)

flink = '<a href="{0}">{0}</a>'.format
tridy = '1A 1B 1L 2A 2B 2L 3A 3B 3L 4A 4B 4L 1VE 1VT 2VE 2VT 3VE 3VT'.split()
vyber_tridy = ( '<!DOCTYPE html><title>rozvrh</title>'
    + '<body style="background-color:silver"><h1>Vyber třídu</h1>'
    + '<br><br>'.join(map(flink, tridy)) )


@app.route('/')
@app.route('/<trida>')
def index(trida = None):
    if not trida:
        return vyber_tridy
    trida = trida.upper() if trida[0].isnumeric() else trida.title()
    with open('rozvrh.json') as rozvrh, open('zmeny.json') as zmeny:
        rozvrhy = json.loads(rozvrh.read())
        zmeny = json.loads(zmeny.read())
    if trida != '*':
        rozvrhy = list(filter(lambda r: r['trida'] == trida, rozvrhy))
    apply_zmeny(rozvrhy, zmeny)
    if 'missing_akce' in g:
        print('\nmissing:', g.missing_akce)
    return render_template('index.html.j2',
                            rozvrhy = rozvrhy,
                            zmeny = zmeny,
                            missing = 'missing_akce' in g and g.missing_akce,
                            trida_from_url = trida)


def get_days():
    today = date.today()
    go_back_days = today.weekday()
    if go_back_days:
        mon = today - timedelta(days = go_back_days if go_back_days < 5 else go_back_days - 7)
    else:
        mon = today
    return today, mon, mon + timedelta(1), mon + timedelta(2), mon + timedelta(3), mon + timedelta(4)

def apply_zmeny(rozvrhy, zmeny):
    tday, mon, tue, wed, thu, fri = map(isoformat, get_days())
    g.days = {'mon': mon, 'tue': tue, 'wed': wed, 'thu': thu, 'fri': fri}
    for zset in zmeny:
        for r in rozvrhy:
            if zset['valid'] == mon:
                day = r['mon']
            elif zset['valid'] == tue:
                day = r['tue']
            elif zset['valid'] == wed:
                day = r['wed']
            elif zset['valid'] == thu:
                day = r['thu']
            elif zset['valid'] == fri:
                day = r['fri']
            else:
                continue
            for z in zset['zmeny']:
                if r['trida'] == z['trida']:
                    apply_zmena(day, z)

def apply_zmena(day, zmena):
    h = zmena['hodina']
    akce = zmena['akce']
    handle = zmena_handlers[akce]
    if not handle and akce.startswith('supl. ('):
        handle = handle_supluje
    if not handle and akce.startswith('spojeno ('):
        new = _build_subj(zmena, zmena='zmena')
        if type(day[h]) is list:
            day[h].append(new)
        else:
            day[h] = [day[h], new]
        return
    if not handle:
        if 'missing_akce' not in g:
            g.missing_akce = set()
        g.missing_akce.add(akce)
        return
    if type(day[h]) is list:
        for i in range(len(day[h])):
            if zmena['skupina'] in day[h][i]['group']:
                day[h][i] = handle(day[h][i], zmena)
    else:
        day[h] = handle(day[h], zmena)


form_title = "{akce} {pozn}".format_map

def _build_subj(_zmena, **add):
    subj = {
        'subject': _zmena['predmet'],
        'group': _zmena['skupina'] and "({})".format(_zmena['skupina']),
        'teacher': _zmena['ucitel'],
        'room': _zmena['mistnost'],
        'title': form_title(_zmena)}
    return dict(subj, **add)

def handle_odpada(subj, zmena):
    if subj and subj['subject'] == zmena['predmet']:
        subj['zmena'] = 'odpada'
        subj['title'] = form_title(zmena)
    return subj

def handle_spoji(subj, zmena):
    subj['supl'] = zmena['ucitel']
    subj['presun'] = zmena['mistnost']
    subj['title'] = form_title(zmena)
    return subj

def handle_vymena_r(subj, zmena):
    return handle_odpada(subj, zmena)

def handle_vymena_l(subj, zmena):
    return _build_subj(zmena, zmena='zmena')

def handle_presun_r(subj, zmena):
    return handle_odpada(subj, zmena)

def handle_presun_l(subj, zmena):
    return handle_vymena_l(subj, zmena)

def handle_zmena(subj, zmena):
    subj = subj or defaultdict(type(None))
    subj['presun'] = zmena['mistnost']
    subj['title'] = form_title(zmena)
    return subj

def handle_supluje(subj, zmena):
    if not subj:
        return handle_vymena_l(subj, zmena)
    if zmena['predmet'] and subj['subject'] != zmena['predmet']:
        subj['subject'] = zmena['predmet']
        subj['zmena'] = 'zmena'
    if zmena['mistnost'] and subj['room'] != zmena['mistnost']:
        subj['presun'] = zmena['mistnost']
    if zmena['skupina'] and subj['group'] != zmena['skupina']:
        subj['new-grp'] = zmena['skupina']
    subj['supl'] = zmena['ucitel']
    subj['title'] = form_title(zmena)
    return subj

def handle_navic(subj, zmena):
    return _build_subj(zmena, zmena='zmena')


zmena_handlers = defaultdict(type(None), {
    'odpadá': handle_odpada,
    'spojí': handle_spoji,
    'výměna >>': handle_vymena_r,
    'výměna <<': handle_vymena_l,
    'přesun >>': handle_presun_r,
    'přesun <<': handle_presun_l,
    'změna': handle_zmena,
    'supluje': handle_supluje,
    'navíc': handle_navic})



if __name__ == '__main__':
    app.run(debug = True)
