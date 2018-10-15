"""
@author: ist-egu
"""

from __future__ import division

import shapely.geometry.point as point
import os
import numpy as np
import xlrd

import pycity_base.classes.Timer
import pycity_base.classes.Weather
import pycity_base.classes.Prices
import pycity_base.classes.Environment

import pycity_base.classes.demand.DomesticHotWater as DomesticHotWater
import pycity_base.classes.demand.ElectricalDemand as ElectricalDemand
import pycity_base.classes.demand.SpaceHeating as SpaceHeating
import pycity_base.classes.HeatingCurve as HeatingCurve

import updatedClassses.demand.Apartment as Apartment
import updatedClassses.Building as Building
import updatedClassses.CityDistrict as CityDistrict
import updatedClassses.Supply.BES as BES
import updatedClassses.Supply.PV as PV
import updatedClassses.Supply.Battery as Battery
import updatedClassses.Supply.CHP as CHP
import updatedClassses.Supply.Boiler as Boiler
import updatedClassses.Supply.WindEnergyConverter as WT
import updatedClassses.Supply.HydroelectricPumpStorage as HydroElectric
import updatedClassses.Supply.PowerToGasConverter as P2G
import updatedClassses.Supply.PowerToGasStorage as P2GStorage
import updatedClassses.NaturalSource.GasSource as GasSource
import updatedClassses.NaturalSource.WaterSource as WaterSource


def run_test():

    #  Generate timer, weather and price objects
    timer = pycity_base.classes.Timer.Timer()
    weather = pycity_base.classes.Weather.Weather(timer)
    prices = pycity_base.classes.Prices.Prices()

    #  Generate environment
    environment = pycity_base.classes.Environment.Environment(timer, weather, prices)


    print("Network Specification")
    print('Attributes of the connection mediums will be defined at initialization:')
    networksDictionary = {}
    networksDictionary['Electricity'] = {'busVoltage': 1000, 'diameter': 0.2, 'spConductance': 1.68 * 10 ** -8}
    networksDictionary['Gas'] = {'diameter': 0.5, 'gasDensity': 0.8, 'darcyFactor': 0.03}
    networksDictionary['Heat'] = {'diameter': 0.5, 'spConductance': 0.591}
    networksDictionary['Water'] = {'diameter': 0.5, 'waterDensity': 1000, 'darcyFactor': 0.03}
    print()
    print("For example: networksDictionary['ElectricCable']=[0.2,1.68*10**-8]")
    print('Diameters of electric cables in the district: ',networksDictionary['Electricity']['diameter'],'m')
    print('Specific conductance of electric cables in the district',networksDictionary['Electricity']['spConductance'],'ohm.m')
    print()


    print("Generate city district object")
    cityDistrict = CityDistrict.CityDistrict(environment,networksDictionary)
    #  Empty dictionary for positions
    dict_pos = {}

    #  Generate shapely point positions
    dict_pos[0] = point.Point(0, 40)    #WT
    dict_pos[1] = point.Point(0, 35)    #P2G converter
    dict_pos[2] = point.Point(0, 30)    #P2G storage
    dict_pos[3] = point.Point(40, -20)  #PV
    dict_pos[4] = point.Point(45, -20)  #HE
    dict_pos[5] = point.Point(110, 30)  #Building1
    dict_pos[6] = point.Point(180, 60)  #Building2
    dict_pos[7] = point.Point(240, 30)  #Building3
    dict_pos[8] = point.Point(290, -30)  #Building4
    dict_pos[9]= point.Point(300, -300)  #Gas Source
    dict_pos[10]= point.Point(500, -300)  #Gas Source
    dict_pos[11]=point.Point(80,30)     #CHP for district heating
    print()
    print("Points on the city district object:")
    for no in range(len(dict_pos)):
        print("Position number",no,"at location",str(dict_pos[no].x)+','+str(dict_pos[no].y))
    print()


    print("Generate PV farm within city district")
    pv = PV.PV(environment, 200, 0.15)
    print(pv)

    print('Add PV field to the city district position 3')
    nodePV=cityDistrict.addEntity(entity=pv, position=dict_pos[3])
    print()

    print('Generate Hydroelectric pump storage  within city district')
    capacity=4 * 3600 * 1000    #4 kWh
    ffInit = 0.5
    etaCharge = 0.96
    etaDischarge = 0.95
    height=20
    pump = HydroElectric.HydroElectric(environment,ffInit, capacity,height,etaCharge, etaDischarge)
    print(pump)


    print('Add HE to city district position 4')
    nodeHE=cityDistrict.addEntity(entity=pump, position=dict_pos[4])
    print()


    print('Generate WindEnergyConverter city district from the type ENERCON E-126')
    src_path = os.path.dirname(os.path.dirname(__file__))
    wind_data_path = os.path.join(src_path, 'inputs', 'wind_energy_converters.xlsx')
    wecDatasheets = xlrd.open_workbook(wind_data_path)
    ENERCON_E_126 = wecDatasheets.sheet_by_name("ENERCON_E_126")
    hubHeight = ENERCON_E_126.cell_value(0,1)
    mapWind = []
    mapPower = []
    counter = 0
    while ENERCON_E_126._dimnrows > 3+counter:
        mapWind.append(ENERCON_E_126.cell_value(3+counter,0))
        mapPower.append(ENERCON_E_126.cell_value(3+counter,1))
        counter += 1

    mapWind = np.array(mapWind)
    mapPower = np.array(mapPower) * 1000

    wec = WT.WindEnergyConverter(environment, mapWind,
                                 mapPower, hubHeight)
    print(wec)

    print('Add Wind turbine field to city district position 0')
    nodeWT=cityDistrict.addEntity(entity=wec, position=dict_pos[0])
    print()


    print('Create a power to gas conversion with a storage unit')
    maxInput=10000    #10 kW
    efficiency = 0.7

    #Create a storage unit
    ff=0.6
    capacity=20*1000*3600   #20kWh

    p2g = P2G.P2G(environment,maxInput, efficiency)
    storage=P2GStorage.P2GStorage(environment,ff,capacity)
    print(p2g)
    print(storage)

    print('Add power to gas storage converter to city district position 1')
    print('Add power to gas storage storage unit to city district position 2')
    nodeP2G=cityDistrict.addEntity(entity=p2g, position=dict_pos[1])
    nodeP2Gstor=cityDistrict.addEntity(entity=storage, position=dict_pos[2])
    print()

    #Create a CHP
    lower_activation_limit_DH = 0.2
    q_nominal_DH = 100000
    t_max_DH = 90
    p_nominal_DH = 60000
    omega_DH = 0.9
    dh_CHP = CHP.CHP(environment, p_nominal_DH, q_nominal_DH, omega_DH, t_max_DH,
                     lower_activation_limit_DH)

    print('Add CHP unit for district heating')
    nodeCHP=cityDistrict.addEntity(entity=dh_CHP,position=dict_pos[11])
    print()



    # Create CHPs to add to BESs 5 and 6
    lower_activation_limit = 0.5
    q_nominal = 10000
    t_max = 90
    p_nominal = 6000
    omega = 0.9
    heater_chp = CHP.CHP(environment, p_nominal, q_nominal, omega, t_max,
                     lower_activation_limit)


    # Create a Boiler add to BES 7
    lower_activation_limit = 0.5
    q_nominal = 10000
    t_max = 90
    eta = 0.9
    heater_boiler = Boiler.Boiler(environment, q_nominal, eta, t_max,
                           lower_activation_limit)

    #Create a PV and Battery for BES 8
    pv_Roof = PV.PV(environment, 40, 0.15)
    battery = Battery.Battery(environment, 0.5, 4 * 3600 * 1000)


    print('Generate building objects within loop')
    #  #-------------------------------------------------------------------
    buildingnodes=[]
    buildings=[]
    for i in range(5,9):

        #  Generate heat demand curve for space heating
        heat_demand = SpaceHeating.SpaceHeating(environment,
                                                method=1,  # Standard load profile
                                                livingArea=1460,
                                                specificDemand=166)

        #  Generate electrical demand curve
        el_demand = ElectricalDemand.ElectricalDemand(environment,
                                                      method=1,  # Standard load profile
                                                      annualDemand=30000)

        #  Generate domestic hot water demand curve
        dhw_annex42 = DomesticHotWater.DomesticHotWater(environment,
                                                        tFlow=60,
                                                        thermal=True,
                                                        method=1,  # Annex 42
                                                        dailyConsumption=700,
                                                        supplyTemperature=25)

        #  Generate apartment and add demand durves
        apartment = Apartment.Apartment(environment)
        apartment.addEntity(heat_demand)
        apartment.addMultipleEntities([el_demand, dhw_annex42])

        bes = BES.BES(environment)

        if i in [5,6]:
            bes.addDevice(heater_chp)

        elif i==7:
            bes.addDevice(heater_boiler)

        elif i==8:
            bes.addDevice(pv_Roof)
            bes.addDevice(battery)

        #  Generate heating curve
        heatingCurve = HeatingCurve.HeatingCurve(environment)

        #  Generate building and add apartment and heating curve
        building = Building.Building(environment,True)
        entities = [apartment, heatingCurve,bes]
        building.addMultipleEntities(entities)

        #  Add buildings to city district
        buildingnodes.append(cityDistrict.addEntity(entity=building, position=dict_pos[i]))
        buildings.append(building)

    print('Add them to the city district positons 5-8')
    nodeB5=buildingnodes[0]
    nodeB6=buildingnodes[1]
    nodeB7=buildingnodes[2]
    nodeB8=buildingnodes[3]
    print()


    print('Create a gas source object')
    districtGasSource=GasSource.GasSource(environment)
    print(districtGasSource)
    print('Add it to the city district position 9')
    nodeGS=cityDistrict.addEntity(entity=districtGasSource, position=dict_pos[9])
    print()


    print('Create a water source object')
    districtWaterSource=WaterSource.WaterSource(environment)
    print('Add it to the city district position 10')
    nodeWS=cityDistrict.addEntity(entity=districtWaterSource, position=dict_pos[10])
    print()


    print("Node and object information of the city objects")
    print("-------------------------------------------------------------------")
    print('Number of building entities:',cityDistrict.get_nb_of_building_entities())
    print('Node id list of building entities:',cityDistrict.get_list_build_entity_node_ids())
    print()

    print('Number of PV farms:',cityDistrict.get_nb_of_entities(entity_name='pv'))
    print('Number of Wind farms:',cityDistrict.get_nb_of_entities(entity_name='windenergyconverter'))
    print('Number of Hydroelectric pump storage units:',cityDistrict.get_nb_of_entities(entity_name='heps'))
    print('Number of P2G converters:',cityDistrict.get_nb_of_entities(entity_name='p2gConverter'))
    print()

    print('Node information:')
    print('All nodes',cityDistrict.nodes())
    print('Nodelists_heating:', cityDistrict.nodelists_heating)
    print('Nodelists_electricty:',cityDistrict.nodelists_electricity)
    print('Nodelists_gas:',cityDistrict.nodelists_gas)
    print('Nodelists_water:',cityDistrict.nodelists_water)
    print()

    print('Power supply from uncontrollable (renewable) generators')

    print('PV power:')
    print(cityDistrict.getPVPower())
    print()

    print('Wind turbine power:')
    print(cityDistrict.getWindEnergyConverterPower())
    print()
    print('Please type enter')
    #input()

    print('Aggregation of demand at consumer ends')

    print('Return aggregated space heating power curve:')
    print(cityDistrict.get_aggr_space_h_power_curve())
    print()

    print('Return aggregated electrical power curve:')
    print(cityDistrict.get_aggr_el_power_curve())
    print()


    print('Return hot water power curve:')
    print(cityDistrict.get_aggr_dhw_power_curve())
    print()

    print('Return aggregated water demand curve:')
    print(cityDistrict.get_aggr_water_demand_power_curve())
    print()

    print('Please type enter')
    #input()

    print('Assigning schedules to controllable objects')
    print()

    np.random.seed(0)

    print('Power to gas conversion: how much electric power will be supplied')
    conversionSchedule = -np.random.randint(90001, size=192)
    print(conversionSchedule)
    print()
    print('Power to gas storage: how much gas power will be supplied')
    storageSchedule=conversionSchedule*0.6
    print(storageSchedule)
    print()
    print('Hydroelectric pump storage: how much electric power will be supplied')
    pumpSchedule = np.random.random_integers(-3000,101,192)
    print(pumpSchedule)
    print()
    print('District heating CHP: how much electric power will be supplied')
    chpDH_Schedule = np.array([0.5]*192)
    print(chpDH_Schedule)
    print()
    print('District Gas Source: how much gas power will be supplied')
    gasSupplySchedule = np.random.random_integers(0,100000,192)
    print(gasSupplySchedule)
    print()
    print('District Water Source: how much water will be supplied')
    waterSupplySchedule = np.random.random_integers(0,1000,192)
    print(waterSupplySchedule)
    print()
    print('Same schedule is assigned to CHPs of the buildings')
    chpSchedule=np.array([0.0]*192)
    print(chpSchedule)
    print()
    print('Schedule assigned to gas boilers of the buildings')
    boilerSchedule=np.array([0.6]*192)
    print(boilerSchedule)
    print()
    print('Battery schedule assigned')
    batterySchedule=np.random.random_integers(-3000,3001,timer.timestepsUsedHorizon)
    print(batterySchedule)
    print()


    for building in buildings:
        if buildings.index(building)<2:
            building.bes.chp.setResults(chpSchedule)
        elif buildings.index(building)==2:
            building.bes.boiler.setResults(boilerSchedule)
        elif buildings.index(building)==3:
            building.bes.battery.setResults(batterySchedule)

    dh_CHP.setResults(chpDH_Schedule)
    pump.setResults(pumpSchedule)
    p2g.setResults(conversionSchedule)
    storage.setResults(storageSchedule)
    districtGasSource.setResults(gasSupplySchedule)
    districtWaterSource.setResults(waterSupplySchedule)



if __name__ == '__main__':
    #  Run program
    run_test()
