import pandas as pd

def load_simulation_data():
    """Load and preprocess simulation data from CSV file."""
    # Define numeric columns
    numeric_cols = [
        'Solar Capacity (MW-DC)',
        'BESS Capacity (MW-AC)',
        'BESS Energy (MWh)',
        'Generator Capacity (MW-AC)',
        'Solar Output - Raw (MWh)',
        'Solar Output - Net (MWh)',
        'BESS Throughput (MWh)',
        'BESS Net Output (MWh)',
        'Generator Output (MWh)',
        'Generator Fuel Input (MMBtu)',
        'Load Served (MWh)'
    ]
    
    try:
        df = pd.read_csv(
            "powerflow_output_frozen.csv",
            thousands=',',  # Handle comma-separated numbers
        )
    except FileNotFoundError:
        raise FileNotFoundError("Simulation data file not found. Please ensure 'powerflow_output_frozen.csv' is in the same directory.")
        
    # Convert numeric columns to float
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def get_unique_values(df):
    """Get unique values for dropdowns."""
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