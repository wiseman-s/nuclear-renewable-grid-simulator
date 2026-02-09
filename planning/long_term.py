import pandas as pd
import numpy as np

def long_term_plan(years=15, annual_growth=0.045, nuclear_commission_year=8):
    years_list = list(range(2026, 2026 + years))
    demand = 1850 * (1 + annual_growth) ** np.arange(years)   # starting from current avg
    
    nuclear_added = np.where(np.array(years_list) >= 2026 + nuclear_commission_year, 1000, 0)
    
    df = pd.DataFrame({
        'year': years_list,
        'peak_demand_mw': (demand * 1.35).round(),   # peak ~35% above avg
        'nuclear_capacity_mw': nuclear_added,
        'total_capacity_mw': 3840 + np.cumsum([200] * years)   # rough expansion
    })
    df['renewable_share'] = np.where(df['nuclear_capacity_mw'] > 0, 0.92, 0.88)
    return df