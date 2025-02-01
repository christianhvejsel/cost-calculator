"""Script to run LCOE test cases."""

import pandas as pd
from datetime import datetime
import time
from pathlib import Path

from lcoe_calculations import DataCenter

# Input/Output file paths
INPUT_CSV_PATH = Path('data/test_cases_all.csv')
OUTPUT_CSV_PATH = Path('data/test_cases_all_results.csv')

def run_test_case(case_data: pd.Series) -> float:
    """Run a single test case and return the LCOE."""
    # Convert capacity strings to floats by removing 'MW' suffix
    def parse_mw(value):
        if pd.isna(value):
            return 0
        if isinstance(value, str):
            return float(value.replace('MW', '').strip())
        return float(value)
    
    # Parse capacities
    solar_mw = parse_mw(case_data.iloc[4])
    bess_mw = parse_mw(case_data.iloc[5])
    gen_mw = parse_mw(case_data.iloc[6])
    
    # Print system spec
    print(f"Location: {case_data.iloc[3]}")
    print(f"System Spec: {int(solar_mw)}MW | {int(bess_mw)}MW | {int(gen_mw)}MW")
    
    data_center = DataCenter(
        location=case_data.iloc[3],
        solar_pv_capacity_mw=solar_mw,
        bess_max_power_mw=bess_mw,
        generator_capacity_mw=gen_mw,
        generator_type='Gas Engine' if case_data.iloc[7] == 'GEN' else 'Gas Turbine'
    )
    
    # Calculate LCOE
    lcoe, _ = data_center.calculate_lcoe()
    return lcoe

def main():
    """Run all test cases."""
    # Load test cases
    test_cases = pd.read_csv(INPUT_CSV_PATH, header=None)
    
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create rows for timestamp and LCOE results
    timestamp_row = pd.Series(['Run Timestamp', '', '', timestamp] + [''] * (len(test_cases.columns) - 4), index=test_cases.columns)
    lcoe_row = pd.Series(['LCOE ($/MWh)', '', ''] + [''] * (len(test_cases.columns) - 3), index=test_cases.columns)
    
    # Run each test case
    for case_num in range(1, len(test_cases.columns) - 3):  # Skip first 3 columns
        print(f"Running case {case_num}...")
        try:
            start_time = time.time()
            case_data = test_cases.iloc[:, case_num + 2]  # +2 to skip first 3 columns
            lcoe = run_test_case(case_data)
            calculation_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            lcoe_row.iloc[case_num + 3] = f"{lcoe:.2f}"
            print(f"Case {case_num} complete: LCOE = ${lcoe:.2f}/MWh ({calculation_time:.0f} ms)")
        except Exception as e:
            print(f"Error running case {case_num}: {str(e)}")
            lcoe_row.iloc[case_num + 3] = 'ERROR'
    
    # Append timestamp and results to the original CSV
    test_cases = pd.concat([test_cases, pd.DataFrame([timestamp_row, lcoe_row])], ignore_index=True)
    test_cases.to_csv(OUTPUT_CSV_PATH, index=False, header=False)
    print(f"\nAll cases complete. Results appended to {OUTPUT_CSV_PATH}")

if __name__ == "__main__":
    main() 