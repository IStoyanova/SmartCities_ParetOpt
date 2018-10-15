"""
author: ist-egu
"""

import numpy as np

def calculateIO_device(device,current_values=True):
    """
    Returns the impact of device operation on the available sources of each domain
    pOut: float
        Electricity
    gOut: float
        Gas
    hOut: float
        Heat
    wOut: float
        Water
    cOut: float
        Carbon emission
    """

    if current_values:
        timesteps = device.environment.timer.timestepsUsedHorizon
    else:
        timesteps = device.environment.timer.timestepsTotal


    if device._kind=="battery":
        pOut = device.getResults(current_values)[2] - device.battery.getResults(current_values)[1]
        gOut = np.zeros(timesteps)
        hOut = np.zeros(timesteps)
        wOut = np.zeros(timesteps)
        cOut = np.zeros(timesteps)

    if device._kind=="boiler":
        pOut = np.zeros(timesteps)
        gOut = -device.getResults(current_values)[1]
        hOut = device.getResults(current_values)[0]
        wOut = np.zeros(timesteps)
        cOut = device.getResults(current_values)[2]

    if device._kind=="chp":
        pOut = device.getResults(current_values)[0]
        gOut = -device.getResults(current_values)[2]
        hOut = device.getResults(current_values)[1]
        wOut = np.zeros(timesteps)
        cOut = device.getResults(current_values)[3]

    if device._kind=="heatpump":
        pOut = -device.getResults(current_values)[0]
        gOut = np.zeros(timesteps)
        hOut = device.getResults(current_values)[1]
        wOut = np.zeros(timesteps)
        cOut = np.zeros(timesteps)

    if device._kind=="pv":
        pOut = device.getPower(currentValues=current_values)[0:timesteps]
        gOut = np.zeros(timesteps)
        hOut = np.zeros(timesteps)
        wOut = np.zeros(timesteps)
        cOut = np.zeros(timesteps)

    if device._kind=="windenergyconverter":
        pOut = device.getPower(currentValues=current_values)[0:timesteps]
        gOut = np.zeros(timesteps)
        hOut = np.zeros(timesteps)
        wOut = np.zeros(timesteps)
        cOut = np.zeros(timesteps)

    if device._kind=="heps":
        pOut = device.getPower(currentValues=current_values)[0:timesteps]
        gOut = np.zeros(timesteps)
        hOut = np.zeros(timesteps)
        wOut = device.getResults(currentValues=current_values)[4]-device.getResults(currentValues=current_values)[3]
        cOut = np.zeros(timesteps)

    if device._kind=="gassource":
        pOut = np.zeros(timesteps)
        gOut = device.getResults(currentValues=current_values)
        hOut = np.zeros(timesteps)
        wOut = np.zeros(timesteps)
        cOut = np.zeros(timesteps)

    if device._kind=="watersource":
        pOut = np.zeros(timesteps)
        gOut = np.zeros(timesteps)
        hOut = np.zeros(timesteps)
        wOut = device.getResults(currentValues=current_values)
        cOut = np.zeros(timesteps)

    if device._kind=="p2gConverter":
        pOut = -device.getResults(currentValues=current_values)[0]
        gOut = device.getResults(currentValues=current_values)[1]
        hOut = np.zeros(timesteps)
        wOut = np.zeros(timesteps)
        cOut = np.zeros(timesteps)

    if device._kind=="p2gStorage":
        pOut = np.zeros(timesteps)
        gOut = device.getResults(currentValues=current_values)[2]-device.getResults(currentValues=current_values)[1]
        hOut = np.zeros(timesteps)
        wOut = np.zeros(timesteps)
        cOut = np.zeros(timesteps)

    return pOut,gOut,hOut,wOut,cOut


def calculateIO_bes(bes,current_values=True):
    """
    Returns the impact of bes operation on the available sources of each domain
    pOut: float
        Electricity
    gOut: float
        Gas
    hOut: float
        Heat
    wOut: float
        Water
    cOut: float
        Carbon emission
    """

    if current_values:
        timesteps = bes.environment.timer.timestepsUsedHorizon
    else:
        timesteps = bes.environment.timer.timestepsTotal

    pOut = bes.getPowerCurves(current_values)[0]
    gOut = bes.getPowerCurves(current_values)[1]
    hOut = bes.getPowerCurves(current_values)[2]
    wOut = np.zeros(timesteps)
    cOut = bes.getPowerCurves(current_values)[3]

    return pOut, gOut, hOut, wOut, cOut

def calculateIO_building(building,current_values=True):
    """
    Returns the impact of building operation on the available sources of each domain
    pOut: float
        Electricity
    gOut: float
        Gas
    hOut: float
        Heat
    wOut: float
        Water
    cOut: float
        Carbon emission
    """

    if current_values:
        timesteps = building.environment.timer.timestepsUsedHorizon
    else:
        timesteps = building.environment.timer.timestepsTotal

    powDemand = building.get_power_curves(current_values)[0][0:timesteps]
    thDemand  = building.get_power_curves(current_values)[1][0:timesteps]
    watDemand = building.get_waterDemand_profile(current_values)[0:timesteps]

    powSupply = calculateIO_bes(building.bes)[0]
    gasSupply = calculateIO_bes(building.bes)[1]
    thSupply  = calculateIO_bes(building.bes)[2]
    watSupply = calculateIO_bes(building.bes)[3]
    cSupply   = calculateIO_bes(building.bes)[4]

    pOut = powSupply-powDemand
    gOut = gasSupply
    hOut = thSupply-thDemand
    wOut = watSupply-watDemand
    cOut = cSupply

    return pOut, gOut, hOut, wOut, cOut

def calculateIO_load(load,current_values=True):
    #TODO: Add 
    """
    Returns the impact of demand curves on the available resource of each domain
    pOut: float
        Electricity
    gOut: float
        Gas
    hOut: float
        Heat
    wOut: float
        Water
    cOut: float
        Carbon emission
    """

    if current_values:
        timesteps = load.environment.timer.timestepsUsedHorizon
    else:
        timesteps = load.environment.timer.timestepsTotal


    if load._kind=="electricaldemand":
        pOut = -load.get_power(current_values)[0:timesteps]
        gOut = np.zeros(timesteps)
        hOut = np.zeros(timesteps)
        wOut = np.zeros(timesteps)
        cOut = np.zeros(timesteps)

    if load._kind=="spaceheating":
        pOut = np.zeros(timesteps)
        gOut = np.zeros(timesteps)
        hOut = -load.get_power(current_values)[0:timesteps]
        wOut = np.zeros(timesteps)
        cOut = np.zeros(timesteps)


def calculateIO_agg(aggregator,current_values=True):
    """
    Returns the impact of aggregator operation on the available sources of each domain
    pOut: float
        Electricity
    gOut: float
        Gas
    hOut: float
        Heat
    wOut: float
        Water
    cOut: float
        Carbon emission
    """
    if current_values:
        timesteps = aggregator[0].environment.timer.timestepsUsedHorizon
    else:
        timesteps = aggregator[1].environment.timer.timestepsTotal

    pOut = np.zeros(timesteps)
    gOut = np.zeros(timesteps)
    hOut = np.zeros(timesteps)
    wOut = np.zeros(timesteps)
    cOut = np.zeros(timesteps)

    for obj in aggregator:
        if obj._kind in ["electricaldemand","spaceheating"]:
            pOut += calculateIO_load(obj)[0]
            gOut += calculateIO_load(obj)[1]
            hOut += calculateIO_load(obj)[2]
            wOut += calculateIO_load(obj)[3]
            cOut += calculateIO_load(obj)[4]
        if obj._kind in ["battery","boiler","chp","heatpump","pv","wec","gassource","watersource","p2gConverter","p2gStorage"]:
            pOut += calculateIO_device(obj)[0]
            gOut += calculateIO_device(obj)[1]
            hOut += calculateIO_device(obj)[2]
            wOut += calculateIO_device(obj)[3]
            cOut += calculateIO_device(obj)[4]
        if obj._kind=="bes":
            pOut += calculateIO_bes(obj)[0]
            gOut += calculateIO_bes(obj)[1]
            hOut += calculateIO_bes(obj)[2]
            wOut += calculateIO_bes(obj)[3]
            cOut += calculateIO_bes(obj)[4]
        if obj._kind == "building":
            pOut += calculateIO_building(obj)[0]
            gOut += calculateIO_building(obj)[1]
            hOut += calculateIO_building(obj)[2]
            wOut += calculateIO_building(obj)[3]
            cOut += calculateIO_building(obj)[4]


    return pOut, gOut, hOut, wOut, cOut

