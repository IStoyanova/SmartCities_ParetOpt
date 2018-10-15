"""
upgrade
@author: ist-egu
"""

from updatedClassses.Transport.TranportationMedium import TransportMedium

class HeatPipe(TransportMedium):
    def __init__(self,environment,length,diameter,specificConductivity=0.591):
        """
        Parameter
        ---------
        length: pipeLength: m
        diameter: diameter of the heat pipe: m2
        specificConductivity: specific conduction of the conducting material: W/m.K
        """

        self.R=length/(specificConductivity*diameter*diameter*3.14/4)   #Thermal resistance K/W

        super(HeatPipe, self).__init__(environment)
        self._kind = "heatpipe"


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
        flowQuantity : array_like
            Heat flow rate through the Pipe
        nonFlowQuantity : array_like
            Temperature drop across the Pipe
        """

        return (self._getFlowQuantity(currentValues),
                self._getNonFlowQuantity(currentValues))

    def setResults(self, hFlow):
        """
        Save flowing heat flow rate and temperature drop.
        """

        self._setFlowQuantity(hFlow)  #W
        self._setNonFlowQuantity(hFlow*self.R)  #K



