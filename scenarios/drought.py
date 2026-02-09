"""
scenarios/drought.py

Applies reduced hydro availability due to drought conditions.
Multiplies hydro capacity by a severity factor.
"""

import pandas as pd
from grid.dispatch import merit_order_dispatch


def apply_drought(
    demand_profile,
    severity='moderate',
    include_nuclear=True
):
    """
    Simulate dispatch under drought conditions (reduced hydro output).
    
    Parameters:
    -----------
    demand_profile : list or np.array
        Hourly demand values (MW)
        
    severity : str
        One of: 'mild', 'moderate', 'severe'
        (affects hydro capacity multiplier)
        
    include_nuclear : bool
        Whether to include nuclear baseload in the dispatch
        
    Returns:
    --------
    pd.DataFrame
        Dispatch results with columns for each source + 'unserved_mw'
    """
    severity_factors = {
        'mild':     0.85,     # ~15% reduction
        'moderate': 0.65,     # ~35% reduction
        'severe':   0.40,     # ~60% reduction
        'extreme':  0.20      # optional extra level
    }
    
    if severity not in severity_factors:
        raise ValueError(
            f"Invalid drought severity '{severity}'. "
            f"Choose from: {list(severity_factors.keys())}"
        )
    
    hydro_reduction_factor = severity_factors[severity]
    
    # Run dispatch with modified hydro capacity
    dispatch_df = merit_order_dispatch(
        demand_profile=demand_profile,
        include_nuclear=include_nuclear,
        drought_factor=hydro_reduction_factor
    )
    
    # Add metadata column for easier filtering/visualization
    dispatch_df['drought_severity'] = severity
    dispatch_df['hydro_capacity_factor'] = hydro_reduction_factor
    
    return dispatch_df