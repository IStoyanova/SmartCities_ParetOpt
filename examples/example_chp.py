"""
@author: ist-egu
"""

from __future__ import division
import numpy as np

import updatedClassses.Supply.CHP as CHP

import pycity_base.classes.Timer
import pycity_base.classes.Weather
import pycity_base.classes.Prices
import pycity_base.classes.Environment

def run_test():
    # Create environment
    timer = pycity_base.classes.Timer.Timer()
    weather = pycity_base.classes.Weather.Weather(timer, useTRY=True)
    prices = pycity_base.classes.Prices.Prices()
    environment = pycity_base.classes.Environment.Environment(timer, weather, prices)

    # Create CHP
    lower_activation_limit = 0.5
    q_nominal = 10000
    t_max = 90
    p_nominal = 6000
    omega = 0.9
    heater = CHP.CHP(environment, p_nominal, q_nominal, omega, t_max,
                     lower_activation_limit)

    # Print results
    print()
    print(("Type: " + heater._kind))
    print()
    print(("Maximum electricity output: " + str(heater.pNominal)))
    print(("Total efficiency: "           + str(heater.omega)))
    print(("Power to heat ratio: "        + str(heater.sigma)))
    print(("Maximum heat output: "        + str(heater.qNominal)))
    print(("Maximum fuel input: "        + str(heater.fNominal)))
    print(("Maximum flow temperature: "   + str(heater.tMax)))
    print(("Lower activation limit: "     + str(heater.lowerActivationLimit)))

    print()
    print(("Nominals: " + str(heater.getNominalValues())))

    result_schedule = np.random.randint(2, size=timer.timestepsUsedHorizon)
    heater.setResults(result_schedule)

    results = heater.getResults(True)
    print()
    print("Schedule: " + str(results[4]))
    print()
    print("Electricity output: " + str(results[0]))
    print()
    print("Heat output: " + str(results[1]))
    print()
    print("Fuel input: " + str(results[2]))
    print()
    print("Emission: " + str(results[3]))

if __name__ == '__main__':
    #  Run program
    run_test()
