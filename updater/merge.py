import json
from sys import argv, stderr
from operator import itemgetter


x = []

for fname in argv[1:]:
    with open(fname) as file:
        txt = file.read()
        o = json.loads(txt) if txt else None
        if type(o) is list:
            x.extend(o)
        elif type(o) is dict:
            x.append(o)
        elif o is None:
            pass
        else:
            print('merge.py: unknown type parsed', type(o), file=stderr)

dates, i = set(), -1
while i + 1 < len(x):
    i += 1
    if x[i]['valid'] in dates:
        x.pop(i)
        i -= 1
    else:
        dates.add(x[i]['valid'])

x.sort(key=itemgetter('valid'), reverse=True)

print(json.dumps(x[:15]))
