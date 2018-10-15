"""
upgrade
@author: ist-egu
"""
from updatedClassses.Transport.TranportationMedium import TransportMedium

class Cable(TransportMedium):
    def __init__(self,environment,length,diameter=0.2,spesificResistance=1.68*10**-8):


        self.rho=spesificResistance     #Specific resistance of copper ohm.m
        self.L=length                   #Cable length: m
        self.A=3.141*(diameter/2)**2    #Cross section of cable: m2
        self.R=self.rho*length/self.A

        super(Cable, self).__init__(environment)
        self._kind = "electriccable"


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
            Current flowing through the Cable
        nonFlowQuantity : array_like
            Voltage drop across the Cable
        """

        return (self._getFlowQuantity(currentValues),
                self._getNonFlowQuantity(currentValues))

    def setResults(self, current):
        """
        Save flowing current and voltage drop.
        """

        self._setFlowQuantity(current)
        self._setNonFlowQuantity(current*self.R)



