"""Module for financial calculations and proforma generation."""

import pandas as pd
from typing import Dict, Optional, Union, Tuple

_BESS_HRS_STORAGE = 4


def calculate_capex(
    solar_pv_capacity_mw: float,
    bess_max_power_mw: float,
    natural_gas_capacity_mw: float,
    datacenter_load_mw: float,
    # Solar PV costs ($/W)
    pv_modules: float = 0.220,
    pv_inverters: float = 0.050,
    pv_racking: float = 0.180,
    pv_balance_system: float = 0.120,
    pv_labor: float = 0.200,
    # BESS costs ($/kWh)
    bess_units: float = 200.0,
    bess_balance_of_system: float = 40.0,
    bess_labor: float = 20.0,
    # Generator costs ($/kW )
    gen_gensets: float = 800.0,
    gen_balance_of_system: float = 200.0,
    gen_labor: float = 150.0,
    # System Integration costs ($/kW)
    si_microgrid: float = 300.0,
    si_controls: float = 50.0,
    si_labor: float = 60.0,
    # Soft Costs (percentages)
    soft_costs_general_conditions: float = 0.50,
    soft_costs_epc_overhead: float = 5.00,
    soft_costs_design_engineering: float = 0.50,
    soft_costs_permitting: float = 0.05,
    soft_costs_startup: float = 0.25,
    soft_costs_insurance: float = 0.50,
    soft_costs_taxes: float = 5.00
) -> Dict[str, float]:
    """Calculate CAPEX for each system component."""
    
    # Calculate Solar CAPEX
    solar_capex = solar_pv_capacity_mw * 1_000_000 * (
        pv_modules + pv_inverters + pv_racking + pv_balance_system + pv_labor
    )
    
    # Calculate BESS CAPEX
    bess_system_mwh = bess_max_power_mw * _BESS_HRS_STORAGE
    bess_capex = bess_system_mwh * 1000 * (
        bess_units + bess_balance_of_system + bess_labor
    )
    
    # Calculate Generator CAPEX
    generator_capex = natural_gas_capacity_mw * 1000 * (
        gen_gensets + gen_balance_of_system + gen_labor
    )
    
    # Calculate System Integration CAPEX
    system_integration_capex = datacenter_load_mw * 1000 * (
        si_microgrid + si_controls + si_labor
    )
    
    # Calculate total hard costs
    total_hard_costs = (
        solar_capex +
        bess_capex +
        generator_capex +
        system_integration_capex
    )
    
    # Calculate soft costs
    soft_costs = total_hard_costs * (
        soft_costs_general_conditions/100 +
        soft_costs_epc_overhead/100 +
        soft_costs_design_engineering/100 +
        soft_costs_permitting/100 +
        soft_costs_startup/100 +
        soft_costs_insurance/100 +
        soft_costs_taxes/100
    )
    
    return {
        'solar': solar_capex / 1_000_000,  # Convert to millions
        'bess': bess_capex / 1_000_000,
        'generator': generator_capex / 1_000_000,
        'system_integration': system_integration_capex / 1_000_000,
        'soft_costs': soft_costs / 1_000_000
    }

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
    depreciation_schedule: pd.DataFrame,
    investment_tax_credit_pct: float,
    cost_of_debt_pct: float = 7.5,
    leverage_pct: float = 70.0,
    debt_term_years: int = 20,
    cost_of_equity_pct: float = 11.0,
    combined_tax_rate_pct: float = 21.0,
    construction_time_years: int = 2,
) -> Optional[pd.DataFrame]:
    """
    Calculate the proforma financial model for a solar datacenter project.
    
    Args:
        simulation_data (pd.DataFrame): Pre-filtered powerflow simulation data
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
        depreciation_schedule (pd.DataFrame): Depreciation schedule
    
    Returns:
        Optional[pd.DataFrame]: Proforma financial model with years as index and metrics as columns.
                              Returns None if no matching simulation data is found.
    """
    if simulation_data.empty:
        return None
    
    # Create years index (-1 to 20)
    years = list(range(-1, 21))
    proforma = pd.DataFrame(index=years)
    proforma.index.name = 'Year'
    
    # Fill in operating metrics from simulation data
    operating_years = simulation_data['Operating Year'].unique()
    for year in operating_years:
        year_data = simulation_data[simulation_data['Operating Year'] == year].iloc[0]
        proforma.loc[year, 'Operating Year'] = year
        proforma.loc[year, 'Solar Output - Raw (MWh)'] = year_data['Solar Output - Raw (MWh)']
        proforma.loc[year, 'Solar Output - Net (MWh)'] = year_data['Solar Output - Net (MWh)']
        proforma.loc[year, 'BESS Throughput (MWh)'] = year_data['BESS Throughput (MWh)']
        proforma.loc[year, 'BESS Net Output (MWh)'] = year_data['BESS Net Output (MWh)']
        proforma.loc[year, 'Generator Output (MWh)'] = year_data['Generator Output (MWh)']
        proforma.loc[year, 'Generator Fuel Input (MMBtu)'] = year_data['Generator Fuel Input (MMBtu)']
        proforma.loc[year, 'Load Served (MWh)'] = year_data['Load Served (MWh)']
    
    # Calculate debt service
    total_capex = solar_capex + bess_capex + generator_capex + system_integration_capex + soft_costs_capex
    total_debt = total_capex * (leverage_pct / 100)
    interest_rate = cost_of_debt_pct / 100
    
    # Calculate fixed debt service payment
    # PMT = PV * r * (1 + r)^n / ((1 + r)^n - 1)
    fixed_payment = total_debt * interest_rate * (1 + interest_rate)**debt_term_years / ((1 + interest_rate)**debt_term_years - 1)
    
    # Initialize debt values for year 1
    proforma.loc[1, 'Debt Outstanding, Yr Start'] = total_debt
    
    # Calculate debt service for each year
    for year in range(1, debt_term_years + 1):
        # Interest expense is rate * start of period balance
        proforma.loc[year, 'Interest Expense'] = -1.0 * proforma.loc[year, 'Debt Outstanding, Yr Start'] * interest_rate
        
        # Total debt service is the fixed payment
        proforma.loc[year, 'Debt Service'] = -1.0 * fixed_payment
        
        # Principal is the difference between total payment and interest
        proforma.loc[year, 'Principal Payment'] = proforma.loc[year, 'Debt Service'] - proforma.loc[year, 'Interest Expense']
        
        if year < debt_term_years:
            # Update debt for next year
            proforma.loc[year+1, 'Debt Outstanding, Yr Start'] = proforma.loc[year, 'Debt Outstanding, Yr Start'] + proforma.loc[year, 'Principal Payment']
    
    # Fill in operating rates and calculate EBITDA first
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
            
            # Calculate hard CAPEX (total excl. soft costs) for Fixed O&M calculation
            total_hard_capex = solar_capex + bess_capex + generator_capex + system_integration_capex

            hard_capex_om_totals = (
                proforma.loc[year, 'Solar Fixed O&M Rate'] * solar_pv_capacity_mw * 1000 +
                proforma.loc[year, 'Battery Fixed O&M Rate'] * bess_max_power_mw * 1000 +
                proforma.loc[year, 'Generator Fixed O&M Rate'] * natural_gas_capacity_mw * 1000 +
                proforma.loc[year, 'BOS Fixed O&M Rate'] * datacenter_load_mw * 1000
            ) / 1_000_000
      
            # Calculate Fixed O&M Cost
            proforma.loc[year, 'Fixed O&M Cost'] = hard_capex_om_totals + (proforma.loc[year, 'Soft O&M Rate'] / 100) * total_hard_capex
            
            # Calculate Fuel Cost
            proforma.loc[year, 'Fuel Cost'] = (proforma.loc[year, 'Fuel Unit Cost'] * 
                                           proforma.loc[year, 'Generator Fuel Input (MMBtu)']) / 1_000_000
            
            # Calculate Variable O&M Cost
            proforma.loc[year, 'Variable O&M Cost'] = (proforma.loc[year, 'Generator Variable O&M Rate'] * 
                                                   proforma.loc[year, 'Generator Output (MWh)'] * 1000) / 1_000_000
            
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
                                         proforma.loc[year, 'Load Served (MWh)']) / 1_000_000
            
            # Calculate EBITDA (Revenue - Total Operating Costs)
            proforma.loc[year, 'EBITDA'] = (proforma.loc[year, 'Revenue'] + 
                                        proforma.loc[year, 'Total Operating Costs'])  # Total Operating Costs is already negative

    # Now calculate tax items after EBITDA is populated
    # First, calculate the renewable portion of CAPEX (solar + BESS)
    renewable_capex = solar_capex + bess_capex
    total_capex = solar_capex + bess_capex + generator_capex + system_integration_capex + soft_costs_capex

    # Calculate Federal Investment Tax Credit amount
    # ITC applicability on soft costs is the same as the proportion of hard capex that's renewable.
    renewable_proportion_of_hard_capex = renewable_capex / total_hard_capex
    tax_credit_amount = total_capex * renewable_proportion_of_hard_capex * (investment_tax_credit_pct / 100)
    proforma.loc[1, 'Federal ITC'] = tax_credit_amount

    # Calculate depreciation for each year
    for year in range(1, 21):  # 20-year depreciation schedule
        
        # Calculate depreciation amount
        proforma.loc[year, 'Depreciation Schedule'] = depreciation_schedule[year-1]
        # IRS rule: we have to reduce depreciable basis by half the tax credit amount
        amount_that_is_depreciable = total_capex - tax_credit_amount / 2
        proforma.loc[year, 'Depreciation (MACRS)'] = -1.0 * (depreciation_schedule[year-1] / 100) * amount_that_is_depreciable

    # Calculate taxable income and tax benefit/liability for each year
    tax_rate = combined_tax_rate_pct / 100
    for year in range(1, 21):
        if year in proforma.index:
            # Taxable income is EBITDA minus depreciation minus interest
            proforma.loc[year, 'Taxable Income'] = (
                proforma.loc[year, 'EBITDA'] + 
                proforma.loc[year, 'Depreciation (MACRS)'] + 
                proforma.loc[year, 'Interest Expense']
            )
            
            # Tax benefit/liability is taxable income times tax rate, plus ITC in year 1
            tax_on_income = proforma.loc[year, 'Taxable Income'] * tax_rate
            itc_benefit = proforma.loc[year, 'Federal ITC'] if year == 1 else 0
            proforma.loc[year, 'Tax Benefit (Liability)'] = -1.0 * tax_on_income + itc_benefit

    # Format numbers
    proforma = proforma.round(2)
    
    return proforma 