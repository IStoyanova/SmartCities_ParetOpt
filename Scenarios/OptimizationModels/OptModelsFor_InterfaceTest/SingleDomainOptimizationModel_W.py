from Scenarios.Infrastructure import *

print('Optimization of the water domain operation')
print()
model=Model("Optimum_Water")
T=96

#'District Gas Source: how much water power will be supplied'
ws_nom=100000000
waterSupplySchedule =model.addVars(T,lb=0.0,ub=1.0,vtype=GRB.CONTINUOUS, name="water_source")

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



#Water balance for buildings
model.addConstrs((b3_wat[i] ==  building3.get_waterDemand_profile()[i] for i in range(T)))
model.addConstrs((b4_wat[i] ==  building4.get_waterDemand_profile()[i] for i in range(T)))
model.addConstrs((b5_wat[i] ==  building5.get_waterDemand_profile()[i] for i in range(T)))
model.addConstrs((b6_wat[i] ==  building6.get_waterDemand_profile()[i] for i in range(T)))
model.addConstrs((b7_wat[i] ==  building7.get_waterDemand_profile()[i] for i in range(T)))
model.addConstrs((b8_wat[i] ==  building8.get_waterDemand_profile()[i] for i in range(T)))
model.addConstrs((b9_wat[i] ==  building9.get_waterDemand_profile()[i] for i in range(T)))
model.addConstrs((b10_wat[i] ==  building10.get_waterDemand_profile()[i] for i in range(T)))
model.addConstrs((b11_wat[i] ==  building11.get_waterDemand_profile()[i] for i in range(T)))
model.addConstrs((b12_wat[i] ==  building12.get_waterDemand_profile()[i] for i in range(T)))

model.addConstrs((waterSupplySchedule[i] * ws_nom
                ==
                b3_wat[i] +
                b4_wat[i] +
                b5_wat[i] +
                b6_wat[i] +
                b7_wat[i] +
                b8_wat[i] +
                b9_wat[i] +
                b10_wat[i] +
                b11_wat[i] +
                b12_wat[i]
                for i in range(T)))

model.setObjective(sum(waterSupplySchedule[t]
                       for t in range(T)),GRB.MINIMIZE)


model.optimize()
