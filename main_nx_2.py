import json
import networkx as nx
import matplotlib.pyplot as plt
import itertools


files = ['1455_01_01', '1465_01_19', '1485_01_01', '1529_01_01']
tag2id = {}
id2tag = {}
triplets = {}
i = 0
with open('tags.json', encoding='utf-8') as f:
    tag2name = json.load(f)

for filename in files:
    polarity_sum = [0] * 5
    g = nx.DiGraph()
    with open(f'{filename}_processed.json', encoding='utf-8') as f:
        data = json.load(f)
        countries = data['countries']
        diplomacy = data['diplomacy']

    for tag, data in countries.items():
        if tag in tag2id:
            g.add_node(tag2id[tag])
        else:
            g.add_node(i)
            tag2id[tag] = i
            id2tag[i] = tag
            i += 1

    for tag, data in countries.items():
        if 'rival' in data:
            if type(data['rival']) is list:
                for rival in data['rival']:
                    g.add_edge(tag2id[tag], tag2id[rival['country']], type='rival')
                    g.add_edge(tag2id[rival['country']], tag2id[tag], type='rival')
            else:
                g.add_edge(tag2id[tag], tag2id[data['rival']['country']], type='rival')
                g.add_edge(tag2id[data['rival']['country']], tag2id[tag], type='rival')

    for alliance in diplomacy['alliance']:
        if 'end_date' not in alliance:
            f, s = (tag2id[alliance['first']], tag2id[alliance['second']])
            if not ((f, s) in g.edges or (s, f) in g.edges):
                g.add_edge(f, s, type='ally')
                g.add_edge(s, f, type='ally')

    for comp in sorted(filter(lambda x: len(x) > 2, nx.weakly_connected_components(g)), key=len, reverse=True):
        c = g.subgraph(comp).copy()
        polarity_count = [0] * 5
        d = nx.to_undirected(c)
        for triplet in list(itertools.combinations(filter(lambda x: g.degree[x] > 1, c.nodes), 3)):
            polarity = 0
            triplet_edges = list(itertools.combinations(triplet, 2))
            f = 0
            for edge in triplet_edges:
                if edge in d.edges:
                    f += 1
            if f >= 2:
                for edge in triplet_edges:
                    if edge in d.edges:
                        if d.edges[edge]['type'] == 'rival':
                            polarity += 1
                polarity_count[polarity] += 1
                if triplet in triplets:
                    triplets[triplet].append(g.subgraph(triplet).to_undirected())
                else:
                    triplets[triplet] = [g.subgraph(triplet).to_undirected()]
            else:
                polarity_count[4] += 1
        polarity_sum = [polarity_sum[x] + polarity_count[x] for x in range(len(polarity_count))]
    print(polarity_sum)


def is_balanced(G: nx.Graph):
    pol = 1
    edges = list(itertools.combinations(G.nodes, 2))
    for ed in edges:
        if ed in G.edges:
            if G.edges[ed]['type'] == 'rival':
                pol += 1
    return pol % 2


def is_complete(G: nx.Graph):
    return len(G.edges) == 3


complete = [0, 0]
incomplete = [0, 0]
incomplete_to_complete = [0, 0, 0, 0]
complete_to_incomplete = [0, 0, 0, 0]
print(len(list(filter(lambda x: len(x) == 4, triplets.values()))))
print(len(list(filter(lambda x: len(x) == 4 and
                      not all([nx.utils.graphs_equal(x[i], x[i+1]) for i in range(3)]), triplets.values()))))

for triplet, graphs in triplets.items():
    if len(graphs) == 4:
        if not all([nx.utils.graphs_equal(graphs[i], graphs[i+1]) for i in range(3)]):
            for i in range(4):
                if i > 0:
                    k = is_balanced(graphs[i]) - is_balanced(graphs[i-1])
                    if k != 0:
                        k = (k + 1)//2
                        if is_complete(graphs[i-1]):
                            if is_complete(graphs[i]):
                                complete[k] += 1
                            else:
                                complete_to_incomplete[k] += 1
                        else:
                            if is_complete(graphs[i]):
                                incomplete_to_complete[k] += 1
                            else:
                                incomplete[k] += 1
                    else:
                        if is_complete(graphs[i-1]) and not is_complete(graphs[i]):
                            complete_to_incomplete[2+is_balanced(graphs[i])] += 1
                        elif not is_complete(graphs[i-1]) and is_complete(graphs[i]):
                            incomplete_to_complete[2+is_balanced(graphs[i])] += 1


print('Zmiany dla trójek o 2 krawędziach:')
print(f'Ze "zbalansowanej" na "niezbalansowaną": {incomplete[0]}')
print(f'Z "niezbalansowanej" na "zbalansowaną": {incomplete[1]}')
print(f'Ze "zbalansowanej" na niezbalansowaną (3 krawędzie)": {incomplete_to_complete[0]}')
print(f'Z "niezbalansowanej" na zbalansowaną (3 krawędzie)": {incomplete_to_complete[1]}')
print(f'Z "niezbalansowanej" na niezbalansowaną (3 krawędzie)": {incomplete_to_complete[2]}')
print(f'Ze "zbalansowanej" na zbalansowaną (3 krawędzie)": {incomplete_to_complete[3]}')
print('Zmiany dla trójek o 3 krawędziach:')
print(f'Ze zbalansowanej na niezbalansowaną: {complete[0]}')
print(f'Z niezbalansowanej na zbalansowaną: {complete[1]}')
print(f'Ze zbalansowanej na "niezbalansowaną" (2 krawędzie)": {complete_to_incomplete[0]}')
print(f'Z niezbalansowanej na "zbalansowaną" (2 krawędzie)": {complete_to_incomplete[1]}')
print(f'Z niezbalansowanej na "niezbalansowaną" (2 krawędzie)": {complete_to_incomplete[2]}')
print(f'Z zbalansowanej na "zbalansowaną" (2 krawędzie)": {complete_to_incomplete[3]}')

for triplet, graphs in triplets.items():
    if len(graphs) == 4:
        if not all([nx.utils.graphs_equal(graphs[i], graphs[i+1]) for i in range(3)]):
            fig, axs = plt.subplots(2, 2, figsize=(10, 7))
            for i in range(4):
                ax = plt.subplot(221 + i)
                labels = {}
                colors = ['red' if graphs[i][u][v]['type'] == 'rival' else 'blue' for u, v in graphs[i].edges]
                for node in graphs[i].nodes:
                    labels[node] = tag2name[id2tag[node]]
                a, b, c = graphs[i].nodes
                pos = {a: (0, 1), b: (-0.5, 0), c: (0.5, 0)}
                nx.draw_networkx_nodes(graphs[i], pos=pos)
                nx.draw_networkx_edges(graphs[i], pos=pos, edge_color=colors)
                nx.draw_networkx_labels(graphs[i], pos, labels)
                ax.margins(0.25)
                ax.title.set_text(files[i])

                if i > 0:
                    k = is_balanced(graphs[i]) - is_balanced(graphs[i-1])
                    if k != 0:
                        k = (k + 1)//2
                        if is_complete(graphs[i-1]):
                            if is_complete(graphs[i]):
                                print(f't{7 + k}')
                            else:
                                print(f't{9 + k}')
                        else:
                            if is_complete(graphs[i]):
                                print(f't{3 + k}')
                            else:
                                print(f't{1 + k}')
                    else:
                        if is_complete(graphs[i-1]) and not is_complete(graphs[i]):
                            print(f't{11 + is_balanced(graphs[i])}')
                        elif not is_complete(graphs[i-1]) and is_complete(graphs[i]):
                            print(f't{5 + is_balanced(graphs[i])}')
            print('')
            plt.show()
