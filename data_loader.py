import pandas as pd
from typing import Dict, List

from defaults import SIMULATION_DATA_PATH

def load_simulation_data(file_path: str) -> pd.DataFrame:
    """Load and preprocess simulation data from CSV file."""
    # Define numeric columns
    numeric_cols = [
        'Solar Capacity (MW-DC)',
        'BESS Capacity (MW-AC)',
        'BESS Energy (MWh)',
        'Generator Capacity (MW-AC)',
        'Solar Output - Raw (MWh)',
        'Solar Output - Net (MWh)',
        'BESS charged (MWh)',
        'BESS discharged (MWh)',
        'Generator Output (MWh)',
        'Load Served (MWh)'
    ]
    
    try:
        df = pd.read_csv(
            file_path,
            thousands=',',  # Handle comma-separated numbers
        )
    except FileNotFoundError:
        raise FileNotFoundError(f"Simulation data file not found. Please ensure {file_path} is present.")
        
    # Convert numeric columns to float
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def get_unique_values() -> Dict[str, List[str]]:
    """Get unique values for dropdowns."""
    df = load_simulation_data(SIMULATION_DATA_PATH)
    locations = sorted(df['Location'].unique())
    solar_capacities = sorted([int(x) for x in df['Solar Capacity (MW-DC)'].unique() if not pd.isna(x)])
    bess_capacities = sorted([int(x) for x in df['BESS Capacity (MW-AC)'].unique() if not pd.isna(x)])
    generator_capacities = sorted([int(x) for x in df['Generator Capacity (MW-AC)'].unique() if not pd.isna(x)])
    
    return {
        'locations': locations,
        'solar_capacities': solar_capacities,
        'bess_capacities': bess_capacities,
        'generator_capacities': generator_capacities
    } 