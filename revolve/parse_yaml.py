#!/usr/bin/env python

import yaml
import networkx as nx
import matplotlib.pyplot as plt

n_size = 200
a_size = 20


# def adjust_loc(o_loc):
#
#     if o_loc == 0:
#
#         return 0
#
#     elif o_loc == 1:
#
#         return 2


def find_nodes(graph, body_dict, pos, c_pos):

    type = body_dict['type']

    if type == 'Core':

        colour_node = 'yellow'

    elif type == 'FixedBrick':

        colour_node = 'blue'

    elif type == 'ActiveHinge':

        colour_node = 'red'

    graph.add_node(body_dict['id'], colour=colour_node)

    pos[body_dict['id']] = c_pos

    if 'children' in body_dict:

        for child in body_dict['children']:

            if child == 0:

                c_pos

            graph, pos, c_pos = find_nodes(graph, body_dict['children'][child],
                                           pos, c_pos)

    return graph, pos, c_pos


def find_edges(graph, body_dict):

    for child in body_dict['children']:

        graph.add_edge(body_dict['id'], body_dict['children'][child]['id'],
                       colour='black', id=body_dict['id'] + str(child))

        # print(body_dict['children'][child]['id'])

        if 'children' in body_dict['children'][child]:

            graph = find_edges(graph, body_dict['children'][child])

    return graph



with open("robot_150.yaml", 'r') as stream:
    try:
        body_dict = yaml.load(stream)['body']
    except yaml.YAMLError as exc:
        print(exc)

# print(body_dict)

graph = nx.DiGraph()

pos = {}

# current position
c_pos = [0, 0]

graph, pos, c_pos = find_nodes(graph, body_dict, pos, c_pos)
graph = find_edges(graph, body_dict)

nodes, colours_nodes = zip(*nx.get_node_attributes(graph,'colour').items())
edges, colours_edges = zip(*nx.get_edge_attributes(graph,'colour').items())

# print(colours_nodes)

# print(graph.nodes)
# print(graph.edges)

nx.draw(graph, pos, with_labels=True, node_size=n_size, edgelist=edges,
		node_color=colours_nodes, arrowstyle='->', arrowsize=a_size,
		edge_color=colours_edges, width = 0.2)

plt.show()
