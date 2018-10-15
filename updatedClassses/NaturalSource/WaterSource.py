from __future__ import division
import numpy as np
import pycity_base.functions.handleData as handleData

class WaterSource(object):
    def __init__(self,environment,labels=None):
        """
        Parameters
        ----------
        environment : Environment object
            Common to all other objects. Includes time and weather instances
        labels: list of strings
            Optional, lists the labels of the object
        """
        self._kind='watersource'
        self.labels = labels

        self.environment=environment

        timestepsTotal       = environment.timer.timestepsTotal
        timestepsUsedHorizon = environment.timer.timestepsUsedHorizon

        self.totalWOutput=np.zeros(timestepsTotal)
        self.currentWOutput=np.zeros(timestepsUsedHorizon)

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
            remowed : array_like
                Removed water volume
            """
            removal = handleData.getValues(currentValues, self.currentWOutput,
                                             self.totalWOutput)
            return removal

    def setResults(self, schedule):
        """
        Save resulting water volume output
        """
        # Save water removal
        results = handleData.saveResult(self.environment.timer,
                                        self.currentWOutput,
                                        self.totalWOutput,
                                        schedule)
        (self.currentWOutput, self.totalWOutput) = results

