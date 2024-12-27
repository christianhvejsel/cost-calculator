import numpy as np

def calculate_wacc(cost_of_debt, cost_of_equity, leverage, tax_rate):
    """Calculate the Weighted Average Cost of Capital"""
    debt_ratio = leverage / 100
    equity_ratio = 1 - debt_ratio
    wacc = (cost_of_debt/100 * debt_ratio * (1 - tax_rate/100)) + (cost_of_equity/100 * equity_ratio)
    return wacc

def calculate_capex(solar_capacity, bess_capacity, config):
    """Calculate total capital expenditure"""
    # Solar CAPEX
    solar_capex = solar_capacity * 1e6 * sum([
        config['modules'],
        config['inverters'],
        config['racking'],
        config['balance_system'],
        config['labor']
    ])
    
    # BESS CAPEX
    bess_capex = bess_capacity * 1e3 * sum([
        config['bess_units'],
        config['bess_bos'],
        config['bess_labor']
    ])
    
    return solar_capex + bess_capex

def calculate_annual_opex(solar_capacity, bess_capacity, config):
    """Calculate annual operating expenses"""
    solar_opex = solar_capacity * config['solar_om_fixed']
    bess_opex = bess_capacity * config['bess_om_fixed']
    return solar_opex + bess_opex

def calculate_lcoe(params):
    """
    Calculate Levelized Cost of Energy
    
    params: dictionary containing all necessary parameters
    """
    # Calculate WACC
    wacc = calculate_wacc(
        params['cost_of_debt'],
        params['cost_of_equity'],
        params['leverage'],
        params['combined_tax_rate']
    )
    
    # Calculate total CAPEX
    total_capex = calculate_capex(
        params['solar_pv_capacity'],
        params['bess_max_power'],
        params
    )
    
    # Apply ITC
    capex_after_itc = total_capex * (1 - params['investment_tax_credit']/100)
    
    # Calculate annual OPEX
    annual_opex = calculate_annual_opex(
        params['solar_pv_capacity'],
        params['bess_max_power'],
        params
    )
    
    # Assume 25-year project lifetime
    n_years = 25
    
    # Calculate annual energy production (simplified)
    # Assuming 20% capacity factor for solar
    annual_energy = params['solar_pv_capacity'] * 8760 * 0.20  # MWh
    
    # Calculate present value of costs
    pv_costs = capex_after_itc
    for year in range(n_years):
        opex_escalated = annual_opex * (1 + params['om_escalator']/100)**year
        pv_costs += opex_escalated / (1 + wacc)**(year + 1)
    
    # Calculate present value of energy
    pv_energy = 0
    for year in range(n_years):
        pv_energy += annual_energy / (1 + wacc)**(year + 1)
    
    # Calculate LCOE
    lcoe = pv_costs / pv_energy
    
    return lcoe 