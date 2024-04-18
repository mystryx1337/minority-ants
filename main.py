# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import networkx as nx
import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.animation import FuncAnimation


def start_animation():
    animation.event_source.start()

def stop_animation():
    animation.event_source.stop()
def update(frame):
    # Aktuelle Kantenfarben ändern
    new_edge_colors = edge_colors.copy()
    for i, edge in enumerate(G.edges):
        if i == frame:
            new_edge_colors[i] = "red"
        else:
            new_edge_colors[i] = "black"

    # Graphen mit neuen Farben und Labels zeichnen
    nx.draw_networkx(G, node_color=node_colors, edge_color=new_edge_colors, edge_labels=edge_labels)

def print_hi(name):

    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Strg+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    G = nx.DiGraph()

    # Knoten hinzufügen
    G.add_nodes_from(["A", "B", "C", "D", "E"])

    # Kanten mit Gewichten hinzufügen
    G.add_weighted_edges_from([("A", "B", 2), ("B", "C", 4), ("C", "D", 1), ("D", "E", 3), ("E", "A", 5)])

    node_colors = ["red", "green", "blue", "yellow", "purple"]
    edge_colors = ["black"] * len(G.edges)
    edge_labels = {(tail, head): str(weight) for tail, head, weight in G.edges.data()}

    # Animation erstellen
    animation = FuncAnimation(plt.gcf(), update, frames=len(G.edges), interval=500)

    root = tk.Tk()

    start_button = tk.Button(root, text="Start Animation", command=start_animation)
    start_button.pack()

    stop_button = tk.Button(root, text="Stop Animation", command=stop_animation)
    stop_button.pack()

    # Graphen anzeigen
    nx.draw(G)
    plt.show()

    root.mainloop()

    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
