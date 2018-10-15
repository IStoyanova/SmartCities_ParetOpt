from Scenarios.Infrastructure import *

print('Optimization of the gas domain operation')
print()
model=Model("OptimumOperation")
T=96

#'District Gas Source: how much gas power will be supplied'
gs_nom=100000000
gasSupplySchedule =model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS, name="gas_source")

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


model.addConstrs(boilerSchedule3[i] * boil_nom == building3.get_power_curves()[1][i] for i in range(T))
model.addConstrs(boilerSchedule4[i] * boil_nom == building4.get_power_curves()[1][i] for i in range(T))
model.addConstrs(boilerSchedule5[i] * boil_nom == building5.get_power_curves()[1][i] for i in range(T))
model.addConstrs(boilerSchedule6[i] * boil_nom == building6.get_power_curves()[1][i] for i in range(T))
model.addConstrs(boilerSchedule7[i] * boil_nom == building7.get_power_curves()[1][i] for i in range(T))
model.addConstrs(boilerSchedule8[i] * boil_nom == building8.get_power_curves()[1][i] for i in range(T))
model.addConstrs(boilerSchedule9[i] * boil_nom == building9.get_power_curves()[1][i] for i in range(T))
model.addConstrs(boilerSchedule10[i] * boil_nom == building10.get_power_curves()[1][i] for i in range(T))
model.addConstrs(boilerSchedule11[i] * boil_nom == building11.get_power_curves()[1][i] for i in range(T))
model.addConstrs(boilerSchedule12[i] * boil_nom == building12.get_power_curves()[1][i] for i in range(T))


model.addConstrs((b3_gas[i] ==  boilerSchedule3[i]  * boil_nom/heater_boiler3.eta for i in range(T)))
model.addConstrs((b4_gas[i] ==  boilerSchedule4[i]  * boil_nom/heater_boiler4.eta for i in range(T)))
model.addConstrs((b5_gas[i] ==  boilerSchedule5[i]  * boil_nom/heater_boiler5.eta for i in range(T)))
model.addConstrs((b6_gas[i] ==  boilerSchedule6[i]  * boil_nom/heater_boiler6.eta for i in range(T)))
model.addConstrs((b7_gas[i] ==  boilerSchedule7[i]  * boil_nom/heater_boiler7.eta for i in range(T)))
model.addConstrs((b8_gas[i] ==  boilerSchedule8[i]  * boil_nom/heater_boiler8.eta for i in range(T)))
model.addConstrs((b9_gas[i] ==  boilerSchedule9[i]  * boil_nom/heater_boiler9.eta for i in range(T)))
model.addConstrs((b10_gas[i] ==  boilerSchedule10[i]  * boil_nom/heater_boiler10.eta for i in range(T)))
model.addConstrs((b11_gas[i] ==  boilerSchedule11[i]  * boil_nom/heater_boiler11.eta for i in range(T)))
model.addConstrs((b12_gas[i] ==  boilerSchedule12[i]  * boil_nom/heater_boiler12.eta for i in range(T)))

# Total gas supply balance
model.addConstrs((gasSupplySchedule[i] * gs_nom
                ==
                b3_gas[i] +b4_gas[i] +b5_gas[i] +b6_gas[i] +b7_gas[i] +b8_gas[i] +b9_gas[i] +b10_gas[i] +b11_gas[i] +b12_gas[i]
                for i in range(T)))


model.setObjective(sum(gasSupplySchedule[i]*gs_nom
                           for i in range(T)),GRB.MINIMIZE)


model.optimize()

if __name__ == '__main__':
    directEmission=0
    for i in range(T):
        directEmission+=(0 * dh_CHP.fNominal +
                            b3_gas[i].X +
                            b4_gas[i].X +
                            b5_gas[i].X +
                            b6_gas[i].X +
                            b7_gas[i].X +
                            b8_gas[i].X +
                            b9_gas[i].X +
                            b10_gas[i].X +
                            b11_gas[i].X +
                            b12_gas[i].X) * 0.2/1000/3600*900
    print('direct emission',directEmission, 'kg CO2')

