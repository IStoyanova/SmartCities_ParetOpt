#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 06 20:01:19 2015

@author: Thomas
"""

"""
upgrade
@author: ist-egu
"""

import numpy as np
import pycity_base.functions.handleData as handleData


class Battery(object):
    """
    Implementation of the battery
    """

    def __init__(self, environment, socInit, capacity, selfDischarge=0.00,etaCharge=1.00, etaDischarge=1.00,labels=None):
        """
        Parameters
        ----------
        environment : Environment object
            Common to all other objects. Includes time and weather instances
        socInit : float (0 <= socInit <= 1)
            Initial state of charge
        capacity : float
            Battery's capacity in Joule
        maxCharge: float
            Maximum charge power in W
        maxDisharge: float
            Maximum discharge power in W
        selfDischarge : float (0 <= selfDischarge <= 1)
            Rate of self discharge per time step (without unit)
        etaCharge : float (0 <= etaCharge <= 1)
            Charging efficiency (without unit)
        etaDischarge : float (0 <= etaDischarge <= 1)
            Discharging efficiency (without unit)
        labels: list of strings
            Optional, lists the labels of the object
        """
        self._kind = "battery"
        self.labels=labels

        self.environment = environment
        self.capacity = capacity
        self.maxCharge=capacity/14400
        self.maxDischarge=capacity/14400
        self.selfDischarge = selfDischarge
        self.etaCharge = etaCharge
        self.etaDischarge = etaDischarge
        self.socInit = socInit


        self.dT=environment.timer.timeDiscretization
        timestepsTotal       = environment.timer.timestepsTotal
        timestepsUsedHorizon = environment.timer.timestepsUsedHorizon

        self.totalSoc          = np.zeros(timestepsTotal)
        self.totalPCharge      = np.zeros(timestepsTotal)
        self.totalPDischarge   = np.zeros(timestepsTotal)
        self.currentSoc        = np.zeros(timestepsUsedHorizon)
        self.currentPCharge    = np.zeros(timestepsUsedHorizon)
        self.currentPDischarge = np.zeros(timestepsUsedHorizon)

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
        soc : array_like
            State of charge
        charge : array_like
            Charging power
        discharge : array_like
            Discharging power
        """
        soc = handleData.getValues(currentValues, self.currentSoc,
                                   self.totalSoc)
        charge = handleData.getValues(currentValues, self.currentPCharge,
                                      self.totalPCharge)
        discharge = handleData.getValues(currentValues, self.currentPDischarge,
                                         self.totalPDischarge)
        return soc, charge, discharge

    def setResults(self, schedule):
        """
        Save resulting state of charge, charging and discharging powers.
        """
        # Save state of charge
        charge_schedule=np.zeros(len(schedule))
        discharge_schedule=np.zeros(len(schedule))
        soc=np.array([self.socInit*self.capacity]*len(schedule))

        charge_schedule[schedule<0]=-schedule[schedule<0]
        discharge_schedule[schedule>0]=schedule[schedule>0]



        add2soc=np.concatenate((np.array([0]), np.cumsum((charge_schedule*self.etaCharge-discharge_schedule/self.etaDischarge)*self.dT)[:len(schedule)-1]), axis=0)
        soc_schedule=soc+add2soc

        results = handleData.saveResultInit(self.environment.timer,
                                            self.currentSoc,
                                            self.totalSoc,
                                            soc_schedule/self.capacity)
        (self.currentSoc, self.totalSoc, self.socInit) = results

        # Save charging power
        results = handleData.saveResult(self.environment.timer,
                                        self.currentPCharge,
                                        self.totalPCharge,
                                        charge_schedule)
        (self.currentPCharge, self.totalPCharge) = results

        # Save discharging power
        results = handleData.saveResult(self.environment.timer,
                                        self.currentPDischarge,
                                        self.totalPDischarge,
                                        discharge_schedule)
        (self.currentPDischarge, self.totalPDischarge) = results

    def getNominalValues(self):
        """
        Get battery's capacity, rate of self discharge, charging and
        discharging efficiency.
        """
        return (self.capacity, self.selfDischarge,
                self.etaCharge, self.etaDischarge)
