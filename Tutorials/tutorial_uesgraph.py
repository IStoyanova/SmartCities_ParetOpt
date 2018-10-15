
#!/usr/bin/env python
# coding=utf-8
"""
This is a tutorial script to learn about uesgraph.py usage and its main
structure.

Just run this script to start the tutorial. It is going to pause its
execution at every user input function to go over every command step by step.
Continue by pressing enter.
You should follow the source code while executing the script to understand
the Python networkx commands, which are not going to be printed in the
output window.

We recommend getting familiar with Python package networkx.
networkx is a package to work with mathematical graphs.
networkx.Graph inherites to uesgraph class.
Thus, every attribute and method of networkx.graph can be used within uesgraph.
See networkx stable docu at:
https://networkx.readthedocs.org/en/stable/
"""

import shapely.geometry.point as point

#  Import statement for networkx (as nx)
import networkx as nx

#  Import statement to get uesgraph
from updatedClassses import UESGraph_myVersion as uesgraph


def run_part_1_nx_graph():
    """
    Executing tutorial code part 1 (networkx.Graph usage)
    """
    print('1. Getting familiar with networkx.Graph:')
    print('#################################################')
    print('The class UESGraph is an inheritance from network.Graph.')
    print('Thus, UESGraph holds all methods and attributes of nx.Graph.')
    print('Please follow the lines within the source code!')
    #  Here you are right :-)

    print('\nPress enter to continue:')
    input()
    print('Part 1.A')
    print('#---------------------------------------#')
    print('We are now going to create a graph object (with networkx.Graph) ')
    print('and add nodes and one edge.')

    #  Generate an empty networkx.Graph
    graph = nx.Graph()

    #  Adding node with id 1 to graph
    graph.add_node(1)
    print('\nPrint list of all nodes within graph: ', graph.nodes())

    #  Add further node with id 2 to graph
    graph.add_node(2)
    print('\nPrint list of all nodes within graph: ', graph.nodes())

    #  Add edge between node 1 and 2
    graph.add_edge(1, 2)
    print('\nPrint list of edges of graph: ', graph.edges())

    #  We are now having a graph with two nodes, which are connected by an edge
    print('\nPress enter to continue:')
    input()
    print('Part 1.B')
    print('#---------------------------------------#\n')

    print('We are now going to add attributes to nodes and edges:')
    #  Attributes are stored within dictionary (pairs of keys and values)
    #  We assume that our graph represents a 'social network' (of two persons)

    #  Adding an attribute "name" to node 1
    graph.node[1]['name'] = 'Klaus'
    #  In this case, 'name' is the dictionary key and 'Klaus' the value

    print('Print attribute "name" of node 1: ', graph.node[1]['name'])

    #  Adding an attribute "name" to node 2
    graph.node[2]['name'] = 'Claudia'

    print('Print attribute "name" of node 2: ', graph.node[2]['name'])

    #  Adding an attribute "connection" to edge (1, 2)
    graph.edge[1][2]['connection'] = 'friendship'

    print('Print attribute "connection" of edge (1, 2): ' +
          graph.edge[1][2]['connection'])

    #  Plot list of nodes with node data
    print('Show all nodes with attributes:', graph.nodes(data=True))
    #  Plot list of edges with edge data
    print('Show all edges with attributes: ', graph.edges(data=True))

    print('\nFinished part 1')
    print('#################################################\n')


def run_part_2_uesgraph():
    """
    Executes part 2 of uesgraph tutorial (general uesgraph usage)
    """

    print('2. Getting familiar with uesgraph usage:')
    print('#################################################')
    print('Please follow the lines within the source code!')

    print('\nPress enter to continue:')
    input()
    print('Part 2.A')
    print('#---------------------------------------#')
    print('We are now going to generate a UESGraph and add building nodes, ' +
          'street and heating network edges.')

    #  Initialize uesgraph object
    ues_graph = uesgraph.UESGraph()

    #  Plot description of uesgraph object
    print(ues_graph)

    #  uesgraph has different attributes, which are initialized as empty lists
    #  or dictionaries with emtpy lists
    print('Show uesgraph attribute nodelist_building (after init): ',
          ues_graph.nodelist_building)
    print('Show uesgraph attribute nodelist_heating (after init): ',
          ues_graph.nodelists_heating)
    #  The attribue nodelist_building (list) holds every building node
    #  The attribute nodelist_heating (dict) holds the network name as key
    #  as well as a list of node ids as values

    print('\nPress enter to continue:')
    input()
    print('Part 2.B')
    print('#---------------------------------------#\n')

    print('Adding a building node to uesgraph object.')

    #  Generate position as shapely Point object (coordinates 0 / 0)
    position_1 = point.Point(0, 0)

    #  Add a building node with method add_building (with position as input)
    ues_graph.add_building(position=position_1)


    print('Nodelist_building', ues_graph.nodelist_building)
    #  New node ids are automatically generated within uesgraph object,
    #  starting with 1001 and counting up by 1

    #  Add two street nodes to uesgraph
    str_id_1 = ues_graph.add_street_node(position=point.Point(0, 5))
    str_id_2 = ues_graph.add_street_node(position=point.Point(5, 5))

    print('Nodelist_street', ues_graph.nodelist_street)
    print('Access data of street node 1: ', ues_graph.node[str_id_1])

    #  Add two heating network nodes
    ht_id_1 = ues_graph.add_network_node(network_type='heating',
                                         position=point.Point(5, 0))
    ht_id_2 = ues_graph.add_network_node(network_type='heating',
                                         position=point.Point(10, 0))

    print('Nodelists_heating:', ues_graph.nodelists_heating)
    print()

    """
    print('Iteration control for heating network')
    for nodes in ues_graph.nodelists_heating['default']:
        print('Node number',nodes)
    input()
    """

    #  two street nodes and two heating network nodes.

    print('\nPress enter to continue:')
    input()
    print('Part 2.C')
    print('#---------------------------------------#\n')

    print('Now we are going to add street and heating network edges.')


    #  Add street network edge (between node str_id_1 and str_id_2)
    ues_graph.add_edge(str_id_1, str_id_2, network_type='street')
    #  We are adding an attribute 'network_type' as key with value 'street'

    print('Show all edges with data: ', ues_graph.edges(data=True))

    #  Add heating network edge (between node str_id_1 and str_id_2)
    ues_graph.add_edge(ht_id_1, ht_id_2, network_type='heating')
    #  We are adding an attribute 'network_type' as key with value 'street'

    print('Show all edges with data: ', ues_graph.edges(data=True))

    #  Now the ues_graph holds a street and a heating network edge

    print('\nPress enter to continue:')
    input()
    print('Part 2.D')
    print('#---------------------------------------#\n')

    print('Now we are going add and remove a new building node')

    #  Add a building node with method add_building
    b_id_new = ues_graph.add_building(position=point.Point(100, 100))

    print('Nodelist_building (with new node): ', ues_graph.nodelist_building)

    #  Remove new building node from uesgraph
    ues_graph.remove_building(node_number=b_id_new)


    print('Nodelist_building (after removal): ', ues_graph.nodelist_building)

    print('\nFinished part 2')
    print('#################################################\n')




def run_tutorial_uesgraph():
    """
    Executes tutorial for uesgraph usage.
    """

    print('Start of uesgraph tutorial')
    print('#################################################\n')

    print('General explanations:')
    print('uesgraphs is a Python package to describe and manage' +
          ' Urban Energy Systems in a Python graph structure.')
    print('Its main class is uesgraph.UESGraph. It manages structure and' +
          ' data of a district energy system')
    print('\nPress enter to continue:')
    input()

    #  Executing part 1 of tutorial (networkx.graph usage)
    run_part_1_nx_graph()

    print('\nPress enter to continue:')
    input()

    #  Execute part 2 of tutorial (uesgraph usage)
    run_part_2_uesgraph()

    print('End of tutorial')
    print('#################################################')


if __name__ == '__main__':

    #  Execute tutorial
    run_tutorial_uesgraph()
