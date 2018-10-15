"""
@author: ist-egu
"""

from __future__ import division
import numpy as np
import pycity_base.functions.handleData as handleData
import updatedClassses.NaturalSource.GasSource as GasSource

class P2GStorage(GasSource.GasSource):

    def __init__(self,environment,FFInit,capacity,etaCharge=1.0,etaDischarge=1.0,labels=None):
        """
        Parameters
        ----------
        environment : Environment object
            Common to all other objects. Includes time and weather instances
        FFInit : float
            initial fill factor of the storage unit
        capacity : float
            Energy capcacity of the  storage:J
        etaCharge : float
            Charging efficiency of the storage unit
        etaDischarge : float
            Disharging efficiency of the storage unit
        labels: list of strings
            Optional, lists the labels of the object
        """

        #Storage facility's parameters
        self.capacity=capacity
        self.maxCharge=capacity/14400
        self.maxDischarge=capacity/14400
        self.ffInit=FFInit
        self.etaCharge=etaCharge
        self.etaDischarge=etaDischarge

        self.dT = environment.timer.timeDiscretization

        super().__init__(environment)

        self._kind = "p2gStorage"
        self.labels=labels

        self.totalSchedule=np.zeros(environment.timer.timestepsTotal)
        self.totalFF          = np.zeros(environment.timer.timestepsTotal)
        self.totalGInput   = np.zeros(environment.timer.timestepsTotal)
        self.currentSchedule=np.zeros(environment.timer.timestepsTotal)
        self.currentFF        = np.zeros(environment.timer.timestepsUsedHorizon)
        self.currentGInput = np.zeros(environment.timer.timestepsUsedHorizon)


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
        GInput: array_like
            Charging gas power
        GOutput : array_like
            Discharging gas power
        """

        ff=handleData.getValues(currentValues, self.currentFF,
                                      self.totalFF)
        GInput = handleData.getValues(currentValues, self.currentGInput,
                                      self.totalGInput)
        GOutput = handleData.getValues(currentValues, self.currentGOutput,
                                         self.totalGOutput)


        return ff,GInput, GOutput

    def setResults(self, schedule):
        """
        Save resulting fill factor, charging and discharging gas powers
        """
        print()
        print("Schedule assinged to storage")

        GCharge_schedule=np.zeros(len(schedule))
        GDischarge_schedule=np.zeros(len(schedule))

        GCharge_schedule[schedule<0]=-schedule[schedule<0]
        GDischarge_schedule[schedule>0]=schedule[schedule>0]

        ff=np.array([self.ffInit*self.capacity]*len(schedule))
        add2ff=np.concatenate((np.array([0]), np.cumsum((GCharge_schedule*self.etaCharge-GDischarge_schedule/self.etaDischarge)*self.dT)[:len(schedule)-1]), axis=0)
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
                                            ff_schedule/self.capacity)
        (self.currentFF, self.totalFF, self.ffInit) = results

        # Save charging power
        results = handleData.saveResult(self.environment.timer,
                                        self.currentGInput,
                                        self.totalGInput,
                                        GCharge_schedule)
        (self.currentGInput, self.totalGInput) = results

        # Save discharging power
        results = handleData.saveResult(self.environment.timer,
                                        self.currentGOutput,
                                        self.totalGOutput,
                                        GDischarge_schedule)
        (self.currentGOutput, self.totalGOutput) = results

    def getNominalValues(self):
        """
        Get gas storage's energy capacity, charging and discharging efficiency
        """
        return (self.capacity,self.etaCharge, self.etaDischarge)