import json

def calculate_total_emissions(dispatch_df):
    """Lifecycle CO₂eq in tonnes (gCO₂/kWh → tonnes/MWh)"""
    with open('data/emissions_factors.json', 'r') as f:
        factors = json.load(f)
    
    total_co2_tonnes = 0.0
    for src in dispatch_df.columns:
        if src in factors and src != 'unserved_mw':
            energy_mwh = dispatch_df[src].sum()
            factor_g_per_kwh = factors[src]
            tonnes = energy_mwh * (factor_g_per_kwh / 1000)  # g/kWh → t/MWh
            total_co2_tonnes += tonnes
    
    return total_co2_tonnes