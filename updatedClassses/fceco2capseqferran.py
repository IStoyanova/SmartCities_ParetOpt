"""
@author: ist-fce
"""

import numpy as np
import pycity_base.functions.handleData as handleData


class co2capseq(object):
    """
    Implementation of a CO2 capturing and sequestration that takes electricity as input ans negative CO2 as
    output"""

    def __init__(self,environment, maxinput=10000000,maxelimination=0.8,rate=3,  labels=None):
        """
        Workflow
        --------
        1 :object used in the optimization as a co2 eliminator,
        2 :takes gas and electricity as inputs and eliminates co2

        Parameter
        ---------
        environment : Environment object
            Common to all other objects. Includes time and weather instances

        labels: list of strings
            Optional, lists the labels of the object

        maxinput: corresponds to the maximum capacity of co2 (mesured in units of energy to be created) that the
         machines are designed to eliminate

         maxelimination: corresponds to maximum percentage of co2 that can be elimnated compared to the generation

         rate: is the ratio of elimination/generation to eliminate

        """
        self._kind = "co2capseq"
        self.labels = labels
        self.maxinput = maxinput
        self.maxelimination=maxelimination
        self.environment = environment
        self.rate=rate
        timestepsTotal = environment.timer.timestepsTotal
        timestepsUsedHorizon = environment.timer.timestepsUsedHorizon
        self.totalSchedule = np.zeros(timestepsTotal)
        self.currentSchedule = np.zeros(timestepsUsedHorizon)



    def _setSchedule(self, schedule):
        """ Save the computed schedule to the device """
        results = handleData.saveResult(self.environment.timer,
                                        self.currentSchedule,
                                        self.totalSchedule,
                                        schedule)
        (self.currentSchedule, self.totalSchedule) = results


    def _getSchedule(self, currentValues=True):
        """
        Return the schedule. If currentValues=True: current values,
        else: total values
        """
        return handleData.getValues(currentValues,
                                    self.currentSchedule,
                                    self.totalSchedule)
