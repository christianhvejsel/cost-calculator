"""Main Streamlit application for Solar Datacenter LCOE Calculator."""

import streamlit as st
import pandas as pd
from data_loader import load_simulation_data, get_unique_values
from calculations import calculate_pro_forma
from st_formatting import format_proforma, display_proforma
from charts import create_capacity_chart, create_capex_chart, create_energy_mix_chart
from typing import Dict

def init_data():
    """Initialize data and unique values."""
    try:
        df = load_simulation_data()
        return df, get_unique_values(df)
    except FileNotFoundError as e:
        st.error(str(e))
        st.stop()

def create_input_sections():
    """Create all input sections in the Streamlit app."""
    st.title("Solar Datacenter LCOE Calculator", anchor=False)
    
    # System Capacity Inputs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        datacenter_load = st.number_input("Data Center Demand (MW)", 
                                          value=100, 
                                          min_value=0,
                                          step=100,
                                          format="%d")
    with col2:
        solar_pv_capacity = st.selectbox(
            "Solar PV Capacity (MW-DC)",
            options=unique_values['solar_capacities']
        )
    with col3:
        bess_max_power = st.selectbox(
            "BESS Max Power (MW), 4h store",
            options=unique_values['bess_capacities']
        )
    with col4:
        natural_gas_capacity = st.selectbox(
            "Natural Gas Capacity (MW)",
            options=unique_values['generator_capacities']
        )
    
    # Display capacity chart
    st.plotly_chart(
        create_capacity_chart(datacenter_load, solar_pv_capacity, bess_max_power, natural_gas_capacity),
        use_container_width=True
    )
    
    # Non-megawatt configuration inputs
    col1, col2 = st.columns(2)
    with col1:
        location = st.selectbox("Location", options=unique_values['locations'])
    with col2:
        generator_type = st.selectbox("Generator Type", ["Gas Engine", "Gas Turbine", "Diesel Generator"], index=0)
    
    # Financial Inputs
    with st.expander("Financial Inputs"):
        col1, col2 = st.columns(2)
        with col1:
            lcoe = st.number_input("LCOE ($/MWh)", value=107.35, format="%.2f")
            cost_of_debt = st.number_input("Cost of Debt (%)", value=7.5, min_value=0.0, max_value=100.0)
            leverage = st.number_input("Leverage (%)", value=70.0, min_value=0.0, max_value=100.0)
            debt_term = st.number_input("Debt Term (years)", value=20, min_value=1)
        with col2:
            cost_of_equity = st.number_input("Cost of Equity (%)", value=11.0, min_value=0.0, max_value=100.0)
            investment_tax_credit = st.number_input("Investment Tax Credit (%)", value=30.0, min_value=0.0, max_value=100.0)
            combined_tax_rate = st.number_input("Combined Tax Rate (%)", value=21.0, min_value=0.0, max_value=100.0)
    
    # CAPEX Inputs
    with st.expander("CAPEX Inputs"):
        construction_time = st.number_input("Construction Time (years)", value=2, min_value=1)
        
        # Solar PV
        st.subheader("Solar PV")
        col1, col2 = st.columns(2)
        with col1:
            modules = st.number_input("Modules ($/W)", value=0.220, format="%.3f")
            inverters = st.number_input("Inverters ($/W)", value=0.050, format="%.3f")
            racking = st.number_input("Racking and Foundations ($/W)", value=0.180, format="%.3f")
        with col2:
            balance_system = st.number_input("Balance of System ($/W)", value=0.120, format="%.3f")
            labor = st.number_input("Labor ($/W)", value=0.200, format="%.3f")
    
        # BESS
        st.subheader("Battery Energy Storage System")
        col1, col2 = st.columns(2)
        with col1:
            bess_units = st.number_input("BESS Units ($/kWh)", value=200, format="%d")
            bess_bos = st.number_input("Balance of System ($/kWh)", value=40, format="%d")
        with col2:
            bess_labor = st.number_input("Labor ($/kWh)", value=20, format="%d")

        # Generators
        st.subheader("Generators")
        col1, col2 = st.columns(2)
        with col1:
            gensets = st.number_input("Gensets ($/kW)", value=800, format="%d")
            gen_bos = st.number_input("Balance of System ($/kW)", value=200, format="%d")
        with col2:
            gen_labor = st.number_input("Labor ($/kW)", value=150, format="%d")

        # System Integration
        st.subheader("System Integration")
        col1, col2 = st.columns(2)
        with col1:
            microgrid = st.number_input("Microgrid Switchgear, Transformers, etc. ($/kW)", value=300, format="%d")
            controls = st.number_input("Controls ($/kW)", value=50, format="%d")
        with col2:
            si_labor = st.number_input("System Integration Labor ($/kW)", value=60, format="%d")

        # Soft Costs
        st.subheader("Soft Costs (CAPEX)")
        col1, col2 = st.columns(2)
        with col1:
            general_conditions = st.number_input("General Conditions (%)", value=0.50, format="%.2f")
            epc_overhead = st.number_input("EPC Overhead (%)", value=5.00, format="%.2f")
            design_engineering = st.number_input("Design, Engineering, and Surveys (%)", value=0.50, format="%.2f")
        with col2:
            permitting = st.number_input("Permitting & Inspection (%)", value=0.05, format="%.2f")
            startup = st.number_input("Startup & Commissioning (%)", value=0.25, format="%.2f")
            insurance = st.number_input("Insurance (%)", value=0.50, format="%.2f")
            taxes = st.number_input("Taxes (%)", value=5.00, format="%.2f")
    
    # O&M Inputs
    with st.expander("O&M Inputs"):
        col1, col2 = st.columns(2)
        with col1:
            solar_om_fixed = st.number_input("Solar Fixed O&M ($/kW)", value=11, format="%d")
            bess_om_fixed = st.number_input("BESS Fixed O&M ($/kW)", value=2.5, format="%.1f")
            bos_om_fixed = st.number_input("BOS Fixed O&M ($/kW-load)", value=6.0, format="%.1f")
            soft_om_pct = st.number_input("Soft O&M (% of hard capex)", value=0.25, format="%.2f")
            
            # Generator O&M costs based on type
            if generator_type == "Gas Engine":
                generator_om_fixed = st.number_input("Generator Fixed O&M ($/kW)", value=10, format="%d")
                generator_om_variable = st.number_input("Generator Variable O&M ($/kWh)", value=0.025, format="%.3f")
            elif generator_type == "Gas Turbine":
                generator_om_fixed = st.number_input("Generator Fixed O&M ($/kW)", value=10, format="%d")
                generator_om_variable = st.number_input("Generator Variable O&M ($/kWh)", value=0.025, format="%.3f")
            else:  # Diesel Generator
                generator_om_fixed = st.number_input("Generator Fixed O&M ($/kW)", value=10, format="%d")
                generator_om_variable = st.number_input("Generator Variable O&M ($/kWh)", value=0.025, format="%.3f")
            
            om_escalator = st.number_input("O&M Escalator (% p.a.)", value=2.50, min_value=0.0)
        with col2:
            fuel_price = st.number_input("Fuel Price ($/MMBtu)", value=5.00, min_value=0.0)
            fuel_escalator = st.number_input("Fuel Escalator (% p.a.)", value=3.00, min_value=0.0)
    
    return {
        'location': location,
        'datacenter_load_mw': datacenter_load,
        'solar_pv_capacity_mw': solar_pv_capacity,
        'bess_max_power_mw': bess_max_power,
        'natural_gas_capacity_mw': natural_gas_capacity,
        'generator_type': generator_type,
        'generator_om_fixed_dollar_per_kw': generator_om_fixed,
        'generator_om_variable_dollar_per_kwh': generator_om_variable,
        'fuel_price_dollar_per_mmbtu': fuel_price,
        'fuel_escalator_pct': fuel_escalator,
        'solar_om_fixed_dollar_per_kw': solar_om_fixed,
        'bess_om_fixed_dollar_per_kw': bess_om_fixed,
        'bos_om_fixed_dollar_per_kw_load': bos_om_fixed,
        'soft_om_pct': soft_om_pct,
        'om_escalator_pct': om_escalator,
        'lcoe_dollar_per_mwh': lcoe,
        'cost_of_debt_pct': cost_of_debt,
        'leverage_pct': leverage,
        'debt_term_years': debt_term,
        'cost_of_equity_pct': cost_of_equity,
        'investment_tax_credit_pct': investment_tax_credit,
        'combined_tax_rate_pct': combined_tax_rate,
        'construction_time_years': construction_time,
        # Solar PV CAPEX
        'modules': modules,
        'inverters': inverters,
        'racking': racking,
        'balance_system': balance_system,
        'labor': labor,
        # BESS CAPEX
        'bess_units': bess_units,
        'bess_bos': bess_bos,
        'bess_labor': bess_labor,
        # Generator CAPEX
        'gensets': gensets,
        'gen_bos': gen_bos,
        'gen_labor': gen_labor,
        # System Integration CAPEX
        'microgrid': microgrid,
        'controls': controls,
        'si_labor': si_labor,
        # Soft Costs
        'general_conditions': general_conditions,
        'epc_overhead': epc_overhead,
        'design_engineering': design_engineering,
        'permitting': permitting,
        'startup': startup,
        'insurance': insurance,
        'taxes': taxes
    }

def calculate_capex(
    solar_pv_capacity_mw: float,
    bess_max_power_mw: float,
    natural_gas_capacity_mw: float,
    datacenter_load_mw: float,
    # Solar PV unit costs
    modules: float = 0.220,
    inverters: float = 0.050,
    racking: float = 0.180,
    balance_system: float = 0.120,
    labor: float = 0.200,
    # BESS unit costs
    bess_units: float = 200.0,
    bess_bos: float = 40.0,
    bess_labor: float = 20.0,
    # Generator unit costs
    gensets: float = 800.0,
    gen_bos: float = 200.0,
    gen_labor: float = 150.0,
    # System Integration unit costs
    microgrid: float = 300.0,
    controls: float = 50.0,
    si_labor: float = 60.0,
    # Soft Costs percentages
    general_conditions: float = 0.50,
    epc_overhead: float = 5.00,
    design_engineering: float = 0.50,
    permitting: float = 0.05,
    startup: float = 0.25,
    insurance: float = 0.50,
    taxes: float = 5.00
) -> Dict[str, float]:
    """Calculate CAPEX for each system component."""
    
    # Calculate Solar CAPEX
    solar_capex = solar_pv_capacity_mw * 1_000_000 * (
        modules + inverters + racking + balance_system + labor
    )
    
    # Calculate BESS CAPEX
    bess_capex = bess_max_power_mw * 1000 * (
        bess_units + bess_bos + bess_labor
    )
    
    # Calculate Generator CAPEX
    generator_capex = natural_gas_capacity_mw * 1000 * (
        gensets + gen_bos + gen_labor
    )
    
    # Calculate System Integration CAPEX
    system_integration_capex = datacenter_load_mw * 1000 * (
        microgrid + controls + si_labor
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
        general_conditions/100 +
        epc_overhead/100 +
        design_engineering/100 +
        permitting/100 +
        startup/100 +
        insurance/100 +
        taxes/100
    )
    
    return {
        'solar': solar_capex / 1_000_000,  # Convert to millions
        'bess': bess_capex / 1_000_000,
        'generator': generator_capex / 1_000_000,
        'system_integration': system_integration_capex / 1_000_000,
        'soft_costs': soft_costs / 1_000_000
    }

def filter_simulation_data(df: pd.DataFrame, location: str, system_spec: str) -> pd.DataFrame:
    """Filter simulation data based on location and system spec."""
    return df[
        (df['Location'].str.strip() == location) &
        (df['System Spec'] == system_spec)
    ]

def calculate_energy_mix(filtered_data: pd.DataFrame) -> Dict[str, float]:
    """Calculate energy mix from filtered simulation data."""
    total_solar = filtered_data['Solar Output - Net (MWh)'].sum()
    total_bess = filtered_data['BESS Net Output (MWh)'].sum()
    total_generator = filtered_data['Generator Output (MWh)'].sum()
    total_load = filtered_data['Load Served (MWh)'].sum()
    
    # Convert to TWh
    solar_twh = total_solar / 1_000_000
    bess_twh = total_bess / 1_000_000
    generator_twh = total_generator / 1_000_000
    
    # Calculate renewable percentage (non-generator portion)
    renewable_percentage = 100 * (1 - total_generator / total_load)
    
    return {
        'solar_twh': solar_twh,
        'bess_twh': bess_twh,
        'generator_twh': generator_twh,
        'renewable_percentage': renewable_percentage
    }

def main():
    """Main application function."""
    st.set_page_config(page_title="Solar Datacenter LCOE Calculator", layout="wide")
    
    # Initialize data
    global simulation_data, unique_values
    simulation_data, unique_values = init_data()
    
    # Create input sections and get inputs
    inputs = create_input_sections()
    
    # Calculate CAPEX based on inputs
    capex = calculate_capex(
        solar_pv_capacity_mw=inputs['solar_pv_capacity_mw'],
        bess_max_power_mw=inputs['bess_max_power_mw'],
        natural_gas_capacity_mw=inputs['natural_gas_capacity_mw'],
        datacenter_load_mw=inputs['datacenter_load_mw'],
        # Solar PV unit costs
        modules=inputs['modules'],
        inverters=inputs['inverters'],
        racking=inputs['racking'],
        balance_system=inputs['balance_system'],
        labor=inputs['labor'],
        # BESS unit costs
        bess_units=inputs['bess_units'],
        bess_bos=inputs['bess_bos'],
        bess_labor=inputs['bess_labor'],
        # Generator unit costs
        gensets=inputs['gensets'],
        gen_bos=inputs['gen_bos'],
        gen_labor=inputs['gen_labor'],
        # System Integration unit costs
        microgrid=inputs['microgrid'],
        controls=inputs['controls'],
        si_labor=inputs['si_labor'],
        # Soft Costs percentages
        general_conditions=inputs['general_conditions'],
        epc_overhead=inputs['epc_overhead'],
        design_engineering=inputs['design_engineering'],
        permitting=inputs['permitting'],
        startup=inputs['startup'],
        insurance=inputs['insurance'],
        taxes=inputs['taxes']
    )

    # Calculate total CAPEX
    total_capex = sum(capex.values())
    
    # CAPEX Section
    st.header("CAPEX")
    st.metric("Total CAPEX", f"${total_capex:,.1f}M")
    st.plotly_chart(create_capex_chart(capex, total_capex), use_container_width=True)
    
    # Filter simulation data
    system_spec = f"{inputs['solar_pv_capacity_mw']}MW | {inputs['bess_max_power_mw']}MW | {inputs['natural_gas_capacity_mw']}MW"
    filtered_data = filter_simulation_data(simulation_data, inputs['location'], system_spec)
    
    if filtered_data.empty:
        st.error("No matching simulation data found for the selected inputs. Please adjust your parameters.")
        st.stop()
    
    # Renewable Energy Section
    st.header("Renewable Energy")
    energy_mix = calculate_energy_mix(filtered_data)
    st.metric("Renewable Energy Percentage", f"{energy_mix['renewable_percentage']:.1f}%")
    st.plotly_chart(create_energy_mix_chart(energy_mix), use_container_width=True)

    # Generate Proforma button
    if st.button("Generate Proforma"):
        # Remove CAPEX-related inputs that aren't needed in calculate_pro_forma
        proforma_inputs = {k: v for k, v in inputs.items() if k not in [
            'modules', 'inverters', 'racking', 'balance_system', 'labor',
            'bess_units', 'bess_bos', 'bess_labor',
            'gensets', 'gen_bos', 'gen_labor',
            'microgrid', 'controls', 'si_labor',
            'general_conditions', 'epc_overhead', 'design_engineering',
            'permitting', 'startup', 'insurance', 'taxes'
        ]}
        
        proforma = calculate_pro_forma(
            simulation_data=filtered_data,  # Pass filtered data instead of full dataset
            **proforma_inputs,  # Pass filtered inputs
            solar_capex=capex['solar'],
            bess_capex=capex['bess'],
            generator_capex=capex['generator'],
            system_integration_capex=capex['system_integration'],
            soft_costs_capex=capex['soft_costs']
        )
        
        st.subheader("Proforma Results")
        
        # Display the formatted proforma
        display_proforma(proforma)
        
        # Add download button for CSV
        formatted_proforma = format_proforma(proforma)
        csv = formatted_proforma.to_csv().encode('utf-8')
        st.download_button(
            "Download Proforma as CSV",
            csv,
            "proforma.csv",
            "text/csv",
            key='download-csv'
        )

if __name__ == "__main__":
    main()
