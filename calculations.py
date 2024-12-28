"""Module for financial calculations and proforma generation."""

import pandas as pd
from typing import Dict, Optional, Union, Tuple

def calculate_pro_forma(
    simulation_data: pd.DataFrame,
    location: str,
    datacenter_load_mw: Union[int, float],
    solar_pv_capacity_mw: Union[int, float],
    bess_max_power_mw: Union[int, float],
    natural_gas_capacity_mw: Union[int, float],
    generator_type: str,
    # CapEx inputs (in millions)
    solar_capex: float,
    bess_capex: float,
    generator_capex: float,
    system_integration_capex: float,
    soft_costs_capex: float,
    # O&M and other inputs
    generator_om_fixed_dollar_per_kw: float,
    generator_om_variable_dollar_per_kwh: float,
    fuel_price_dollar_per_mmbtu: float,
    fuel_escalator_pct: float,
    solar_om_fixed_dollar_per_kw: float,
    bess_om_fixed_dollar_per_kw: float,
    bos_om_fixed_dollar_per_kw_load: float,
    soft_om_pct: float,
    om_escalator_pct: float,
    lcoe_dollar_per_mwh: float,
    cost_of_debt_pct: float = 7.5,
    leverage_pct: float = 70.0,
    debt_term_years: int = 20,
    cost_of_equity_pct: float = 11.0,
    investment_tax_credit_pct: float = 30.0,
    combined_tax_rate_pct: float = 21.0,
    construction_time_years: int = 2
) -> Optional[pd.DataFrame]:
    """
    Calculate the proforma financial model for a solar datacenter project.
    
    Args:
        simulation_data (pd.DataFrame): Powerflow simulation runs in the format of `powerflow_output_frozen.csv`
        location (str): Project location
        solar_pv_capacity_MW (Union[int, float]): Solar PV capacity in MW-DC
        bess_max_power_MW (Union[int, float]): Battery storage power capacity in MW
        natural_gas_capacity_MW (Union[int, float]): Natural gas generator capacity in MW
        generator_type (str): Type of generator ('Gas Engine', 'Gas Turbine', or 'Diesel Generator')
        generator_om_fixed_dollar_per_kW (float): Fixed O&M cost for generator in $/kW
        generator_om_variable_dollar_per_MWh (float): Variable O&M cost for generator in $/MWh
        fuel_price_dollar_per_MMBtu (float): Fuel price in $/MMBtu
        fuel_escalator_pct (float): Annual fuel price escalation rate in %
        solar_om_fixed_dollar_per_kW (float): Fixed O&M cost for solar in $/kW
        bess_om_fixed_dollar_per_kW (float): Fixed O&M cost for battery in $/kW
        bos_om_fixed_dollar_per_kW_load (float): Fixed O&M cost for BOS in $/kW-load
        soft_om_pct (float): Soft O&M cost as a percentage of total CAPEX. Note: this is specified 
            as a percentage, ie a value of 100 means 100% of total CAPEX.
        om_escalator_pct (float): Annual O&M cost escalation rate in %
        cost_of_debt_pct (float, optional): Cost of debt in %. Defaults to 7.5.
        leverage_pct (float, optional): Project leverage in %. Defaults to 70.0.
        debt_term_years (int, optional): Debt term in years. Defaults to 20.
        cost_of_equity_pct (float, optional): Cost of equity in %. Defaults to 11.0.
        investment_tax_credit_pct (float, optional): Investment tax credit in %. Defaults to 30.0.
        combined_tax_rate_pct (float, optional): Combined tax rate in %. Defaults to 21.0.
        construction_time_years (int, optional): Construction time in years. Defaults to 2.
    
    Returns:
        Optional[pd.DataFrame]: Proforma financial model with years as index and metrics as columns.
                              Returns None if no matching simulation data is found.
    """
    # Create System Spec string for filtering
    system_spec = f"{solar_pv_capacity_mw}MW | {bess_max_power_mw}MW | {natural_gas_capacity_mw}MW"
    
    # Filter simulation data based on inputs
    filtered_data = simulation_data[
        (simulation_data['Location'].str.strip() == location) &
        (simulation_data['System Spec'] == system_spec)
    ]
    
    if filtered_data.empty:
        return None
    
    # Create years index (-1 to 20)
    years = list(range(-1, 21))
    proforma = pd.DataFrame(index=years)
    proforma.index.name = 'Year'
    
    # Fill in operating metrics from simulation data
    operating_years = filtered_data['Operating Year'].unique()
    for year in range(21):  # Extended to 20 years
        if year in operating_years:
            year_data = filtered_data[filtered_data['Operating Year'] == year].iloc[0]
            proforma.loc[year, 'Operating Year'] = year
            proforma.loc[year, 'Solar Output - Raw (MWh)'] = year_data['Solar Output - Raw (MWh)']
            proforma.loc[year, 'Solar Output - Net (MWh)'] = year_data['Solar Output - Net (MWh)']
            proforma.loc[year, 'BESS Throughput (MWh)'] = year_data['BESS Throughput (MWh)']
            proforma.loc[year, 'BESS Net Output (MWh)'] = year_data['BESS Net Output (MWh)']
            proforma.loc[year, 'Generator Output (MWh)'] = year_data['Generator Output (MWh)']
            proforma.loc[year, 'Generator Fuel Input (MMBtu)'] = year_data['Generator Fuel Input (MMBtu)']
            proforma.loc[year, 'Load Served (MWh)'] = year_data['Load Served (MWh)']
    
    # Fill in operating rates (these don't change with year except for escalation)
    for year in years:
        if year > 0:  # Only calculate for operating years (after year 0)
            om_escalation = (1 + om_escalator_pct/100)**(year-1)  # Start from year 1
            fuel_escalation = (1 + fuel_escalator_pct/100)**(year-1)
            
            # Unit rates
            proforma.loc[year, 'Fuel Unit Cost'] = -1.0 * fuel_price_dollar_per_mmbtu * fuel_escalation
            proforma.loc[year, 'Solar Fixed O&M Rate'] = -1.0 * solar_om_fixed_dollar_per_kw * om_escalation
            proforma.loc[year, 'Battery Fixed O&M Rate'] = -1.0 * bess_om_fixed_dollar_per_kw * om_escalation
            proforma.loc[year, 'Generator Fixed O&M Rate'] = -1.0 * generator_om_fixed_dollar_per_kw * om_escalation
            proforma.loc[year, 'Generator Variable O&M Rate'] = -1.0 * generator_om_variable_dollar_per_kwh * om_escalation
            proforma.loc[year, 'BOS Fixed O&M Rate'] = -1.0 * bos_om_fixed_dollar_per_kw_load * om_escalation
            proforma.loc[year, 'Soft O&M Rate'] = -1.0 * (soft_om_pct) * om_escalation
            
            # Calculate total CAPEX for Fixed O&M calculation
            total_capex = solar_capex + bess_capex + generator_capex + system_integration_capex + soft_costs_capex
            
            # Calculate Fixed O&M Cost
            # Fixed O&M Cost = (Solar O&M + BESS O&M + Generator O&M + BOS O&M) + Soft O&M pct * Total CAPEX
            # proforma.loc[year, 'Fixed O&M Cost'] = (
            #     proforma.loc[year, 'Solar Fixed O&M Rate'] * solar_pv_capacity_mw * 1000 +
            #     proforma.loc[year, 'Battery Fixed O&M Rate'] * bess_max_power_mw * 1000 +
            #     proforma.loc[year, 'Generator Fixed O&M Rate'] * natural_gas_capacity_mw * 1000 +
            #     proforma.loc[year, 'BOS Fixed O&M Rate'] * datacenter_load_mw * 1000 +
            #     (proforma.loc[year, 'Soft O&M Rate'] / 100) * total_capex
            # ) / 1_000_000
            proforma.loc[year, 'Fixed O&M Cost'] = total_capex

            
            # Calculate Fuel Cost
            proforma.loc[year, 'Fuel Cost'] = (proforma.loc[year, 'Fuel Unit Cost'] * 
                                             proforma.loc[year, 'Generator Fuel Input (MMBtu)']) / 1_000_000
            
            # Calculate Variable O&M Cost
            proforma.loc[year, 'Variable O&M Cost'] = (proforma.loc[year, 'Generator Variable O&M Rate'] * 
                                                     proforma.loc[year, 'Generator Output (MWh)'] * 1000) / 1_000_000  # Convert MWh to kWh
            
            # Calculate total operating costs
            proforma.loc[year, 'Total Operating Costs'] = (
                proforma.loc[year, 'Fuel Cost'] +
                proforma.loc[year, 'Fixed O&M Cost'] +
                proforma.loc[year, 'Variable O&M Cost']
            )
            
            # Set LCOE from input
            proforma.loc[year, 'LCOE'] = lcoe_dollar_per_mwh
            
            # Calculate Revenue (LCOE * Load Served)
            proforma.loc[year, 'Revenue'] = (lcoe_dollar_per_mwh * 
                                           proforma.loc[year, 'Load Served (MWh)']) / 1_000_000  # Convert to millions
            
            # Calculate EBITDA (Revenue - Total Operating Costs)
            proforma.loc[year, 'EBITDA'] = (proforma.loc[year, 'Revenue'] + 
                                          proforma.loc[year, 'Total Operating Costs'])  # Total Operating Costs is already negative
    
    # Format numbers
    proforma = proforma.round(2)
    
    return proforma 