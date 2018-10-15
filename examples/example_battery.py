"""
@author: ist-egu
"""

from __future__ import division
import numpy as np

import updatedClassses.Supply.Battery as Battery
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

    # Create Battery
    capacity = 4 * 3600 * 1000 # 4 kWh = 4 * 3600*1000 J
    socInit = 0.5 
    selfDischarge = 0.00
    etaCharge = 1.00
    etaDischarge = 1.00
    battery = Battery.Battery(environment, socInit, capacity,
                              selfDischarge, etaCharge, etaDischarge)

    # Print results
    print()
    print(("Initial state of charge: "   + str(battery.socInit)))
    print(("Rate of self discharge: "    + str(battery.selfDischarge)))
    print(("Efficiency at discharging: " + str(battery.etaDischarge)))
    print(("Efficiency at charging: "    + str(battery.etaCharge)))
    print(("Battery's total capacity: "  + str(battery.capacity)))

    print()
    print(("Nominals: " + str(battery.getNominalValues())))

    np.random.seed(0)
    batterySchedule = np.random.random_integers(-3000,3001,timer.timestepsUsedHorizon)
    battery.setResults(batterySchedule)

    results = battery.getResults(True)
    print()
    print(("Given schedule: "+str(batterySchedule)))
    print()
    print(("SOC: " + str(results[0])))
    print()
    print(("SOC in kWh: " + str(results[0]*capacity/(3600 * 1000))))
    print()
    print(("Charging power: " + str(results[1])))
    print()
    print(("Disharging power: " + str(results[2])))


if __name__ == '__main__':
    #  Run program
    run_test()