"""
@author: ist-egu
"""

import numpy as np

from pycity_base.classes.Environment import Environment
from pycity_base.classes.Prices import Prices
from pycity_base.classes.Timer import Timer
from pycity_base.classes.Weather import Weather
from updatedClassses.Transport.Cable import Cable

print("TEST")
print()

print("Environment Definition")
timer=Timer()
weather = Weather(timer, useTRY=True)
prices = Prices()
env = Environment(timer, weather, prices)
print(env)
print()

print("Cable Initiation")
myCable=Cable(env,500)
print(myCable)
print()

currentRandom = np.random.rand(timer.timestepsUsedHorizon)*500
print("Randomly created current set")
print(currentRandom)
myCable.setResults(currentRandom)

result1,result2=myCable.getResults()

print()
print("Cable resistance")
print(myCable.R)
print()
print("current flowing through")
print(result1)
print("voltage drop across")
print(result2)
print()