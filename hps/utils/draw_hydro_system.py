"""
"""
#%%
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from hps.system.edges import Discharge, Spillage, Bypass
from hps import HydroSystem


def draw_hydro_system(hsystem: HydroSystem, title: str = "", ax=None):
    """
    Method to draw a hydro system.

    :param hsystem: A hydro system object.
    :param title: Title of the figure.
    :returns: A matplotlib axis.
    """
    G = nx.MultiDiGraph()  # Can have multiple directed edges between nodes
    G.add_nodes_from([node.name for node in hsystem.my_nodes])
    for edge in hsystem.my_edges:
        G.add_edge(edge.parent.name, edge.child.name, type=type(edge))

    spillage_edges = [(u, v) for (u, v, l) in G.edges(data=True) if l["type"] == Spillage]  # type:ignore
    discharge_edges = [(u, v) for (u, v, l) in G.edges(data=True) if l["type"] == Discharge]  # type:ignore
    bypass_edges = [(u, v) for (u, v, l) in G.edges(data=True) if l["type"] == Bypass]  # type:ignore

    pos = graphviz_layout(G, prog="dot")

    if not ax:
        fig, ax = plt.subplots(1, 1, subplot_kw={"title": title}, figsize=(9, 6))

    ax.axis("off")

    # Power Stations
    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=[node.name for node in hsystem.power_stations],
        node_color="#99d888",
        node_size=800,
        node_shape="s",
        ax=ax,
    )

    # Reservoirs
    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=[node.name for node in hsystem.reservoirs],
        node_color="#1285ba",
        node_size=800,
        node_shape="v",
        ax=ax,
    )

    # Creeks
    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=[node.name for node in hsystem.creeks],
        node_color="#e4e4a5",
        node_size=800,
        node_shape="1",
        ax=ax,
    )

    # Oceans
    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=[node.name for node in hsystem.oceans],
        node_color="#4e6bef",
        node_size=800,
        node_shape="_",
        ax=ax,
    )

    # Gates
    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=[node.name for node in hsystem.gates],
        node_color="#c2c2d6",
        node_size=800,
        node_shape="o",
        ax=ax,
    )

    # Spillage
    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=spillage_edges,
        width=2,
        edge_color="#b9b1a7",
        style="dashed",
        alpha=1.0,
        connectionstyle="arc3, rad = -0.1",
        arrowsize=20,
        ax=ax,
    )

    # Discharge
    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=discharge_edges,
        width=3,
        edge_color="#83c4f6",
        alpha=1.0,
        connectionstyle="arc3, rad = 0.1",
        arrowstyle="-|>",
        arrowsize=20,
        ax=ax,
    )

    # Bypass
    nx.draw_networkx_edges(
        G, pos, edgelist=bypass_edges, width=2, edge_color="#f6bb83", style="dotted", alpha=1.0, arrowsize=20, ax=ax
    )

    nx.draw_networkx_labels(G, pos, font_size=15, font_family="sans-serif", ax=ax)

    return ax


def view_graph(G):
    print(f"Nodes in graph: {G.nodes}")
    print(f"Edges in graph: {G.edges}")
    pos = nx.spring_layout(G)

    # Extract node attributes
    if len(nx.get_node_attributes(G, "population")) != 0:
        labels = {key: key + ":" + str(value) for (key, value) in nx.get_node_attributes(G, "population").items()}
        nx.draw(G, pos=pos, with_labels=True, labels=labels)
    else:
        nx.draw(G, pos, with_labels=True)

    # Extract edge attributes
    if len(nx.get_edge_attributes(G, "distance")) != 0:
        edge_labels = nx.get_edge_attributes(G, "distance")
        nx.draw_networkx_edge_labels(G, pos=pos, labels=edge_labels)
    plt.figure(figsize=(12, 12))
    plt.show()


# %%
