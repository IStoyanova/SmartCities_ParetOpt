"""
@author: ist-egu
"""


from __future__ import division
import numpy as np
import pycity_base.functions.handleData as handleData


class P2G(object):

    def __init__(self,environment,maxInput,eta=0.7,labels=None):
        """
        Parameters
        ----------
        environment : Environment object
            Common to all other objects. Includes time and weather instances
        FFInit : float
            initial fill factor of the upper reservoir
        maxOutput : float
            Maximum electric power input of P2G converter
        eta: float
            Power to gas conversion efficiency
        labels: list of strings
            Optional, lists the labels of the object
        """
        self._kind = "p2gConverter"
        self.labels = labels

        self.maxPInput=maxInput
        self.eta=eta

        self.environment = environment

        timestepsTotal       = environment.timer.timestepsTotal
        timestepsUsedHorizon = environment.timer.timestepsUsedHorizon

        #Time Dependent Variables: Energy potential and water content in the water reservoir
        self.totalSchedule=np.zeros(timestepsTotal)
        self.totalPInput      = np.zeros(timestepsTotal)
        self.totalGOutput =np.zeros(timestepsTotal)
        self.currentSchedule   = np.zeros(timestepsUsedHorizon)
        self.currentPInput    = np.zeros(timestepsUsedHorizon)
        self.currentGOutput =np.zeros(timestepsUsedHorizon)

    def getPower(self,currentValues=True):
        return handleData.getValues(currentValues,
                                              self.currentSchedule,
                                              self.totalSchedule)

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
        PInput : array_like
            Input electric power
        GOutput : array_like
            Output gas power
        """
        PInput = handleData.getValues(currentValues, self.currentPInput,
                                      self.totalPInput)
        GOutput= handleData.getValues(currentValues, self.currentGOutput,
                                         self.totalGOutput)
        return PInput, GOutput

    def setResults(self, schedule):
        """
        Save resulting input electric and output gas powers
        """
        #Save schedule
        results = handleData.saveResult(self.environment.timer,
                                        self.currentSchedule,
                                        self.totalSchedule,
                                        schedule)
        (self.currentSchedule, self.totalSchedule) = results

        # Save input electric power
        results = handleData.saveResult(self.environment.timer,
                                        self.currentPInput,
                                        self.totalPInput,
                                        schedule)
        (self.currentPInput, self.totalPInput) = results

        # Save output gas power
        results = handleData.saveResult(self.environment.timer,
                                        self.currentGOutput,
                                        self.totalGOutput,
                                        schedule*self.eta)
        (self.currentGOutput, self.totalGOutput) = results

    def getNominalValues(self):
        """
        Get P2G converter's maximum power input
        """
        return (self.maxPInput,self.eta)










