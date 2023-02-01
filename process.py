import json

files = ['1455_01_01', '1465_01_19', '1485_01_01', '1529_01_01']
for filename in files:
    with open(f'{filename}.json', encoding='utf-8') as f:
        data = json.load(f)

    l = []
    for tag, country_data in data['countries'].items():
        try:
            if country_data['capital'] == 0 or len(country_data['owned_provinces']) == 0:
                l.append(tag)
        except KeyError:
            l.append(tag)

    for x in l:
        del data['countries'][x]

    with open(f'{filename}_processed.json', 'w+', encoding='utf-8') as f:
        json.dump(data, f)

data = {}
with open('tags.txt', encoding='utf-8') as f:
    for line in f:
        if line[0] != '#' and line.rstrip() != '':
            if '#' in line:
                line = line.split('#')[0]
            data[line[0:3]] = line[17:-6]

with open('tags.json', 'w+', encoding='utf-8') as f:
    json.dump(data, f)
