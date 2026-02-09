import json

def calculate_total_cost(dispatch_df):
    """Simple variable O&M + fuel cost in USD (rough 2025 Kenya context)"""
    with open('data/generation_costs.json', 'r') as f:
        costs = json.load(f)
    
    total_cost_usd = 0.0
    for src in dispatch_df.columns:
        if src in costs and src != 'unserved_mw':
            energy_mwh = dispatch_df[src].sum()  # MW * 1h = MWh
            var_cost = costs[src]['variable_cost_usd_per_mwh']
            total_cost_usd += energy_mwh * var_cost
    
    return total_cost_usd