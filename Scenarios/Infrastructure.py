"""file modified by ferran after coments where it is mentioned. lines starting at 35, 82, 105, 294"""

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
import updatedClassses.Aggregator as Aggregator
import updatedClassses.Building as Building
import updatedClassses.CityDistrict as CityDistrict
import updatedClassses.NaturalSource.GasSource as GasSource
import updatedClassses.NaturalSource.WaterSource as WaterSource
import updatedClassses.Supply.BES as BES
import updatedClassses.Supply.Battery as Battery
import updatedClassses.Supply.Boiler as Boiler
import updatedClassses.Supply.CHP as CHP
import updatedClassses.Supply.HeatPump as HP
import updatedClassses.Supply.HydroelectricPumpStorage as HydroElectric
import updatedClassses.Supply.PV as PV
import updatedClassses.Supply.PowerToGasConverter as P2G
import updatedClassses.Supply.PowerToGasStorage as P2GStorage
import updatedClassses.Supply.WindEnergyConverter as WT
import updatedClassses.demand.Apartment as Apartment
"""line modified"""
import updatedClassses.fceco2capseqferran as co2capseq
import updatedClassses.fcevehicleferran as vehicle
import updatedClassses.fceservicesferran as services
import updatedClassses.fcestreetlightingferran as streetlighting
"""line modified till here"""


#  Generate timer, weather and price objects
timer = pycity_base.classes.Timer.Timer()
weather = pycity_base.classes.Weather.Weather(timer)
prices = pycity_base.classes.Prices.Prices()

#  Generate environment
environment = pycity_base.classes.Environment.Environment(timer, weather, prices)

#Network Specification
networksDictionary={}
networksDictionary['Electricity']={'busVoltage':1000,'diameter':0.2,'spConductance':1.68*10**-8}
networksDictionary['Gas']={'diameter':0.5,'gasDensity':0.8,'darcyFactor':0.03}
networksDictionary['Heat']={'diameter':0.5,'spConductance':0.591}
networksDictionary['Water']={'diameter':0.5,'waterDensity':1000,'darcyFactor':0.03}

#Generate city district object
cityDistrict = CityDistrict.CityDistrict(environment,networksDictionary)

#  Generate shapely point positions
location = {}
location[1] = point.Point(-5000, -100)  #Gas Source
location[2] = point.Point(0, 0)         #District Heating CHP
location[3] = point.Point(100, 20)      #Building3
location[4] = point.Point(120, 20)      #Building4
location[5] = point.Point(160, 20)      #Building5
location[6] = point.Point(200, 20)      #Building6
location[7] = point.Point(160, -20)     #Building7
location[8] = point.Point(200, -20)     #Building8
location[9] = point.Point(1500, 50)     #Building9
location[10]= point.Point(1600, 50)     #Building10
location[11]= point.Point(1700, 50)     #Building11
location[12]= point.Point(1800,50)      #Building12
location[13]= point.Point(2000,180)     #Wind Turbine
location[14]= point.Point(2000,100)     #Power-to-Gas Converter
location[15]= point.Point(2000,95)      #Power-to-Gas Storage
location[16]= point.Point(1500,-50)     #Photovoltaic Farm
location[17]= point.Point(1500,-30)     #Hydroelectric Pump Storage
location[18]= point.Point(2000,-30)     #Water Source

"""line modified"""
location[19]= point.Point(-5000, -50)   #co2capseq
"""line modified till here"""

print("Points on the city district object:")
for no in range(1,19):
    print("Position number",no,"at location",str(location[no].x)+','+str(location[no].y))
print()

#District gas source at location[1]
districtGasSource=GasSource.GasSource(environment,labels=[1001,'Municipal'])
nodeGS=cityDistrict.addEntity(entity=districtGasSource, position=location[1])

#CHP for district heating region at location[2]
lower_activation_limit_DH = 0.2
q_nominal_DH = 400000
t_max_DH = 90
p_nominal_DH = 240000
omega_DH = 0.9
dh_CHP = CHP.CHP(environment, p_nominal_DH, q_nominal_DH, omega_DH,t_max_DH,
                 lower_activation_limit_DH,labels=[1002,'DH'])
nodeCHP=cityDistrict.addEntity(entity=dh_CHP,position=location[2])

""" lines modified"""

#bus generation
# bus energy demand per time steap and fuel tank level
fuelusagexTs=5000
busgascap = 187500
bus1=vehicle.vehicle(environment, 1,'ngb', 'none',busgascap, fuelusagexTs,1,'excelcurves', [998,'bus1'])

#ev generation
nocars=100
EVbattcap=40000
EVenergyconsumption=3500
EVSOCchargingperTS=0.125
EVcomm=vehicle.vehicle(environment, nocars,'ev', 'commute',EVbattcap,
                       EVenergyconsumption, EVSOCchargingperTS,'excelcurves',  [997,'EV'])

#natural gas car generation
nocarsng=30
ngcap=150000
ngcenergyconsumption=4000
ngcpleass=vehicle.vehicle(environment, nocarsng,'ngc', 'plesure',ngcap,
                       ngcenergyconsumption, 1,'excelcurves',  [997,'EV'])

#services generation
bakery=services.services(environment, 1, 'ba', 'excelcurves', [996,'ba'])
business=services.services(environment,1, 'bu', 'excelcurves', [995,'bu'])
shop=services.services(environment, 1, 'sh', 'excelcurves', [994,'sh'])

#co2capseq
co2capseq=co2capseq.co2capseq(environment, maxinput=10000000,maxelimination=0.8,rate=3 )

""" lines modified till here"""


#Buildings
#Standard demand profiles
#  Generate heat demand curve for space heating
heat_demand = SpaceHeating.SpaceHeating(environment,
                                        method=1,  # Standard load profile
                                        livingArea=146,
                                        specificDemand=166)

#  Generate electrical demand curve
el_demand = ElectricalDemand.ElectricalDemand(environment,
                                              method=1,  # Standard load profile
                                              annualDemand=3000)

#  Generate domestic hot water demand curve
dhw_annex42 = DomesticHotWater.DomesticHotWater(environment,
                                                tFlow=60,
                                                thermal=True,
                                                method=1,  # Annex 42
                                                dailyConsumption=70,
                                                supplyTemperature=25)

#  Generate apartment and add demand durves
apartment = Apartment.Apartment(environment)
apartment.addEntity(heat_demand)
apartment.addMultipleEntities([el_demand, dhw_annex42])


# Boilers for buildings
lower_activation_limit = 0.5
q_nominal = 300000
t_max = 90
eta = 0.9
heater_boiler3 = Boiler.Boiler(environment, q_nominal, eta, t_max,lower_activation_limit)
heater_boiler4 = Boiler.Boiler(environment, q_nominal, eta, t_max,lower_activation_limit)
heater_boiler5 = Boiler.Boiler(environment, q_nominal, eta, t_max,lower_activation_limit)
heater_boiler6 = Boiler.Boiler(environment, q_nominal, eta, t_max,lower_activation_limit)
heater_boiler7 = Boiler.Boiler(environment, q_nominal, eta, t_max,lower_activation_limit)
heater_boiler8 = Boiler.Boiler(environment, q_nominal, eta, t_max,lower_activation_limit)
heater_boiler9 = Boiler.Boiler(environment, q_nominal, eta, t_max,lower_activation_limit)
heater_boiler10 = Boiler.Boiler(environment, q_nominal, eta, t_max,lower_activation_limit)
heater_boiler11 = Boiler.Boiler(environment, q_nominal, eta, t_max,lower_activation_limit)
heater_boiler12 = Boiler.Boiler(environment, q_nominal, eta, t_max,lower_activation_limit)

#Batteries for the eastern region buildings
batterCap=100 * 3600 * 1000

battery9 = Battery.Battery(environment, 0.5, batterCap,labels=[1009])
battery10 = Battery.Battery(environment, 0.5, batterCap,labels=[1010])
battery11 = Battery.Battery(environment, 0.5, batterCap,labels=[1011])
battery12 = Battery.Battery(environment, 0.5, batterCap,labels=[1012])


#Heat pumps for eastern region buildings
#  Heatpump data path
src_path = os.path.dirname(os.path.dirname(__file__))
hp_data_path = os.path.join(src_path, 'inputs', 'heat_pumps.xlsx')
heatpumpData = xlrd.open_workbook(hp_data_path)
dimplex_LA12TU = heatpumpData.sheet_by_name("Dimplex_LA12TU")

# Size of the worksheet
number_rows = dimplex_LA12TU._dimnrows
number_columns = dimplex_LA12TU._dimncols

# Flow, ambient and max. temperatures
tFlow = np.zeros(number_columns - 2)
tAmbient = np.zeros(int((number_rows - 7) / 2))
tMax = dimplex_LA12TU.cell_value(0, 1)

firstRowCOP = number_rows - len(tAmbient)

qNominal = np.empty((len(tAmbient), len(tFlow)))
cop = np.empty((len(tAmbient), len(tFlow)))

for i in range(number_columns - 2):
    tFlow[i] = dimplex_LA12TU.cell_value(3, 2 + i)

for col in range(len(tFlow)):
    for row in range(len(tAmbient)):
        qNominal[row, col] = dimplex_LA12TU.cell_value(int(4 + row),
                                                       int(2 + col))
        cop[row, col] = dimplex_LA12TU.cell_value(int(firstRowCOP + row),
                                                  int(2 + col))

pNominal = qNominal / cop
lower_activation_limit_hp = 0.0

heater_hp9 = HP.Heatpump(environment, tAmbient, tFlow, qNominal, pNominal, cop,tMax, lower_activation_limit_hp)
heater_hp10 = HP.Heatpump(environment, tAmbient, tFlow, qNominal, pNominal, cop,tMax, lower_activation_limit_hp)
heater_hp11 = HP.Heatpump(environment, tAmbient, tFlow, qNominal, pNominal, cop,tMax, lower_activation_limit_hp)
heater_hp12 = HP.Heatpump(environment, tAmbient, tFlow, qNominal, pNominal, cop,tMax, lower_activation_limit_hp)

#Generate bes
bes3 = BES.BES(environment)
bes4 = BES.BES(environment)
bes5 = BES.BES(environment)
bes6 = BES.BES(environment)
bes7 = BES.BES(environment)
bes8 = BES.BES(environment)
bes9 = BES.BES(environment)
bes10 = BES.BES(environment)
bes11 = BES.BES(environment)
bes12 = BES.BES(environment)

#Add BES devices to the BES
bes3.addDevice(heater_boiler3)
bes4.addDevice(heater_boiler4)
bes5.addDevice(heater_boiler5)
bes6.addDevice(heater_boiler6)
bes7.addDevice(heater_boiler7)
bes8.addDevice(heater_boiler8)
bes9.addMultipleDevices([heater_boiler9,heater_hp9,battery9])
bes10.addMultipleDevices([heater_boiler10,heater_hp10,battery10])
bes11.addMultipleDevices([heater_boiler11,heater_hp11,battery11])
bes12.addMultipleDevices([heater_boiler12,heater_hp12,battery12])

#  Generate heating curve
heatingCurve = HeatingCurve.HeatingCurve(environment)



appartmentDict={}
appartmentDict['west']=[]
appartmentDict['east']=[]
for a in range(12):
    if a<8:
        appartmentDict['west'].append(apartment)
        appartmentDict['east'].append(apartment)
    else:
        appartmentDict['west'].append(apartment)


#  Generate building and add apartment and heating curve
building3 = Building.Building(environment,True,[1003,'DH'])
building4 = Building.Building(environment,True,[1004,'DH'])
building5 = Building.Building(environment,True,[1005,'DH'])
building6 = Building.Building(environment,True,[1006,'DH'])
building7 = Building.Building(environment,True,[1007,'DH'])
building8 = Building.Building(environment,True,[1008,'DH'])
building9 = Building.Building(environment,False,[1009,'DistrictE'])
building10 = Building.Building(environment,False,[1010,'DistrictE'])
building11 = Building.Building(environment,False,[1011,'DistrictE'])
building12 = Building.Building(environment,False,[1012,'DistrictE'])


buildingList=[building3,building4,building5,building6,building7,building8,building9,building10,building11,building12]
apartmentList=[appartmentDict['west'],appartmentDict['west'],appartmentDict['west'],appartmentDict['west'],appartmentDict['west'],appartmentDict['west'],appartmentDict['east'],appartmentDict['east'],appartmentDict['east'],appartmentDict['east']]
besList=[bes3,bes4,bes5,bes6,bes7,bes8,bes9,bes10,bes11,bes12]

for building in buildingList:
    index=buildingList.index(building)
    building.addMultipleEntities(apartmentList[index])
    building.addEntity(besList[index])
    building.addEntity(heatingCurve)


"""lines modifies"""
#  street lighting
energyxTS=2700
light=streetlighting.streetlighting(environment,len(buildingList) ,'auto', energyxTS , [979,'light'])
"""lines modifies till here"""


#  Residential buildings at location[3]-location[12]
nodeB3=cityDistrict.addEntity(entity=building3, position=location[3])
nodeB4=cityDistrict.addEntity(entity=building4, position=location[4])
nodeB5=cityDistrict.addEntity(entity=building5, position=location[5])
nodeB6=cityDistrict.addEntity(entity=building6, position=location[6])
nodeB7=cityDistrict.addEntity(entity=building7, position=location[7])
nodeB8=cityDistrict.addEntity(entity=building8, position=location[8])
nodeB9=cityDistrict.addEntity(entity=building9, position=location[9])
nodeB10=cityDistrict.addEntity(entity=building10, position=location[10])
nodeB11=cityDistrict.addEntity(entity=building11, position=location[11])
nodeB12=cityDistrict.addEntity(entity=building12, position=location[12])

#WindEnergyConverter with the type ENERCON E-48 at location[13]
src_path = os.path.dirname(os.path.dirname(__file__))
wind_data_path = os.path.join(src_path, 'inputs', 'wind_energy_converters.xlsx')
wecDatasheets = xlrd.open_workbook(wind_data_path)
ENERCON_E_48 = wecDatasheets.sheet_by_name("ENERCON_E_48")
hubHeight = ENERCON_E_48.cell_value(0,1)
mapWind = []
mapPower = []
counter = 0
while ENERCON_E_48._dimnrows > 3+counter:
    mapWind.append(ENERCON_E_48.cell_value(3+counter,0))
    mapPower.append(ENERCON_E_48.cell_value(3+counter,1))
    counter += 1

mapWind = np.array(mapWind)
mapPower = np.array(mapPower) * 1000

wec = WT.WindEnergyConverter(environment, mapWind,
                             mapPower, hubHeight,labels=[1013,'Renewable'])
nodeWT=cityDistrict.addEntity(entity=wec, position=location[13])



#A power to gas conversion with a storage unit location[14] and location[15]
maxInput=50000    #100 kW
efficiency = 0.7
ff=0.2
capacity=200*1000*3600   #200kWh

p2g = P2G.P2G(environment,maxInput, efficiency,labels=[1014,'Renewable'])
storage=P2GStorage.P2GStorage(environment,ff,capacity,labels=[1015,'Renewable'])

nodeP2G=cityDistrict.addEntity(entity=p2g, position=location[14])
nodeP2Gstor=cityDistrict.addEntity(entity=storage, position=location[15])


#PV farm at location[16]
pv = PV.PV(environment, 10000, 0.15,labels=[1016,'Renewable'])
nodePV=cityDistrict.addEntity(entity=pv, position=location[16])

#Hydroelectric pump storage at location[17]
capacity=200 * 3600 * 1000
ffInit = 0.2
etaCharge = 1.00
etaDischarge = 1.00
height=20
pump = HydroElectric.HydroElectric(environment,ffInit, capacity,height,etaCharge, etaDischarge,labels=[1017,'Renewable'])
nodeHE=cityDistrict.addEntity(entity=pump, position=location[17])

#District water source at location[18]
districtWaterSource=WaterSource.WaterSource(environment,labels=[1018,'Municipal'])
nodeWS=cityDistrict.addEntity(entity=districtWaterSource, position=location[18])

agg_municipal=Aggregator.Aggregator(environment,cityDistrict,'agg1')
agg_DH=Aggregator.Aggregator(environment,cityDistrict,'agg2')
agg_E=Aggregator.Aggregator(environment,cityDistrict,'agg3')
agg_RES=Aggregator.Aggregator(environment,cityDistrict,'agg4')

agg_municipal.addEntity('Municipal')
agg_DH.addEntity('DH')
agg_E.addEntity('DistrictE')
agg_RES.addEntity('Renewable')


wf_curve=cityDistrict.getWindEnergyConverterPower()
pv_curve=cityDistrict.getPVPower()
res_curve=pv_curve+wf_curve
total_heat_curve=cityDistrict.get_aggr_space_h_power_curve()
total_ele_load=cityDistrict.get_aggr_el_power_curve()
total_hot_water_curve=cityDistrict.get_aggr_dhw_power_curve()
total_water_curve=cityDistrict.get_aggr_water_demand_power_curve()


if __name__ == '__main__':
    print("Node and object information of the city objects")
    print("-------------------------------------------------------------------")
    print('Number of building entities:',cityDistrict.get_nb_of_building_entities())
    print('Node id list of building entities:',cityDistrict.get_list_build_entity_node_ids())
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
    print(pv_curve)
    print()
    print('Wind turbine power:')
    print(wf_curve)
    print()
    print('Aggregation of demand at consumer ends')
    print('Return aggregated space heating power curve:')
    #print(total_heat_curve())
    print()
    print('Return aggregated electrical power curve:')
    print(total_ele_load)
    print()
    print('Return hot water power curve:')
    print(total_hot_water_curve)
    print()
    print('Return aggregated water demand curve:')
    print(total_water_curve)
    print()


    print("Apartment demand curves")
    eleLoad=apartment.get_el_power_curve()
    heatLoad=apartment.get_space_heat_power_curve()
    waterLoad=apartment.get_water_demand_curve()

    timesteps = range(96)

    #BES3
    b3_ele_dmnd=building3.get_power_curves()[0]
    b3_th_dmnd=building3.get_power_curves()[1]
    b3_wat_dmnd=building3.get_waterDemand_profile()


    fig3=plt.figure(3)
    fig3.subplots_adjust(hspace=0.15,wspace=0.29)

    ele_b3_dmnd=plt.subplot(3, 3, 1,xlim=(0, 96))
    th_b3_dmnd =plt.subplot(3, 3, 2,xlim=(0, 96))
    wat_b3_dmnd=plt.subplot(3, 3, 3,xlim=(0, 96))
    ele_b3_dmnd.set_title('Electricity')
    th_b3_dmnd.set_title('Heat')
    wat_b3_dmnd.set_title('Water')

    for sp in [ele_b3_dmnd,th_b3_dmnd,wat_b3_dmnd]:
        sp.grid('on')
        sp.set_xlim(0,16)
        sp.set_xticks(range(0,100,16))
        sp.set_xlabel('Time Step')

    ele_b3_dmnd.plot(timesteps, b3_ele_dmnd[0:96]/1000, 'g-',label='Electrical Demand')
    th_b3_dmnd.plot(timesteps, b3_th_dmnd[0:96]/1000, 'r-',label='Thermal Demand')
    wat_b3_dmnd.plot(timesteps, b3_wat_dmnd[0:96]*1000, 'b-',label='Water Demand')

    fig3.show()

    #BES10
    b10_ele_dmnd=building10.get_power_curves()[0]
    b10_th_dmnd=building10.get_power_curves()[1]
    b10_wat_dmnd=building10.get_waterDemand_profile()


    fig10=plt.figure(10)
    fig10.subplots_adjust(hspace=0.15,wspace=0.29)

    ele_b10_dmnd=plt.subplot(3, 3, 1,xlim=(0, 96))
    th_b10_dmnd =plt.subplot(3, 3, 2,xlim=(0, 96))
    wat_b10_dmnd=plt.subplot(3, 3, 3,xlim=(0, 96))
    ele_b10_dmnd.set_title('Electricity')
    th_b10_dmnd.set_title('Heat')
    wat_b10_dmnd.set_title('Water')

    for sp in [ele_b10_dmnd,th_b10_dmnd,wat_b10_dmnd]:
        sp.grid('on')
        sp.set_xlim(0,96)
        sp.set_xticks(range(0,100,16))
        sp.set_xlabel('Time Step')

    ele_b10_dmnd.plot(timesteps, b10_ele_dmnd[0:96]/1000, 'g-',label='Electrical Demand')
    th_b10_dmnd.plot(timesteps, b10_th_dmnd[0:96]/1000, 'r-',label='Thermal Demand')
    wat_b10_dmnd.plot(timesteps, b10_wat_dmnd[0:96]*1000, 'b-',label='Water Demand')

    fig10.show()
    plt.show()
