#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 09 12:26:24 2015

@author: tsz
"""

"""
upgrade
@author: ist-egu
"""


import numpy as np
import pycity_base.functions.handleData as handleData

class BES(object):
    """
    Building Energy System (BES) is able to contain the following devices:
        Battery, Boiler, Combined Heat and Power (CHP) unit, Electrical 
        heater, Heatpump, Inverter (AC/DC and DC/AC), Photovoltaics (PV) and 
        Thermal Energy Storage (TES) unit
    """
    
    def __init__(self, environment,labels=None):
        """
        Workflow
        --------
        1 : Create an empty building energy system (BES) that only contains 
            the environment pointer
        2 : Add devices such as thermal energy storage unit to the BES, by 
            invoking the addDevice or addMultipleDevices methods.
        
        Parameter
        ---------
        environment : Environment object
            Common to all other objects. Includes time and weather instances
        labels: list of strings
            Optional, lists the labels of the object
        """
        self.environment = environment
        
        self._kind = "bes"
        self.labels=labels
        
        # Initialize all devices as empty lists
        self.battery          = []
        self.boiler           = []
        self.chp              = []
        self.electricalHeater = []
        self.heatpump         = []
        self.inverterAcdc     = []
        self.inverterDcac     = []
        self.pv               = []
        self.tes              = []
        
        # The new BES is still empty
        self.hasBattery          = False
        self.hasBoiler           = False
        self.hasChp              = False
        self.hasElectricalHeater = False
        self.hasHeatpump         = False
        self.hasInverterAcdc     = False
        self.hasInverterDcac     = False
        self.hasPv               = False
        self.hasTes              = False


        timestepsTotal       = environment.timer.timestepsTotal
        timestepsUsedHorizon = environment.timer.timestepsUsedHorizon

        self.totalPOutput =np.zeros(timestepsTotal)
        self.currentPOutput   = np.zeros(timestepsUsedHorizon)
        self.totalGOutput =np.zeros(timestepsTotal)
        self.currentGOutput   = np.zeros(timestepsUsedHorizon)
        self.totalQOutput =np.zeros(timestepsTotal)
        self.currentQOutput   = np.zeros(timestepsUsedHorizon)
        self.totalCOutput =np.zeros(timestepsTotal)
        self.currentCOutput   = np.zeros(timestepsUsedHorizon)

    def addDevice(self, objectInstance):
        """
        Add a device object
        
        Example
        -------
        >>> myChp = CHP(...)
        >>> myBes = BES(...)
        >>> myBes.addDevice(myChp)
        """
        if objectInstance._kind == "battery":
            self.battery = objectInstance
            self.hasBattery = True
        
        elif objectInstance._kind == "boiler":
            self.boiler = objectInstance
            self.hasBoiler = True
        
        elif objectInstance._kind == "chp":
            self.chp = objectInstance
            self.hasChp = True
        
        elif objectInstance._kind == "electricalheater":
            self.electricalHeater = objectInstance
            self.hasElectricalHeater = True
        
        elif objectInstance._kind == "heatpump":
            self.heatpump = objectInstance
            self.hasHeatpump = True
        
        elif objectInstance._kind == "inverter":
            if objectInstance.inputAC:
                self.inverterAcdc = objectInstance
                self.hasInverterAcdc = True
            else:
                self.inverterDcac = objectInstance
                self.hasInverterDcac = True
        
        elif objectInstance._kind == "pv":
            self.pv = objectInstance
            self.hasPv = True
            
        elif objectInstance._kind == "tes":
            self.tes = objectInstance
            self.hasTes = True
            
    def addMultipleDevices(self, devices):
        """
        Add multiple devices to the existing BES
        
        Parameter
        ---------
        devices : List-like
            List (or tuple) of devices that are added to the BES
            
        Example
        -------
        >>> myBoiler = Boiler(...)
        >>> myChp = CHP(...)
        >>> myBes = BES(...)
        >>> myBes.addMultipleDevices([myBoiler, myChp])
        """
        for device in devices:
            self.addDevice(device)
    
    def getHasDevices(self, 
                      allDevices=True, 
                      battery=False, 
                      boiler=False, 
                      chp=False, 
                      electricalHeater=False, 
                      heatpump=False, 
                      inverterAcdc=False, 
                      inverterDcac=False, 
                      pv=False, 
                      tes=False):
        """
        Get information if certain devices are installed devices.
        The result is in alphabetical order, starting with "battery"
        
        Parameters
        ----------
        allDevices : boolean, optional
            If true: Return all installed devices
            If false: Only return the specified devices
        battery : boolean, optional
            Return information on the battery?
        boiler : boolean, optional
            Return information on the boiler?
        chp : boolean, optional
            Return information on the chp unit?
        electricalHeater : boolean, optional
            Return information on the electrical heater?
        heatpump : boolean, optional
            Return information on the heat pump?
        inverterAcdc : boolean, optional
            Return information on the AC-DC inverter?
        inverterDcac : boolean, optional
            Return information on the DC-AC inverter?
        pv : boolean, optional
            Return information on the PV modules?
        tes : boolean, optional
            Return information on the thermal energy storage?
        """
        if allDevices:
            result = (self.hasBattery, 
                      self.hasBoiler, 
                      self.hasChp, 
                      self.hasElectricalHeater, 
                      self.hasHeatpump, 
                      self.hasInverterAcdc, 
                      self.hasInverterDcac, 
                      self.hasPv, 
                      self.hasTes)

        else:
            result = ()
            if battery:
                result += (self.hasBattery,)
                
            if boiler:
                result += (self.hasBoiler,)

            if chp:
                result += (self.hasChp,)

            if electricalHeater:
                result += (self.hasElectricalHeater,)

            if heatpump:
                result += (self.hasHeatpump,)

            if inverterAcdc:
                result += (self.hasInverterAcdc,)

            if inverterDcac:
                result += (self.hasInverterDcac,)

            if pv:
                result += (self.hasPv,)
                
            if tes:
                result += (self.hasTes,)
        
        return result

    def getPowerCurves(self, current_values=True):
        """
        Return results.

        Parameter
        ---------
        currentValues : boolean, optional
            - True : Return only values for this scheduling period
            - False : Return values for all scheduling periods

        Order
        -----
        POutput : array_like
            Total electricity output of BES
        QOutput : array_like
            Total heat output of BES
        GOutput: array_like
            Total gas output of BES
        COutput: array_like
            Total emission output of BES
        """

        self.setPowerCurves(current_values)

        pOutput=handleData.getValues(current_values,
                                       self.currentPOutput,
                                       self.totalPOutput)

        gOutput=handleData.getValues(current_values,
                                       self.currentGOutput,
                                       self.totalGOutput)

        qOutput=handleData.getValues(current_values,
                                       self.currentQOutput,
                                       self.totalQOutput)

        cOutput=handleData.getValues(current_values,
                                       self.currentCOutput,
                                       self.totalCOutput)

        return pOutput,gOutput,qOutput,cOutput

    def setPowerCurves(self,current_values=True):

        if current_values:
            timesteps = self.environment.timer.timestepsUsedHorizon
        else:
            timesteps = self.environment.timer.timestepsTotal

        POutput   = np.zeros(timesteps)
        GOutput  = np.zeros(timesteps)
        QOutput  = np.zeros(timesteps)
        COutput= np.zeros(timesteps)

        #TODO: Add remaining devices: electricalHeater, heatPump, inverters, tes
        if self.battery!=[]:
            POutput+=self.battery.getResults(current_values)[2]-self.battery.getResults(current_values)[1]

        if self.boiler!=[]:
            GOutput-=self.boiler.getResults(current_values)[1]
            QOutput+=self.boiler.getResults(current_values)[0]
            COutput+=self.boiler.getResults(current_values)[2]

        if self.chp!=[]:
            GOutput-=self.chp.getResults(current_values)[2]
            QOutput+=self.chp.getResults(current_values)[1]
            POutput+=self.chp.getResults(current_values)[0]
            COutput+=self.chp.getResults(current_values)[3]

        if self.heatpump!=[]:
            QOutput+=self.heatpump.getResults(current_values)[1]
            POutput-=self.heatpump.getResults(current_values)[0]

        if self.pv!=[]:
            POutput+=self.pv.getPower(currentValues=current_values)[0:timesteps]


        # Save output electrical power
        results = handleData.saveResult(self.environment.timer,
                                        self.currentPOutput,
                                        self.totalPOutput,
                                        POutput)
        (self.currentPOutput, self.totalPOutput) = results


        # Save output gas power
        results = handleData.saveResult(self.environment.timer,
                                        self.currentGOutput,
                                        self.totalGOutput,
                                        GOutput)
        (self.currentGOutput, self.totalGOutput) = results


        # Save output thermal power
        results = handleData.saveResult(self.environment.timer,
                                        self.currentQOutput,
                                        self.totalQOutput,
                                        QOutput)
        (self.currentQOutput, self.totalQOutput) = results


        # Save emission
        results = handleData.saveResult(self.environment.timer,
                                        self.currentCOutput,
                                        self.totalCOutput,
                                        COutput)
        (self.currentCOutput, self.totalCOutput) = results