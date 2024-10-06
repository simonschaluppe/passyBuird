# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 13:10:17 2021

@author: Simon
"""
from pathlib import Path

import numpy as np

DEFAULT_MODULE = "LG_Electronics_Inc__LG320N1C_G4" #must be in pvlib module database
DEFAULT_INVERTER = "Fronius_International_GmbH__Fronius_Primo_10_0_1_208_240__240V_" #3 strings á 12 modules = 36 modules ~ 10 kWp

class PV:
    """
    PV Profile with .TSD in [kWh per hour]
    """

    def __init__(self, csv=None, kWp=1., cost_kWp=1500, array=None):

        if array is not None:
            self.TSD_source = np.array(array)
            self.path = "Directly from Array input"
        elif csv is not None:
            self.TSD_source = np.genfromtxt(csv)
            self.path = csv
        else:
            raise ValueError("Missing Source: Either 'csv' or 'array' argument must be supplied!")
        self.source_kWp = kWp
        self.cost_kWp = cost_kWp # cost per kWh

        self.set_kWp(kWp)

    def set_kWp(self, kWp):

        self.TSD = self.TSD_source / self.source_kWp * kWp
        self.kWp = kWp
        self.cost = kWp * self.cost_kWp

    def __repr__(self):
        width = len(self.path)+10
        return f"""PV-System {str(self.path)}
{"-"*width}
kWp: {self.kWp:>{width-5}.1f}
kWh/a: {self.TSD.sum():>{width-7}.0f}
cost [€]: {self.cost:>{width-10}.0f}"""

    def save(self, folder="../../data", filename=None):
        if filename is None:
            filename = f"Generic_{self.kWp:.0f}kWp.csv"
        np.savetxt(Path(folder, filename),self.TSD)

