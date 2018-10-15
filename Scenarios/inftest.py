
from __future__ import division

import matplotlib.pyplot as plt
import numpy as np
import shapely.geometry.point as point
import xlrd
from gurobipy import *

import pycity_base.classes.Environment
import pycity_base.classes.HeatingCurve as HeatingCurve
import pycity_base.classes.Prices
import pycity_base.classes.Timer
import pycity_base.classes.Weather
import pycity_base.classes.demand.DomesticHotWater as DomesticHotWater
import pycity_base.classes.demand.ElectricalDemand as ElectricalDemand
import pycity_base.classes.demand.SpaceHeating as SpaceHeating

import updatedClassses.vehicle as vehicle
import updatedClassses.streetlighting as streetlighting

#  Generate timer, weather and price objects
timer = pycity_base.classes.Timer.Timer()
weather = pycity_base.classes.Weather.Weather(timer)
prices = pycity_base.classes.Prices.Prices()

a = np.zeros(5)
print(a)

b=[]
for t in range(5):
    b.insert(t, 0)

print(b)

#  Generate environment
environment = pycity_base.classes.Environment.Environment(timer, weather, prices)

energyxTS=1
light=streetlighting.streetlighting(environment ,1 ,energyxTS=energyxTS, labels=None)