"""
@author: ist-egu
"""

import numpy as np

from pycity_base.classes.Environment import Environment
from pycity_base.classes.Prices import Prices
from pycity_base.classes.Timer import Timer
from pycity_base.classes.Weather import Weather
from updatedClassses.Transport.WaterPipe import WaterPipe

print("TEST")
print()

print("Environment Definition")
timer=Timer()
weather = Weather(timer, useTRY=True)
prices = Prices()
env = Environment(timer, weather, prices)
print(env)
print()

print("WaterPipe Initiation")
myPipe=WaterPipe(env,500,1)
print(myPipe)
print()

vrateRandom = np.random.rand(timer.timestepsUsedHorizon)*6
print("Randomly created volumeflowrate set")
print(vrateRandom)
myPipe.setResults(vrateRandom)

result1,result2=myPipe.getResults()

print()
print("volume flow rate through")
print(result1)
print("pressure drop across")
print(result2)
print()