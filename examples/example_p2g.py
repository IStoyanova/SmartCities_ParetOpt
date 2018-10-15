"""
@author: ist-egu
"""

from __future__ import division
import numpy as np

import updatedClassses.Supply.PowerToGasConverter as P2G
import updatedClassses.Supply.PowerToGasStorage as P2GStorage
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

    # Create a power to gas conversion unit
    maxInput=10000    #10 kW
    efficiency = 0.7

    #Create a storage unit
    ff=0.6
    capacity=20*1000*3600   #20kWh

    p2g = P2G.P2G(environment,maxInput, efficiency)
    storage=P2GStorage.P2GStorage(environment,ff,capacity)

    # Print results
    print()
    print(("Nominals of the converter: " + str(p2g.getNominalValues())))
    print(("Nominals of the storage: " + str(storage.getNominalValues())))

    np.random.seed(0)
    conversionSchedule = np.random.randint(3001, size=timer.timestepsUsedHorizon)
    storageSchedule=conversionSchedule*-0.7*0.9      #90% of the generation is stored
    p2g.setResults(conversionSchedule)
    storage.setResults(storageSchedule)

    results_converter = p2g.getResults(True)
    results_storage=storage.getResults(True)
    print()
    print(("Conversion schedule: "+str(conversionSchedule)))
    print()
    print(("Converted electric power: " + str(results_converter[0])))
    print()
    print(("Gas power output: " + str(results_converter[1])))
    print()
    print(("Storage schedule: "+str(storageSchedule)))
    print()
    print(("Fill factor at the gas storage: " + str(results_storage[0])))
    print()
    print(("Filled gas power to the storage: " + str(results_storage[1])))
    print()
    print(("Removed gas power from the storage: " + str(results_storage[2])))


if __name__ == '__main__':
    #  Run program
    run_test()