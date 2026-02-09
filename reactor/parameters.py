import numpy as np

# Standard 6-group data (U-235 thermal, Keepin)
BETA = np.array([0.000215, 0.001424, 0.001274, 0.002568, 0.000748, 0.000273])
LAMBDA = np.array([0.0124, 0.0305, 0.111, 0.301, 1.14, 3.01])
BETA_TOTAL = np.sum(BETA)

# Two realistic reactor types (you can add more)
REACTOR_TYPES = {
    "PWR (typical 1000 MW)": {
        "lambda_prompt": 1e-4,
        "alpha_fuel": -2.5e-5,      # strong Doppler
        "alpha_coolant": -2.0e-5,
        "T_fuel0": 850.0,
        "T_coolant0": 580.0
    },
    "SMR (demo-friendly)": {
        "lambda_prompt": 5e-5,      # faster prompt response
        "alpha_fuel": -1.2e-5,      # weaker → nice overshoot visible
        "alpha_coolant": -1.0e-5,
        "T_fuel0": 750.0,
        "T_coolant0": 550.0
    }
}