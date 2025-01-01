#!/usr/bin/env python3
"""Command line wrapper for LCOE calculation."""

import argparse
from calculations import DataCenter

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Calculate LCOE for a datacenter configuration')
    
    # Required arguments
    parser.add_argument('--location', required=True, help='Location of the datacenter')
    parser.add_argument('--solar', type=int, required=True, dest='solar_pv_capacity_mw',
                       help='Solar PV capacity in MW')
    parser.add_argument('--bess', type=int, required=True, dest='bess_max_power_mw',
                       help='BESS power capacity in MW')
    parser.add_argument('--generator', type=int, required=True, dest='generator_capacity_mw',
                       help='Generator capacity in MW')
    
    # Optional arguments (all parameter names match DataCenter class)
    parser.add_argument('--generator-type', choices=['Gas Engine', 'Gas Turbine'],
                       help='Type of generator')
    parser.add_argument('--datacenter-load-mw', type=int,
                       help='Datacenter load in MW')
    parser.add_argument('--bess-hrs-storage', type=int,
                       help='BESS hours of storage')
    parser.add_argument('--solar-capex-total-dollar-per-w', type=float,
                       help='Solar CAPEX in $/W')
    parser.add_argument('--bess-capex-total-dollar-per-kwh', type=float,
                       help='BESS CAPEX in $/kWh')
    parser.add_argument('--generator-capex-total-dollar-per-kw', type=float,
                       help='Generator CAPEX in $/kW')
    parser.add_argument('--system-integration-capex-total-dollar-per-kw', type=float,
                       help='System integration CAPEX in $/kW')
    parser.add_argument('--soft-costs-capex-total-pct', type=float,
                       help='Soft costs CAPEX as percentage')
    parser.add_argument('--fuel-price-dollar-per-mmbtu', type=float,
                       help='Fuel price in $/MMBtu')
    parser.add_argument('--fuel-escalator-pct', type=float,
                       help='Fuel price escalator in % per year')
    parser.add_argument('--om-solar-fixed-dollar-per-kw', type=float,
                       help='Solar fixed O&M in $/kW')
    parser.add_argument('--om-bess-fixed-dollar-per-kw', type=float,
                       help='BESS fixed O&M in $/kW')
    parser.add_argument('--om-generator-fixed-dollar-per-kw', type=float,
                       help='Generator fixed O&M in $/kW')
    parser.add_argument('--om-generator-variable-dollar-per-kwh', type=float,
                       help='Generator variable O&M in $/kWh')
    parser.add_argument('--om-bos-fixed-dollar-per-kw-load', type=float,
                       help='Balance of system fixed O&M in $/kW-load')
    parser.add_argument('--om-soft-pct', type=float,
                       help='Soft O&M as percentage of hard costs')
    parser.add_argument('--om-escalator-pct', type=float,
                       help='O&M escalator in % per year')
    parser.add_argument('--investment-tax-credit-pct', type=float,
                       help='Investment tax credit percentage')
    parser.add_argument('--cost-of-debt-pct', type=float,
                       help='Cost of debt percentage')
    parser.add_argument('--leverage-pct', type=float,
                       help='Debt leverage percentage')
    parser.add_argument('--debt-term-years', type=int,
                       help='Debt term in years')
    parser.add_argument('--cost-of-equity-pct', type=float,
                       help='Cost of equity percentage')
    parser.add_argument('--combined-tax-rate-pct', type=float,
                       help='Combined tax rate percentage')
    parser.add_argument('--construction-time-years', type=int,
                       help='Construction time in years')
    parser.add_argument('--depreciation-schedule', type=float, nargs='+',
                       help='Depreciation schedule (space-separated list of percentages)')
    
    return vars(parser.parse_args())


if __name__ == '__main__':
    args = parse_args()
    
    # Remove None values from args
    kwargs = {k: v for k, v in args.items() if v is not None}
    
    # Create DataCenter instance and calculate LCOE
    data_center = DataCenter(**kwargs)
    lcoe, proforma = data_center.calculate_lcoe()
    
    print(f"\nResults for {kwargs['location']} for {kwargs['solar_pv_capacity_mw']}MW solar | {kwargs['bess_max_power_mw']}MW BESS | {kwargs['generator_capacity_mw']}MW generator")
    print(f"LCOE: ${lcoe:.2f}/MWh")
