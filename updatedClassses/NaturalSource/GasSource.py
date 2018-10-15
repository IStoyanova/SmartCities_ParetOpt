from __future__ import division
import numpy as np
import pycity_base.functions.handleData as handleData

class GasSource(object):
    def __init__(self,environment,labels=None):
        """
        Parameters
        ----------
        environment : Environment object
            Common to all other objects. Includes time and weather instances
        labels: list of strings
            Optional, lists the labels of the object
        """
        self._kind='gassource'
        self.environment=environment
        self.labels=labels

        timestepsTotal       = environment.timer.timestepsTotal
        timestepsUsedHorizon = environment.timer.timestepsUsedHorizon

        self.totalGOutput=np.zeros(timestepsTotal)
        self.currentGOutput=np.zeros(timestepsUsedHorizon)

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
            GOutput : array_like
                Removed gas power
            """
            removal = handleData.getValues(currentValues, self.currentGOutput,
                                             self.totalGOutput)
            return removal

    def setResults(self, schedule):
        """
        Save resulting gas power output
        """
        # Save gas power removal
        results = handleData.saveResult(self.environment.timer,
                                        self.currentGOutput,
                                        self.totalGOutput,
                                        schedule)
        (self.currentGOutput, self.totalGOutput) = results

