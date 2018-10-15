#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
street lighting object of pycity
"""

"""
upgrade
@author: ist-fce
"""

import numpy as np
import warnings
import xlrd
import os
import pycity_base.functions.slp_electrical as slp_el


class streetlighting(object):
    """
    Implementation of a

    """
    
    def __init__(self, environment, number=2, method='',energyxTS=2700, labels=None):
        """
        Workflow
        --------
        1 :

        2 : .
        
        Parameter
        ---------
        environment : Environment object
            Common to all other objects. Includes time and weather instances

        """
        self._kind = "light"
        self.labels=labels
        
        self.environment = environment
        self.number=number
        self.method=method
        self.energyxTS = energyxTS




    def get_energy_curves(self, current_values=True):
        Ta=96
        n=1
        if self.method == 'auto':
            n=2
        b=[]
        for t in range(Ta):
            b.insert(t,0)

        usage = xlrd.open_workbook('sup_vehicle1.xlsx')
        first_sheet = usage.sheet_by_index(0)


        ba = first_sheet.col_slice(colx=7,
                                        start_rowx=2,
                                        end_rowx=98)

        for t in range(Ta):
                b[t] = (float("{0:.4f}".format(ba[t].value))) * self.energyxTS * self.number *n



        return b









