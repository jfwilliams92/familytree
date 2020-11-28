import networkx as nx
import numpy as np
import json
import copy
from copy import deepcopy
# for testing
# import matplotlib.pyplot as plt

# for testing and development
people_path = "data/people.json"

with open(people_path) as fd:
    people_data = json.load(fd)

relationship_path = "data/relationships.json"

with open(relationship_path) as fd:
    relationship_data = json.load(fd)

class FamilyTree():
    def __init__(self, people, relationships):
        self._graph = nx.DiGraph()
        self._people = copy.deepcopy(people['people'])
        self._relationships = copy.deepcopy(relationships['relationships'])

        # add nodes to the graph
        # tuple of (label, attributes dictionary)
        self._graph.add_nodes_from(((p['id'], p['data']) for p in self._people))

        # add edges to the graph
        # 3-tuple of (node_one_label, node_two_label, edge attributes dictionary)
        self._graph.add_edges_from(((r['node_one_id'], r['node_two_id'], r['data']) for r in self._relationships))

    def update_node_positions(self, layout='spring'):
        layout_map = {
            'spring': nx.spring_layout,
            'circular': nx.circular_layout
        }

        layout_func = layout_map[layout]
        node_positions = layout_func(self._graph)

        for node_id, pos in node_positions.items():
            self._graph.nodes[node_id]['pos'] = pos

    def calculate_descendants(self, node):
        pass

    def shortest_path_between(self, node_1, node_2):
        if len(nx.ancestors(self._graph, node_1)) < len(nx.ancestors(self._graph, node_2)):
            func_args = (node_1, node_2)
        else:
            func_args = (node_2, node_1)
        
        shortest_path_between = nx.shortest_path(self._graph, *func_args)

        edge_tuples = list(zip(shortest_path_between[:-1], shortest_path_between[1:]))
    
        edge_indices = []
        for idx, edge in enumerate(self._graph.edges):
            if edge in edge_tuples:
                edge_indices.append(idx)

        return edge_indices

    def determine_familial_relationship(self, node_1, node_2):

        # in a directed graph, lowest common ancestor has to calculated in the correct order
        # whichever node has fewer ancestors comes first in the func call
        if len(nx.ancestors(self._graph, node_1)) < len(nx.ancestors(self._graph, node_2)):
            func_args = (node_1, node_2)
        else:
            func_args = (node_2, node_1)
            
        # find the node id of the lowest common ancestor
        lca = nx.lowest_common_ancestor(self._graph, *func_args)
        #print(lca)

        # figure out how many generations to lowest common ancestor for each
        node_1_gens = nx.shortest_path_length(self._graph, source=lca, target=node_1)
        node_2_gens = nx.shortest_path_length(self._graph, source=lca, target=node_2)

        # 
        if min(node_1_gens, node_2_gens) > 1:
            removed_cousin = abs(node_1_gens - node_2_gens)
            cousin_level = min(node_1_gens, node_2_gens) - 1

            return f'{cousin_level}x cousins, {removed_cousin}x removed'
        
        relationship_matrix = np.array(
            [
                ['common ancestor', 'parent', 'grandparent'],
                ['child', 'brother/sister', 'uncle/aunt'],
                ['grandchild', 'nephew/niece', 'cousin']
            ]       
        )

        grand_level = min(abs(node_1_gens - node_2_gens) - 1, 1)
        great_level = abs(node_1_gens - node_2_gens) - 2

        n_1 = min(2, node_1_gens)
        n_2 = min(2, node_2_gens)

        if great_level > 0:
            great_string = f'{great_level}x great-'
        else:
            great_string = ''

        return great_string + (grand_level * 'grand') + relationship_matrix[n_1,n_2]
        
    def subselect_tree(self, node):
        selected_nodes = [node] + list(nx.descendants(self._graph, source=node))
        return self._graph.subgraph(selected_nodes)

def create_tree():
    return FamilyTree(people_data, relationship_data)