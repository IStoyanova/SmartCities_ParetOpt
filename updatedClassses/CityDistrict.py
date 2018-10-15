#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python code with city district class. Usage requires installation of uesgraphs
Python package.
uesgraphs can be downloaded on Github: https://github.com/RWTH-EBC/uesgraphs
"""

"""
upgrade
@author: ist-egu
"""

from newFunctions.ModularCalculation_Flow import *
from updatedClassses.UESGraph import UESGraph


class CityDistrict(UESGraph):
    def __init__(self, environment=None, networkSpecification=None):
        """
        Constructor of city district object.

        Parameters
        ----------
        environment : object
            Environment object of pycity
        networkSpecification: dict of dicts
            Network transportation medium specifications

        Attributes
        ----------
        _kind : str
            Type of object ('citydistrict')
        voltage : float
            Bus voltage of the electricity network

        Annotations
        -----------
        To prevent different methods of subclass nx.Graph from failing
        the environment object is used as optional input for __init__
        (not as fix input). E.g. when generating subgraph via .subgraph()
        method, user has to add environment after initialization.
        """

        #  Add pointer to environment
        self.environment = environment
        self.networkSpecification = networkSpecification

        #  Initialize super class
        super(CityDistrict, self).__init__()

        #  List of possible entity names (might be extended by user
        #  when using own entity._kind)
        self.entity_name_list = ['building', 'pv', 'windenergyconverter', 'p2gConverter', 'p2gStorage', 'heps',
                                 'gassource', 'watersource', 'chp']

        #  Define object type
        self._kind = 'citydistrict'

        # Network specification
        self.defineConnection(self.environment, self.networkSpecification)
        self.voltage = 1000 if networkSpecification == None else self._voltage

    def addEntity(self, entity, position, name=None,
                  is_supply_electricity=None, is_supply_heating=False,
                  is_supply_cooling=False, is_supply_gas=False,
                  is_supply_water=False, is_supply_other=False):
        """
        Method adds entity (e.g. building object) to city district object.
        Method appends the added nodes to the related network nodelists e.g. nodelists_electricity['default]

        Parameters
        ----------
        entity : object
            Standard entity object (building, windenergyconverter or pv)
        position : shapely.geometry.Point object
            New node's position
        name : str, optional
            Name of entity (default: None)
        is_supply_electricity : bool, optional
            Boolean to define, if entity is of kind electrical supply
            (default: None)
            True - Entity is electric supplier
            False - Entity is not an electric supplier
            When initialized as "None", method automatically decides if value
            is True or False, based on _kind of entity
            ("building" - False; "windenergyconverter" - True; "pv" - True)
        is_supply_heating : bool, optional
            Boolean to define, if entity is of kind heating supply
            (default: False)
        is_supply_cooling : bool, optional
            Boolean to define, if entity is of kind cooling supply
            (default: False)
        is_supply_gas : bool, optional
            Boolean to define, if entity is of kind gas supply
            (default: False)
        is_supply_water : bool, optional
            Boolean to define, if entity is of kind water supply
            (default: False)
        is_supply_other : bool, optional
            Boolean to define, if entity is of kind other supply
            (default: False)

        Returns
        -------
        node_number : int
            Node number

        Example
        -------
        >>> myBuilding = Building(...)
        >>> myCityDistrict = CityDistrict(...)
        >>> myCityDistrict.addEntity(myBuilding)
        """

        # Is there connection between the entity and the networks
        connection2cooling = False
        connection2heating = False
        connection2electricity = False
        connection2gas = False
        connection2water = False

        if self.environment is None:
            #  Extract environment from entity
            self.environment = entity.environment

        # Automatically decide via entity._kind
        if is_supply_electricity is None:
            if entity._kind == "building":
                is_supply_electricity = True
                connection2electricity = True
                connection2gas = True
                connection2water = True
                if entity.hasDHConnection == True:
                    connection2heating = True

            elif entity._kind == "windenergyconverter":
                is_supply_electricity = True
                connection2electricity = True

            elif entity._kind == "pv":
                is_supply_electricity = True
                connection2electricity = True

            elif entity._kind == "p2gConverter":
                is_supply_electricity = False
                is_supply_gas = True
                connection2electricity = True
                connection2gas = True

            elif entity._kind == "p2gStorage":
                is_supply_electricity = False
                is_supply_gas = True
                connection2gas = True

            elif entity._kind == "heps":
                is_supply_electricity = True
                is_supply_water = True
                connection2electricity = True
                connection2water = True

            elif entity._kind == 'chp':
                is_supply_electricity = True
                is_supply_heating = True
                connection2electricity = True
                connection2gas = True
                connection2heating = True

            elif entity._kind == "gassource":
                is_supply_electricity = False
                is_supply_gas = True
                connection2gas = True

            elif entity._kind == "watersource":
                is_supply_electricity = False
                is_supply_water = True
                connection2water = True

            else:
                raise ValueError('Unknown kind of entity. Select known ' +
                                 'entity (building, windenergyconverter, pv, heps, p2gConverter, p2gStorage, gassource, watersource)' +
                                 ' or clearly define parameter ' +
                                 'is_supply_electricity, when using own ' +
                                 'entity type.')

        # If entity._kind is new, extend entities list
        if entity._kind not in self.entity_name_list:
            self.entity_name_list.append(entity._kind)

        # Use add_building method of uesgraph (in ues graph, every demand
        #  and every supplier is linked to a building). PV or wec "buildings"
        #  are buildings with zero energy demand (only generation is taken
        #  into account). Add building node to graph (node_type='building')
        node_number = self.add_building(name=name, position=position,
                                        is_supply_electricity=is_supply_electricity,
                                        is_supply_heating=is_supply_heating,
                                        is_supply_cooling=is_supply_cooling,
                                        is_supply_gas=is_supply_gas,
                                        is_supply_water=is_supply_water,
                                        is_supply_other=is_supply_other)

        print("Entity adding:", entity, "to Node", node_number)

        #  Add entity as attribute to node with returned node_number
        self.add_node(node_number, entity=entity)

        """
        Adding nodes to the related nodelists

        Example
        >>>nodeC=myCityDistrict.addEntity(myBuilding)
        >>>connection2gas=True          --> self.nodelists_gas['default'].append(nodeC)
        >>>connection2electricity=True  --> self.nodelists_electricity'default'].append(nodeC)
        >>>connection2heating=True      --> self.nodelists_heating['default'].append(nodeC)
        """
        if connection2heating == True:
            self.nodelists_heating['default'].append(node_number)
        if connection2cooling == True:
            self.nodelists_cooling['default'].append(node_number)
        if connection2electricity == True:
            self.nodelists_electricity['default'].append(node_number)
        if connection2gas == True:
            self.nodelists_gas['default'].append(node_number)
        if connection2water == True:
            self.nodelists_water['default'].append(node_number)

        return node_number

    def addMultipleEntities(self, entities, positions):
        """
        Add multiple entities to the existing city district.

        Parameter
        ---------
        entities_tuple : List-like
            List (or tuple) of entities that are added to the city district
        positions : List-like
            List (or tuple) of positions (of entities) that are added to city
            district
            (list of shapely.geometry.Point objects)

        Example
        -------
        >>> import shapely.geometry.point as point
        >>> myPV  = PV(...)
        >>> myWEC = WindEnergyConverter(...)
        >>> myCityDistrict = CityDistrict(...)
        >>> pos_1 = point.Point(0, 0)
        >>> pos_2 = point.Point(0, 10)
        >>> myCityDistrict.addMultipleEntities([myPV, myWEC], [pos_1, pos_2])
        """
        assert len(entities) == len(positions), ('Number of entities must ' +
                                                 'match to number of positions')

        for i in range(len(entities)):
            curr_entity = entities[i]
            curr_pos = positions[i]
            self.addEntity(entity=curr_entity, position=curr_pos)

    def _getRESPower(self, generators, current_values=True):
        """
        Get the (aggregated) forecast of all renewable electricity generators.

        Parameters
        ----------
        current_values : bool, optional
            Defines, if only current horizon or all timesteps should be used.
            (default: True)
            False - Use complete number of timesteps
            True - Use horizon

        Returns
        -------
        power : np.array
            Power curve
        """
        if current_values:
            timesteps = self.environment.timer.timestepsHorizon
        else:
            timesteps = self.environment.timer.timestepsTotal

        power = np.zeros(timesteps)
        for generator in generators:
            power += generator.getPower(currentValues=current_values)

        return power

    def _getEmission(self, emitters, current_values=True):
        """
        Get the (aggregated) emission from all carbon emitters.

        Parameters
        ----------
        current_values : bool, optional
            Defines, if only current horizon or all timesteps should be used.
            (default: True)
            False - Use complete number of timesteps
            True - Use horizon

        Returns
        -------
        emission : np.array
            Emission mass curve
        """
        if current_values:
            timesteps = self.environment.timer.timestepsUsedHorizon
        else:
            timesteps = self.environment.timer.timestepsTotal

        emission = np.zeros(timesteps)
        for emitter in emitters:
            if emitter._kind == 'bes':
                emission += emitter.getPowerCurves(current_values)[3]
            elif emitter._kind == 'chp':
                emission += emitter.getResults(current_values)[3]

        return emission

    def getPVPower(self, current_values=True):
        """
        Get the (aggregated) forecast of all (stand alone) pv units / pv farms.

        Parameters
        ----------
        current_values : bool, optional
            Defines, if only current horizon or all timesteps should be used.
            (default: True)
            False - Use complete number of timesteps
            True - Use horizon

        Returns
        -------
        pv_res_power : np.array
            Array with pv power values of all pv farms
        """

        if current_values:
            timesteps = self.environment.timer.timestepsHorizon
        else:
            timesteps = self.environment.timer.timestepsTotal

        # Create empty list of pv entities
        pv_entities = []

        #  Loop over all nodes
        for n in self:
            #  If node holds attribute 'node_type'
            if 'node_type' in self.node[n]:
                #  If node_type is building
                if self.node[n]['node_type'] == 'building':
                    #  If entity is of type pv
                    if self.node[n]['entity']._kind == 'pv':
                        #  Add pv entity to list
                        pv_entities.append(self.node[n]['entity'])
                    elif self.node[n]['entity']._kind == 'building':
                        if self.node[n]['entity'].bes.hasPv:
                            pv_entities.append(self.node[n]['entity'].bes.pv)

        if len(pv_entities) == 0:
            return np.zeros(timesteps)
        else:
            return self._getRESPower(pv_entities, current_values=
            current_values)

    def getWindEnergyConverterPower(self, current_values=True):
        """
        Get the (aggregated) forecast of all wind energy converters.

        Parameters
        ----------
        current_values : bool, optional
            Defines, if only current horizon or all timesteps should be used.
            (default: True)
            False - Use complete number of timesteps
            True - Use horizon

        Returns
        -------
        wind_res_power : np.array
            Array with wind power values of all wind farms
        """

        if current_values:
            timesteps = self.environment.timer.timestepsHorizon
        else:
            timesteps = self.environment.timer.timestepsTotal

        # Create empty list of pv entities
        wind_entities = []

        #  Loop over all nodes
        for n in self:
            #  If node holds attribute 'node_type'
            if 'node_type' in self.node[n]:
                #  If node_type is building
                if self.node[n]['node_type'] == 'building':
                    #  If entity is of type pv
                    if self.node[n]['entity']._kind == 'windenergyconverter':
                        #  Add pv entity to list
                        wind_entities.append(self.node[n]['entity'])

        if len(wind_entities) == 0:
            return np.zeros(timesteps)
        else:
            return self._getRESPower(wind_entities, current_values=
            current_values)

    def getElectricCurrents(self, current_values=True):
        """
        Returns
        -------
        currentSolutionDict: The values of the electrical currents flowing through the edges

        # A function that returns the dictionary of the values of the flow quantities through the edges
        # e.g. dict={1008: {1009: 50}, 1001: {1002: 20, 1003: -15}, 1003: {1004: -40, 1006: -40}, 1006: {1007: -63}, 1007: {1008: 20}}
        # dict[1008][1009]=50 ==> means current from 1008 to 1009 is 50A

        """
        if current_values:
            timesteps = self.environment.timer.timestepsUsedHorizon
        else:
            timesteps = self.environment.timer.timestepsTotal

        nodecurrent_dict_init=createMatrixFor_b_vector(self,'ele',current_values)
        currentSolutionDict_init = createMatrixFor_x_Vector(timesteps, self.nodelists_electricity,self.edgelist_electricity)

        currentSolutionDict = reduceAndSolve(timesteps,nodecurrent_dict_init,currentSolutionDict_init,self.nodelists_electricity,self.edgelist_electricity)

        return currentSolutionDict

    def getGasFlows(self, current_values=True):
        """
        Returns
        -------
        gasFlowSolutionDict: The values of the gas power flow through the edges

        """
        if current_values:
            timesteps = self.environment.timer.timestepsUsedHorizon
        else:
            timesteps = self.environment.timer.timestepsTotal


        nodeinflow_dict = createMatrixFor_b_vector(self, 'gas', current_values)

        gasFlowSolutionDict = createMatrixFor_x_Vector(timesteps, self.nodelists_gas, self.edgelist_gas)
        gasFlowSolutionDict = reduceAndSolve(timesteps, nodeinflow_dict, gasFlowSolutionDict,
                                             self.nodelists_gas, self.edgelist_gas)

        return gasFlowSolutionDict

    def getHeatFlows(self, current_values=True):
        """
        Returns
        -------
        heatFlowSolutionDict: The values of the heat power flow through the edges
        """
        if current_values:
            timesteps = self.environment.timer.timestepsUsedHorizon
        else:
            timesteps = self.environment.timer.timestepsTotal

        nodeinflow_dict_init = createMatrixFor_b_vector(self, 'heat', current_values)
        heatFlowSolutionDict_init = createMatrixFor_x_Vector(timesteps, self.nodelists_heating, self.edgelist_heating)

        heatFlowSolutionDict = reduceAndSolve(timesteps, nodeinflow_dict_init, heatFlowSolutionDict_init,
                                             self.nodelists_heating, self.edgelist_heating)

        return heatFlowSolutionDict

    def getWaterFlows(self, current_values=True):
        """
        Returns
        -------
        waterFlowSolutionDict: The values of the water flows through the edges
        """
        if current_values:
            timesteps = self.environment.timer.timestepsUsedHorizon
        else:
            timesteps = self.environment.timer.timestepsTotal


        nodeinflow_dict_init = createMatrixFor_b_vector(self, 'water', current_values)
        waterFlowSolutionDict_init = createMatrixFor_x_Vector(timesteps, self.nodelists_water,self.edgelist_water)

        waterFlowSolutionDict = reduceAndSolve(timesteps, nodeinflow_dict_init, waterFlowSolutionDict_init,
                                             self.nodelists_water, self.edgelist_water)

        return waterFlowSolutionDict

    def getEmission(self, current_values=True):
        """
        Detects the objects that emits carbon and returns the aggregated emission of the CityDistrict

        -------
        emission : np.array
            Array with net carbon emission of emitting objects
        """

        if current_values:
            timesteps = self.environment.timer.timestepsUsedHorizon
        else:
            timesteps = self.environment.timer.timestepsTotal

        # Create empty list of pv entities
        emitting_entities = []

        #  Loop over all nodes
        for n in self:
            #  If node holds attribute 'node_type'
            if 'node_type' in self.node[n]:
                #  If node_type is building
                if self.node[n]['node_type'] == 'building':
                    #  If entity is a building object
                    if self.node[n]['entity']._kind == 'building':
                        #  If building has a BES
                        if self.node[n]['entity'].hasBes:
                            #  Add bes to list
                            emitting_entities.append(self.node[n]['entity'].bes)
                    elif self.node[n]['entity']._kind == 'chp':
                        # Add chp to list
                        emitting_entities.append(self.node[n]['entity'])

        if len(emitting_entities) == 0:
            return np.zeros(timesteps)
        else:
            return self._getEmission(emitting_entities, current_values=
            current_values)

    def get_power_curves(self, current_values=True):
        """
        Get the aggregated electricity and heat power forecast of all
        buildings.

        Returns tuple of electrical and thermal power array

        Parameters
        ----------
        current_values : bool, optional
            Defines, if only current horizon or all timesteps should be used.
            (default: True)
            False - Use complete number of timesteps
            True - Use horizon

        Order
        -----
        ElectricityDemand : Array_like
            Aggregated electrical demand
        HeatDemand : Array_like
            Aggregated heat demand
        """
        if current_values:
            timesteps = self.environment.timer.timestepsHorizon
        else:
            timesteps = self.environment.timer.timestepsTotal
        power_el = np.zeros(timesteps)
        power_th = np.zeros(timesteps)

        #  Loop over all nodes
        for n in self:
            #  If node holds attribute 'node_type'
            if 'node_type' in self.node[n]:
                #  If node_type is building
                if self.node[n]['node_type'] == 'building':
                    #  If entity is kind building
                    if self.node[n]['entity']._kind == 'building':
                        temp = self.node[n]['entity'].get_power_curves(
                            current_values=current_values)
                        power_el += temp[0]
                        power_th += temp[1]

        return (power_el, power_th)

    def get_aggr_space_h_power_curve(self, current_values=False,
                                     nodelist=None):
        """
        Returns aggregated space heating power curve for all buildings
        within city district.

        Parameters
        ----------
        current_values : bool, optional
            Defines, if only current horizon or all timesteps should be used.
            (default: False)
            False - Use complete number of timesteps
            True - Use horizon
        nodelist : list (of ints), optional
            Defines which nodes should be used to return annual space
            heating demand in kWh (default: None).
            If nodelist is None, all nodes with building entities will
            be used.

        Returns
        -------
        agg_th_p_curve : np.array
            Space heating thermal power curve in W per timestep
        """

        if current_values:  # Use horizon
            size = self.environment.timer.timestepsHorizon
        else:  # Use all timesteps
            size = self.environment.timer.timestepsTotal
        agg_th_p_curve = np.zeros(size)

        if nodelist is None:
            use_nodes = self
        else:
            for n in nodelist:
                assert n in self.nodes(), ('Node ' + str(n) + 'is not '
                                                              'within city object!')
            use_nodes = nodelist

        # Loop over all nodes
        for n in use_nodes:
            #  If node holds attribute 'node_type'
            if 'node_type' in self.node[n]:
                #  If node_type is building
                if self.node[n]['node_type'] == 'building':
                    #  If entity is kind building
                    if self.node[n]['entity']._kind == 'building':
                        th_power_curve = self.node[n]['entity']. \
                                             get_space_heating_power_curve(
                            current_values=current_values)[0:size]
                        agg_th_p_curve += th_power_curve

        return agg_th_p_curve

    def get_aggr_el_power_curve(self, current_values=False,
                                nodelist=None):
        """
        Returns aggregated electrical power curve for all buildings
        within city district.

        Parameters
        ----------
        current_values : bool, optional
            Defines, if only current horizon or all timesteps should be used.
            (default: False)
            False - Use complete number of timesteps
            True - Use horizon
        nodelist : list (of ints), optional
            Defines which nodes should be used to return annual space
            heating demand in kWh (default: None).
            If nodelist is None, all nodes with building entities will
            be used.

        Returns
        -------
        agg_el_p_curve : np.array
            Electrical power curve in W per timestep
        """

        if current_values:  # Use horizon
            size = self.environment.timer.timestepsHorizon
        else:  # Use all timesteps
            size = self.environment.timer.timestepsTotal
        agg_el_p_curve = np.zeros(size)

        if nodelist is None:
            use_nodes = self
        else:
            for n in nodelist:
                assert n in self.nodes(), ('Node ' + str(n) + 'is not '
                                                              'within city object!')
            use_nodes = nodelist

        # Loop over all nodes
        for n in use_nodes:
            #  If node holds attribute 'node_type'
            if 'node_type' in self.node[n]:
                #  If node_type is building
                if self.node[n]['node_type'] == 'building':
                    #  If entity is kind building
                    if self.node[n]['entity']._kind == 'building':
                        el_power_curve = self.node[n]['entity']. \
                                             get_electric_power_curve(
                            current_values=current_values)[0:size]
                        agg_el_p_curve += el_power_curve

        return agg_el_p_curve


    def get_aggr_dhw_power_curve(self, current_values=False,
                                 nodelist=None):
        """
        Returns aggregated domestic hot water (dhw) power curve for all
        buildings within city district.

        Parameters
        ----------
        current_values : bool, optional
            Defines, if only current horizon or all timesteps should be used.
            (default: False)
            False - Use complete number of timesteps
            True - Use horizon
        nodelist : list (of ints), optional
            Defines which nodes should be used to return annual space
            heating demand in kWh (default: None).
            If nodelist is None, all nodes with building entities will
            be used.

        Returns
        -------
        agg_dhw_p_curve : np.array
            DHW power curve in W per timestep
        """

        if current_values:  # Use horizon
            size = self.environment.timer.timestepsHorizon
        else:  # Use all timesteps
            size = self.environment.timer.timestepsTotal
        agg_dhw_p_curve = np.zeros(size)

        if nodelist is None:
            use_nodes = self
        else:
            for n in nodelist:
                assert n in self.nodes(), ('Node ' + str(n) + 'is not '
                                                              'within city object!')
            use_nodes = nodelist

        # Loop over all nodes
        for n in use_nodes:
            #  If node holds attribute 'node_type'
            if 'node_type' in self.node[n]:
                #  If node_type is building
                if self.node[n]['node_type'] == 'building':
                    #  If entity is kind building
                    if self.node[n]['entity']._kind == 'building':
                        dhw_power_curve = self.node[n]['entity']. \
                                              get_dhw_power_curve(
                            current_values=current_values)[0:size]
                        agg_dhw_p_curve += dhw_power_curve

        return agg_dhw_p_curve

    def get_aggr_water_demand_power_curve(self, current_values=False,
                                          nodelist=None):
        """
        Returns aggregated water demand curve for all
        buildings within city district.

        Parameters
        ----------
        current_values : bool, optional
            Defines, if only current horizon or all timesteps should be used.
            (default: False)
            False - Use complete number of timesteps
            True - Use horizon
        nodelist : list (of ints), optional
            Defines which nodes should be used to return water
            demand in l (default: None).
            If nodelist is None, all nodes with building entities will
            be used.

        Returns
        -------
        agg_water_demand_curve : np.array
            Water demand curve in m3 per timestep
        """

        if current_values:  # Use horizon
            size = self.environment.timer.timestepsHorizon
        else:  # Use all timesteps
            size = self.environment.timer.timestepsTotal
        agg_water_demand_curve = np.zeros(size)

        if nodelist is None:
            use_nodes = self
        else:
            for n in nodelist:
                assert n in self.nodes(), ('Node ' + str(n) + 'is not '
                                                              'within city object!')
            use_nodes = nodelist

        # Loop over all nodes
        for n in use_nodes:
            #  If node holds attribute 'node_type'
            if 'node_type' in self.node[n]:
                #  If node_type is building
                if self.node[n]['node_type'] == 'building':
                    #  If entity is kind building
                    if self.node[n]['entity']._kind == 'building':
                        water_curve = self.node[n]['entity']. \
                                          get_waterDemand_profile(current_values=current_values)[0:size]
                        agg_water_demand_curve += water_curve

        return agg_water_demand_curve

    def getFlowTemperatures(self):
        """ 
        Get the aggregated flow temperature forecast.
        """

        timesteps = self.environment.timer.timestepsHorizon
        flowTemperature = np.zeros(timesteps)

        #  Loop over all nodes
        for n in self:
            #  If node holds attribute 'node_type'
            if 'node_type' in self.node[n]:
                #  If node_type is building
                if self.node[n]['node_type'] == 'building':
                    #  If entity is kind building
                    if self.node[n]['entity']._kind == 'building':
                        flow_temp = self.node[n]['entity'].getFlowTemperature()
                        flowTemperature = np.maximum(flowTemperature,
                                                     flow_temp)

        return flowTemperature

    def get_nb_of_entities(self, entity_name):
        """
        Returns number of nodes of specific entity (e.g. "building", "pv",
        "windenergyconverter")

        Parameters
        ----------
        entity_name: str
            Standard entity names (building, windenergyconverter or pv)

        Returns
        -------
        nb_of_entities : int
            Number of nodes holding specific entity
        """
        assert entity_name in self.entity_name_list

        nb_of_entities = 0

        for n in self:
            #  If node holds attribute 'node_type'
            if 'node_type' in self.node[n]:
                #  If node_type is building
                if self.node[n]['node_type'] == 'building':
                    if 'entity' in self.node[n]:
                        #  If entity is of kind entity_name
                        if self.node[n]['entity']._kind == entity_name:
                            nb_of_entities += 1
        return nb_of_entities

    def get_node_numbers_of_entities(self, entity_name):
        """
        Returns list with node numbers, which hold specific kind of entity
        (e.g. "building", "pv", "windenergyconverter")

        Parameters
        ----------
        entity_name: str
            Standard entity names (building, windenergyconverter or pv)

        Returns
        -------
        node_nb_list : list (of ints)
            List holding node numbers
        """
        assert entity_name in self.entity_name_list

        node_nb_list = []

        for n in self:
            #  If node holds attribute 'node_type'
            if 'node_type' in self.node[n]:
                #  If node_type is building
                if self.node[n]['node_type'] == 'building':
                    if 'entity' in self.node[n]:
                        #  If entity is of kind entity_name
                        if self.node[n]['entity']._kind == entity_name:
                            node_nb_list.append(n)
        return node_nb_list

    def get_nb_of_building_entities(self):
        """
        Returns number of nodes holding entities of kind "building"
        (without PV- and windfarms).

        Returns
        -------
        nb_buildings : int
            Number of buildings
        """
        nb_buildings = self.get_nb_of_entities(entity_name='building')
        return nb_buildings

    def get_list_build_entity_node_ids(self):
        """
        Returns list with node ids holding building entities.
        (without PV- and windfarms)

        Returns
        -------
        build_node_id_list : list (of ints)
            List holding building entity node ids
        """
        build_node_id_list = self.get_node_numbers_of_entities(entity_name=
                                                               'building')
        return build_node_id_list
