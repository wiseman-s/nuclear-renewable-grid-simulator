import numpy as np
from .parameters import REACTOR_TYPES

class ThermalFeedback:
    def __init__(self, reactor_type="SMR (demo-friendly)"):
        params = REACTOR_TYPES[reactor_type]
        self.alpha_fuel = params["alpha_fuel"]
        self.alpha_coolant = params["alpha_coolant"]
        self.Tf0 = params["T_fuel0"]
        self.Tc0 = params["T_coolant0"]

    def __call__(self, Tf, Tc):
        return self.alpha_fuel * (Tf - self.Tf0) + self.alpha_coolant * (Tc - self.Tc0)

    @staticmethod
    def dTfdt(P, Tf, Tc, reactor_type="SMR (demo-friendly)"):
        power = P * 1e9
        HT = 1.5e7
        return (power - HT * (Tf - Tc)) / 1e7

    @staticmethod
    def dTcdt(P, Tf, Tc, reactor_type="SMR (demo-friendly)"):
        power = P * 1e9
        HT = 1.5e7
        return (HT * (Tf - Tc)) / 5e6