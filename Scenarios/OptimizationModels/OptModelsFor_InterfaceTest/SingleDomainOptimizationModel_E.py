from Scenarios.Infrastructure import *

print('Optimization of the electricity domain operation')
print()
model=Model("OptimumSingleE")

T=96

heatFlow=[50]*192 #heat flow temperature 50C

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

imported=model.addVars(T,lb=0.0,vtype=GRB.CONTINUOUS,name='imported')
utilization_pv=model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS,name='utilization_pv')
utilization_wec=model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS,name='utilization_wec')


model.update()


model.addConstr(batterySOC9[0], '==', battery9.socInit)
model.addConstr(batterySOC10[0], '==', battery10.socInit)
model.addConstr(batterySOC11[0], '==', battery11.socInit)
model.addConstr(batterySOC12[0], '==', battery12.socInit)

model.addConstrs((batterySOC9[i+1]  == batterySOC9[i]  - batterySchedule9[i]  *bat_nom *battery9.dT /battery9.capacity  for i in range(T)))
model.addConstrs((batterySOC10[i+1] == batterySOC10[i] - batterySchedule10[i] *bat_nom *battery10.dT/battery10.capacity for i in range(T)))
model.addConstrs((batterySOC11[i+1] == batterySOC11[i] - batterySchedule11[i] *bat_nom *battery11.dT/battery11.capacity for i in range(T)))
model.addConstrs((batterySOC12[i+1] == batterySOC12[i] - batterySchedule12[i] *bat_nom *battery12.dT/battery12.capacity for i in range(T)))

model.addConstrs((b3_ele[i] ==  building3.get_power_curves()[0][i] for i in range(T)))
model.addConstrs((b4_ele[i] ==  building4.get_power_curves()[0][i] for i in range(T)))
model.addConstrs((b5_ele[i] ==  building5.get_power_curves()[0][i] for i in range(T)))
model.addConstrs((b6_ele[i] ==  building6.get_power_curves()[0][i] for i in range(T)))
model.addConstrs((b7_ele[i] ==  building7.get_power_curves()[0][i] for i in range(T)))
model.addConstrs((b8_ele[i] ==  building8.get_power_curves()[0][i] for i in range(T)))

model.addConstrs((b9_ele[i] + batterySchedule9[i] * bat_nom ==  building9.get_power_curves()[0][i] for i in range(T)))
model.addConstrs((b10_ele[i] + batterySchedule10[i] * bat_nom ==  building10.get_power_curves()[0][i] for i in range(T)))
model.addConstrs((b11_ele[i] + batterySchedule11[i] * bat_nom ==  building11.get_power_curves()[0][i] for i in range(T)))
model.addConstrs((b12_ele[i] + batterySchedule12[i] * bat_nom ==  building12.get_power_curves()[0][i] for i in range(T)))

model.addConstrs((b3_ele[i]+b4_ele[i]+b5_ele[i]+b6_ele[i]+b7_ele[i]+b8_ele[i]+b9_ele[i]+b10_ele[i]+b11_ele[i]+b12_ele[i]
                  ==
                  utilization_pv[i]*cityDistrict.getPVPower()[i]+
                  utilization_wec[i]*cityDistrict.getWindEnergyConverterPower()[i]+
                  imported[i]
                  for i in range(T)))

model.setObjective(sum(imported[i] for i in range(T)),GRB.MINIMIZE)

model.optimize()

if model.STATUS==GRB.INFEASIBLE:
    model.computeIIS()
    model.write("model.ilp")

if __name__ == '__main__':
    imported_Ele=0
    nonUtil_Ele=0
    for i in range(T):
        imported_Ele+=imported[i].X/1000/3600*900
        nonUtil_Ele+=((1 - utilization_wec[i].X) * cityDistrict.getWindEnergyConverterPower()[i] + (1 - utilization_pv[i].X) *cityDistrict.getPVPower()[i])/1000/3600*900
    print('import total',imported_Ele, 'kWh')
    print('non-utilized total',nonUtil_Ele,'kWh')
