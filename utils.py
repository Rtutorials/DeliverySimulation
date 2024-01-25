import numpy as np
import networkx as nx

def get_unit_step(coords_1, coords_2, speed):

    edge_length = np.sqrt(np.power((coords_2 - coords_1), 2).sum())
    unit_step = (coords_2 - coords_1)*speed/max(edge_length, 0.01)
    
    return unit_step

def get_shortest_distance(sim, node_1, node_2):
    
    distance = 0
    node_coords_G = sim.node_coords_G
    
    shortest_path = nx.shortest_path(sim.graph, node_1, node_2)
    for i in range(len(shortest_path) - 1):
        u = shortest_path[i]; v = shortest_path[i+1]
        edge_dir = node_coords_G[v] - node_coords_G[u]
        edge_distance = np.sqrt(np.power(edge_dir, 2).sum())
        distance += edge_distance
    
    return distance