"""
@author: ist-egu
"""

from newFunctions.ModularCalculation_IO import *

class Aggregator(object):
    """
    Implementation of an aggregator that consists of multiple entities
    """

    def __init__(self,environment,cityquarter,name):
        """

        :param environment: object
            Environment object of pycity
        :param cityquarter: object
            CityDistrict object of pycity
        :param name: string
            Aggregator name
        """

        self._kind = "aggregator"

        self.environment = environment
        self.name=name
        self.quarter=cityquarter

        self.entityList=[]

    def addEntity(self,label):

        """
        Aggregate the objects that are labelled as 'label'

        Example
        -------
        >>> myAggregator = Aggregator(...)
        >>> myAggregator.addEntity('DH')
        """

        #  Loop over all nodes
        for n in self.quarter:
            #  If node holds attribute 'node_type'
            if 'node_type' in self.quarter.node[n]:
                #  If node_type is building
                if self.quarter.node[n]['node_type'] == 'building':
                    #If object is labelled as 'label'
                    if label in self.quarter.node[n]['entity'].labels:
                        self.entityList.append(self.quarter.node[n]['entity'])

    def addMultipleEntities(self,entities):

        for entity in entities:
            self.addEntity(entity)

    def get_agg_ele_power(self, current_values=True):
        """
        Returns electric power curve

        Parameters
        ----------
        current_values : bool, optional
            Defines, if only current horizon or all timesteps should be used.
            (default: False)
            False - Use complete number of timesteps
            True - Use horizon

        Returns
        -------
        el_power_curve : array-like
           Electrical power curve in W
        """

        return calculateIO_agg(self.entityList,current_values)[0]


    def get_agg_gas_power(self, current_values=True):
        """
        Returns gas power curve

        Parameters
        ----------
        current_values : bool, optional
            Defines, if only current horizon or all timesteps should be used.
            (default: False)
            False - Use complete number of timesteps
            True - Use horizon

        Returns
        -------
        gas_power_curve : array-like
           Gas power curve in W
        """

        return calculateIO_agg(self.entityList,current_values)[1]

    def get_agg_heat_power(self, current_values=True):
        """
        Returns heat power curve

        Parameters
        ----------
        current_values : bool, optional
            Defines, if only current horizon or all timesteps should be used.
            (default: False)
            False - Use complete number of timesteps
            True - Use horizon

        Returns
        -------
        th_power_curve : array-like
           Thermal power curve in W
        """

        return calculateIO_agg(self.entityList,current_values)[2]

    def get_agg_water(self, current_values=True):
        """
        Returns water curve

        Parameters
        ----------
        current_values : bool, optional
            Defines, if only current horizon or all timesteps should be used.
            (default: False)
            False - Use complete number of timesteps
            True - Use horizon

        Returns
        -------
        agg_water_curve : array-like
           Water curve in m3/s
        """

        return calculateIO_agg(self.entityList,current_values)[3]

    def get_agg_emission(self,current_values=True):
        """
        Returns emission curve

        Parameters
        ----------
        current_values : bool, optional
            Defines, if only current horizon or all timesteps should be used.
            (default: False)
            False - Use complete number of timesteps
            True - Use horizon

        Returns
        -------
        agg_emission_curve : array-like
           Emission curve in kg
        """

        return calculateIO_agg(self.entityList,current_values)[4]

    def get_all_source_agg(self, current_values=True):
        """
        Returns electric, gas, heat power and water curve

        Parameters
        ----------
        current_values : bool, optional
            Defines, if only current horizon or all timesteps should be used.
            (default: False)
            False - Use complete number of timesteps
            True - Use horizon
        """

        return self.get_agg_ele_power(current_values),self.get_agg_gas_power(current_values),self.get_agg_heat_power(current_values),self.get_agg_water(current_values),self.get_agg_emission(current_values)
