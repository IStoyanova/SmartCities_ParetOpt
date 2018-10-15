"""
@author: ist-egu
"""

from __future__ import division
import numpy as np

import updatedClassses.Supply.HydroelectricPumpStorage as HydroElectric
import pycity_base.classes.Timer
import pycity_base.classes.Weather
import pycity_base.classes.Prices
import pycity_base.classes.Environment

def run_test():

    # Create environment
    timer = pycity_base.classes.Timer.Timer()
    weather = pycity_base.classes.Weather.Weather(timer)
    prices = pycity_base.classes.Prices.Prices()
    environment = pycity_base.classes.Environment.Environment(timer, weather, prices)

    # Create a hydroelectric pump storage
    capacity=4 * 3600 * 1000    #4 kWh
    ffInit = 0.5
    etaCharge = 1.00
    etaDischarge = 1.00
    height=20
    pump = HydroElectric.HydroElectric(environment,ffInit, capacity,height,etaCharge, etaDischarge)


    # Print results
    print()
    print(("Initial state of charge: "   + str(pump.ffInit)))
    print(("Efficiency at discharging: " + str(pump.etaDischarge)))
    print(("Efficiency at charging: "    + str(pump.etaCharge)))
    print(("Hydroelectric storage's energy capacity: "  + str(pump.energyCapacity)))
    print(("Effective height of the upper reservoir: "  + str(pump.h)))
    print(("Upper reservoir's water capacity: "  + str(pump.waterCapacity)))

    print()
    print(("Nominals: " + str(pump.getNominalValues())))

    np.random.seed(0)
    pumpSchedule = np.random.random_integers(-3000,3001,timer.timestepsUsedHorizon)
    pump.setResults(pumpSchedule)

    results = pump.getResults(True)
    print()
    print(("Given schedule: "+str(pumpSchedule)))
    print()
    print(("FF: " + str(results[0])))
    print()
    print(("FF in Joule: " + str(results[0]*capacity)))
    print()
    print(("FF in kWh: " + str(results[0]*capacity/(3600*1000))))
    print()
    print(("Charging power: " + str(results[1])))
    print()
    print(("Disharging power: " + str(results[2])))
    print()
    print(("Filled water: " + str(results[3])))
    print()
    print(("Removed water: " + str(results[4])))



if __name__ == '__main__':
    #  Run program
    run_test()