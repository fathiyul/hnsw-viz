import matplotlib.pyplot as plt
import networkx as nx

def visualize_graph(arrays, connected_nodes_hnsw, level):
    G = nx.Graph(connected_nodes_hnsw[level])
    pos = {i: arrays[i] for i in connected_nodes_hnsw[level]}

    plt.figure(figsize=(10, 10))
    nx.draw(G, pos, with_labels=True, node_color='lightblue',
            node_size=400, font_size=12, font_weight='bold')
    nx.draw_networkx_edges(G, pos, width=1)
    plt.title(f"Small World, Level-{level}", fontsize=20)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(f'hnsw_graph_level_{level}.png', format='png', dpi=300, bbox_inches='tight')
    plt.close()

def visualize_levels(arrays, connected_nodes_hnsw, n_levels):
    color_mapper = create_color_mapper(n_levels)
    plt.figure(figsize=(10, 10))
    plt.scatter(arrays[:,0], arrays[:,1], 
                c=[get_color(i, connected_nodes_hnsw, color_mapper) for i in range(len(arrays))])
    plt.title("HNSW Levels Visualization")
    plt.savefig('hnsw_levels_visualization.png', format='png', dpi=300, bbox_inches='tight')
    plt.close()

def create_color_mapper(n_levels):
    colormap = plt.cm.viridis
    color_mapper = {}
    for level in range(n_levels-1, -1, -1):
        color_mapper[level] = colormap(level / (n_levels - 1))
    return color_mapper

def get_color(i, connected_nodes_level, levels_color):
    for level in range(len(connected_nodes_level)-1, -1, -1):
        if i in connected_nodes_level[level]:
            return levels_color[level]