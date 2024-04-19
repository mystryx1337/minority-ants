import networkx as nx
import plot
import minority_ants as ma


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    G = nx.DiGraph()

    # Kanten mit Gewichten und Pheromonen hinzufügen
    G.add_edges_from([("A", "B", {'weight': 2, 'pheromone': 0.5}),
                      ("B", "A", {'weight': 2, 'pheromone': 0.7}),
                      ("B", "C", {'weight': 4, 'pheromone': 0.3}),
                      ("C", "D", {'weight': 1, 'pheromone': 0.8}),
                      ("D", "E", {'weight': 3, 'pheromone': 0.2}),
                      ("E", "B", {'weight': 5, 'pheromone': 0.6})])

    ants = ma.Minority_Ants(G)
    ants.start()

    plot.Render(G)
    ants.stop()
