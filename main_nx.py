import json
import networkx as nx
import matplotlib.pyplot as plt
import itertools

g = nx.DiGraph()
files = ['1455_01_01', '1465_01_19', '1475_01_02', '1485_01_01']

with open('1455_01_01_processed.json', encoding='utf-8') as f:
    data = json.load(f)
    countries = data['countries']
    diplomacy = data['diplomacy']

with open('positions.json', encoding='utf-8') as f:
    positions = json.load(f)

with open('tags.json', encoding='utf-8') as f:
    tag2name = json.load(f)

i = 0
pos = {}
tag2id = {}
id2tag = {}
labels = {}
for tag, data in countries.items():
    x, y = positions[str(data["capital"])]["position"][2:4]
    g.add_node(i)
    pos[i] = (x*7, y*7)
    labels[i] = tag2name[tag]
    tag2id[tag] = i
    id2tag[i] = tag
    i += 1

for tag, data in countries.items():
    if 'rival' in data:
        if type(data['rival']) is list:
            for rival in data['rival']:
                g.add_edge(tag2id[tag], tag2id[rival['country']], type='rival')
        else:
            g.add_edge(tag2id[tag], tag2id[data['rival']['country']], type='rival')

for alliance in diplomacy['alliance']:
    if 'end_date' not in alliance:
        f, s = (tag2id[alliance['first']], tag2id[alliance['second']])
        if not ((f, s) in g.edges or (s, f) in g.edges):
            g.add_edge(f, s, type='ally')
            g.add_edge(s, f, type='ally')

edges = g.edges()
colors = ['red' if g[u][v]['type'] == 'rival' else 'blue' for u, v in edges]

triplets = []
for comp in sorted(filter(lambda x: len(x) > 2, nx.weakly_connected_components(g)), key=len, reverse=True):
    c = g.subgraph(comp).copy()
    triadic_census = nx.triadic_census(c)
    for key, value in triadic_census.items():
        print(f"{key}: {value}")
    print('')
    polarity_count = [0] * 5
    d = nx.to_undirected(c)
    for triplet in list(itertools.combinations(c.nodes, 3)):
        polarity = 0
        triplet_edges = list(itertools.combinations(triplet, 2))
        f = True
        for edge in triplet_edges:
            if edge not in d.edges:
                f = False
        if f:
            for edge in triplet_edges:
                if d.edges[edge]['type'] == 'rival':
                    polarity += 1
            polarity_count[polarity] += 1
            triplets.append(triplet)
        else:
            polarity_count[4] += 1
    print(polarity_count)
    print('')
    nx.draw_networkx_nodes(c, pos=pos)
    nx.draw_networkx_edges(c, pos=pos, edge_color=colors)
    nx.draw_networkx_labels(c, pos, labels)
    plt.show()

