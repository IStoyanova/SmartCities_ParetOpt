#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 06 15:57:15 2015

@author: tsz
"""

"""
upgrade
@author: ist-egu
"""

import numpy as np
import pycity_base.functions.handleData as handleData


class HeatingDevice(object):
    """
    Superclass of all heating devices.
    """

    def __init__(self, environment, qNominal, tMax=85, lowerActivationLimit=1):
        """
        Parameters
        ----------
        environment : Environment object
            Common to all other objects. Includes time and weather instances
        qNominal : Array of float
            Nominal heat output in Watt
        tMax : Float, optional
            Maximum provided temperature in °C
        lowerActivationLimit : float (0 <= lowerActivationLimit <= 1)
            Define the lower activation limit. For example, heat pumps are
            typically able to operate between 50 % part load and rated load.
            In this case, lowerActivationLimit would be 0.5
            Two special cases:
            Linear behavior: lowerActivationLimit = 0
            Two-point controlled: lowerActivationLimit = 1
        """
        self._kind = "heatingdevice"

        timestepsTotal = environment.timer.timestepsTotal
        timestepsUsedHorizon = environment.timer.timestepsUsedHorizon

        self.environment = environment
        self.qNominal = qNominal
        self.tMax = tMax
        self.lowerActivationLimit = lowerActivationLimit
        self.totalFInput  = np.zeros(timestepsTotal)
        self.totalQOutput  = np.zeros(timestepsTotal)
        self.totalSchedule = np.zeros(timestepsTotal)
        self.totalEmission=np.zeros(timestepsTotal)
        self.currentFInput  = np.zeros(timestepsUsedHorizon)
        self.currentQOutput  = np.zeros(timestepsUsedHorizon)
        self.currentSchedule = np.zeros(timestepsUsedHorizon)
        self.currentEmission=np.zeros(timestepsUsedHorizon)

    def _setSchedule(self, schedule):
        """ Save the computed schedule to the heating device """
        results = handleData.saveResult(self.environment.timer,
                                        self.currentSchedule,
                                        self.totalSchedule,
                                        schedule)
        (self.currentSchedule, self.totalSchedule) = results

    def _setFInput(self,fInput,emmisionRate=None):
        results = handleData.saveResult(self.environment.timer,
                                    self.currentFInput,
                                    self.totalFInput,
                                    fInput)
        (self.currentFInput, self.totalFInput) = results


        if emmisionRate!=None:
            results = handleData.saveResult(self.environment.timer,
                                        self.currentEmission,
                                        self.totalEmission,
                                        fInput*emmisionRate)
            (self.currentEmission, self.totalEmission) = results

    def _setQOutput(self, qOutput):
        """ Save the computed heat output to the heating device """
        results = handleData.saveResult(self.environment.timer,
                                        self.currentQOutput,
                                        self.totalQOutput,
                                        qOutput)
        (self.currentQOutput, self.totalQOutput) = results


    def _getSchedule(self, currentValues=True):
        """
        Return the schedule. If currentValues=True: current values,
        else: total values
        """
        return handleData.getValues(currentValues,
                                    self.currentSchedule,
                                    self.totalSchedule)

    def _getQOutput(self, currentValues=True):
        """
        Return the heat output. If currentValues=True: current values,
        else: total values
        """
        return handleData.getValues(currentValues,
                                    self.currentQOutput,
                                    self.totalQOutput)

    def _getFInput(self,currentValues=True):
        """
        Return the fuel input. If currentValues=True: current values,
        else: total values
        """
        return handleData.getValues(currentValues,
                                    self.currentFInput,
                                    self.totalFInput)

    def _getEmission(self,currentValues=True):
        """
        Return the emission. If currentValues=True: current values,
        else: total values
        """
        return handleData.getValues(currentValues,
                                    self.currentEmission,
                                    self.totalEmission)