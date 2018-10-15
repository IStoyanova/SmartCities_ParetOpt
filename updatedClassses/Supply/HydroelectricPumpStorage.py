"""
author: ist-egu
"""

"""
NOTES
1- etaCharge and etaDischarge are also including power electronic units connected to input and output
"""

import numpy as np
import pycity_base.functions.handleData as handleData


class HydroElectric(object):
    g=9.81      #Gravity: m/s2
    d=997       #Water density: kg/m3

    def __init__(self,environment,FFInit,capacity,effectiveHeight,etaCharge=0.95, etaDischarge=0.95,labels=None):
        """
        Parameters
        ----------
        environment : Environment object
            Common to all other objects. Includes time and weather instances
        FFInit : float
            initial fill factor of the upper reservoir
        capacity : float
            Energy capcacity of the  storage:J
        effectiveHeight : float
            Height of the upper reservoir
        labels: list of strings
            Optional, lists the labels of the object
        """
        self._kind = "heps"
        self.labels = labels

        self.environment = environment

        #Storage facility's parameters
        self.h = effectiveHeight                                            #Effective height of the upper reservoir
        self.energyCapacity=capacity                                        #Energy capacity of the upper reservoir: Joule
        self.maxCharge=capacity/14400
        self.maxDischarge=capacity/14400
        self.waterCapacity=capacity/(self.d*self.g*self.h)                  #Water volume capacity of the upper reservoir: m3
        self.etaCharge=etaCharge                                            #Hydropump efficiency
        self.etaDischarge=etaDischarge                                      #Turbine+Generator efficiency
        self.ffInit=FFInit                                                  #Initial fill factor

        self.dT = environment.timer.timeDiscretization
        timestepsTotal       = environment.timer.timestepsTotal
        timestepsUsedHorizon = environment.timer.timestepsUsedHorizon

        #Time Dependent Variables: Energy potential and water content in the water reservoir
        self.totalSchedule         = np.zeros(timestepsTotal)
        self.totalFF          = np.zeros(timestepsTotal)
        self.totalPCharge      = np.zeros(timestepsTotal)
        self.totalPDischarge   = np.zeros(timestepsTotal)
        self.totalWCharge =np.zeros(timestepsTotal)
        self.totalWDischarge =np.zeros(timestepsTotal)
        self.currentSchedule   = np.zeros(timestepsUsedHorizon)
        self.currentFF        = np.zeros(timestepsUsedHorizon)
        self.currentPCharge    = np.zeros(timestepsUsedHorizon)
        self.currentPDischarge = np.zeros(timestepsUsedHorizon)
        self.currentWCharge =np.zeros(timestepsUsedHorizon)
        self.currentWDischarge =np.zeros(timestepsUsedHorizon)

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
        ff : array_like
            Fill factor
        PCharge : array_like
            Charging power
        PDischarge : array_like
            Discharging power
        WCharge : array_like
            Stored water
        WDischarge : array_like
            Removed water

        """
        ff = handleData.getValues(currentValues, self.currentFF,
                                   self.totalFF)
        PCharge = handleData.getValues(currentValues, self.currentPCharge,
                                      self.totalPCharge)
        PDischarge = handleData.getValues(currentValues, self.currentPDischarge,
                                         self.totalPDischarge)
        WCharge = handleData.getValues(currentValues, self.currentWCharge,
                                      self.totalPCharge)
        WDischarge = handleData.getValues(currentValues, self.currentWDischarge,
                                         self.totalPDischarge)

        return ff, PCharge, PDischarge, WCharge, WDischarge

    def getPower(self,currentValues=True):
        return handleData.getValues(currentValues,
                                              self.currentSchedule,
                                              self.totalSchedule)

    def setResults(self, schedule):
        """
        Save resulting state of charge, charging and discharging powers, filled and removed water
        """
        PCharge_schedule=np.zeros(len(schedule))
        PDischarge_schedule=np.zeros(len(schedule))

        PCharge_schedule[schedule<0]=-schedule[schedule<0]
        PDischarge_schedule[schedule>0]=schedule[schedule>0]

        #TODO: Change the length issue
        ff=np.array([self.ffInit*self.energyCapacity]*len(schedule))
        add2ff=np.concatenate((np.array([0]), np.cumsum((PCharge_schedule*self.etaCharge-PDischarge_schedule/self.etaDischarge)*self.dT)[:len(schedule)-1]), axis=0)
        ff_schedule=ff+add2ff

        #Save schedule
        results = handleData.saveResult(self.environment.timer,
                                        self.currentSchedule,
                                        self.totalSchedule,
                                        schedule)
        (self.currentSchedule, self.totalSchedule) = results

        # Save fill factor
        results = handleData.saveResultInit(self.environment.timer,
                                            self.currentFF,
                                            self.totalFF,
                                            ff_schedule/self.energyCapacity)
        (self.currentFF, self.totalFF, self.ffInit) = results

        # Save charging power
        results = handleData.saveResult(self.environment.timer,
                                        self.currentPCharge,
                                        self.totalPCharge,
                                        PCharge_schedule)
        (self.currentPCharge, self.totalPCharge) = results


        # Save discharging power
        results = handleData.saveResult(self.environment.timer,
                                        self.currentPDischarge,
                                        self.totalPDischarge,
                                        PDischarge_schedule)
        (self.currentPDischarge, self.totalPDischarge) = results

        # Save filled water
        results = handleData.saveResult(self.environment.timer,
                                        self.currentWCharge,
                                        self.totalWCharge,
                                        PCharge_schedule*self.etaCharge/(self.d*self.g*self.h))
        (self.currentWCharge, self.totalWCharge) = results

        # Save remowed water
        results = handleData.saveResult(self.environment.timer,
                                        self.currentWDischarge,
                                        self.totalWDischarge,
                                        PDischarge_schedule/(self.etaDischarge*self.d*self.g*self.h))
        (self.currentWDischarge, self.totalWDischarge) = results


    def getNominalValues(self):
        """
        Get hydroelectric pump storage's energy capacity, charging and discharging efficiency, water capacity, effective height of upper reservior
        """
        return (self.energyCapacity,
                self.etaCharge, self.etaDischarge, self.waterCapacity,self.h)










