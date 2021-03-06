#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri May 22 14:39:29 2015

@author: tsz
"""

from __future__ import division

import os

import numpy as np
import xlrd

import pycity_base.classes.Building as Building
import pycity_base.classes.Environment
import pycity_base.classes.HeatingCurve as HeatingCurve
import pycity_base.classes.Prices
import pycity_base.classes.Timer
import pycity_base.classes.Weather
import pycity_base.classes.demand.Apartment as Apartment
import pycity_base.classes.demand.DomesticHotWater as DomesticHotWater
import pycity_base.classes.demand.ElectricalDemand as ElectricalDemand
import pycity_base.classes.demand.SpaceHeating as SpaceHeating
import pycity_base.classes.supply.BES as BES
import pycity_base.classes.supply.HeatPump as HeatPump


def run_test():
    timer = pycity_base.classes.Timer.Timer()
    weather = pycity_base.classes.Weather.Weather(timer)
    prices = pycity_base.classes.Prices.Prices()

    environment = pycity_base.classes.Environment.Environment(timer, weather, prices)

    heat_demand = SpaceHeating.SpaceHeating(environment,
                                            method=1,  # Standard load profile
                                            livingArea=146,
                                            specificDemand=166)

    el_demand = ElectricalDemand.ElectricalDemand(environment,
                                                  method=1,  # Standard load profile
                                                  annualDemand=3000)

    dhw_annex42 = DomesticHotWater.DomesticHotWater(environment,
                                                    tFlow=60,
                                                    thermal=True,
                                                    method=1,  # Annex 42
                                                    dailyConsumption=70,
                                                    supplyTemperature=25)

    apartment = Apartment.Apartment(environment)
    apartment.addEntity(heat_demand)
    apartment.addMultipleEntities([el_demand, dhw_annex42])

    #  Heatpump data path
    src_path = os.path.dirname(os.path.dirname(__file__))
    hp_data_path = os.path.join(src_path, 'inputs', 'heat_pumps.xlsx')
    heatpumpData = xlrd.open_workbook(hp_data_path)
    dimplex_LA12TU = heatpumpData.sheet_by_name("Dimplex_LA12TU")

    # Size of the worksheet
    number_rows = dimplex_LA12TU._dimnrows
    number_columns = dimplex_LA12TU._dimncols

    # Flow, ambient and max. temperatures
    tFlow = np.zeros(number_columns-2)
    tAmbient = np.zeros(int((number_rows-7)/2))
    tMax = dimplex_LA12TU.cell_value(0,1)

    firstRowCOP = number_rows - len(tAmbient)

    qNominal = np.empty((len(tAmbient), len(tFlow)))
    cop = np.empty((len(tAmbient), len(tFlow)))

    for i in range(number_columns-2):
        tFlow[i] = dimplex_LA12TU.cell_value(3, 2+i)

    for col in range(len(tFlow)):
        for row in range(len(tAmbient)):
            qNominal[row, col] = dimplex_LA12TU.cell_value(int(4+row),
                                                           int(2+col))
            cop[row, col] = dimplex_LA12TU.cell_value(int(firstRowCOP+row),
                                                      int(2+col))

    pNominal = qNominal / cop

    # Create HP
    lower_activation_limit = 0.5

    heatpump = HeatPump.Heatpump(environment, tAmbient, tFlow, qNominal,
                                 pNominal, cop, tMax, lower_activation_limit)

    bes = BES.BES(environment)
    bes.addDevice(heatpump)

    heatingCurve = HeatingCurve.HeatingCurve(environment)

    building = Building.Building(environment)
    entities = [apartment, bes, heatingCurve]
    building.addMultipleEntities(entities)


    print()
    print(building.get_power_curves())

    print()
    print(building.getHeatpumpNominals())

    print()
    print(building.flowTemperature)

    print(building.get_space_heating_power_curve())
    print(len(building.get_space_heating_power_curve()))

    print(building.get_electric_power_curve())
    print(len(building.get_electric_power_curve()))

    print(building.get_dhw_power_curve())
    print(len(building.get_dhw_power_curve()))

if __name__ == '__main__':
    #  Run program
    run_test()