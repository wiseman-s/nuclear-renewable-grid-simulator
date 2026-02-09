# grid/dispatch.py

import json
import numpy as np
import pandas as pd

def load_sources():
    """Load generation source parameters from JSON"""
    try:
        with open('data/generation_costs.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("generation_costs.json not found in data/ folder")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON in generation_costs.json")

def merit_order_dispatch(demand_profile, include_nuclear=True, drought_factor=1.0, outage=False):
    """
    Simple merit-order economic dispatch (priority by variable cost)
    
    Parameters:
        demand_profile: array-like of hourly demand values (MW)
        include_nuclear: bool
        drought_factor: float [0–1] → multiplier on hydro capacity
        outage: bool → force nuclear offline
    
    Returns:
        pd.DataFrame with columns = sources + 'unserved_mw'
    """
    sources = load_sources()
    
    if not include_nuclear:
        sources.pop('nuclear', None)
    if outage:
        sources.pop('nuclear', None)
    
    # Apply drought to hydro
    if 'hydro' in sources:
        sources['hydro']['capacity_mw'] *= drought_factor
    
    # Sort sources by variable cost (lowest → highest)
    order = sorted(
        sources.keys(),
        key=lambda s: sources[s]['variable_cost_usd_per_mwh']
    )
    
    n_hours = len(demand_profile)
    dispatch = {src: np.zeros(n_hours) for src in sources}
    unserved = np.zeros(n_hours)
    
    for h in range(n_hours):
        remaining = demand_profile[h]
        
        for src in order:
            cap = sources[src]['capacity_mw']
            dispatched = min(remaining, cap)
            dispatch[src][h] = dispatched
            remaining -= dispatched
            if remaining <= 0:
                break
        
        unserved[h] = max(remaining, 0)
    
    df = pd.DataFrame(dispatch)
    df['unserved_mw'] = unserved
    return df