from Scenarios.OptimizationModels.OptModelsFor_DomainPriorityTest.OptimizationModel_EG import *
from newFunctions.ExcelPrint import *

#'Power to gas conversion: how much electric power will be converted'
conversionSchedule_set =[]

#'Power to gas storage: how much gas power will be supplied')
storageSchedule_set=[]

#'Hydroelectric pump storage: how much electric power will be supplied')
pumpSchedule_set=[]

#'District heating CHP: how much electric power will be supplied')
chpDH_Schedule_set = []

#'District Gas Source: how much gas power will be supplied')
gasSupplySchedule_set = []

#'District Water Source: how much water will be supplied')
waterSupplySchedule_set = []

#'Schedules assigned to gas boilers of the buildings')
boilerSchedule3_set=[]
boilerSchedule4_set=[]
boilerSchedule5_set=[]
boilerSchedule6_set=[]
boilerSchedule7_set=[]
boilerSchedule8_set=[]
boilerSchedule9_set=[]
boilerSchedule10_set=[]
boilerSchedule11_set=[]
boilerSchedule12_set=[]

#'Schedule assigned to heatpumps of the buildings')
hpSchedule9_set=[]
hpSchedule10_set=[]
hpSchedule11_set=[]
hpSchedule12_set=[]

#'Schedule assigned to batteries of the buildings')
batterySchedule9_set=[]
batterySchedule10_set=[]
batterySchedule11_set=[]
batterySchedule12_set=[]


#Assignment of optimization values
for t in range(T):
    conversionSchedule_set.append(conversionSchedule[t].X * p2g_nom)

    storageSchedule_set.append(storageSchedule[t].X*p2g_sto_nom)

    pumpSchedule_set.append(pumpSchedule[t].X * pump_nom)

    chpDH_Schedule_set.append(chpDH_Schedule[t].X)

    gasSupplySchedule_set.append(gasSupplySchedule[t].X*gs_nom)

    waterSupplySchedule_set.append(waterSupplySchedule[t].X*ws_nom)

    boilerSchedule3_set.append(boilerSchedule3[t].X )
    boilerSchedule4_set.append(boilerSchedule4[t].X)
    boilerSchedule5_set.append(boilerSchedule5[t].X)
    boilerSchedule6_set.append(boilerSchedule6[t].X)
    boilerSchedule7_set.append(boilerSchedule7[t].X)
    boilerSchedule8_set.append(boilerSchedule8[t].X)
    boilerSchedule9_set.append(boilerSchedule9[t].X)
    boilerSchedule10_set.append(boilerSchedule10[t].X)
    boilerSchedule11_set.append(boilerSchedule11[t].X)
    boilerSchedule12_set.append(boilerSchedule12[t].X)

    hpSchedule9_set.append(hpSchedule9[t].X)
    hpSchedule10_set.append(hpSchedule10[t].X)
    hpSchedule11_set.append(hpSchedule11[t].X)
    hpSchedule12_set.append(hpSchedule12[t].X)

    batterySchedule9_set.append(batterySchedule9[t].X*bat_nom)
    batterySchedule10_set.append(batterySchedule10[t].X*bat_nom)
    batterySchedule11_set.append(batterySchedule11[t].X*bat_nom)
    batterySchedule12_set.append(batterySchedule12[t].X*bat_nom)

for t in range(T,192):
    hpSchedule9_set.append(0.0)
    hpSchedule10_set.append(0.0)
    hpSchedule11_set.append(0.0)
    hpSchedule12_set.append(0.0)

print('Simulation')
p2g.setResults(np.array(conversionSchedule_set))
storage.setResults(np.array(storageSchedule_set))
pump.setResults(np.array(pumpSchedule_set))
dh_CHP.setResults(np.array(chpDH_Schedule_set))
districtGasSource.setResults(np.array(gasSupplySchedule_set))
districtWaterSource.setResults(np.array(waterSupplySchedule_set))

building3.bes.boiler.setResults(np.array(boilerSchedule3_set))
building4.bes.boiler.setResults(np.array(boilerSchedule4_set))
building5.bes.boiler.setResults(np.array(boilerSchedule5_set))
building6.bes.boiler.setResults(np.array(boilerSchedule6_set))
building7.bes.boiler.setResults(np.array(boilerSchedule7_set))
building8.bes.boiler.setResults(np.array(boilerSchedule8_set))
building9.bes.boiler.setResults(np.array(boilerSchedule9_set))
building10.bes.boiler.setResults(np.array(boilerSchedule10_set))
building11.bes.boiler.setResults(np.array(boilerSchedule11_set))
building12.bes.boiler.setResults(np.array(boilerSchedule12_set))

building9.bes.battery.setResults(np.array(batterySchedule9_set))
building10.bes.battery.setResults(np.array(batterySchedule10_set))
building11.bes.battery.setResults(np.array(batterySchedule11_set))
building12.bes.battery.setResults(np.array(batterySchedule12_set))

building9.bes.heatpump.setResults(heatFlow,np.array(hpSchedule9_set))
building10.bes.heatpump.setResults(heatFlow,np.array(hpSchedule10_set))
building11.bes.heatpump.setResults(heatFlow,np.array(hpSchedule11_set))
building12.bes.heatpump.setResults(heatFlow,np.array(hpSchedule12_set))

wb=print2Excel(cityDistrict)

wb.save('Results\SingleDomainOptimization_ElePrior.xlsx')
print("Results are available in 'Results' folder", "'SingleDomainOptimization_ElePrior.xlsx' file")

