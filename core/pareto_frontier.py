"""Script to process ensemble results and find Pareto optimal points."""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def load_latest_results() -> pd.DataFrame:
    """Load the most recent ensemble results file."""
    data_dir = Path(".")  # Look in current directory
    ensemble_files = list(data_dir.glob("ensemble_results_raw_*.csv"))
    if not ensemble_files:
        raise FileNotFoundError("No ensemble results files found in current directory")
    
    # Get the most recent file
    latest_file = max(ensemble_files, key=lambda x: x.stat().st_mtime)
    print(f"Loading results from {latest_file}")
    
    return pd.read_csv(latest_file)

def find_pareto_optimal_points(group: pd.DataFrame) -> pd.DataFrame:
    """Find Pareto frontier points for a group of cases.
    
    When plotting LCOE against renewable percentage, the Pareto frontier is the set of points that cannot 
    be improved in one dimension without being worse in the other dimension.
    
    Algorithm:
    1. Find the minimum LCOE point
    2. For points with higher renewable percentage:
       - Remove point if there exists a point with higher renewables AND lower LCOE
    3. For points with lower renewable percentage:
       - Remove point if there exists a point with lower renewables AND lower LCOE
    """
    # Sort by renewable percentage
    group = group.sort_values('renewable_percentage')
    
    # Find the minimum LCOE point
    min_lcoe_idx = group['lcoe'].idxmin()
    min_lcoe_point = group.loc[min_lcoe_idx]
    min_lcoe_renewable_pct = min_lcoe_point['renewable_percentage']
    
    # Split into left and right of minimum
    left_points = group[group['renewable_percentage'] < min_lcoe_renewable_pct].copy()
    right_points = group[group['renewable_percentage'] > min_lcoe_renewable_pct].copy()
    
    # Process right points (increasing renewable percentage)
    pareto_right = []
    if not right_points.empty:
        for _, point in right_points.iterrows():
            # Only add point if it has lower LCOE than all points with higher renewables
            higher_renewable_points = right_points[right_points['renewable_percentage'] > point['renewable_percentage']]
            if higher_renewable_points.empty or point['lcoe'] <= higher_renewable_points['lcoe'].min():
                # Additional check for first point: must be higher than minimum LCOE
                if len(pareto_right) == 0 and point['lcoe'] <= min_lcoe_point['lcoe']:
                    continue
                pareto_right.append(point)
    
    # Process left points (decreasing renewable percentage)
    pareto_left = []
    if not left_points.empty:
        for _, point in left_points.iloc[::-1].iterrows():  # Reverse order
            # Only add point if it has lower LCOE than all points with lower renewables
            lower_renewable_points = left_points[left_points['renewable_percentage'] < point['renewable_percentage']]
            if lower_renewable_points.empty or point['lcoe'] <= lower_renewable_points['lcoe'].min():
                # Additional check for first point: must be higher than minimum LCOE
                if len(pareto_left) == 0 and point['lcoe'] <= min_lcoe_point['lcoe']:
                    continue
                pareto_left.append(point)
    
    # Convert lists to DataFrames
    pareto_left_df = pd.DataFrame(pareto_left) if pareto_left else pd.DataFrame()
    pareto_right_df = pd.DataFrame(pareto_right) if pareto_right else pd.DataFrame()
    min_lcoe_df = pd.DataFrame([min_lcoe_point])
    
    # Combine all Pareto optimal points using concat
    pareto_points = pd.concat(
        [pareto_left_df, min_lcoe_df, pareto_right_df],
        ignore_index=True
    )
    
    # Sort by renewable percentage for final output
    pareto_points = pareto_points.sort_values('renewable_percentage')
    
    return pareto_points

def process_ensemble_data(results: List[Dict[str, Any]]) -> pd.DataFrame:
    """Process ensemble data to find Pareto optimal points.
    
    Args:
        results: List of dictionaries containing simulation results
        
    Returns:
        DataFrame containing Pareto optimal points
    """
    # Convert results to DataFrame if not already
    if isinstance(results, list):
        df = pd.DataFrame(results)
    else:
        df = results
        
    # Remove any failed calculations
    df = df[df['status'] == 'success'].copy()
    
    # Find Pareto optimal points
    pareto_points = find_pareto_optimal_points(df)
    
    # Print summary
    logger.info("\nProcessing Summary:")
    logger.info(f"Original points: {len(df)}")
    logger.info(f"Pareto optimal points: {len(pareto_points)}")
    logger.info(f"LCOE range: ${pareto_points['lcoe'].min():.2f}/MWh to ${pareto_points['lcoe'].max():.2f}/MWh")
    logger.info(f"Renewable % range: {pareto_points['renewable_percentage'].min():.1f}% to {pareto_points['renewable_percentage'].max():.1f}%")
    
    return pareto_points

def main():
    # Load the data
    df = load_latest_results()
    
    # Process the data
    pareto_points = process_ensemble_data(df)
    
    # Print overall summary
    logger.info("\nOverall Summary:")
    logger.info(f"Original configurations: {len(df)}")
    logger.info(f"Pareto optimal configurations: {len(pareto_points)}")
    logger.info(f"Reduction: {(1 - len(pareto_points)/len(df))*100:.1f}%")

if __name__ == "__main__":
    main() 