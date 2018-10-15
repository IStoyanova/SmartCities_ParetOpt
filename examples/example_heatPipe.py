"""
@author: ist-egu
"""

import numpy as np

from pycity_base.classes.Environment import Environment
from pycity_base.classes.Prices import Prices
from pycity_base.classes.Timer import Timer
from pycity_base.classes.Weather import Weather
from updatedClassses.Transport.HeatPipe import HeatPipe

print("TEST")
print()

print("Environment Definition")
timer=Timer()
weather = Weather(timer, useTRY=True)
prices = Prices()
env = Environment(timer, weather, prices)
print(env)
print()

print("HeatPipe Initiation")
myPipe=HeatPipe(env,100,0.5)
print(myPipe)
print()

hrateRandom = np.random.rand(timer.timestepsUsedHorizon)*10
print("Randomly created current set")
print(hrateRandom)
myPipe.setResults(hrateRandom)

result1,result2=myPipe.getResults()

print()
print("heat flow rate through")
print(result1)
print("temperature drop across")
print(result2)
print()