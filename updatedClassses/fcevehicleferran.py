#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vehicle object of pycity
"""

"""
upgrade
@author: ist-fce
"""

import numpy as np

import xlrd
import os
import pycity_base.functions.slp_electrical as slp_el


class vehicle(object):
    """
    Implementation of a vehicle that consists of a quantity of types
    types:natural gas car(ngc), natural gas bus(ngb), EV(ev)
    schedule: if the car is used as commuting car or as plesure car)
    """
    
    def __init__(self, environment, number=1, type='ev', schedule='plesure', fuelstorage=0,
                 fuelusagexTs=0,SOCrechargexts=1,method='coded', labels=None):
        """
        Workflow
        --------
        1 : Create a kind of vehicle and quantity of them and return the energy usage per time step

        2 : .
        
        Parameter
        ---------
        environment : Environment object
            Common to all other objects. Includes time and weather instances
        type: kinf of veheicle
        number
        fuel storage: maximim energy in fuel tank or batteries
        fuel usage per time step
        SOC recharge per time step: maximum capacity of energy that can  be given to the vehicle every time step
        method by wich the demand curves are generated

        """
        self._kind = "vehicle"
        self.labels=labels
        
        self.environment = environment
        self.number=number
        self.type=type
        self.schedule=schedule
        self.fuelstorage=fuelstorage
        self.fuelusagexTs=fuelusagexTs
        self.SOCrechargexts=SOCrechargexts
        self.method=method




    def get_total_energy_vehicles(self, current_values=True):
        a=self.number*self.fuelstorage
        return a



    def get_energy_curves(self, current_values=True):
        Ta=96
        initialPosition = self.environment.timer.currentTimestep
        timestepsHorizon = self.environment.timer.timestepsHorizon
        finalPosition = initialPosition + timestepsHorizon

        b= np.zeros(timestepsHorizon)


        if self.method=='excelcurves':
            usage = xlrd.open_workbook('sup_vehicle1.xlsx')
            first_sheet = usage.sheet_by_index(0)

            if self.type == 'ngb':
                ba = first_sheet.col_slice(colx=3,
                                           start_rowx=2+initialPosition,
                                           end_rowx=2+finalPosition)

            if (self.type == 'ev' or self.type == 'ngc') and self.schedule == 'commute':

                ba = first_sheet.col_slice(colx=1,
                                          start_rowx=2,
                                          end_rowx=98)

            if (self.type == 'ev' or self.type == 'ngc') and self.schedule == 'plesure':
                ba = first_sheet.col_slice(colx=2,
                                           start_rowx=2,
                                           end_rowx=98)


            for t in range(Ta):
                b[t] = float("{0:.4f}".format( ba[t].value* (self.fuelusagexTs / self.fuelstorage)))




        if self.method=='coded':
            if self.type == 'ngb':
                for t in range(30, 70):
                    b[t] = (self.fuelusagexTs / self.fuelstorage)

            if (self.type == 'ev' or self.type == 'ngc') and self.schedule == 'commute':
                for t in range(20, 30):
                    b[t] = 0.3 * (self.fuelusagexTs / self.fuelstorage)
                for t in range(30, 36):
                    b[t] = 0.9 * (self.fuelusagexTs / self.fuelstorage)
                for t in range(36, 50):
                    b[t] = 0.5 * (self.fuelusagexTs / self.fuelstorage)
                for t in range(50, 56):
                    b[t] = 1 * (self.fuelusagexTs / self.fuelstorage)
                for t in range(56, 75):
                    b[t] = 0.3 * (self.fuelusagexTs / self.fuelstorage)

            if (self.type == 'ev' or self.type == 'ngc') and self.schedule == 'pleasure':

                for t in range(30, 36):
                    b[t] = 0.3 * (self.fuelusagexTs / self.fuelstorage)
                for t in range(36, 50):
                    b[t] = 0.5 * (self.fuelusagexTs / self.fuelstorage)
                for t in range(50, 56):
                    b[t] = 0.7 * (self.fuelusagexTs / self.fuelstorage)
                for t in range(56, 75):
                    b[t] = 1 * (self.fuelusagexTs / self.fuelstorage)
                for t in range(75, 80):
                    b[t] = 0.5 * (self.fuelusagexTs / self.fuelstorage)

        return b



    def get_charging_curves(self, current_values=True):
        Ta = 96
        c = []
        for t in range(Ta):
            c.insert(t, 1)

        if self.method == 'excelcurves':
            usage = xlrd.open_workbook('sup_vehicle1.xlsx')
            first_sheet = usage.sheet_by_index(0)

            if self.type == 'ngb':
                ca = first_sheet.col_slice(colx=6,
                                           start_rowx=2,
                                           end_rowx=98)


            if (self.type == 'ev' or self.type == 'ngc') and self.schedule == 'commute':

                ca = first_sheet.col_slice(colx=4,
                                          start_rowx=2,
                                          end_rowx=98)

            if (self.type == 'ev' or self.type == 'ngc') and self.schedule == 'plesure':
                ca = first_sheet.col_slice(colx=6,
                                           start_rowx=2,
                                           end_rowx=98)






            for t in range(Ta):
                    c[t] =float("{0:.4f}".format( ca[t].value * (self.SOCrechargexts)))







        if self.method == 'coded':

            if self.type == 'ngb':

                for t in range(31, 70, 2):
                    c[t] = 0

            if (self.type == 'ev' or self.type == 'ngc') and self.schedule == 'commute':
                for t in range(20, 30):
                    c[t] = 0.7 * (self.SOCrechargexts)
                for t in range(30, 36):
                    c[t] = 0.1 * (self.SOCrechargexts)
                for t in range(36, 50):
                    c[t] = 0.5 * (self.SOCrechargexts)
                for t in range(50, 56):
                    c[t] = 0 * (self.SOCrechargexts)
                for t in range(56, 75):
                    c[t] = 0.7 * (self.SOCrechargexts)

            if (self.type == 'ev' or self.type == 'ngc') and self.schedule == 'pleasure':

                for t in range(30, 36):
                    c[t] = 0.7 * (self.SOCrechargexts)
                for t in range(36, 50):
                    c[t] = 0.5 * (self.SOCrechargexts)
                for t in range(50, 56):
                    c[t] = 0.3 * (self.SOCrechargexts)
                for t in range(56, 75):
                    c[t] = 0 * (self.SOCrechargexts)
                for t in range(75, 80):
                    c[t] = 0.5 * (self.SOCrechargexts)

        return c


    def get_ocupancy(self, current_values=True):
        if self.type == 'ngb':
            return 15

        if self.type == 'ev':
            return 2


    def get_vehicle_curves(self, current_values=True):
        return ( self.get_energy_curves(), self.get_charging_curves())


