from Scenarios.OptimizationModels.OptimizationModels_2.OptimizationModel_EG import imported_Ele,emmD_Ele,emmI_Ele,emmT_Ele,chp_Ele,storage_list_single_ele
from Scenarios.OptimizationModels.OptimizationModels_2.OptimizationModel_GE import imported_Gas,emmD_Gas,emmI_Gas,emmT_Gas,chp_Gas,storage_list_single_gas
from Scenarios.OptimizationModels.OptimizationModels_2.OptimizationModel_EGTW import imported_Cross,emmD_Cross,emmI_Cross,emmT_Cross,chp_Cross,storage_list_cross

import matplotlib.pyplot as plt


timesteps=range(96)
figEleImp=plt.figure(3)


figEleIm=plt.subplot(2,2,1)
figEleIm.plot(timesteps, imported_Ele, 'b-',label='Electricity prior')
figEleIm.plot(timesteps, imported_Cross, 'g-',label='Cross-domain')
figEleIm.set_ylabel('kW_el')
figEleIm.set_xlabel('Time Steps')
figEleIm.set_xlim(0, 96)
figEleIm.set_xticks(range(0,100,16))
figEleIm.grid(True)

figEleIm2=plt.subplot(2,2,2,sharey=figEleIm)
figEleIm2.plot(timesteps, imported_Gas, 'r-',label='Gas prior')
figEleIm2.plot(timesteps, imported_Cross, 'g-',label='Cross-domain')
figEleIm2.set_xlabel('Time Steps')
figEleIm2.set_xlim(0, 96)
figEleIm2.set_xticks(range(0,100,16))
figEleIm2.grid(True)


figEleImp.show()

#Emission
figEmm=plt.figure(1)
figEmm.suptitle('Emission', fontsize=20)
figEmm.subplots_adjust(hspace=0.39,top=0.88)

citOp=plt.subplot(3, 2, 1)
citOp.grid('on')
citOp.set_ylabel('Direct')
citOp.plot(timesteps, emmD_Ele, 'b-',label='Electricity prior')
citOp.plot(timesteps, emmD_Cross, 'g-',label='Cross-domain')


impOp=plt.subplot(3, 2, 3,sharex=citOp)
impOp.grid('on')
impOp.set_ylabel('Indirect')
impOp.plot(timesteps, emmI_Ele, 'b-',label='Electricity prior')
impOp.plot(timesteps, emmI_Ele, 'g-',label='Cross-domain')


totOp=plt.subplot(3, 2, 5,sharex=citOp)
totOp.set_ylabel('Total')
totOp.set_xlabel('Time Steps')
totOp.set_xlim(0, 96)
totOp.set_xticks(range(0,100,16))
totOp.grid('on')
totOp.plot(timesteps, emmT_Ele, 'b-',label='Electricity prior')
totOp.plot(timesteps, emmT_Cross, 'g-',label='Cross-domain')

citOp2=plt.subplot(3, 2, 2,sharey=citOp)
citOp2.grid('on')
citOp2.plot(timesteps, emmD_Gas, 'r-',label='Gas prior')
citOp2.plot(timesteps, emmD_Cross, 'g-',label='Cross-domain')


impOp2=plt.subplot(3, 2, 4,sharex=citOp2,sharey=impOp)
impOp2.grid('on')
impOp2.plot(timesteps, emmI_Gas, 'r-',label='Gas prior')
impOp2.plot(timesteps, emmI_Cross, 'g-',label='Cross-domain')


totOp2=plt.subplot(3, 2, 6,sharex=citOp2,sharey=totOp)
totOp2.set_xlabel('Time Steps')
totOp2.set_xlim(0, 96)
totOp2.set_xticks(range(0,100,16))
totOp2.grid('on')
totOp2.plot(timesteps, emmT_Gas, 'r-',label='Gas prior')
totOp2.plot(timesteps, emmT_Cross, 'g-',label='Cross-domain')

figChp=plt.figure(2)

figchp1=plt.subplot(3,1,1)
figchp1.plot(timesteps, chp_Ele, 'b-',label='Electricity prior')
figchp1.set_xlim(0, 96)
figchp1.set_xticks(range(0,100,16))
figchp1.grid(True)

figchp2=plt.subplot(3,1,2,sharex=figchp1)
figchp2.plot(timesteps, chp_Gas, 'r-',label='Gas prior')
figchp2.set_xlim(0, 96)
figchp2.set_xticks(range(0,100,16))
figchp2.grid(True)

figchp3=plt.subplot(3,1,3,sharex=figchp1)
figchp3.plot(timesteps, chp_Cross, 'g-',label='Cross-domain')
figchp3.set_xlabel('Time Steps')
figchp3.set_xlim(0, 96)
figchp3.set_xticks(range(0,100,16))
figchp3.grid(True)

figChp.show()

#Storage devices
figSto=plt.figure(4)
figSto.subplots_adjust(wspace=0.20, top=0.86)


sp1=plt.subplot(3, 3, 1)
sp1.plot(timesteps, storage_list_single_ele[0], 'b-')
sp1.title.set_text('Electricity prior')
sp1.set_ylabel('Battery')
sp1.set_yticks(range(0,100,20))
sp1.grid('on')

sp2=plt.subplot(3, 3, 2,sharey=sp1)
sp2.plot(timesteps, storage_list_single_gas[0], 'r-')
sp2.title.set_text('Gas prior')
sp2.set_yticks(range(0,100,20))
sp2.grid('on')

sp3=plt.subplot(3, 3, 3,sharey=sp1)
sp3.plot(timesteps, storage_list_cross[0], 'g-')
sp3.title.set_text('Cross')
sp3.set_yticks(range(0,100,20))
sp3.grid('on')

sp4=plt.subplot(3, 3, 4,sharex=sp1)
sp4.plot(timesteps, storage_list_single_ele[1], 'b-')
sp4.set_ylabel('HE')
sp4.set_yticks(range(0,100,20))
sp4.grid('on')

sp5=plt.subplot(3, 3, 5,sharex=sp2,sharey=sp4)
sp5.plot(timesteps, storage_list_single_gas[1], 'r-')
sp5.set_yticks(range(0,100,20))
sp5.grid('on')

sp6=plt.subplot(3, 3, 6,sharex=sp3,sharey=sp4)
sp6.plot(timesteps, storage_list_cross[1], 'g-')
sp6.set_yticks(range(0,100,20))
sp6.grid('on')

sp7=plt.subplot(3, 3, 7,sharex=sp1)
sp7.plot(timesteps, storage_list_single_ele[2], 'b-')
sp7.set_ylabel('P2G')
sp7.set_xlabel('Time Steps')
sp7.set_xlim(0, 96)
sp7.set_yticks(range(0,100,20))
sp7.grid('on')

sp8=plt.subplot(3, 3, 8,sharex=sp2,sharey=sp7)
sp8.plot(timesteps, storage_list_single_gas[2], 'r-')
sp8.set_xlabel('Time Steps')
sp8.set_xlim(0, 96)
sp8.set_yticks(range(0,100,20))
sp8.grid('on')

sp9=plt.subplot(3, 3, 9,sharex=sp3,sharey=sp7)
sp9.plot(timesteps, storage_list_cross[2], 'g-')
sp9.set_xlabel('Time Steps')
sp9.set_xlim(0, 96)
sp9.set_yticks(range(0,100,20))
sp9.grid('on')

xticklabels = sp1.get_xticklabels()+sp2.get_xticklabels()+sp3.get_xticklabels()+sp4.get_xticklabels()+sp5.get_xticklabels()+sp6.get_xticklabels()
yticklabels =sp2.get_yticklabels()+sp3.get_yticklabels()+sp5.get_yticklabels()+sp6.get_yticklabels()+sp8.get_yticklabels()+sp9.get_yticklabels()
plt.setp(xticklabels, visible=False)
plt.setp(yticklabels, visible=False)

plt.show()