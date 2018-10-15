"""
upgrade
@author: ist-egu
"""

from updatedClassses.Transport.TranportationMedium import TransportMedium

class WaterPipe(TransportMedium):
    def __init__(self,environment,length=10,diameter=0.1,rho=1000,lamda=0.03):

        self.rho = rho                  #gas density: kg/m3
        self.lamda = lamda              #darcy friction factor
        self.L=length                   #gas pipe length: m
        self.D=diameter                 #gas pipe diameter: m

        super(WaterPipe, self).__init__(environment)
        self._kind = "waterpipe"


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
            Water volume flow rate through the Pipe
        nonFlowQuantity : array_like
            Pressure drop across the Pipe
        """

        return (self._getFlowQuantity(currentValues),
                self._getNonFlowQuantity(currentValues))

    def setResults(self, vRate):
        """
        Save volume flow rate of the water and pressure drop.
        """

        self._setFlowQuantity(vRate)  #m3/s
        self._setNonFlowQuantity((vRate/(3.141*(0.5*self.D)*(0.5*self.D)))*(vRate/(3.141*(0.5*self.D)*(0.5*self.D)))*self.lamda*self.L/self.D*self.rho/2)  #bar
        #TODO: Check the darcy formula






