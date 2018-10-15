from Scenarios.Infrastructure import *

print('Optimization of the multi-domain operation')
print()
model=Model("OptimumOperation")


T=96

#'Power to gas conversion: how much electric power will be supplied'
p2g_nom=p2g.maxPInput
conversionSchedule=model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS, name="Power2GasConverter")

#'Power to gas storage: how much gas power will be supplied'
p2g_sto_nom=storage.maxDischarge
storageSchedule=model.addVars(T,lb=-1.0,ub=1.0,vtype=GRB.CONTINUOUS, name="Power2GasStorage")
storageSOC=model.addVars(T+1,lb=0.1,ub=1.0,vtype=GRB.CONTINUOUS, name="Power2GasStorageSOC")

#'Hydroelectric pump storage: how much electric power will be supplied'
pump_nom=pump.maxDischarge
pumpSchedule=model.addVars(T,lb=-1.0,ub=1.0,vtype=GRB.CONTINUOUS, name="heps")
pumpSOC=model.addVars(T+1,lb=0.05,ub=1.0,vtype=GRB.CONTINUOUS, name="pumpSOC")

#'District heating CHP: how much electric power will be supplied'
chpDH_Schedule=model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS, name="dh_chp")

#'District Gas Source: how much gas power will be supplied'
gs_nom=100000000
gasSupplySchedule =model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS, name="gas_source")

#'District Gas Source: how much water power will be supplied'
ws_nom=100000000
waterSupplySchedule =model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS, name="water_source")

#'Schedule assigned to gas boilers of the buildings'
boil_nom=heater_boiler3.qNominal
boilerSchedule3=model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS, name="boiler3")
boilerSchedule4=model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS, name="boiler4")
boilerSchedule5=model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS, name="boiler5")
boilerSchedule6=model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS, name="boiler6")
boilerSchedule7=model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS, name="boiler7")
boilerSchedule8=model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS, name="boiler8")
boilerSchedule9=model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS, name="boiler9")
boilerSchedule10=model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS, name="boiler10")
boilerSchedule11=model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS, name="boiler11")
boilerSchedule12=model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS, name="boiler12")


#'Schedule assigned to heat pumps of the buildings'
heatFlow=[60]*192 #heat flow temperature 60C
hp_nom=heater_hp9.getNominalValues(heatFlow)
hpSchedule9 =model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS, name="hp9")
hpSchedule10=model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS, name="hp10")
hpSchedule11=model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS, name="hp11")
hpSchedule12=model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS, name="hp12")

#'Battery schedule assigned'
bat_nom=battery9.maxDischarge
batterySchedule9=model.addVars(T,lb=-1.0,ub=1.0,vtype=GRB.CONTINUOUS, name="battery9")
batterySchedule10=model.addVars(T,lb=-1.0,ub=1.0,vtype=GRB.CONTINUOUS, name="battery10")
batterySchedule11=model.addVars(T,lb=-1.0,ub=1.0,vtype=GRB.CONTINUOUS, name="battery11")
batterySchedule12=model.addVars(T,lb=-1.0,ub=1.0,vtype=GRB.CONTINUOUS, name="battery12")

batterySOC9=model.addVars(T+1,lb=0.2,ub=1.0,vtype=GRB.CONTINUOUS, name="batterySOC9")
batterySOC10=model.addVars(T+1,lb=0.2,ub=1.0,vtype=GRB.CONTINUOUS, name="batterySOC10")
batterySOC11=model.addVars(T+1,lb=0.2,ub=1.0,vtype=GRB.CONTINUOUS, name="batterySOC11")
batterySOC12=model.addVars(T+1,lb=0.2,ub=1.0,vtype=GRB.CONTINUOUS, name="batterySOC12")

imported=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS,name='imported')
utilization_pv=model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS,name='utilization_pv')
utilization_wec=model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS,name='utilization_wec')


#'Building electricity import'
b3_ele=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b3_ele")
b4_ele=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b4_ele")
b5_ele=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b5_ele")
b6_ele=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b6_ele")
b7_ele=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b7_ele")
b8_ele=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b8_ele")
b9_ele=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b9_ele")
b10_ele=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b10_ele")
b11_ele=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b11_ele")
b12_ele=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b12_ele")

#'Building gas import'
b3_gas=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b3_gas")
b4_gas=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b4_gas")
b5_gas=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b5_gas")
b6_gas=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b6_gas")
b7_gas=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b7_gas")
b8_gas=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b8_gas")
b9_gas=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b9_gas")
b10_gas=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b10_gas")
b11_gas=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b11_gas")
b12_gas=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b12_gas")

#'Building heat import'
b3_th=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b3_th")
b4_th=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b4_th")
b5_th=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b5_th")
b6_th=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b6_th")
b7_th=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b7_th")
b8_th=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b8_th")


#'Building water import'
b3_wat =model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b3_wat")
b4_wat =model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b4_wat")
b5_wat =model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b5_wat")
b6_wat =model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b6_wat")
b7_wat =model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b7_wat")
b8_wat =model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b8_wat")
b9_wat =model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b9_wat")
b10_wat=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b10_wat")
b11_wat=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b11_wat")
b12_wat=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS, name="b12_wat")

model.update()

#Heat balance for district heating region W
model.addConstrs(chpDH_Schedule[t]*dh_CHP.qNominal==b3_th[t]+b4_th[t]+b5_th[t]+b6_th[t]+b7_th[t]+b8_th[t] for t in range(T))

#Heat balance for buildings W
model.addConstrs(boilerSchedule3[t] * boil_nom + b3_th[t]== building3.get_power_curves()[1][t] for t in range(T))
model.addConstrs(boilerSchedule4[t] * boil_nom + b4_th[t]== building4.get_power_curves()[1][t] for t in range(T))
model.addConstrs(boilerSchedule5[t] * boil_nom + b5_th[t]== building5.get_power_curves()[1][t] for t in range(T))
model.addConstrs(boilerSchedule6[t] * boil_nom + b6_th[t]== building6.get_power_curves()[1][t] for t in range(T))
model.addConstrs(boilerSchedule7[t] * boil_nom + b7_th[t]== building7.get_power_curves()[1][t] for t in range(T))
model.addConstrs(boilerSchedule8[t] * boil_nom + b8_th[t]== building8.get_power_curves()[1][t] for t in range(T))

#Heat balance for buildings E
model.addConstrs(boilerSchedule9[t] * boil_nom + hpSchedule9[t] *hp_nom[1][t]== building9.get_power_curves()[1][t] for t in range(T))
model.addConstrs(boilerSchedule10[t]* boil_nom + hpSchedule10[t]*hp_nom[1][t]== building10.get_power_curves()[1][t] for t in range(T))
model.addConstrs(boilerSchedule11[t]* boil_nom + hpSchedule11[t]*hp_nom[1][t]== building11.get_power_curves()[1][t] for t in range(T))
model.addConstrs(boilerSchedule12[t]* boil_nom + hpSchedule12[t]*hp_nom[1][t]== building12.get_power_curves()[1][t] for t in range(T))

# Power balance for buildings W
model.addConstrs(b3_ele[t] == building3.get_power_curves()[0][t] for t in range(T))
model.addConstrs(b4_ele[t] == building4.get_power_curves()[0][t] for t in range(T))
model.addConstrs(b5_ele[t] == building5.get_power_curves()[0][t] for t in range(T))
model.addConstrs(b6_ele[t] == building6.get_power_curves()[0][t] for t in range(T))
model.addConstrs(b7_ele[t] == building7.get_power_curves()[0][t] for t in range(T))
model.addConstrs(b8_ele[t] == building8.get_power_curves()[0][t] for t in range(T))

# Power balance for buildings E
model.addConstrs(b9_ele[t] + batterySchedule9[t] * bat_nom - hpSchedule9[t] * hp_nom[0][t]== building9.get_power_curves()[0][t] for t in range(T))
model.addConstrs(b10_ele[t] + batterySchedule10[t] * bat_nom - hpSchedule10[t] * hp_nom[0][t]== building10.get_power_curves()[0][t] for t in range(T))
model.addConstrs(b11_ele[t] + batterySchedule11[t] * bat_nom - hpSchedule11[t] * hp_nom[0][t]== building11.get_power_curves()[0][t] for t in range(T))
model.addConstrs(b12_ele[t] + batterySchedule12[t] * bat_nom - hpSchedule12[t] * hp_nom[0][t]== building12.get_power_curves()[0][t] for t in range(T))

#Storage balance storage units
model.addConstr(batterySOC9[0], '==', battery9.socInit)
model.addConstr(batterySOC10[0], '==', battery10.socInit)
model.addConstr(batterySOC11[0], '==', battery11.socInit)
model.addConstr(batterySOC12[0], '==', battery12.socInit)
model.addConstr(storageSOC[0], '==', storage.ffInit)
model.addConstr(pumpSOC[0], '==', pump.ffInit)


model.addConstrs((batterySOC9[t+1]  == batterySOC9[t]  - batterySchedule9[t]  *bat_nom *battery9.dT /battery9.capacity  for t in range(T)))
model.addConstrs((batterySOC10[t+1] == batterySOC10[t] - batterySchedule10[t] *bat_nom *battery10.dT/battery10.capacity for t in range(T)))
model.addConstrs((batterySOC11[t+1] == batterySOC11[t] - batterySchedule11[t] *bat_nom *battery11.dT/battery11.capacity for t in range(T)))
model.addConstrs((batterySOC12[t+1] == batterySOC12[t] - batterySchedule12[t] *bat_nom *battery12.dT/battery12.capacity for t in range(T)))
model.addConstrs((storageSOC[t + 1] == storageSOC[t] - storageSchedule[t] * p2g_sto_nom * storage.dT / storage.capacity for t in range(T)))
model.addConstrs((pumpSOC[t + 1] == pumpSOC[t] - pumpSchedule[t] * pump_nom * pump.dT / pump.energyCapacity for t in range(T)))

# Total power balance
model.addConstrs((utilization_pv[t]*cityDistrict.getPVPower()[t] +
                  utilization_wec[t] *cityDistrict.getWindEnergyConverterPower()[t] +
                  chpDH_Schedule[t] * dh_CHP.pNominal +
                  pumpSchedule[t] * pump_nom+
                  imported[t]-
                  conversionSchedule[t] * p2g_nom
                ==
                b3_ele[t] +
                b4_ele[t] +
                b5_ele[t] +
                b6_ele[t] +
                b7_ele[t] +
                b8_ele[t] +
                b9_ele[t] +
                b10_ele[t] +
                b11_ele[t] +
                b12_ele[t] for t in range(T)))



#Gas balance for buildings
model.addConstrs((b3_gas[t] ==  boilerSchedule3[t]  * boil_nom/heater_boiler3.eta for t in range(T)))
model.addConstrs((b4_gas[t] ==  boilerSchedule4[t]  * boil_nom/heater_boiler4.eta for t in range(T)))
model.addConstrs((b5_gas[t] ==  boilerSchedule5[t]  * boil_nom/heater_boiler5.eta for t in range(T)))
model.addConstrs((b6_gas[t] ==  boilerSchedule6[t]  * boil_nom/heater_boiler6.eta for t in range(T)))
model.addConstrs((b7_gas[t] ==  boilerSchedule7[t]  * boil_nom/heater_boiler7.eta for t in range(T)))
model.addConstrs((b8_gas[t] ==  boilerSchedule8[t]  * boil_nom/heater_boiler8.eta for t in range(T)))
model.addConstrs((b9_gas[t] ==  boilerSchedule9[t]  * boil_nom/heater_boiler9.eta for t in range(T)))
model.addConstrs((b10_gas[t] ==  boilerSchedule10[t]  * boil_nom/heater_boiler10.eta for t in range(T)))
model.addConstrs((b11_gas[t] ==  boilerSchedule11[t]  * boil_nom/heater_boiler11.eta for t in range(T)))
model.addConstrs((b12_gas[t] ==  boilerSchedule12[t]  * boil_nom/heater_boiler12.eta for t in range(T)))

#Power to Gas Converter and Storage balance
#model.addConstrs(-storageSOC[t]*p2g_sto_nom<=conversionSchedule[t]* p2g_nom * p2g.eta for t in range(T))

# Total gas supply balance
model.addConstrs((gasSupplySchedule[t] * gs_nom +
                conversionSchedule[t] * p2g_nom * p2g.eta +
                storageSchedule[t] * p2g_sto_nom
                ==
                chpDH_Schedule[t] * dh_CHP.fNominal +
                b3_gas[t] +
                b4_gas[t] +
                b5_gas[t] +
                b6_gas[t] +
                b7_gas[t] +
                b8_gas[t] +
                b9_gas[t] +
                b10_gas[t] +
                b11_gas[t] +
                b12_gas[t]
                for t in range(T)))

#Water balance for buildings
model.addConstrs((b3_wat[t] ==  building3.get_waterDemand_profile()[t] for t in range(T)))
model.addConstrs((b4_wat[t] ==  building4.get_waterDemand_profile()[t] for t in range(T)))
model.addConstrs((b5_wat[t] ==  building5.get_waterDemand_profile()[t] for t in range(T)))
model.addConstrs((b6_wat[t] ==  building6.get_waterDemand_profile()[t] for t in range(T)))
model.addConstrs((b7_wat[t] ==  building7.get_waterDemand_profile()[t] for t in range(T)))
model.addConstrs((b8_wat[t] ==  building8.get_waterDemand_profile()[t] for t in range(T)))
model.addConstrs((b9_wat[t] ==  building9.get_waterDemand_profile()[t] for t in range(T)))
model.addConstrs((b10_wat[t] ==  building10.get_waterDemand_profile()[t] for t in range(T)))
model.addConstrs((b11_wat[t] ==  building11.get_waterDemand_profile()[t] for t in range(T)))
model.addConstrs((b12_wat[t] ==  building12.get_waterDemand_profile()[t] for t in range(T)))


#Total water balance
model.addConstrs((waterSupplySchedule[t] * ws_nom+
                  pumpSchedule[t]*pump_nom/(pump.d*pump.g*pump.h)
                  ==
                  b3_wat[t] +
                  b4_wat[t] +
                  b5_wat[t] +
                  b6_wat[t] +
                  b7_wat[t] +
                  b8_wat[t] +
                  b9_wat[t] +
                  b10_wat[t] +
                  b11_wat[t] +
                  b12_wat[t]
                  for t in range(T)))

model.setObjective(sum((imported[t]/0.4+
                        chpDH_Schedule[t] * dh_CHP.fNominal +
                        b3_gas[t] +
                        b4_gas[t] +
                        b5_gas[t] +
                        b6_gas[t] +
                        b7_gas[t] +
                        b8_gas[t] +
                        b9_gas[t] +
                        b10_gas[t] +
                        b11_gas[t] +
                        b12_gas[t]) * 0.2*900 / 3600 / 1000
                       for t in range(T)), GRB.MINIMIZE)


model.optimize()
