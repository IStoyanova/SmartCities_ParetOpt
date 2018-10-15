#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 06 16:16:07 2015

@author: tsz
"""

"""
upgrade
@author: ist-egu
"""

import numpy as np
import updatedClassses.Supply.HeatingDevice as HeatingDevice
import pycity_base.functions.handleData as handleData


class CHP(HeatingDevice.HeatingDevice):
    """
    Implementation of the CHP unit
    """
    specificEmission=0.2/3600/1000  #0.2 kg/kWh--->kg/W.s

    def __init__(self,
                 environment,
                 pNominal,
                 qNominal,
                 omega,
                 tMax=85,
                 lowerActivationLimit=1,
                 labels = None):
        """
        Parameters
        ---------
        environment : environment object
            Common to all other objects. Includes time and weather instances
        pNominal : array of float
            nominal electricity output in Watt
        qNominal : array of float
            nominal heat output in Watt
        fNominal: array of float
            nominal fuel inpit in Wat
        omega : array of float
            total efficiency of the CHP unit (without unit)
        tMax : integer, optional
            maximum provided temperature in °C
        lowerActivationLimit : float (0 <= lowerActivationLimit <= 1)
            Define the lower activation limit. For example, heat pumps are
            typically able to operate between 50 % part load and rated load.
            In this case, lowerActivationLimit would be 0.5
            Two special cases:
            Linear behavior: lowerActivationLimit = 0
            Two-point controlled: lowerActivationLimit = 1
        labels: list of strings
            Optional, lists the labels of the object
        """

        self.pNominal = pNominal
        self.omega = omega
        self.fNominal=(pNominal+qNominal)/self.omega
        self.sigma = pNominal / qNominal
        super(CHP, self).__init__(environment,
                                  qNominal,
                                  tMax,
                                  lowerActivationLimit)

        self._kind = "chp"
        self.labels=labels

        self.totalPOutput   = np.zeros(environment.timer.timestepsTotal)
        self.currentPOutput = np.zeros(environment.timer.timestepsUsedHorizon)


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
        pOutput : array_like
            Electricity production of the CHP unit
        qOutput : array_like
            Heat production of the CHP unit
        fInput: array_like
            Fuel consumption of the CHP unit
        emission: array_like
            Carbon emission of the CHP unit
        schedule : array_like
            Operational schedule
        """
        pOutput = handleData.getValues(currentValues,
                                       self.currentPOutput,
                                       self.totalPOutput)

        return pOutput,self._getQOutput(currentValues),self._getFInput(currentValues),self._getEmission(currentValues),self._getSchedule(currentValues)

    def setResults(self,schedule):
        """
        Save resulting electricty, heat output, fuel input (also emission indirectly) and operational schedule.
        """
        self._setSchedule(schedule)
        self._setQOutput(schedule*self.pNominal/self.sigma)
        self._setFInput(schedule*self.fNominal,self.specificEmission)
        result = handleData.saveResult(self.environment.timer,
                                       self.currentPOutput,
                                       self.totalPOutput,
                                       schedule*self.pNominal)
        (self.currentPOutput, self.totalPOutput) = result

    def getNominalValues(self):
        """
        Return the CHP unit's nominal values as a tuple.

        Order: Overall efficiency, power to heat ratio, nominal electricity
        output, nominal heat output, maximum flow temperature and lower
        activation limit.
        """
        return (self.omega, self.sigma, self.pNominal, self.qNominal,
                self.tMax, self.lowerActivationLimit)
