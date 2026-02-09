import pandas as pd
import numpy as np
from grid.dispatch import merit_order_dispatch


def simulate_outage(demand_profile, duration_hours=24, outage_start_hour=0, include_nuclear_before_after=True):
    """
    Simulate nuclear outage starting at outage_start_hour for duration_hours.
    """
    if not isinstance(demand_profile, (list, tuple, np.ndarray)):
        raise ValueError("demand_profile must be array-like")

    n_hours = len(demand_profile)

    before = demand_profile[:outage_start_hour]
    during = demand_profile[outage_start_hour:outage_start_hour + duration_hours]
    after  = demand_profile[outage_start_hour + duration_hours:]

    dispatch_parts = []

    if len(before) > 0:
        df_before = merit_order_dispatch(before, include_nuclear=include_nuclear_before_after)
        dispatch_parts.append(df_before)

    if len(during) > 0:
        df_during = merit_order_dispatch(during, include_nuclear=False)
        dispatch_parts.append(df_during)

    if len(after) > 0:
        df_after = merit_order_dispatch(after, include_nuclear=include_nuclear_before_after)
        dispatch_parts.append(df_after)

    if not dispatch_parts:
        raise ValueError("No data after splitting")

    full_dispatch = pd.concat(dispatch_parts, ignore_index=True)

    # Optional metadata (will be ignored in plotting thanks to numeric filter)
    outage_mask = [False] * n_hours
    for i in range(outage_start_hour, min(outage_start_hour + duration_hours, n_hours)):
        outage_mask[i] = True
    full_dispatch['outage_active'] = outage_mask

    return full_dispatch