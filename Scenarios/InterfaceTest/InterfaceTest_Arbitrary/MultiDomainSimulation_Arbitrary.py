from Scenarios.Infrastructure import *
from newFunctions.ExcelPrint import *

#'Power to gas conversion: how much electric power will be converted'
conversionSchedule_set =[]
p2g_nom=p2g.maxPInput

#'Power to gas storage: how much gas power will be supplied')
storageSchedule_set=[]
p2g_sto_nom=storage.capacity/18000

#'Hydroelectric pump storage: how much electric power will be supplied')
pumpSchedule_set=[]
pump_nom=pump.energyCapacity/18000

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
heatFlow=[50]*192


#Assignment of optimization values
for t in range(192):
    conversionSchedule_set.append(0.7*p2g_nom)

    storageSchedule_set.append(-0.6*p2g_sto_nom)

    pumpSchedule_set.append(-0.4*pump_nom)

    chpDH_Schedule_set.append(0.2)

    gasSupplySchedule_set.append(900000)

    waterSupplySchedule_set.append(0.0006)

    boilerSchedule3_set.append(0.5 if t<=64 and t>32 else 0.2)
    boilerSchedule4_set.append(0.5 if t<=64 and t>32 else 0.2)
    boilerSchedule5_set.append(0.5 if t<=64 and t>32 else 0.2)
    boilerSchedule6_set.append(0.5 if t<=64 and t>32 else 0.2)
    boilerSchedule7_set.append(0.5 if t<=64 and t>32 else 0.2)
    boilerSchedule8_set.append(0.5 if t<=64 and t>32 else 0.2)
    boilerSchedule9_set.append(0.5 if t<=64 and t>32 else 0.2)
    boilerSchedule10_set.append(0.5 if t<=64 and t>32 else 0.2)
    boilerSchedule11_set.append(0.5 if t<=64 and t>32 else 0.2)
    boilerSchedule12_set.append(0.5 if t<=64 and t>32 else 0.2)

    hpSchedule9_set.append(0.5)
    hpSchedule10_set.append(0.5)
    hpSchedule11_set.append(0.5)
    hpSchedule12_set.append(0.5)

    batterySchedule9_set.append(-300 if t<=64 else 300)
    batterySchedule10_set.append(-300 if t<=64 else 300)
    batterySchedule11_set.append(-300 if t<=64 else 300)
    batterySchedule12_set.append(-300 if t<=64 else 300)

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

wb.save('Results/CrossDomainArbitrary.xlsx')
print("Results are available in 'Results' folder", "'CrossDomainArbitrary.xlsx'")






