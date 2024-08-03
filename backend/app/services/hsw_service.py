import numpy as np
from numpy.linalg import norm
from numpy import dot
import random
from math import log
import networkx as nx
import matplotlib.pyplot as plt
import os

class HSWService:
    def __init__(self, N, k, distance_metric="l2"):
        self.N = N
        self.k = k
        self.distance_metric = distance_metric
        self.log_base = 3
        self.n_levels = int(log(N, self.log_base))
        self.arrays = None
        self.connected_nodes_hnsw = None
        self.levels_nodes = None

    def set_data(self, arrays):
        self.arrays = arrays

    def build_index(self):
        min_prob = np.array([self.log_base**(self.n_levels-i) for i in range(self.n_levels)])
        min_prob = min_prob/np.sum(min_prob)
        min_prob = np.concatenate(([0], np.cumsum(min_prob)[:-1]))
        self.connected_nodes_hnsw = [{} for _ in range(self.n_levels)]
        self.levels_nodes = [[] for _ in range(self.n_levels)]

        for i, arr in enumerate(self.arrays):
            # Levels assigning
            assigned_levels = min_prob < random.random()

            for level in range(self.n_levels):
                if not assigned_levels[level]:
                    break

                distances = self._calculate_distances(level, i)

                self.levels_nodes[level].append(i)
                self.connected_nodes_hnsw[level][i] = [self.levels_nodes[level][ix] for ix in np.argsort(distances)[:self.k].tolist()]

                for e in self.connected_nodes_hnsw[level][i]:
                    if e not in self.connected_nodes_hnsw[level]:
                        self.connected_nodes_hnsw[level][e] = []
                    self.connected_nodes_hnsw[level][e].append(i)

    def _calculate_distances(self, level, i):
        if self.distance_metric == "l1":
            return np.sum(np.abs((self.arrays[self.levels_nodes[level]] - self.arrays[i])), axis=1)
        elif self.distance_metric == "l2":
            return np.sqrt(np.sum((self.arrays[self.levels_nodes[level]] - self.arrays[i])**2, axis=1))
        elif self.distance_metric == "dot":
            return - dot(self.arrays[self.levels_nodes[level]], self.arrays[i])
        elif self.distance_metric == "cosine":
            return - dot(self.arrays[self.levels_nodes[level]], self.arrays[i]) / (norm(self.arrays[self.levels_nodes[level]], axis=1)*norm(self.arrays[i]))

    def get_graph(self):
        return self.connected_nodes_hnsw

    def get_levels(self):
        return self.levels_nodes

    def query(self, query_vector):
        starting_node = random.choice(list(self.connected_nodes_hnsw[self.n_levels-1]))
        nodes_color_hnsw = {i: 'lightblue' for i in range(self.N)}
        nodes_color_hnsw[starting_node] = 'pink'
        distance_from_query = {
            starting_node: self._distance_fn(query_vector, self.arrays[starting_node])
        }

        current_node = starting_node
        min_distance = distance_from_query[current_node]
        loop_count = 0

        for level in range(self.n_levels-1, -1, -1):
            while True:
                next_nodes = [n for n in self.connected_nodes_hnsw[level][current_node] if n not in distance_from_query]
                if len(next_nodes) == 0:
                    break
                loop_count += 1

                new_node = None
                for n in next_nodes:
                    nodes_color_hnsw[n] = 'yellow'
                    distance = self._distance_fn(query_vector, self.arrays[n])
                    distance_from_query[n] = distance
                    if distance < min_distance:
                        new_node = n
                        min_distance = distance

                self._visualize_query_step(level, query_vector, nodes_color_hnsw, loop_count)

                if new_node is None:
                    nodes_color_hnsw[current_node] = 'lightgreen'
                    break
                else:
                    nodes_color_hnsw[new_node] = 'lightgreen'
                    current_node = new_node

        visualization_path = self._visualize_query(query_vector, current_node)

        return current_node, distance, visualization_path
    
    def _visualize_query(self, query_vector, result_node):
        plt.figure(figsize=(10, 10))
        plt.scatter(self.arrays[:, 0], self.arrays[:, 1], c='blue', label='Data points')
        plt.scatter(query_vector[0], query_vector[1], c='red', s=100, label='Query')
        plt.scatter(self.arrays[result_node, 0], self.arrays[result_node, 1], c='green', s=100, label='Nearest neighbor')
        plt.legend()
        plt.title("Query Visualization")
        
        os.makedirs("visualizations", exist_ok=True)
        file_path = 'visualizations/query_visualization.png'
        plt.savefig(file_path, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        return os.path.basename(file_path)

    def _distance_fn(self, v1, v2):
        if self.distance_metric == "l1":
            return np.sum(np.abs(v1 - v2))
        elif self.distance_metric == "l2":
            return np.sqrt(np.sum((v1 - v2)**2))
        elif self.distance_metric == "dot":
            return -np.dot(v1, v2)
        elif self.distance_metric == "cosine":
            return -np.dot(v1, v2) / (norm(v1) * norm(v2))

    def _visualize_query_step(self, level, query_vector, nodes_color_hnsw, loop_count):
        G = nx.Graph(self.connected_nodes_hnsw[level])
        pos = {i: self.arrays[i] for i in range(len(self.arrays))}
        query_node = len(self.connected_nodes_hnsw[level])
        pos[query_node] = query_vector

        plt.figure(figsize=(10, 10))
        nx.draw(G, pos, with_labels=True, node_color=[nodes_color_hnsw[node] for node in G.nodes()],
                node_size=400, font_size=12, font_weight='bold')
        nx.draw_networkx_edges(G, pos, width=1)
        nx.draw_networkx_nodes(G, pos, nodelist=[query_node], node_color='red', node_size=400)
        nx.draw_networkx_labels(G, pos, labels={query_node: 'Q'}, font_color='white',
                                font_size=12, font_weight='bold')
        plt.title(f"Hierarchical Navigable Small World, Level{level}", fontsize=20)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig('visualizations/hnsw-query-history.png', format='png', dpi=300, bbox_inches='tight')
        plt.close()

    def visualize_graph(self, level):
        G = nx.Graph(self.connected_nodes_hnsw[level])
        pos = {i: self.arrays[i] for i in self.connected_nodes_hnsw[level]}

        plt.figure(figsize=(10, 10))
        nx.draw(G, pos, with_labels=True, node_color='lightblue',
                node_size=400, font_size=12, font_weight='bold')
        nx.draw_networkx_edges(G, pos, width=1)
        plt.title(f"Small World, Level-{level}", fontsize=20)
        plt.axis('off')
        plt.tight_layout()
        
        file_path = f'visualizations/hnsw_graph_level_{level}.png'
        plt.savefig(file_path, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        return file_path

    def visualize_levels(self):
        plt.figure(figsize=(10, 10))
        colors = plt.cm.viridis(np.linspace(0, 1, len(self.connected_nodes_hnsw)))
        for level, color in zip(range(len(self.connected_nodes_hnsw)), colors):
            nodes = list(self.connected_nodes_hnsw[level].keys())
            plt.scatter(self.arrays[nodes, 0], self.arrays[nodes, 1], c=[color], label=f'Level {level}')
        
        plt.legend()
        plt.title("HNSW Levels Visualization")
        
        file_path = 'visualizations/hnsw_levels_visualization.png'
        plt.savefig(file_path, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        return file_path

    def _create_color_mapper(self):
        colormap = plt.cm.viridis
        color_mapper = {}
        for level in range(self.n_levels-1, -1, -1):
            color_mapper[level] = colormap(level / (self.n_levels - 1))
        return color_mapper

    def _get_color(self, i, connected_nodes_level, levels_color):
        for level in range(self.n_levels-1, -1, -1):
            if i in connected_nodes_level[level]:
                return levels_color[level]