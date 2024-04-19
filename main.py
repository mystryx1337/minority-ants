import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()

# Kanten mit Gewichten und Pheromonen hinzufügen
G.add_edges_from([("A", "B", {'weight': 2, 'pheromone': 0.5}),
                  ("B", "A", {'weight': 2, 'pheromone': 0.7}),
                  ("B", "C", {'weight': 4, 'pheromone': 0.3}),
                  ("C", "D", {'weight': 1, 'pheromone': 0.8}),
                  ("D", "E", {'weight': 3, 'pheromone': 0.2}),
                  ("E", "B", {'weight': 5, 'pheromone': 0.6})])

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    node_colors = ["purple"] * len(G.nodes)
    edge_colors = ["black"] * len(G.edges)
    weight_labels = {(tail, head): f"{data['weight']}" for tail, head, data in G.edges(data=True)}
    pheromone_labels = {(tail, head): f"{data['pheromone']}" for tail, head, data in G.edges(data=True)}

    # Graphen anzeigen
    pos = nx.spring_layout(G)  # positions for all nodes
    nx.draw(G, pos, node_color=node_colors, with_labels=False)
    nx.draw_networkx_labels(G, pos, font_size=12, font_color="white", labels={n: n for n in G.nodes()})
    nx.draw_networkx_edge_labels(G, pos, edge_labels=weight_labels, font_color='red', label_pos=0.1)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=pheromone_labels, font_color='blue', label_pos=0.3)

    plt.show()

