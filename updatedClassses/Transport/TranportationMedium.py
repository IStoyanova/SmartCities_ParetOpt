"""
upgrade
@author: ist-egu
"""

import numpy as np
import pycity_base.functions.handleData as handleData



class TransportMedium(object):
    """
    Superclass of transport mediums
    """

    def __init__(self, environment):
        """
        Parameters
        ----------
        environment : Environment object
            Common to all other objects. Includes time and weather instances
        """

        self._kind = "transportmedium"

        timestepsTotal = environment.timer.timestepsTotal
        timestepsUsedHorizon = environment.timer.timestepsUsedHorizon

        self.environment = environment

        self.totalFlowQuantity  = np.zeros(timestepsTotal)
        self.totalNonFlowQuantity = np.zeros(timestepsTotal)
        self.currentFlowQuantity  = np.zeros(timestepsUsedHorizon)
        self.currentNonFlowQuantity = np.zeros(timestepsUsedHorizon)

    def _setFlowQuantity(self, flowQuantity):
        """ Save the computed flow through the heating device """
        results = handleData.saveResult(self.environment.timer,
                                        self.currentFlowQuantity,
                                        self.totalFlowQuantity,
                                        flowQuantity)
        (self.currentFlowQuantity, self.totalFlowQuantity) = results

    def _setNonFlowQuantity(self, nonflowQuantity):
        """ Save the computed non flow quantity drop across the heating device """
        results = handleData.saveResult(self.environment.timer,
                                        self.currentNonFlowQuantity,
                                        self.totalNonFlowQuantity,
                                        nonflowQuantity)
        (self.currentNonFlowQuantity, self.totalNonFlowQuantity) = results

    def _getFlowQuantity(self, currentValues=True):
        """
        Return the flow quantity. If currentValues=True: current values,
        else: total values
        """
        return handleData.getValues(currentValues,
                                    self.currentFlowQuantity,
                                    self.totalFlowQuantity)

    def _getNonFlowQuantity(self, currentValues=True):
        """
        Return the non flow quantity drop. If currentValues=True: current values,
        else: total values
        """
        return handleData.getValues(currentValues,
                                    self.currentNonFlowQuantity,
                                    self.totalNonFlowQuantity)