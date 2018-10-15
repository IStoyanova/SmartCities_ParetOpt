#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vehicle object of pycity
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


class services(object):
    """
    Implementation of a services that consists of a quantity of types
    types:bakery(ba), busines(bi), shop(sh)

    """
    
    def __init__(self, environment, number=1, type='ba', method='excelcurves', labels=None):
        """
        Workflow
        --------
        1 : acording to the amount of services and the type an electrcity demand is generated.

        2 : .
        
        Parameter
        ---------
        environment : Environment object
            Common to all other objects. Includes time and weather instances

        """
        self._kind = "services"
        self.labels=labels
        
        self.environment = environment
        self.number=number
        self.type=type

        self.method=method




    def get_energy_curves(self, current_values=True):
        Ta=96
        b=[]
        for t in range(Ta):
            b.insert(t,0)

        if self.method=='excelcurves':
            usage = xlrd.open_workbook('sup_vehicle1.xlsx')
            first_sheet = usage.sheet_by_index(0)

            if self.type == 'ba':
                ba = first_sheet.col_slice(colx=8,
                                           start_rowx=2,
                                           end_rowx=98)

            if self.type == 'bu':
                ba = first_sheet.col_slice(colx=9,
                                           start_rowx=2,
                                           end_rowx=98)

            if self.type == 'sh':
                ba = first_sheet.col_slice(colx=10,
                                           start_rowx=2,
                                           end_rowx=98)


            for t in range(Ta):
                b[t] = float("{0:.4f}".format( ba[t].value* (1000)))


        return b



    def get_total_energy_curves(self, current_values=True):
        return (self.number*self.get_energy_curves())





