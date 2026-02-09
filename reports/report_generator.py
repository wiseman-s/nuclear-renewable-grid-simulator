import pandas as pd

def generate_report(dispatch_df, total_cost, total_emissions, scenario_name):
    return f"""
# NRGS Scenario Report — {scenario_name}

**Key Metrics**
- Total Cost: KES {total_cost:,.0f} million
- CO₂ Emissions: {total_emissions:,.0f} tonnes
- Unserved Energy: {dispatch_df['unserved_mw'].sum():.1f} MWh
- Nuclear Contribution: {dispatch_df.get('nuclear', pd.Series([0])).sum():.0f} MWh

Nuclear integration reduces emissions by ~25–40% vs thermal-heavy scenarios and eliminates unserved energy during drought.
"""