#%%

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from hps.system.nodes import Reservoir, Gate
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import hydro_system_models as hsm
from hps import draw_hydro_system
import networkx as nx


def get_parent_nodes_not_gate(hydro_system, nodes):
    parents = [edge.parent for edge in hydro_system.my_edges if edge.child in nodes]
    not_gates = []
    for node in parents:
        if isinstance(node, Gate):
            not_gates += get_parent_nodes_not_gate(hydro_system, [node])
        else:
            not_gates += [node]
    return not_gates


def get_max_and_min_head_diff(hydro_system, ps):
    upper_nodes = get_parent_nodes_not_gate(hydro_system, [ps])
    h_upper_max = max([res.head.hrv for res in upper_nodes])
    h_upper_min = max([res.head.lrv for res in upper_nodes])
    lower_node = [edge.child for edge in hydro_system.my_edges if edge.parent is ps][0]
    h_lower_min, h_lower_max = 0.0, 0.0
    if isinstance(lower_node, Reservoir):
        h_lower_min = lower_node.head.lrv
        h_lower_max = lower_node.head.hrv
    
    return h_upper_max - h_lower_min, h_upper_min - h_lower_max


def visualize_reservoir_heads(hydro_system):
    fig, ax = plt.subplots()
    sum_mm3 = 0.0
    for res in hydro_system.reservoirs:
        try:
            print(res.head.decay)
        except:
            pass
        vol = np.arange(res.head.v_min, res.head.v_max)
        head = [res.head.get_head(v) for v in vol]
        plt.plot(vol, head, label=res.name)
        sum_mm3 += res.max_volume
    plt.xlabel("Volume [Mm3]")
    plt.ylabel("Head [mabsl]")
    plt.legend()

    print(f"Total reservoir capacity: {sum_mm3} [Mm3]")
    return ax


def visualize_power_station_generation(hydro_system, verbose=True):
    fig, axs = plt.subplots(len(hydro_system.power_stations))
    if not isinstance(axs, list) and not isinstance(axs, np.ndarray):
        axs = [axs]

    for idx, ps in enumerate(hydro_system.power_stations):
        gf = ps.generation_function
        
        dis = np.linspace(start=0, stop=gf.q_max, num=100)

        head_max, head_min = get_max_and_min_head_diff(hydro_system, ps)
        head = np.linspace(head_min, head_max, endpoint=True)

        if verbose:
            print(ps.name)
            print(f"P_min = {gf.p_min}, P_max ={gf.p_max}")
            print(f"q_min = {gf.q_min}, q_max = {gf.q_max}")
            print(f"h_min = {head_min}, h_max = {head_max}")

        power = np.zeros((dis.shape[0], head.shape[0]))
        for i, d in enumerate(dis):
            for j, h in enumerate(head):
                power[i, j] = gf.get_power(d, h)


        axs[idx].plot(dis, power)
        axs[idx].legend(handles=[mpatches.Patch(color='w', label=ps.name)])

        colormap = plt.cm.viridis_r
        colors = [colormap(v) for v, _ in enumerate(axs[idx].lines)]
        for c, j in enumerate(axs[idx].lines):
            j.set_color(colors[c])

        plt.ylabel("Power [MW]")
        plt.xlabel("Discharge [m3/s]")
    
    return axs, dis, power


def view_graph(G):
    import matplotlib.pyplot as plt
    print(f'Nodes in graph: {G.nodes}')
    print(f'Edges in graph: {G.edges}')
    pos = nx.spring_layout(G)

    # Extract node attributes
    if len(nx.get_node_attributes(G, 'population')) != 0:
        labels = {key: key + ':' + str(value) for (key,value) in nx.get_node_attributes(
            G, 'population').items()}
        nx.draw(G, pos = pos, with_labels=True, labels=labels)
    else:
        nx.draw(G, pos, with_labels=True)

    # Extract edge attributes
    if len(nx.get_edge_attributes(G, 'distance')) != 0:
        edge_labels = nx.get_edge_attributes(G, 'distance')
        nx.draw_networkx_edge_labels(G, pos=pos, labels=edge_labels)
    plt.figure(figsize=(12,12))
    plt.show()


# %%
def main():

#%%
    # hydro_system = hsm.hydro_system_small()
    # hydro_system = hsm.hydro_system_medium()
    hydro_system = hsm.hydro_system_large()

    ax, dis, power = visualize_power_station_generation(hydro_system)
    ax = visualize_reservoir_heads(hydro_system)

    fig, ax = plt.subplots(1,1, subplot_kw={"title": ""}, figsize=(12, 8))
    ax = draw_hydro_system(hydro_system, ax=ax)
    plt.show()



#%%
if __name__ == '__main__':
    main()