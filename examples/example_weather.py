#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 11 14:12:12 2015

@author: tsz
"""

from __future__ import division

import pycity_base.classes.Timer
import pycity_base.classes.Weather

import matplotlib.pyplot as plt

def run_test():
    timer = pycity_base.classes.Timer.Timer()
    weather = pycity_base.classes.Weather.Weather(timer)

    (tamb, qdir,qdif, vw, phiamb, pamb) = weather.getWeatherForecast(getTAmbient=True,
                                                                getQDirect=True,
                                                                getQDiffuse=True,
                                                                getVWind=True,
                                                                getPhiAmbient=True,
                                                                getPAmbient=True)

    print()
    print("Ambient temperature: " + str(tamb))
    print()
    print("Direct radiation: " + str(qdir) )
    print()
    print("Wind velocity: " + str(vw))
    print()
    print("Relative humidity: " + str(phiamb))
    print()
    print("Ambient pressure: " + str(pamb))
    print()


    timesteps = range(96)

    fig = plt.figure(1)

    sb1 = plt.subplot(3,1, 1)
    sb1.plot(timesteps, tamb[0:96], 'g-',label='Ambient temperature')
    sb1.set_ylabel(u'\xb0'+str('C'))
    sb1.grid('on')
    plt.legend(loc="best")

    sb2 = plt.subplot(3,1, 2,sharex=sb1)
    sb2.plot(timesteps,qdir[0:96], 'b-' ,label='Direct Radiation')
    sb2.plot(timesteps, qdif[0:96], 'r-', label='Diffuse Radiation')
    sb2.set_ylabel('W/m2')
    sb2.set_ylim(-10, 100)
    sb2.grid('on')
    plt.legend(loc="best")

    sb3 = plt.subplot(3,1,3,sharex=sb1)
    sb3.plot(timesteps, vw[0:96], 'k-',label='Wind velocity')
    sb3.set_ylabel('m/s')
    sb3.set_xlabel('Time Steps')
    sb3.set_xlim(0, 96)
    sb3.grid('on')
    plt.legend(loc="best")

    # sb1.get_xaxis().set_ticklabels([])
    # sb2.get_xaxis().set_ticklabels([])
    sb3.set_xticks(range(0, 100, 16))

    fig.savefig('5_02')

    plt.show()




if __name__ == '__main__':
    #  Run program
    run_test()
