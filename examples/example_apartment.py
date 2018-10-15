"""
@author: ist-egu
"""

from __future__ import division
import pycity_base.classes.Timer
import pycity_base.classes.Weather
import pycity_base.classes.Prices
import pycity_base.classes.Environment

import updatedClassses.demand.Apartment as Apartment
import pycity_base.classes.demand.DomesticHotWater as DomesticHotWater
import pycity_base.classes.demand.ElectricalDemand as ElectricalDemand
import pycity_base.classes.demand.SpaceHeating as SpaceHeating


def run_test():
    #  Generate environment
    timer = pycity_base.classes.Timer.Timer()
    weather = pycity_base.classes.Weather.Weather(timer)
    prices = pycity_base.classes.Prices.Prices()

    environment = pycity_base.classes.Environment.Environment(timer, weather,
                                                         prices)

    #  Generate heat demand object
    heat_demand = SpaceHeating.SpaceHeating(environment,
                                            method=1,  # Standard load profile
                                            livingArea=146,
                                            specificDemand=166)

    #  Generate electrical demand object
    el_demand = ElectricalDemand.ElectricalDemand(environment,
                                                  method=1,
                                                  # Standard load profile
                                                  annualDemand=3000)

    #  Generate hot water demand object (based on Annex 42 profiles)
    dhw_annex42 = DomesticHotWater.DomesticHotWater(environment,
                                                    tFlow=60,
                                                    thermal=True,
                                                    method=1,  # Annex 42
                                                    dailyConsumption=70,
                                                    supplyTemperature=25)

    #  Initialize apartment object
    apartment = Apartment.Apartment(environment)

    #  Add entities to apartment object
    entities = [heat_demand, el_demand, dhw_annex42]
    apartment.addMultipleEntities(entities)

    print('Get all power curves of apartment (for current horizon):')
    print(apartment.get_power_curves())
    print()

    print('Get space heating power curve for whole year:')
    print(apartment.get_space_heat_power_curve(current_values=True))
    print()

    print('Get electrical power curve for whole year:')
    print(sum(apartment.get_el_power_curve(current_values=True)))
    print()

    print('Get hot water power curve for whole year:')
    print(apartment.get_dhw_power_curve(current_values=True))
    print()

    print('Get water demand curve for whole year:')
    print(sum(apartment.get_water_demand_curve(current_values=True))*180*900)
    print()


if __name__ == '__main__':
    #  Run program
    run_test()