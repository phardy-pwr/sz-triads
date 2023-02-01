import json
from pyvis.network import Network
from datetime import datetime

net = Network(directed=True)
# net.toggle_drag_nodes(False)
net.toggle_physics(False)

with open('processed.json', encoding='utf-8') as f:
    data = json.load(f)
    countries = data['countries']
    diplomacy = data['diplomacy']

with open('positions.json', encoding='utf-8') as f:
    positions = json.load(f)

with open('tags.json', encoding='utf-8') as f:
    tag2name = json.load(f)


net.add_node(0, shape='image', image="map.png", physics=False, size=6000, x=15000, y=-5000)
i = 1
# i = 0
tag2id = {}
id2tag = {}
for tag, data in countries.items():
    x, y = positions[str(data["capital"])]["position"][2:4]
    net.add_node(i, label=tag2name[tag], x=x*7, y=y*-7, physics=False)
    tag2id[tag] = i
    id2tag[i] = tag
    i += 1

for alliance in diplomacy['alliance']:
    if 'end_date' not in alliance:
        f, s = (alliance['first'], alliance['second'])
        net.add_edge(tag2id[f], tag2id[s])
        net.add_edge(tag2id[s], tag2id[f])

for tag, data in countries.items():
    if 'rival' in data:
        if type(data['rival']) is list:
            for rival in data['rival']:
                net.add_edge(tag2id[tag], tag2id[rival['country']], color='ff2222')
        else:
            net.add_edge(tag2id[tag], tag2id[data['rival']['country']], color='ff2222')
# for dependency in diplomacy['dependency']:
#     if 'end_date' not in dependency or \
#             datetime.strptime(dependency['end_date'], '%Y-%m-%dT%H:%M:%S.%fZ') > datetime(1454, 12, 31):
#         f, s = (dependency['first'], dependency['second'])
#         if s in tag2id and f in tag2id:
#             colors = {
#                 'personal_union': '44bb44',
#                 'vassal': 'eebb44',
#                 'march': 'ee4444',
#                 'tributary_state': 'bbbb22',
#                 'daimyo_vassal': 'bb22bb'
#             }
#             color = colors[dependency['subject_type']]
#             net.add_edge(tag2id[f], tag2id[s], color=color)

net.save_graph('nodes.html')
