# -*- coding:utf8 -*-
"""
This module contains the District class to describe the UES
"""

"""
upgrade
@author: ist-egu
"""

import copy
import datetime
import json
import math
import os
import uuid
import warnings
import xml.etree.ElementTree
from functools import partial
from itertools import combinations

import networkx as nx
import numpy as np
import pandas as pd
import shapely.geometry as sg
import shapely.ops as ops
from shapely import affinity
from shapely.prepared import prep
from updatedClassses.Transport.Cable import Cable
from updatedClassses.Transport.GasPipe import GasPipe
from updatedClassses.Transport.HeatPipe import HeatPipe

from updatedClassses.Transport.WaterPipe import WaterPipe

try:
    import pyproj
except:
    msg = 'Could not import pyproj package. Thus, from_osm function ' \
          'is not going to work. If you require it, you have to install ' \
          'from_osm package.'
    warnings.warn(msg)


class UESGraph(nx.Graph):
    """
    Uses a nx.Graph to manage structure and data of a District Energy System

    Attributes
    ----------
    name : str
        Name of the graph
    input_ids : dict
        When input is read from json files with ids in their meta data,
        these ids are stored in this dict
    nodelist_street : list
        List of node ids for all street nodes
    nodelist_building : list
        List of node ids for all building nodes
    nodelists_heating : dict
        Dictionary contains nodelists for all heating networks. Keys are names
        of the networks in str format, values are lists of all node ids that
        belong to the network
    nodelists_cooling : dict
        Dictionary contains nodelists for all cooling networks. Keys are names
        of the networks in str format, values are lists of all node ids that
        belong to the network
    nodelists_electricity : dict
        Dictionary contains nodelists for all electricity networks. Keys are
        names of the networks in str format, values are lists of all node
        ids that belong to the network
    nodelists_gas : dict
        Dictionary contains nodelists for all gas networks. Keys are names
        of the networks in str format, values are lists of all node ids that
        belong to the network
    nodelists_others : dict
        Dictionary contains nodelists for all other networks. Keys are names
        of the networks in str format, values are lists of all node ids that
        belong to the network
    network_types : list
        A list of all supported network types with their names in str format
    nodes_by_name : dict
        A dictionary with building names for keys and node numbers for values.
        Used to retrieve node numbers for a given building name.
    positions : dict
        In general, positions in uesgraphs are defined by
        `shapely.geometry.point` objects. This attribute converts the positions
        into a dict of numpy arrays only for use in uesgraphs.visuals, as the
        networkx drawing functions need this format.
    min_position : shapely.geometry.point object
        Position with smallest x and y values in the graph
    max_position : shapely.geometry.point object
        Position with largest x and y values in the graph
    next_node_number : int
        Node number for the next node to be added
    simplification_level : int
        Higher values indicate more simplification of the graph
        0: no simplification
        1: pipes connected in series are simplified to 1 aggregate pipe
    pipeIDs : list
        List of pipeIDs used in the graph
    """

    def __init__(self):
        """Constructor for District class"""
        super(UESGraph, self).__init__()

        self.name = None
        self.input_ids = {'buildings': None,
                          'nodes': None,
                          'pipes': None,
                          'supplies': None,
                          }
        self.nodelist_street = []
        self.nodelist_building = []
        self.nodelists_heating = {'default': []}
        self.nodelists_cooling = {'default': []}
        self.nodelists_electricity = {'default': []}
        self.nodelists_gas = {'default': []}
        self.nodelists_water = {'default': []}
        self.nodelists_others = {'default': []}

        #The city quarter will have only one network for each domain
        self.edgelist_heating = []
        self.edgelist_cooling = []
        self.edgelist_electricity = []
        self.edgelist_gas = []
        self.edgelist_water = []
        self.edgelist_others = []


        self.network_types = ['heating',
                              'cooling',
                              'electricity',
                              'gas',
                              'water',
                              'others']

        self.nodes_by_name = {}
        self.positions = {}
        self.min_position = None
        self.max_position = None

        self.next_node_number = 1001
        self.simplification_level = 0
        self.pipeIDs = []

    def defineConnection(self,env,dict):
        """
        Defines the specification for the  domain networks and connection mediums

        Parameters
        -------
        env : object
            Environment object of pycity (default: None)
        dict: dictionary
            Network and transportation medium specifications

        Example
        -------
            The electric network will have 1000V bus voltage and consist of power cables with 0.2m diameter and copper material(specific conductance:1.68*10**-8 ohm.m)
            >>>networksDictionary['Electricity']={'busVoltage':1000,'diameter':0.2,'spConductance':1.68*10**-8}
            The gas network will carry natural gas (0.8 kg/m3 density) of gas pipes in the gas network with 0.5m diameter and darcy friction 0.03
            >>>networksDictionary['Gas']={'diameter':0.5,'gasDensity':0.8,'darcyFactor':0.03}
            The heat network will carry heat through a carrier material with 0.591 W/m.K specific conductance in a heat pipe with 0.5m diameter
            >>>networksDictionary['Heat']={'diameter':0.5,'spConductance':0.591}
            The water network will consist of water pipes with 0.5m diameter and dary friction 0.03
            >>>networksDictionary['Water']={'diameter':0.5,'waterDensity':1000,'darcyFactor':0.03}
        """


        self._environment=env

        #TODO:Add default parameters
        self._voltage=dict['Electricity']['busVoltage']
        self._cableD=dict['Electricity']['diameter']
        self._cableSpRes=dict['Electricity']['spConductance']

        self._gasPipeD=dict['Gas']['diameter']
        self._gasPipeRho=dict['Gas']['gasDensity']
        self._gasPipeLambda=dict['Gas']['darcyFactor']

        self._heatPipeD=dict['Heat']['diameter']
        self._heatPipeSpCond=dict['Heat']['spConductance']

        self._waterPipeD=dict['Water']['diameter']
        self._waterPipeRho=dict['Water']['waterDensity']
        self._waterPipeLambda=dict['Water']['darcyFactor']


    @property
    def positions(self):
        for node in self.nodes(data=True):
            if node[0] is not None:
                assert 'position' in node[1], 'No position for:' + str(node[0])
                if node[1]['position'] is not None:
                    self.__positions[node[0]] = np.array([node[1][
                                                              'position'].x, node[1]['position'].y])
        return self.__positions

    @positions.setter
    def positions(self, value):
        self.__positions = value

    def __str__(self):
        description = ('<uesgraphs.district object' +
                       '>'
                       )
        return description

    def __repr__(self):
        description = ('<uesgraphs.district object' +
                       '>'
                       )
        return description

    def new_node_number(self):
        """Returns a new 4 digits node number that is not yet used in graph

        Returns
        -------
        new_number : int
            4 digit number not yet used for nodes in graph
        """
        new_number = self.next_node_number
        self.next_node_number += 1

        return new_number

    def add_network(self, network_type, network_id):
        """Adds a new network of specified type

        Parameters
        ----------
        network_type : str
            Specifies the type of the new network as {'heating', 'cooling',
            'electricity', 'gas', 'others'}
        network_id : str
            Name of the new network
        """
        assert network_type in self.network_types, 'Network type not known'
        assert type(network_id) == type(str()), 'Network name must be a string'

        if network_type == 'heating':
            self.nodelists_heating[network_id] = []
        elif network_type == 'cooling':
            self.nodelists_cooling[network_id] = []
        elif network_type == 'electricity':
            self.nodelists_electricity[network_id] = []
        elif network_type == 'gas':
            self.nodelists_gas[network_id] = []
        elif network_type == 'water':
            self.nodelists_water[network_id] = []
        elif network_type == 'others':
            self.nodelists_others[network_id] = []

    def _update_min_max_positions(self, position):
        """Updates values for min_positions and max_positions

        Parameters
        ----------
        position : shapely Point object
            Definition of the node position with a Point object
        """
        if type(position) == type(sg.Point(0, 0)):
            if self.min_position is None:
                self.min_position = position
            else:
                if position.x < self.min_position.x:
                    self.min_position = sg.Point(position.x,
                                                 self.min_position.y)
                if position.x > self.max_position.x:
                    self.max_position = sg.Point(position.x,
                                                 self.max_position.y)
            if self.max_position is None:
                self.max_position = position
            else:
                if position.y < self.min_position.y:
                    self.min_position = sg.Point(self.min_position.x,
                                                 position.y)
                if position.y > self.max_position.y:
                    self.max_position = sg.Point(self.max_position.x,
                                                 position.y)

    def add_building(self, name=None, position=None,
                     is_supply_heating=False,
                     is_supply_cooling=False,
                     is_supply_electricity=False,
                     is_supply_gas=False,
                     is_supply_water=False,
                     is_supply_other=False, ):
        """Adds a building node to the District

        Parameters
        ----------
        name : str, int, or float
            A name for the building represented by this node. If None is given,
            the newly assigned node number will also be used as name.
        position : shapely.geometry.Point object
            New node's position
        is_supply_heating : boolean
            True if the building contains a heat supply unit, False if not
        is_supply_cooling : boolean
            True if the building contains a cooling supply unit, False if not
        is_supply_electricity : boolean
            True if the building contains an electricity supply unit, False if
            not
        is_supply_gas : boolean
            True if the building contains a gas supply unit, False if not
        is_supply_water : boolean
            True if the building contains a water supply unit, False if not
        is_supply_other : boolean
            True if the building contains a supply unit for a network of
            network type other, False if not

        Returns
        -------

        node_number : int
            Number of the added node in the graph
        """
        node_number = self.new_node_number()
        if name is None:
            name = node_number

        self._update_min_max_positions(position)

        self.add_node(node_number,
                      name=name,
                      node_type='building',
                      position=position,
                      is_supply_heating=is_supply_heating,
                      is_supply_cooling=is_supply_cooling,
                      is_supply_electricity=is_supply_electricity,
                      is_supply_gas=is_supply_gas,
                      is_supply_water=is_supply_water,
                      is_supply_other=is_supply_other)

        self.nodelist_building.append(node_number)

        self.nodes_by_name[name] = node_number

        return node_number

    def remove_building(self, node_number):
        """Removes the specified building node from the graph

        Parameters
        ----------
        node_number : int
            Identifier of the node in the graph
        """
        if node_number in self.nodelist_building:
            self.nodelist_building.remove(node_number)
            self.remove_node(node_number)
        else:
            warnings.warn('Node number has not been found in building' +
                          'nodelist. Therefore, node has not been removed.')

    def add_street_node(self, position, block=None, resolution=1e-4,
                        check_overlap=True):
        """Adds a street node to the District

        Parameters
        ----------
        position : shapely.Point object
            Definition of the node position with a shapely Point object
        block : int
            Identifier that indicates to which block the node belongs
        resolution : float
            Minimum distance between two points in m. If new position is closer
            than resolution to another existing node, the existing node will be
            returned, no new node will be created.
        check_overlap : boolean
            By default, the method checks whether the new position overlaps
            an existing network node. This can be skipped for performance
            reasons by setting check_overlap=False

        Returns
        -------
        node_number : int
            Number of the added node in the graph
        """
        node_number = self.new_node_number()

        self._update_min_max_positions(position)

        check_node = None
        if check_overlap is True:
            # Check if there is already a node at the given position
            for node in self.nodelist_street:
                if position.distance(self.node[node]['position']) < resolution:
                    check_node = node

        if check_node is not None:
            if block not in self.node[check_node]['blocks']:
                self.node[check_node]['blocks'].append(block)

            return check_node
        else:
            self.add_node(node_number,
                          node_type='street',
                          blocks=[block],
                          position=position)
            self.nodelist_street.append(node_number)

            return node_number

    def remove_street_node(self, node_number):
        """Removes the specified street node from the graph

        Parameters
        ----------
        node_number : int
            Identifier of the node in the graph
        """
        if node_number in self.nodelist_street:
            self.nodelist_street.remove(node_number)
            self.remove_node(node_number)
        else:
            warnings.warn('Node number has not been found in street ' +
                          'nodelist. Therefore, node has not been removed.')

    def add_network_node(self,
                         network_type,
                         network_id='default',
                         position=None,
                         resolution=1e-4,
                         check_overlap=True):
        """Adds a network node to the District

        A network node should not be placed at positions where there is already
        a node of the same network or a building node.

        Parameters
        ----------
        network_type : str
            Defines the network type into which to add the node. The string
            must be one of the network_types defined in `self.network_types`.
        network_id : str
            Specifies, to which network of the given type the node belongs.
            If no value is given, the network 'default' will be used. Before
            using a `network_id`, it must be added to the district with
            `District.add_network()`
        position : shapely.Point object
            Optional definition of the node position with a shapely Point object
        resolution : float
            Minimum distance between two points in m. If new position is closer
            than resolution to another existing node, the existing node will be
            returned, no new node will be created.
        check_overlap : boolean
            By default, the method checks whether the new position overlaps
            an existing network node. This can be skipped for performance
            reasons by setting check_overlap=False

        Returns
        -------
        node_number : int
            Number of the added node in the graph
        """
        assert network_type in self.network_types, 'Unknown network type'
        node_number = self.new_node_number()

        self._update_min_max_positions(position)

        if network_type == 'heating':
            nodelist = self.nodelists_heating[network_id]
        elif network_type == 'cooling':
            nodelist = self.nodelists_cooling[network_id]
        elif network_type == 'electricity':
            nodelist = self.nodelists_electricity[network_id]
        elif network_type == 'gas':
            nodelist = self.nodelists_gas[network_id]
        elif network_type == 'water':
            nodelist = self.nodelists_water[network_id]
        elif network_type == 'others':
            nodelist = self.nodelists_others[network_id]

        # Check if there is already a node at the given position
        if check_overlap is True:
            check_node = None

            for node in nodelist:
                if position.distance(self.node[node]['position']) < resolution:
                    check_node = node
            if check_node is None:
                for node in self.nodelist_building:
                    if position.distance(self.node[node][
                                             'position']) < resolution:
                        check_node = node

            if check_node is not None:
                return check_node
            else:
                self.add_node(node_number,
                              node_type='network_' + network_type,
                              network_id=network_id,
                              position=position)
                if network_type == 'heating':
                    nodelist.append(node_number)
                elif network_type == 'cooling':
                    nodelist.append(node_number)
                elif network_type == 'electricity':
                    nodelist.append(node_number)
                elif network_type == 'gas':
                    nodelist.append(node_number)
                elif network_type == 'water':
                    nodelist.append(node_number)
                elif network_type == 'others':
                    nodelist.append(node_number)
        else:
            self.add_node(node_number,
                          node_type='network_' + network_type,
                          network_id=network_id,
                          position=position)
            if network_type == 'heating':
                nodelist.append(node_number)
            elif network_type == 'cooling':
                nodelist.append(node_number)
            elif network_type == 'electricity':
                nodelist.append(node_number)
            elif network_type == 'gas':
                nodelist.append(node_number)
            elif network_type == 'water':
                nodelist.append(node_number)
            elif network_type == 'others':
                nodelist.append(node_number)

        return node_number

    def remove_network_node(self, node_number):
        """Removes the specified network node from the graph

        Parameters
        ----------
        node_number : int
            Identifier of the node in the graph
        """
        #  Search for occurrence of node number within different network dicts
        network_list = [self.nodelists_heating, self.nodelists_cooling,
                        self.nodelists_electricity, self.nodelists_gas,
                        self.nodelists_others]

        found_node = False

        for nodelists in network_list:  # Loop over dictionary list
            for network in nodelists:  # Loop over keys (networks of same type)
                for node_id in nodelists[network]:  # Loop over node numbers
                    if node_id == node_number:
                        found_node = True
                        found_nodelists = nodelists
                        found_network = network
                        break

        if found_node:
            #  Remove element from nodelist
            found_nodelists[found_network].remove(node_number)
            #  Remove node from graph
            self.remove_node(node_number)
        else:
            warnings.warn('Chosen node number is not part of any network ' +
                          'dict. Cannot be removed.')

    def get_building_node(self, name):
        """Returns the node number for a given building name

        Parameters
        ----------
        name : str
            Name of the building

        Returns
        -------
        node_number : int
            Number of the corresponding node
        """
        if name in self.nodes_by_name.keys():
            return self.nodes_by_name[name]
        else:
            print(name, 'not known')

    def get_node_by_position(self, position, resolution=1e-4):
        """
        Returns node name and node_nb for node(s) on input position.
        If no node is placed on position, returns empty dictionary.

        Parameters
        ----------
        positions : dict
            In general, positions in uesgraphs are defined by
            `shapely.geometry.point` objects. This attribute converts the
            positions into a dict of numpy arrays only for use in
            uesgraphs.visuals, as the networkx drawing functions need this
            format.
        resolution : float
            Minimum distance between two points in m. If  position is closer
            than resolution to another existing node, the existing node will be
            returned.

        Returns
        -------
        result_dict : dict
            Dictionary of nodes on input position (key: node_id, value: name)
        """
        result_dict = {}

        for node in self:
            if 'position' in self.node[node]:
                #  If positions are identical, save name and node_id to dict
                if self.node[node]['position'].distance(position) < resolution:
                    node_name = self.node[node]['name']
                    result_dict[node] = node_name

        return result_dict

    def add_empty_edges(self):
        """
        Connects every pair of uesgraph nodes with network edges.
        """
        for pair in list(combinations(self.nodes(),2)):
            p1,p2=pair
            self.add_edge(p1,p2,heatpipe=None,
                          coolpipe=None,
                          electriccable=None,
                          gascable=None,
                          watercable=None,
                          transportation=None)

    def add_network_edge(self, u, v,
                         network_type,
                         lenghthFactor=1):
        """
        Defines a physical connection between nodes with.

        Parameters
        ----------
        network_type : str
            Defines the network type into which to add the node. The string
            must be one of the network_types defined in `self.network_types`.
        lengthFactor: float >=1
            Defines the length of the transportation medium.


        Example
        -------
            NodeA and NodeB are connected with an electrical cable
            The length of the cable is 1.2 times bigger than the distance between these nodes
            >>>cityDistrict.add_network_edge(NodeA, NodeB, network_type='electricity',lenghthFactor=1.2)


        Returns
        -------
        node_number : int
            Number of the added node in the graph
        """

        assert network_type in self.network_types, 'Unknown network type'

        edge_numbers = u, v

        a,b=self.node[u]['position'], self.node[v]['position']
        distance=math.hypot(b.y - a.y,b.x - a.x)


        if network_type == 'heating':
            self.edgelist_heating.append(edge_numbers)
            self.edge[u][v]['heatpipe']=HeatPipe(self._environment,distance*lenghthFactor,self._heatPipeD,self._heatPipeSpCond)
        elif network_type == 'cooling':
            self.edgelist_cooling.append(edge_numbers)
            self.edge[u][v]['coolpipe']=HeatPipe(self._environment,distance*lenghthFactor,self._heatPipeD,self._heatPipeSpCond)
        elif network_type == 'electricity':
            self.edgelist_electricity.append(edge_numbers)
            self.edge[u][v]['electriccable'] = Cable(self._environment,distance*lenghthFactor,self._cableD,self._cableSpRes)
        elif network_type == 'gas':
            self.edgelist_gas.append(edge_numbers)
            self.edge[u][v]['gaspipe'] = GasPipe(self._environment,distance*lenghthFactor,self._gasPipeD,self._gasPipeRho,self._gasPipeLambda)
        elif network_type == 'water':
            self.edgelist_water.append(edge_numbers)
            self.edge[u][v]['waterpipe'] = WaterPipe(self._environment,distance*lenghthFactor,self._waterPipeD,self._waterPipeRho,self._waterPipeLambda)
        elif network_type == 'others':
            self.edgelist_others.append(edge_numbers)
            self.edge[u][v]['transportation'] = 'othermedium'

        return u,v

    def create_subgraphs(self, network_type,
                         all_buildings=True,
                         streets=False):
        """Returns a list of subgraphs for each network

        Parameters
        ----------
        network_type : str
            One of the network types defined in `self.network_types`. The
            subgraphs for all networks of the chosen network type will be
            returned
        all_buildings : boolean
            Subgraphs will contain all buildings of uesgraph when
            `all_buildings` is True. If False, only those buildings connected
            to a subgraph's network will be part of the corresponding subgraph
        streets : boolean
            Subgraphs will contain streets if `streets` is True.

        Returns
        -------

        subgraphs : list
            List of uesgraph elements for all networks of chosen `network_type`
        """
        assert network_type in self.network_types or network_type is None or \
               network_type == 'proximity', 'Network type not known'

        if network_type == 'heating':
            nodelists = self.nodelists_heating
        elif network_type == 'cooling':
            nodelists = self.nodelists_cooling
        elif network_type == 'electricity':
            nodelists = self.nodelists_electricity
        elif network_type == 'gas':
            nodelists = self.nodelists_gas
        elif network_type == 'water':
            nodelists = self.nodelists_water
        elif network_type == 'others':
            nodelists = self.nodelists_others
        elif network_type is None:
            nodelists = {}

        subgraphs = {}

        if network_type is not None and network_type != 'proximity':
            if nodelists != {'default': []}:
                for network_id in nodelists.keys():
                    # Largely copied from nx.Graph.subgraphs()
                    bunch = nodelists[network_id] + self.nodelist_building
                    # create new graph and copy subgraph into it
                    H = self.__class__()
                    H.max_position = self.max_position
                    H.min_position = self.min_position
                    # copy node and attribute dictionaries
                    for n in bunch:
                        H.node[n] = self.node[n]
                    # namespace shortcuts for speed
                    H_adj = H.adj
                    self_adj = self.adj
                    # add nodes and edges (undirected method)
                    for n in H.node:
                        Hnbrs = {}
                        H_adj[n] = Hnbrs
                        for nbr, d in self_adj[n].items():
                            if nbr in H_adj:
                                # add both representations of edge: n-nbr and
                                # nbr-n
                                Hnbrs[nbr] = d
                                H_adj[nbr][n] = d
                    H.graph = self.graph
                    for building in self.nodelist_building:
                        H.nodelist_building.append(building)
                    if network_type == 'heating':
                        H.nodelists_heating[
                            network_id] = self.nodelists_heating[network_id]
                    elif network_type == 'cooling':
                        H.nodelists_cooling[
                            network_id] = self.nodelists_cooling[network_id]
                    elif network_type == 'electricity':
                        H.nodelists_electricity[
                            network_id] = self.nodelists_electricity[
                            network_id]
                    elif network_type == 'gas':
                        H.nodelists_gas[
                            network_id] = self.nodelists_gas[network_id]
                    elif network_type == 'water':
                        H.nodelists_water[
                            network_id] = self.nodelists_water[network_id]
                    elif network_type == 'others':
                        H.nodelists_others[
                            network_id] = self.nodelists_others[network_id]
                    H.nodes_by_name = self.nodes_by_name
                    subgraphs[network_id] = H

            if all_buildings is False:
                for network_id in subgraphs.keys():
                    to_remove = []
                    for building in subgraphs[network_id].nodelist_building:
                        if nx.degree(subgraphs[network_id], building) == 0:
                            to_remove.append(building)
                    for remove_me in to_remove:
                        subgraphs[network_id].remove_building(remove_me)
        elif network_type is None:
            # create new graph and copy subgraph into it
            H = self.__class__()
            for building in self.nodelist_building:
                if all_buildings is True:
                    H.node[building] = self.node[building]
                    H.nodelist_building.append(building)
                    H._update_min_max_positions(self.node[building][
                                                    'position'])
                else:
                    if (self.node[building]['is_supply_heating'] is False and
                                self.node[building][
                                    'is_supply_cooling'] is False and
                                self.node[building][
                                    'is_supply_electricity'] is False and
                                self.node[building][
                                    'is_supply_gas'] is False and
                                self.node[building][
                                    'is_supply_water'] is False and
                                self.node[building][
                                    'is_supply_other'] is False):
                        H.node[building] = self.node[building]
                        H.nodelist_building.append(building)
                        H._update_min_max_positions(self.node[building][
                                                        'position'])

            subgraphs['default'] = H

        if streets is True:
            for network_id in subgraphs.keys():
                # namespace shortcuts for speed
                H_adj = H.adj
                self_adj = self.adj
                # add nodes and edges for streets
                for n in self.nodelist_street:
                    Hnbrs = {}
                    H_adj[n] = Hnbrs
                    for nbr, d in self_adj[n].items():
                        if nbr in H_adj:
                            if nbr in self.nodelist_street:
                                # add both representations of edge: n-nbr and
                                # nbr-n
                                Hnbrs[nbr] = d
                                H_adj[nbr][n] = d
                    H.nodelist_street.append(n)

        if network_type == 'proximity' and 'proximity' in self.graph:
            H = copy.deepcopy(self)
            H.min_position = None
            H_max_position = None
            proximity = self.graph['proximity']
            for node in self.nodes():
                position = self.node[node]['position']
                if not proximity.contains(position):
                    node_type = self.node[node]['node_type']
                    if 'network' in node_type:
                        H.remove_network_node(node)
                    elif 'building' in node_type:
                        H.remove_building(node)
                    elif 'street' in node_type:
                        H.remove_street_node(node)
            prox_bounds = self.graph['proximity'].bounds
            new_min = sg.Point(prox_bounds[0], prox_bounds[1])
            new_max = sg.Point(prox_bounds[2], prox_bounds[3])
            H.min_position = new_min
            H.max_position = new_max
            return H

        return subgraphs

    def from_json(self, path, network_type, network_id=None):
        """Imports network from json input

        Parameters
        ----------
        path : str
            Path, where input files `substations.json`, `nodes.json`,
            `pipes.json` and `supply.json` are located.
        network_type : str
            Specifies the type of the destination network as {'heating',
            'cooling', 'electricity', 'gas', 'others'}
        network_id : str
            Name of the destination network; If `network_id` is None initially,
            `network_id = `default` will be used
        """
        node_mapping = {}  # input node number => uesgraphs node number

        # Read nodes to dict
        print('    read nodes...')
        input_file = os.path.join(path, 'nodes.json')
        with open(input_file, 'r') as input:
            nodes = json.load(input)
        if 'input_id' in nodes['meta']:
            self.input_ids['nodes'] = nodes['meta']['input_id']

        print('******')
        for node in nodes['data'].keys():
            if 'longitude' in nodes['data'][node] and 'latitude' in nodes[
                'data'][node]:
                this_position = sg.Point(nodes['data'][node]['longitude'],
                                         nodes['data'][node]['latitude'])
                nodes['data'][node]['position'] = this_position
            elif 'x' in nodes['data'][node] and 'y' in nodes['data'][node]:
                this_position = sg.Point(nodes['data'][node]['x'],
                                         nodes['data'][node]['y'])
                nodes['data'][node]['position'] = this_position
            else:
                warnings.warn('No spatial data input data for '
                              'node {}'.format(node))

        # Add buildings
        print('    read buildings...')
        input_file = os.path.join(path, 'buildings.json')
        with open(input_file, 'r') as input:
            buildings = json.load(input)
        if 'input_id' in buildings['meta']:
            self.input_ids['buildings'] = buildings['meta']['input_id']

        print('******')
        for building in buildings['data'].keys():
            building_id = buildings['data'][building]['name']

            if building_id not in self.nodes_by_name.keys():
                if building in nodes['data']:
                    this_position = nodes['data'][building]['position']
                else:
                    if 'longitude' in buildings['data'][building] and \
                                    'latitude' in buildings['data'][building]:
                        this_position = sg.Point(
                            buildings['data'][building]['longitude'],
                            buildings['data'][building]['latitude'])
                        # nodes['data'][building]['position'] = this_position

                        print('building', building)
                        print('this_position', this_position)

                    elif 'x' in buildings['data'][building] and 'y' in \
                            nodes['data'][building]:
                        this_position = sg.Point(buildings['data'][
                                                     building]['x'],
                                                 buildings['data'][
                                                     building]['y'])
                        # buildings['data'][building]['position'] = this_position

                building_node = self.add_building(name=building_id,
                                                  position=this_position)
            else:
                building_node = self.nodes_by_name[building_id]

            node_mapping[int(building)] = building_node

            if str(building) in nodes['data'].keys():
                del nodes['data'][str(building)]

        # Add supplies
        print('    read supplies...')
        input_file = os.path.join(path, 'supplies.json')
        with open(input_file, 'r') as input:
            supplies = json.load(input)
        if 'input_id' in supplies['meta']:
            self.input_ids['supplies'] = supplies['meta']['input_id']

        print('******')
        for supply in supplies['data'].keys():
            supply_id = supplies['data'][supply]['name']

            if supply_id not in self.nodes_by_name.keys():
                this_position = nodes['data'][supply]['position']
                supply_node = self.add_building(name=supply_id,
                                                position=this_position,
                                                is_supply_heating=True)
            else:
                supply_node = self.nodes_by_name[supply_id]

            node_mapping[int(supply)] = supply_node

            if str(supply) in nodes['data'].keys():
                del nodes['data'][str(supply)]

        # Add network nodes from list of so far unused network nodes
        for node in nodes['data'].keys():
            new_node = self.add_network_node(network_type=network_type,
                                             position=nodes['data'][node][
                                                 'position'],
                                             resolution=1e-9,
                                             check_overlap=False)

            if 'name' in nodes['data'][node]:
                self.node[new_node]['name'] = nodes['data'][node]['name']
                self.nodes_by_name[self.node[new_node]['name']] = new_node

            node_mapping[int(node)] = new_node

        # Add edges
        print('    read edges...')
        input_file = os.path.join(path, 'pipes.json')
        with open(input_file, 'r') as input:
            pipes = json.load(input)
        if 'input_id' in pipes['meta']:
            self.input_ids['pipes'] = pipes['meta']['input_id']

        print('******')
        for pipe in pipes['data'].keys():
            if 'pipeID' in pipes['data'][pipe]:
                pipe_id = pipes['data'][pipe]['pipeID']
            else:
                pipe_id = pipe

            if 'diameter_inner' in pipes['data'][pipe]:
                diameter = pipes['data'][pipe]['diameter_inner']
            elif 'diameter' in pipes['data'][pipe]:
                diameter = pipes['data'][pipe]['diameter']
            # else:
            #     diameter = 0.1

            if diameter != 999:
                diameter = round(diameter, 3)
                assert diameter > 0, 'Diameter must be greater than 0'

            node_0 = node_mapping[pipes['data'][pipe]['node_0']]
            node_1 = node_mapping[pipes['data'][pipe]['node_1']]

            self.add_edge(node_0,
                          node_1,
                          pipeID=pipe_id,
                          diameter=diameter,
                          )
            if 'length' in pipes['data'][pipe]:
                self.edge[node_0][node_1]['length'] = pipes['data'][pipe][
                    'length']
            if 'G' in pipes['data'][pipe]:
                self.edge[node_0][node_1]['G'] = pipes['data'][pipe]['G']

            self.pipeIDs.append(int(pipe_id))

        print(' input_ids were', self.input_ids)
        print('...finished')

    def to_json(self, path, name, description='json export from uesgraph'):
        """Saves uesgraph structure to json files

        Parameters
        ----------
        path : str
            Path, where a directory with output files will be created.
        name : str
            The newly created output directory at `path` will be named
            `<name>HeatingUES`
        description : str
            A description string that will be written to all json output
            files' meta data.
        """
        workspace = os.path.join(path)
        if not os.path.exists(workspace):
            os.mkdir(workspace)

        nodes = {}
        pipes = {}
        buildings = {}
        supplies = {}

        meta = {'description': description,
                'source': 'uesgraphs',
                'name': name,
                'created': str(datetime.datetime.now()),
                'simplification_level': self.simplification_level,
                }

        # Write node data from uesgraph to dict for json output
        node_data = {}
        for node in self.nodes():
            node_data[node] = {'x': self.node[node]['position'].x,
                               'y': self.node[node]['position'].y,
                               }
            if 'name' in self.node[node]:
                node_data[node]['name'] = self.node[node]['name']
            else:
                node_data[node]['name'] = str(node)

        nodes['meta'] = {}
        for key in meta.keys():
            nodes['meta'][key] = meta[key]
        nodes['meta']['type'] = 'nodes input data'
        nodes['meta']['input_id'] = str(uuid.uuid4())
        nodes['data'] = node_data

        # Write pipe data from uesgraph to dict for json output
        pipe_data = {}
        for edge in self.edges():
            if 'pipeID' in self.edge[edge[0]][edge[1]]:
                try:
                    pipe_id = str(int(self.edge[edge[0]][edge[1]]['pipeID']))
                except:
                    pipe_id = self.edge[edge[0]][edge[1]]['pipeID']
            else:
                pipe_id = str(edge[0]) + str(edge[1])
            pipe_data[str(pipe_id)] = {'node_0': edge[0],
                                       'node_1': edge[1],
                                       }

            if 'length' in self.edge[edge[0]][edge[1]]:
                length = self.edge[edge[0]][edge[1]]['length']
            else:
                pos_0 = self.node[edge[0]]['position']
                pos_1 = self.node[edge[1]]['position']
                length = pos_0.distance(pos_1)
            pipe_data[str(pipe_id)]['length'] = length

            if 'diameter' in self.edge[edge[0]][edge[1]]:
                diameter = self.edge[edge[0]][edge[1]]['diameter']
                pipe_data[str(pipe_id)]['diameter'] = diameter

            if 'G' in self.edge[edge[0]][edge[1]]:
                G = self.edge[edge[0]][edge[1]]['G']
                pipe_data[str(pipe_id)]['G'] = G

            pipe_data[str(pipe_id)]['pipeID'] = pipe_id

        pipes['meta'] = {}
        for key in meta.keys():
            pipes['meta'][key] = meta[key]
        pipes['meta']['type'] = 'pipes input data'
        pipes['meta']['units'] = {'diameter': 'm',
                                  'length': 'm',
                                  }
        pipes['meta']['input_id'] = str(uuid.uuid4())
        pipes['data'] = pipe_data

        # Write building and supply data from uesgraph to dict for json output
        building_data = {}
        supply_data = {}
        for node in self.nodelist_building:
            if self.node[node]['is_supply_heating'] is True:
                supply_data[node] = {'x': self.node[node]['position'].x,
                                     'y': self.node[node]['position'].y,
                                     'name': self.node[node]['name'],
                                     }
            else:
                building_data[node] = {'x': self.node[node]['position'].x,
                                       'y': self.node[node]['position'].y,
                                       'name': self.node[node]['name'],
                                       }

                if 'heating' in self.node[node]:
                    if 'Kv' in self.node[node]['heating']:
                        Kv = self.node[node]['heating']['Kv']
                        building_data[node]['Kv'] = Kv
                    if 'dp_nom' in self.node[node]['heating']:
                        Kv = self.node[node]['heating']['dp_nom']
                        building_data[node]['Kv'] = Kv
                    if 'm_flow_nom' in self.node[node]['heating']:
                        Kv = self.node[node]['heating']['m_flow_nom']
                        building_data[node]['Kv'] = Kv

        buildings['meta'] = {}
        for key in meta.keys():
            buildings['meta'][key] = meta[key]
        buildings['meta']['type'] = 'buildings input data'
        buildings['meta']['input_id'] = str(uuid.uuid4())
        buildings['data'] = building_data

        supplies['meta'] = {}
        for key in meta.keys():
            supplies['meta'][key] = meta[key]
        supplies['meta']['type'] = 'supply input data'
        supplies['meta']['input_id'] = str(uuid.uuid4())
        supplies['data'] = supply_data

        # Write json files
        with open(os.path.join(workspace, 'nodes.json'), 'w') as outfile:
            json.dump(nodes, outfile,
                      indent=4
                      )
        with open(os.path.join(workspace, 'pipes.json'), 'w') as outfile:
            json.dump(pipes, outfile,
                      indent=4
                      )
        with open(os.path.join(workspace, 'buildings.json'), 'w') as outfile:
            json.dump(buildings, outfile,
                      indent=4
                      )
        with open(os.path.join(workspace, 'supplies.json'), 'w') as outfile:
            json.dump(supplies, outfile,
                      indent=4
                      )

    def from_csv(self, path, network_type, network_id=None):
        """Imports old csv input

        This may be discontinued with development of an improved file format,
        e.g. via CityGML

        Parameters
        ----------
        path : str
            Path, where input files `demand.csv`, `nodes.csv`, `pipes.csv` and
            `supply.csv` are located. These input files follow the format from
            the Campus 1 project.
        network_type : str
            Specifies the type of the destination network as {'heating',
            'cooling', 'electricity', 'gas', 'others'}
        network_id : str
            Name of the destination network; If `network_id` is None initially,
            `network_id = `default` will be
            used

        Notes
        -----
        The demand file contains 10 columns:
            # of demand,
            # of node,
            Kv value in m3/h,
            nominal differential pressure in Pa,
            nominal mass flow rate in kg/s,
            # of building,
            addition to # of building,
            binary use_tables,
            x coordinate,
            y coordinate

        The node file contains 3 columns:
            # of node,
            x coordinate,
            y coordinate

        The supply file contains 10 columns:
            # of supply,
            # of node,
            n/a,
            n/a,
            n/a,
            n/a,
            n/a,
            n/a,
            x coordinate,
            y coordinate
        (Most columns are currently not used, the number of columns is a result
        of keeping the possibility to combine demand and supply in one table)

        The pipes file contains 6 columns:
            # of pipe,
            # of first connected node,
            # of second connected node,
            length of pipe in m,
            diameter of pipe in m,
            G-Value of the pipe insulation
        """
        csv_nodes = {}
        node_mapping = {}  # csv node number => uesgraphs node number
        # Read nodes to dict
        print('    read nodes...')
        input_file = os.path.join(path, 'nodes.csv')
        nodes_input = pd.read_csv(input_file,
                                  header=None,
                                  sep=',',
                                  index_col=0,
                                  names=['node', 'x', 'y'])
        print('******')
        for i in nodes_input.index:
            this_position = sg.Point(nodes_input.loc[i, 'x'],
                                     nodes_input.loc[i, 'y'])
            csv_nodes[i] = this_position

        # Add buildings
        print('    read buildings...')
        input_file = os.path.join(path, 'demand.csv')
        demand_input = pd.read_csv(input_file,
                                   header=None,
                                   sep=',',
                                   index_col=1,
                                   names=['demand_id', 'node',
                                          'Kv', 'dp_nom', 'm_flow_nom',
                                          'building_id_1',
                                          'building_id_2',
                                          'use_tables',
                                          'x', 'y']
                                   )
        print('******')
        for i in demand_input.index:
            this_position = sg.Point(demand_input.loc[i, 'x'],
                                     demand_input.loc[i, 'y'])

            building_id = str(int(demand_input.loc[i, 'building_id_1']))
            if demand_input.loc[i, 'building_id_2'] != 0:
                building_id += chr(int(demand_input.loc[i, 'building_id_2']))

            if building_id not in self.nodes_by_name.keys():
                building = self.add_building(name=building_id,
                                             position=this_position)
            else:
                building = self.nodes_by_name[building_id]

            if 'network_type' not in self.node[building]:
                self.node[building][network_type] = {}
            if demand_input.loc[i, 'Kv'] != 999:
                Kv = float(demand_input.loc[i, 'Kv'])
                self.node[building][network_type]['Kv'] = Kv

            if demand_input.loc[i, 'm_flow_nom'] != 999 and \
                            demand_input.loc[i, 'm_flow_nom'] != 0:
                m_flow_nom = demand_input.loc[i, 'm_flow_nom']
                self.node[building][network_type]['m_flow_nom'] = m_flow_nom

            if demand_input.loc[i, 'dp_nom'] != 999 and \
                            demand_input.loc[i, 'dp_nom'] != 0:
                dp_nom = demand_input.loc[i, 'dp_nom']
                self.node[building][network_type]['dp_nom'] = dp_nom

            node_mapping[i] = building
            nodes_input = nodes_input.drop(i)

        # Add supplies
        print('    read supplies...')
        input_file = os.path.join(path, 'supply.csv')
        supply_input = pd.read_csv(input_file,
                                   header=None,
                                   sep=',',
                                   index_col=1,
                                   names=['supply_id', 'node',
                                          'Kv', 'dp_nom', 'm_flow_nom',
                                          'building_id_1',
                                          'building_id_2',
                                          'use_tables',
                                          'x', 'y']
                                   )
        print('******')
        for i in supply_input.index:
            this_position = sg.Point(supply_input.loc[i, 'x'],
                                     supply_input.loc[i, 'y'])

            if network_type == 'heating':
                curr_name = supply_input.loc[i, 'supply_id']
                curr_name = int(curr_name)
                supply = self.add_building(name=curr_name,
                                           position=this_position,
                                           is_supply_heating=True)
            elif network_type == 'cooling':
                supply = self.add_building(name=supply_input.loc[i,
                                                                 'supply_id'],
                                           position=this_position,
                                           is_supply_cooling=True)
            node_mapping[i] = supply
            nodes_input = nodes_input.drop(i)

        # Add network nodes from list of so far unused network nodes
        for i in nodes_input.index:
            new_node = self.add_network_node(network_type=network_type,
                                             position=csv_nodes[i],
                                             resolution=1e-9,
                                             check_overlap=False)
            node_mapping[i] = new_node

        # Add edges
        print('    read edges...')
        input_file = os.path.join(path, 'pipes.csv')
        pipe_input = pd.read_csv(input_file,
                                 header=None,
                                 sep=',',
                                 index_col=0,
                                 names=['pipe_id',
                                        'node_0',
                                        'node_1',
                                        'length',
                                        'diameter',
                                        'G']
                                 )

        print('******')
        for i in pipe_input.index:
            if pipe_input.loc[i, 'diameter'] != 999:
                diameter = round(pipe_input.loc[i, 'diameter'], 3)
                assert diameter > 0, 'Diameter must be greater than 0'
                self.add_edge(node_mapping[pipe_input.loc[i, 'node_0']],
                              node_mapping[pipe_input.loc[i, 'node_1']],
                              pipeID=i,
                              length=pipe_input.loc[i, 'length'],
                              diameter=diameter,
                              G=pipe_input.loc[i, 'G']
                              )
            else:
                self.add_edge(node_mapping[pipe_input.loc[i, 'node_0']],
                              node_mapping[pipe_input.loc[i, 'node_1']],
                              pipeID=i,
                              length=pipe_input.loc[i, 'length'],
                              diameter=0.1,
                              G=pipe_input.loc[i, 'G']
                              )
        print('...finished')

    def to_csv(self, path, name='Test'):
        """Saves uesgraph structure to old csv input

        This may be discontinued with development of an improved file format,
        e.g. via CityGML

        Parameters
        ----------
        path : str
            Path, where a directory with output files `demand.csv`,
            `nodes.csv`, `pipes.csv` and `supply.csv` will be created. These
            output files follow the format from the Campus 1 project.
        name : str
            The newly created output directory at `path` will be named
            `<name>HeatingUES`

        Notes
        -----
        The demand file contains 10 columns:
            # of demand,
            # of node,
            Kv value in m3/h,
            nominal differential pressure in Pa,
            nominal mass flow rate in kg/s,
            # of building,
            addition to # of building,
            binary use_tables,
            x coordinate,
            y coordinate

        The node file contains 3 columns:
            # of node,
            x coordinate,
            y coordinate

        The supply file contains 10 columns:
            # of supply,
            # of node,
            n/a,
            n/a,
            n/a,
            n/a,
            n/a,
            n/a,
            x coordinate,
            y coordinate
        (Most columns are currently not used, the number of columns is a result
        of keeping the possibility to combine demand and supply in one table)

        The pipes file contains 6 columns:
            # of pipe,
            # of first connected node,
            # of second connected node,
            length of pipe in m,
            diameter of pipe in m,
            G-Value of the pipe insulation
        """
        workspace = os.path.join(path, name + 'HeatingUES')
        if not os.path.exists(workspace):
            os.mkdir(workspace)

        nodes_output = open(os.path.join(workspace, 'nodes.csv'), 'w').close()
        nodes_output = open(os.path.join(workspace, 'nodes.csv'), 'w')
        for node in self.nodes():
            nodes_output.write(str(node) + ',' +
                               str(float(self.node[node]['position'].x)) +
                               ',' +
                               str(float(self.node[node]['position'].y)) +
                               '\n')
        nodes_output.close()

        demand_output = open(os.path.join(workspace, 'demand.csv'),
                             'w').close()
        demand_output = open(os.path.join(workspace, 'demand.csv'), 'w')
        supply_output = open(os.path.join(workspace, 'supply.csv'),
                             'w').close()
        supply_output = open(os.path.join(workspace, 'supply.csv'), 'w')
        for node in self.nodelist_building:
            if self.node[node]['is_supply_heating'] is True:
                supply_output.write(str(self.node[node]['name']) + ',' +
                                    str(node) + ',' +
                                    '999' + ',' +
                                    '999' + ',' +
                                    '999' + ',' +
                                    '999' + ',' +
                                    '0' + ',' +
                                    '0' + ',' +
                                    str(float(self.node[node]['position'].x)) +
                                    ',' +
                                    str(float(self.node[node]['position'].y)) +
                                    '\n')
            else:
                demand_output.write(str(self.node[node]['name']) + ',' +
                                    str(node) + ',' +
                                    '999' + ',' +
                                    '999' + ',' +
                                    '999' + ',' +
                                    str(self.node[node]['name']) + ',' +
                                    '0' + ',' +
                                    '0' + ',' +
                                    str(float(self.node[node]['position'].x)) +
                                    ',' +
                                    str(float(self.node[node]['position'].y)) +
                                    '\n')
        demand_output.close()
        supply_output.close()

        pipes_output = open(os.path.join(workspace, 'pipes.csv'),
                            'w').close()
        pipes_output = open(os.path.join(workspace, 'pipes.csv'), 'w')
        counter = 9000
        for edge in self.edges():
            counter += 1
            if 'G' in self.edge[edge[0]][edge[1]]:
                G = str(self.edge[edge[0]][edge[1]]['G'])
            else:
                G = '999'
            if 'length' in self.edge[edge[0]][edge[1]]:
                length = str(self.edge[edge[0]][edge[1]]['length'])
            else:
                length = str(float(self.node[edge[0]][
                                       'position'].distance(self.node[edge[1]]['position'])))
            if 'diameter' in self.edge[edge[0]][edge[1]]:
                diameter = str(self.edge[edge[0]][edge[1]]['diameter'])
            elif 'diameter_heating' in self.edge[edge[0]][edge[1]]:
                diameter = diameter = str(self.edge[edge[0]][
                                              edge[1]]['diameter_heating'])
            else:
                diameter = '999'

            pipes_output.write(str(counter) + ',' +
                               str(edge[0]) + ',' +
                               str(edge[1]) + ',' +
                               length +
                               ',' +
                               diameter +
                               ',' +
                               G + '\n')
        pipes_output.close()

    def from_osm(self, osm_file, name=None, check_boundary=False,
                 add_str_info=False):
        """Imports buildings and streets from OpenStreetMap data in `osm_file`

        Parameters
        ----------
        osm_file : str
            Full path to osm input file
        name : str
            Name of the city for boundary check
        check_boundary : boolean
            If True, the city boundary will be extracted from the osm file and
            only nodes within this boundary will be accepted
        add_str_info : boolean, optional
            Defines, if network_type = 'street' should be added to street
            egdes (default: False). If set to True, network_type = 'street' is
            added as edge parameter

        Returns
        -------
        self : uesgraph object
            UESGraph for the district read from osm data
        """
        print('Starting import from OpenStreetMap file')
        root = xml.etree.ElementTree.parse(osm_file).getroot()

        # Write all node positions to dict
        print('Reading node positions to dict...')
        nodes = {}
        for node in root.findall('node'):
            lon = float(node.get('lon'))
            lat = float(node.get('lat'))
            nodes[node.get('id')] = {'lon': lon,
                                     'lat': lat,
                                     }

        # Define street tags to be used in uesgraph
        street_tags = ['motorway',
                       'trunk',
                       'primary',
                       'secondary',
                       'tertiary',
                       'unclassified',
                       'residential',
                       'service',
                       ]

        streets = []
        # Get city boundaries
        print('Creating boundary polygon...')
        if check_boundary is True:
            city_boundaries_ways = []
            way_counter = 0
            for relation in root.findall('relation'):
                for tag in relation.findall('tag'):
                    if tag.get('k') == 'name' and tag.get(
                            'v') == name:
                        for member in relation.findall('member'):
                            if member.get('type') == 'way':
                                curr_ref = member.get('ref')
                                for way in root.findall('way'):
                                    if way.get('id') == curr_ref:
                                        curr_points = []
                                        for nd in way.findall('nd'):
                                            curr_lon = nodes[nd.get('ref')][
                                                'lon']
                                            curr_lat = nodes[nd.get('ref')][
                                                'lat']
                                            curr_points.append(sg.Point(
                                                curr_lon, curr_lat))
                                        curr_way = sg.LineString(curr_points)
                                        city_boundaries_ways.append(curr_way)
                                        way_counter += 1

            # Create one boundary polygon
            end_points = []
            boundary_coords = []
            unused_boundaries = []
            for city_boundaries_way in city_boundaries_ways[1:]:
                unused_boundaries.append(city_boundaries_way)
            for i in range(len(city_boundaries_ways)):
                if i == 0:
                    for coords in city_boundaries_ways[i].coords:
                        boundary_coords.append(coords)
                else:
                    distances = {}
                    curr_end = boundary_coords[-1]
                    curr_end_point = sg.Point(curr_end[0], curr_end[1])
                    end_points.append(curr_end_point)
                    for j in range(len(unused_boundaries)):
                        next_start = unused_boundaries[j].coords[0]
                        next_start_point = sg.Point(next_start[0], next_start[1])
                        distance_0 = curr_end_point.distance(next_start_point)
                        next_end = unused_boundaries[j].coords[-1]
                        next_end_point = sg.Point(next_end[0], next_end[1])
                        distance_1 = curr_end_point.distance(next_end_point)
                        distances[distance_0] = [j, 0]
                        distances[distance_1] = [j, 1]

                    min_distance = min(distances.keys())
                    nearest_boundary = distances[min_distance][0]
                    if distances[min_distance][1] == 0:
                        for coords in unused_boundaries[nearest_boundary].coords:
                            boundary_coords.append(coords)
                    elif distances[min_distance][1] == 1:
                        for coords in unused_boundaries[
                                          nearest_boundary].coords[::-1]:
                            boundary_coords.append(coords)
                    del unused_boundaries[distances[min_distance][0]]
            city_boundary = sg.Polygon(boundary_coords)

        # Read buildings and streets
        print('Read building polygons and street ways...')
        all_building_data = {}
        all_street_ways = []
        for way in root.findall('way'):
            curr_positions = []
            curr_dict = {}
            is_building = False
            for nd in way.findall('nd'):
                curr_lat = float(nodes[nd.get('ref')]['lat'])
                curr_lon = float(nodes[nd.get('ref')]['lon'])
                curr_positions.append((curr_lon, curr_lat))
            for tag in way.findall('tag'):
                if tag.get('k') == 'building':  # and tag.get('v') != 'no':
                    if len(curr_positions) > 2:
                        curr_way = sg.Polygon(curr_positions)
                        curr_dict['polygon'] = curr_way
                        is_building = True
                if tag.get('k') == 'addr:housenumber':
                    curr_dict['addr:housenumber'] = tag.get('v')
                if tag.get('k') == 'addr:street':
                    curr_dict['addr:' \
                              'street'] = tag.get('v')
                if tag.get('k') == 'highway' and tag.get('v') in street_tags:
                    all_street_ways.append([])
                    for i in range(len(curr_positions)):
                        curr_position = sg.Point(curr_positions[i][0],
                                                 curr_positions[i][1])
                        all_street_ways[-1].append(curr_position)
            if is_building is True:
                all_building_data[way.get('id')] = curr_dict

        # Filter buildings and streets for locations within boundary
        street_ways = []
        if check_boundary is True:
            print('Filtering buildings and streets...')
            prepared_boundary = prep(city_boundary)
            building_data = {}
            for id in all_building_data.keys():
                if city_boundary.contains(all_building_data[id]['polygon']):
                    building_data[id] = all_building_data[id]

            for street_way in all_street_ways:
                street_ways.append(filter(prepared_boundary.contains,
                                          street_way))
        else:
            building_data = all_building_data
            street_ways = all_street_ways

        print('Add buildings to graph...')
        counter = 0
        curr_keys = list(building_data.keys())
        ordered_keys = sorted(curr_keys)  # Same node ids for same input
        for id in ordered_keys:
            curr_way = building_data[id]['polygon']
            curr_position = curr_way.centroid
            # Taken from http://gis.stackexchange.com/questions/127607/area-in-km-from-polygon-of-coordinates
            geom_aea = ops.transform(
                partial(
                    pyproj.transform,
                    pyproj.Proj(init='EPSG:4326'),
                    pyproj.Proj(
                        proj='aea',
                        lat1=curr_way.bounds[1],
                        lat2=curr_way.bounds[3])),
                curr_way)
            counter += 1
            building = self.add_building(position=curr_position)
            self.node[building]['area'] = geom_aea.area
            self.node[building]['osm_id'] = id
            if 'addr:street' in building_data[id]:
                self.node[building]['addr:street'] = building_data[id][
                    'addr:street']
            if 'addr:housenumber' in building_data[id]:
                self.node[building]['addr:housenumber'] = building_data[id][
                    'addr:housenumber']
                # print('Adding building', counter, 'with area =', geom_area.area)

        print('Add streets to graph...')
        for street_way in street_ways:
            street_nodes = []
            to_line_string = []
            for curr_position in street_way:
                street_nodes.append(self.add_street_node(
                    position=curr_position))
                to_line_string.append(curr_position)
                if len(street_nodes) > 1:
                    if street_nodes[-2] != street_nodes[-1]:
                        if add_str_info:
                            self.add_edge(street_nodes[-2], street_nodes[-1],
                                          network_type='street')
                        else:
                            self.add_edge(street_nodes[-2], street_nodes[-1])
            if len(to_line_string) > 1:
                streets.append(sg.LineString(to_line_string))

        # Add boundary to uesgraph
        if check_boundary is True:
            self.graph['boundary'] = city_boundary

        self.graph['from_osm'] = True

        self.graph['streets'] = streets
        print('Finished import from OpenStreetMap data')
        print('')

        return self

    def number_of_nodes(self, node_type):
        """
        Returns number of nodes for given `node_type`

        Parameters
        ----------
        node_type : str
            {'building', 'street', 'heating', 'cooling', 'electricity',
            'gas', 'other'}

        Returns
        -------
        number_of_nodes : int
            The number of nodes for the given `node_type`
        """
        if node_type == 'building':
            number_of_nodes = len(self.nodelist_building)
        elif node_type == 'street':
            number_of_nodes = len(self.nodelist_street)
        else:
            if node_type == 'heating':
                nodelists = list(self.nodelists_heating.values())
            elif node_type == 'cooling':
                nodelists = list(self.nodelists_cooling.values())
            elif node_type == 'electricity':
                nodelists = list(self.nodelists_electricity.values())
            elif node_type == 'gas':
                nodelists = list(self.nodelists_gas.values())
            elif node_type == 'water':
                nodelists = list(self.nodelists_water.values())
            elif node_type == 'other':
                nodelists = list(self.nodelists_others.values())
            number_of_nodes = 0
            for nodelist in nodelists:
                number_of_nodes += len(nodelist)

        return number_of_nodes

    def calc_network_length(self, network_type):
        """
        Calculates the length of all edges for given `network_type`

        Parameters
        ----------
        network_type : str
            One of the network types defined in `self.network_types`

        Returns
        -------
        total_length : float
            Total length of all edges for given `network_type` in m
        """
        total_length = 0
        for edge in self.edges():
            if network_type in self.node[edge[0]]['node_type'] or \
                            network_type in self.node[edge[1]]['node_type']:
                # Taken from http://gis.stackexchange.com/questions/127607/area-in-km-from-polygon-of-coordinates
                curr_way = sg.LineString([self.node[edge[0]]['position'],
                                          self.node[edge[1]]['position']])
                geom_aea = ops.transform(
                    partial(
                        pyproj.transform,
                        pyproj.Proj(init='EPSG:4326'),
                        pyproj.Proj(
                            proj='aea',
                            lat1=curr_way.bounds[1],
                            lat2=curr_way.bounds[3])),
                    curr_way)
                total_length += geom_aea.length

        return round(total_length, 2)

    def calc_total_building_ground_area(self):
        """
        Returns the sum of all available building ground areas in m**2

        Returns
        -------
        total_ground_area : float
            Sum of all available building ground areas in m**2
        """
        total_ground_area = 0
        counter = 0
        for building in self.nodelist_building:
            if 'area' in self.node[building]:
                total_ground_area += self.node[building]['area']
            else:
                counter += 1

        if counter > 0:
            warnings.warn('{} of {} buildings have no area '
                          'information'.format(counter,
                                               self.number_of_nodes(
                                                   'building')))

        return total_ground_area

    def rotate(self, degrees):
        """
        Rotates all nodes of the graph by `degrees`

        Parameters
        ----------
        degrees : float
            Value of degrees for rotation
        """

        # Find center point of network to plot
        node_points = []
        for node in self.nodes():
            node_points.append(self.node[node]['position'])
        center_point = sg.MultiPoint(node_points).envelope.centroid

        self.min_position = None
        self.max_position = None

        for node in self.nodes():
            self.node[node]['position'] = affinity.rotate(
                self.node[node]['position'],
                degrees,
                origin=center_point)
            self._update_min_max_positions(self.node[node]['position'])

    def network_simplification(self, network_type, network_id='default'):
        """Simplifies a pipe network by replacing serial pipes

        Parameters
        ----------
        network_type : str
            Specifies the type of the network as {'heating', 'cooling',
            'electricity', 'gas', 'others'}
        network_id : str
            Name of the network

        This method searches for network nodes in between two pipes. If such
        a node is found (center), the two pipes will be replaced by a new pipe
        model with weighted average properties of the two pipes. The two
        original pipes and the center node are removed afterwards.
        """
        # Get nodelist for the chosen network
        if network_type == 'heating':
            nodelists = self.nodelists_heating
        elif network_type == 'cooling':
            nodelists = self.nodelists_cooling
        elif network_type == 'electricity':
            nodelists = self.nodelists_electricity
        elif network_type == 'gas':
            nodelists = self.nodelists_gas
        elif network_type == 'water':
            nodelists = self.nodelists_water
        elif network_type == 'other':
            nodelists = self.nodelists_others

        assert network_id in nodelists.keys(), 'Unknown network_id'

        nodelist = nodelists[network_id]

        to_simplify = []

        print(self.edges(data=True))

        # Search for serial pipes to be replaced by one equivalent pipe
        for network_node in nodelist:
            if self.degree(network_node) == 2:
                to_simplify.append(network_node)

        # Group serially connected nodes together
        def _group_neighbors(curr_node, curr_group):
            """Recursive helper function to group nodes by connections

            Parameters
            ----------
            node : int
                Identifier for node. Its neighbors will be checked wether
                they are in list `to_simplify`
            group : list
                Collecting list for connected nodes

            Returns
            -------
            group : list
                Collecting list for connected nodes
            """
            for curr_neighbor in self.neighbors(curr_node):
                if curr_neighbor in to_simplify and curr_neighbor not in \
                        processed:
                    curr_group.append(curr_neighbor)
                    processed.append(curr_neighbor)
                    curr_group = _group_neighbors(curr_neighbor, curr_group)

            return curr_group

        counter = 0
        groups = []
        processed = []
        for node in to_simplify:
            if node not in processed:
                processed.append(node)
                groups.append([node])
                groups[-1] = _group_neighbors(node, groups[-1])

        for group in groups:
            # Find neighbors of the group
            group_neighbors = []
            for node in group:
                for neighbor in self.neighbors(node):
                    if neighbor not in group:
                        group_neighbors.append(neighbor)
            replace_path = nx.shortest_path(self,
                                            group_neighbors[0],
                                            group_neighbors[1])

            # Calculate equivalent properties of new single pipe
            lengths = []
            weighted_diameters = []
            weighted_Gs = []
            pipeIDs = []
            for i in range(len(replace_path[:-1])):
                length = self.edge[replace_path[i]][replace_path[i + 1]][
                    'length']
                lengths.append(length)
                weighted_diameters.append(self.edge[replace_path[i]][replace_path[
                    i + 1]]['diameter'] * length)
                if 'G' in self.edge[replace_path[i]][replace_path[i + 1]]:
                    weighted_Gs.append(self.edge[replace_path[i]][replace_path[
                        i + 1]]['G'] * length)
                pipeIDs.append(self.edge[replace_path[i]][replace_path[
                    i + 1]]['pipeID'])
                self.remove_edge(replace_path[i], replace_path[i + 1])
            new_length = sum(lengths)
            new_diameter = sum(weighted_diameters) / new_length
            if weighted_Gs != []:
                new_G = sum(weighted_Gs) / new_length
            else:
                new_G = 5
            next_pipeID = max(self.pipeIDs) + 1

            description = 'Simplified pipe for pipes'
            for pipeID in pipeIDs:
                description += ' {}'.format(pipeID)

            # Create new pipe
            self.add_edge(replace_path[0], replace_path[-1])
            self.edge[replace_path[0]][replace_path[-1]]['length'] = new_length
            self.edge[replace_path[0]][replace_path[-1]]['diameter'] = \
                new_diameter
            self.edge[replace_path[0]][replace_path[-1]]['G'] = new_G
            self.edge[replace_path[0]][replace_path[-1]]['description'] = \
                description
            self.edge[replace_path[0]][replace_path[-1]]['pipeID'] = \
                next_pipeID
            self.pipeIDs.append(next_pipeID)

        for group in groups:
            for node in group:
                if node in self.nodes():
                    print('Removing node', node)
                    self.remove_network_node(node)
                else:
                    print('Not removing node', node)

        self.simplification_level = 1

    def calc_angle(self, a, b, output='rad'):
        """Returns the angle of a line from point a to b in rad or degrees

        Parameters
        ----------
        a : shapely.geometry.point object
        b : shapely.geometry.point object
        output : str
            Selection of output unit between 'rad' and 'degrees'

        Returns
        -------
        angle : float
            Angle of a line from point a to b in rad or degrees
        """
        assert output in ['rad', 'degrees'], 'Output must be rad or degrees'

        angle = math.atan2(b.y - a.y, b.x - a.x)
        if angle < 0:
            angle = 2 * math.pi + angle
        if output == 'degrees':
            angle_degrees = (angle) * 360 / (2 * math.pi)
            return angle_degrees
        else:
            return angle


    def import_flow_data(self, input_path, source):
        """Imports flow data saved in json files

        The `input_path` should contain 2 directories named `pipes` and
        `buildings`. These sub-directories should contain a json file for
        each pipe or building.

        Parameters
        ----------
        input_path : str
            Path to file structure for the json inputs
        source : {'modelica', 'dhcstatic'}
            Identifier for source of flow information. Choose between a
            dynamic Modelica simulation or static calculation in dhcstatic
        """
        buildings_dir = os.path.join(input_path, 'buildings')
        supplies_dir = os.path.join(input_path, 'supplies')
        pipes_dir = os.path.join(input_path, 'pipes')
        network_dir = os.path.join(input_path, 'network_nodes')

        node_dirs = [buildings_dir,
                     supplies_dir,
                     network_dir]
        for node_dir in node_dirs:
            if os.path.exists(node_dir):
                for result_file in os.listdir(node_dir):
                    result_file = os.path.join(node_dir,
                                               result_file)
                    if os.path.isfile(result_file):
                        with open(result_file, 'r') as input_file:
                            result = json.load(input_file)
                        if 'buildings' in node_dir:
                            name = result['meta']['building']
                        elif 'supplies' in node_dir:
                            name = result['meta']['supply']
                        elif 'network_nodes' in node_dir:
                            name = result['meta']['network_node']
                        try:
                            node = self.nodes_by_name[int(name)]
                        except:
                            node = self.nodes_by_name[name]

                        time = result['data']['time']
                        data = {}
                        if 'temperature_supply' in result['data']:
                            data['temperature_supply'] = result['data'][
                                'temperature_supply']
                        if 'temperature_return' in result['data']:
                            data['temperature_return'] = result['data'][
                                'temperature_return']
                        if 'mass_flow' in result['data']:
                            data['mass_flow'] = result['data'][
                                'mass_flow']
                        if 'valve_opening' in result['data']:
                            data['valve_opening'] = result['data'][
                                'valve_opening']
                        if 'pressure_supply' in result['data']:
                            data['pressure_supply'] = result['data'][
                                'pressure_supply']
                        if 'pressure_return' in result['data']:
                            data['pressure_return'] = result['data'][
                                'pressure_return']
                        if 'heat_demand' in result['data']:
                            data['heat_demand'] = result['data'][
                                'heat_demand']

                        result_data = pd.DataFrame(data=data, index=time)
                        self.node[node][source] = \
                            result_data

        for edge in self.edges():
            # print(edge)
            # print(self.uesgraph.edge[edge[0]][edge[1]])
            pipe_name = self.edge[edge[0]][edge[1]]['pipeID']
            # print('pipe_name', pipe_name)
            pipe_result_file = os.path.join(pipes_dir,
                                            '{}_pipe_data.json'.format(
                                                pipe_name))
            with open(pipe_result_file, 'r') as input:
                pipe_result = json.load(input)

            time = pipe_result['data']['time']

            data = {}
            if 'temperature_supply' in pipe_result['data']:
                data['temperature_supply'] = pipe_result['data'][
                    'temperature_supply']
            if 'temperature_return' in pipe_result['data']:
                data['temperature_return'] = pipe_result['data'][
                    'temperature_return']
            if 'mass_flow' in pipe_result['data']:
                data['mass_flow'] = pipe_result['data'][
                    'mass_flow']
            if 'diameter' in pipe_result['data']:
                data['diameter'] = pipe_result['data'][
                    'diameter']
            if 'pressure_supply' in pipe_result['data']:
                data['pressure_supply'] = pipe_result['data'][
                    'pressure_supply']
            if 'pressure_return' in pipe_result['data']:
                data['pressure_return'] = pipe_result['data'][
                    'pressure_return']
            if 'heat_loss' in pipe_result['data']:
                data['heat_loss'] = pipe_result['data'][
                    'heat_loss']

            for key in data:
                try:
                    if len(data[key]) == 2:
                        data[key] = [data[key][0] for x in time]
                except:
                    None

            result_data = pd.DataFrame(data=data, index=time)
            self.edge[edge[0]][edge[1]][source] = \
                result_data

            print('--------')
            print('{}_pipe_data.json'.format(pipe_name))
            print(self.edge[edge[0]][edge[1]][source]['mass_flow'].tolist()[
                  :20])
