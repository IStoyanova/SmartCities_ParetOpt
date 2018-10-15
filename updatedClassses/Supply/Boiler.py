#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 06 16:50:30 2015

@author: tsz
"""

"""
upgrade
@author: ist-egu
"""

import updatedClassses.Supply.HeatingDevice as HeatingDevice


class Boiler(HeatingDevice.HeatingDevice):
    """
    Implementation of the boiler
    """
    specificEmission=0.2/3600/1000  #0.2 kg/kWh--->kg/W.s
    def __init__(self,
                 environment,
                 qNominal,
                 eta,
                 tMax=85,
                 lowerActivationLimit=1,
                 labels=None):
        """
        Parameter
        ---------
        environment : Environment object
            Common to all other objects. Includes time and weather instances
        qNominal : array of float
            nominal heat output in Watt
        fNominal: array of float
            nominal fuel input in Watt
        eta : array of float
            efficiency (without unit)
        tMax : Integer, optional
            maximum provided temperature in °C
        lowerActivationLimit : Float (0 <= lowerActivationLimit <= 1)
            Define the lower activation limit. For example, heat pumps are
            typically able to operate between 50 % part load and rated load.
            In this case, lowerActivationLimit would be 0.5
            Two special cases:
            Linear behavior: lowerActivationLimit = 0
            Two-point controlled: lowerActivationLimit = 1
        labels: list of strings
            Optional, lists the labels of the object
        """

        self.eta = eta
        self.fNominal=qNominal/self.eta
        super(Boiler, self).__init__(environment,
                                     qNominal,
                                     tMax,
                                     lowerActivationLimit)
        self._kind = "boiler"
        self.labels=labels

    def getResults(self, currentValues=True):
        """
        Return results.

        Parameter
        ---------
        currentValues : boolean, optional
            - True : Return only values for this scheduling period
            - False : Return values for all scheduling periods

        Order
        -----
        qOutput : array_like
            Heat production of the boiler
        schedule : array_like
            Operational schedule
        """
        return self._getQOutput(currentValues),self._getFInput(currentValues),self._getEmission(currentValues),self._getSchedule(currentValues)

    def setResults(self, schedule):
        """
        Save resulting heat output and operational schedule.
        """
        self._setSchedule(schedule)
        self._setQOutput(schedule*self.qNominal)
        self._setFInput(schedule*self.fNominal,self.specificEmission)


    def getNominalValues(self):
        """
        Get the boiler's efficiency, nominal heat output, maximum flow
        temperature and lower activation limit.
        """
        return (self.eta, self.qNominal, self.tMax, self.lowerActivationLimit)
