import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

def forecast_demand(days_ahead=7, annual_growth=0.05):
    df = pd.read_csv('data/kenya_load_profile.csv')
    base_load = df['load_mw'].values
    
    # Create features: hour, day-of-year, growth
    X = np.arange(len(base_load)).reshape(-1, 1)
    y = base_load
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    future_X = np.arange(len(base_load), len(base_load) + days_ahead * 24).reshape(-1, 1)
    forecast = model.predict(future_X)
    
    # Apply annual growth
    growth_factor = (1 + annual_growth) ** (future_X.flatten() / (365 * 24))
    forecast *= growth_factor
    
    return pd.DataFrame({
        'hour': range(len(forecast)),
        'forecast_mw': forecast.round(1)
    })