import networkx as nx
from networkx.drawing.nx_pydot import graphviz_layout
import pandas as pd
import copy 
from copy import deepcopy

EDGE_WEIGHTS = {
    'Spouse': 0.25,
    'Parent': 2.0
}

# a node in the family tree graph
class Person:
    def __init__(self, personid, first_name, middle_name, last_name, suffix, nickname, dob, gender, maiden_name=None, descrip=None):
        self.personid = personid
        self.first_name = first_name 
        self.middle_name = middle_name 
        self.last_name = last_name 
        self.suffix = suffix
        self.nickname = nickname
        self.maiden_name = maiden_name
        self.dob = dob 
        self.gender = gender 
        self.descrip = descrip

# an edge in the family tree graph
class Relationship:
    def __init__(self, relationshipid, person_one, person_two, relationship_type):
        self.relationshipid = relationshipid 
        self.person_one = person_one
        self.person_two = person_two 
        self.relationship_type = relationship_type
        self.weight = EDGE_WEIGHTS.get(self.relationship_type, 1.0)
        self.len = self.weight

class FamilyTree():
    def __init__(self, persons, relationships):
        self.graph_ = nx.DiGraph()
        self.persons_ = copy.deepcopy(persons)
        self.relationships_ = copy.deepcopy(relationships)

        # add nodes to the graph with tuples of (label, attributes dictionary)
        # use Person identifier as node identifier
        self.graph_.add_nodes_from(((person.personid, vars(person)) for person in self.persons_))

        # add edges to the graph
        # 3-tuple of (node_one_label, node_two_label, edge attributes dictionary)
        self.graph_.add_edges_from(((relationship.person_one, relationship.person_two, vars(relationship)) for relationship in self.relationships_))

        self.update_node_positions()

    def update_node_positions(self, layout='dot'):
        """Utilizes networkx layout algorithms to determine optimal spacing of nodes."""

        """
        layout_map = {
            'spring': nx.spring_layout,
            'circular': nx.circular_layout,
            'shell': nx.shell_layout,
            'spiral': nx.spiral_layout,
            'dot': nx.dot_layout
        }

        layout_func = layout_map[layout]
        node_positions = layout_func(self.graph_)
        """

        node_positiions = graphviz_layout(self.graph_, prog="twopi")

        for node_id, pos in node_positiions.items():
            self.graph_.nodes[node_id]['pos'] = pos

    def find_descendants(self, node):
        """Return all descendant nodes for a given node"""

        return nx.descendants(self.graph_, node)

    def find_ancestors(self, node):
        """Return all ancestors for a given node"""

        return nx.ancestors(self.graph_, node)

    def lowest_common_ancestor(self, node_1, node_2):
        
        # in a directed graph, lowest common ancestor has to calculated in the correct order
        # whichever node has fewer ancestors comes first in the func call
        if len(nx.ancestors(self.graph_, node_1)) < len(nx.ancestors(self.graph_, node_2)):
            func_args = (node_1, node_2)
        else:
            func_args = (node_2, node_1)

        # find the node id of the lowest common ancestor
        lca = nx.lowest_common_ancestor(self.graph_, *func_args)

        return lca 

    def shortest_path_between(self, node_1, node_2):
        """Find the edges that give the shortest path between two nodes."""

        # find the lca of node_1 and node_2
        lca = self.lowest_common_ancestor(node_1, node_2)

        # find the path between node_1 and lca, and node_2 and lca
        first_path = nx.shortest_path(self.graph_, lca, node_1)
        second_path = nx.shortest_path(self.graph_, lca, node_2)

        full_path = list(first_path[::-1][:-1]) + list(second_path)
        edge_tuples = list(zip(full_path[:-1], full_path[1:]))

        return edge_tuples

    def edge_idxs_from_tuples(self, edge_tuples):
        """Find edge idxs from edge tuples"""

        edge_indices = []
        for idx, edge in enumerate(self.graph_.edges):
            # check for the flipped edge as well
            edge_flip = (edge[1], edge[0])
            if edge in edge_tuples or edge_flip in edge_tuples:
                edge_indices.append(idx)

        return edge_indices

    def determine_familial_relationship(self, node_1, node_2):
        """Need to add documentation to this.
        Calculates the familial relationship. Cousins occur when there's more than one generation
        to lowest common ancestor for node_1 or 2.
        """

        # find the node id of the lowest common ancestor
        lca = self.lowest_common_ancestor(node_1, node_2)

        # figure out how many generations to lowest common ancestor for each
        node_1_gens = nx.shortest_path_length(self.graph_, source=lca, target=node_1)
        node_2_gens = nx.shortest_path_length(self.graph_, source=lca, target=node_2)

        if min(node_1_gens, node_2_gens) > 1:
            removed_cousin = abs(node_1_gens - node_2_gens)
            cousin_level = min(node_1_gens, node_2_gens) - 1

            return f'{cousin_level}x cousins, {removed_cousin}x removed'
        
        relationship_matrix = [
            ['self', 'parent', 'parent'],
            ['child', 'brother/sister', 'uncle/aunt'],
            ['child', 'nephew/niece', 'cousin']
        ]

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
        selected_nodes = [node] + list(nx.descendants(self.graph_, source=node))
        selected_persons = [person for person in self.persons_ if person.personid in selected_nodes]
        
        return self.graph_.subgraph(selected_nodes)

relationship = pd.read_csv('roots/dev/test_data/test_relationships.csv')
relationships = []
for idx, row in relationship.iterrows():
    if row['Relationship'] != 'Filler':
        relationships.append(
            Relationship(
                row['RelationshipId'],
                row['Id1'],
                row['Id2'],
                row['Relationship']
            )
    )

spouses = relationship.loc[relationship.Relationship == 'Filler', 'Id2'].values

person = pd.read_csv('roots/dev/test_data/test_ppl.csv')
persons = []
for idx, row in person.iterrows():
    if row['PersonId'] not in spouses:
        persons.append(
            Person(
                row['PersonId'], 
                row['First Name'], 
                row['Middle Name'], 
                row['Last Name'], 
                row['Suffix'], 
                row['Nickname'], 
                row['DOB'], 
                row['Gender'], 
                row['Maiden Name']
            )   
        )


def create_tree():
    return FamilyTree(persons, relationships)
