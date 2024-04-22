import networkx as nx
import plot


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    G = nx.DiGraph()

    # Kanten mit Gewichten und Pheromonen hinzufügen
    G.add_edges_from([("A", "B", {'weight': 1, 'pheromone': 0.0}),
                      ("A", "E", {'weight': 1, 'pheromone': 0.0}),
                      ("A", "D", {'weight': 1, 'pheromone': 0.0}),
                      ("A", "S", {'weight': 1, 'pheromone': 0.0}),

                      ("B", "A", {'weight': 1, 'pheromone': 0.0}),
                      ("B", "C", {'weight': 1, 'pheromone': 0.0}),
                      ("B", "D", {'weight': 1, 'pheromone': 0.0}),
                      ("B", "E", {'weight': 1, 'pheromone': 0.0}),
                      ("B", "F", {'weight': 1, 'pheromone': 0.0}),

                      ("C", "B", {'weight': 1, 'pheromone': 0.0}),
                      ("C", "E", {'weight': 1, 'pheromone': 0.0}),
                      ("C", "F", {'weight': 1, 'pheromone': 0.0}),

                      ("D", "A", {'weight': 1, 'pheromone': 0.0}),
                      ("D", "B", {'weight': 1, 'pheromone': 0.0}),
                      ("D", "E", {'weight': 1, 'pheromone': 0.0}),
                      ("D", "G", {'weight': 1, 'pheromone': 0.0}),
                      ("D", "H", {'weight': 1, 'pheromone': 0.0}),
                      ("D", "X", {'weight': 1, 'pheromone': 0.0}),

                      ("E", "A", {'weight': 1, 'pheromone': 0.0}),
                      ("E", "B", {'weight': 1, 'pheromone': 0.0}),
                      ("E", "C", {'weight': 1, 'pheromone': 0.0}),
                      ("E", "D", {'weight': 1, 'pheromone': 0.0}),
                      ("E", "F", {'weight': 1, 'pheromone': 0.0}),
                      ("E", "G", {'weight': 1, 'pheromone': 0.0}),
                      ("E", "H", {'weight': 1, 'pheromone': 0.0}),
                      ("E", "I", {'weight': 1, 'pheromone': 0.0}),

                      ("F", "B", {'weight': 1, 'pheromone': 0.0}),
                      ("F", "C", {'weight': 1, 'pheromone': 0.0}),
                      ("F", "E", {'weight': 1, 'pheromone': 0.0}),
                      ("F", "H", {'weight': 1, 'pheromone': 0.0}),
                      ("F", "I", {'weight': 1, 'pheromone': 0.0}),

                      ("G", "D", {'weight': 1, 'pheromone': 0.0}),
                      ("G", "E", {'weight': 1, 'pheromone': 0.0}),
                      ("G", "H", {'weight': 1, 'pheromone': 0.0}),
                      ("G", "J", {'weight': 1, 'pheromone': 0.0}),
                      ("G", "K", {'weight': 1, 'pheromone': 0.0}),

                      ("H", "D", {'weight': 1, 'pheromone': 0.0}),
                      ("H", "E", {'weight': 1, 'pheromone': 0.0}),
                      ("H", "F", {'weight': 1, 'pheromone': 0.0}),
                      ("H", "G", {'weight': 1, 'pheromone': 0.0}),
                      ("H", "I", {'weight': 1, 'pheromone': 0.0}),
                      ("H", "J", {'weight': 1, 'pheromone': 0.0}),
                      ("H", "K", {'weight': 1, 'pheromone': 0.0}),
                      ("H", "L", {'weight': 1, 'pheromone': 0.0}),

                      ("I", "E", {'weight': 1, 'pheromone': 0.0}),
                      ("I", "F", {'weight': 1, 'pheromone': 0.0}),
                      ("I", "H", {'weight': 1, 'pheromone': 0.0}),
                      ("I", "K", {'weight': 1, 'pheromone': 0.0}),
                      ("I", "L", {'weight': 1, 'pheromone': 0.0}),

                      ("J", "G", {'weight': 1, 'pheromone': 0.0}),
                      ("J", "H", {'weight': 1, 'pheromone': 0.0}),
                      ("J", "K", {'weight': 1, 'pheromone': 0.0}),

                      ("K", "G", {'weight': 1, 'pheromone': 0.0}),
                      ("K", "H", {'weight': 1, 'pheromone': 0.0}),
                      ("K", "I", {'weight': 1, 'pheromone': 0.0}),
                      ("K", "J", {'weight': 1, 'pheromone': 0.0}),
                      ("K", "L", {'weight': 1, 'pheromone': 0.0}),

                      ("L", "H", {'weight': 1, 'pheromone': 0.0}),
                      ("L", "I", {'weight': 1, 'pheromone': 0.0}),
                      ("L", "K", {'weight': 1, 'pheromone': 0.0}),
                      ("L", "Z", {'weight': 1, 'pheromone': 0.0}),

                      ("X", "D", {'weight': 1, 'pheromone': 0.0}),

                      ("S", "A", {'weight': 1, 'pheromone': 0.0}),

                      ("Z", "L", {'weight': 1, 'pheromone': 0.0})])

    AcoPlotObj = plot.AcoPlot(G)
