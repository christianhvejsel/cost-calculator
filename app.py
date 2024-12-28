"""Main Streamlit application for Solar Datacenter LCOE Calculator."""

import streamlit as st
import pandas as pd
from data_loader import load_simulation_data, get_unique_values
from calculations import calculate_pro_forma, calculate_capex
from st_formatting import format_proforma, display_proforma
from charts import create_capacity_chart, create_capex_chart, create_energy_mix_chart
from inputs import create_input_sections
from typing import Dict


def init_data():
    """Initialize data and unique values."""
    try:
        df = load_simulation_data()
        unique_values = get_unique_values(df)
        return df, unique_values
    except FileNotFoundError as e:
        st.error(str(e))
        st.stop()

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
    st.set_page_config(layout="wide", page_title="LCOE Calculator")
    
    # Load simulation data
    df, unique_values = init_data()
    
    # Create input sections
    inputs = create_input_sections(unique_values)
    
    # Calculate CAPEX
    capex = calculate_capex(
        solar_pv_capacity_mw=inputs['solar_pv_capacity_mw'],
        bess_max_power_mw=inputs['bess_max_power_mw'],
        natural_gas_capacity_mw=inputs['natural_gas_capacity_mw'],
        datacenter_load_mw=inputs['datacenter_load_mw'],
        pv_modules=inputs['pv_modules'],
        pv_inverters=inputs['pv_inverters'],
        pv_racking=inputs['pv_racking'],
        pv_balance_system=inputs['pv_balance_system'],
        pv_labor=inputs['pv_labor'],
        bess_units=inputs['bess_units'],
        bess_balance_of_system=inputs['bess_balance_of_system'],
        bess_labor=inputs['bess_labor'],
        gen_gensets=inputs['gensets'],
        gen_balance_of_system=inputs['gen_balance_of_system'],
        gen_labor=inputs['gen_labor'],
        si_microgrid=inputs['si_microgrid'],
        si_controls=inputs['si_controls'],
        si_labor=inputs['si_labor'],
        soft_costs_general_conditions=inputs['soft_costs_general_conditions'],
        soft_costs_epc_overhead=inputs['soft_costs_epc_overhead'],
        soft_costs_design_engineering=inputs['soft_costs_design_engineering'],
        soft_costs_permitting=inputs['soft_costs_permitting'],
        soft_costs_startup=inputs['soft_costs_startup'],
        soft_costs_insurance=inputs['soft_costs_insurance'],
        soft_costs_taxes=inputs['soft_costs_taxes']
    )
    
    # Filter simulation data
    system_spec = f"{inputs['solar_pv_capacity_mw']}MW | {inputs['bess_max_power_mw']}MW | {inputs['natural_gas_capacity_mw']}MW"
    filtered_data = filter_simulation_data(df, inputs['location'], system_spec)
    
    if filtered_data.empty:
        st.error("No matching simulation data found for the selected inputs. Please adjust your parameters.")
        st.stop()
    
    # Calculate energy mix
    energy_mix = calculate_energy_mix(filtered_data)
    
    # Display CAPEX section with metric and chart side by side
    st.subheader("CAPEX Breakdown")
    col1, col2 = st.columns([1, 3])
    with col1:
        total_capex = sum(capex.values())
        st.metric("Total CAPEX", f"${total_capex:,.1f}M")
    with col2:
        st.plotly_chart(create_capex_chart(capex, total_capex), use_container_width=True)
    
    # Display Energy Mix section with metric and chart side by side
    st.subheader("Energy Mix")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("Renewable %", f"{energy_mix['renewable_percentage']:.1f}%")
    with col2:
        st.plotly_chart(create_energy_mix_chart(energy_mix), use_container_width=True)
    
    # Generate Pro Forma button and display
    if st.button('Generate Proforma'):
        pro_forma = calculate_pro_forma(
            simulation_data=filtered_data,
            location=inputs['location'],
            datacenter_load_mw=inputs['datacenter_load_mw'],
            solar_pv_capacity_mw=inputs['solar_pv_capacity_mw'],
            bess_max_power_mw=inputs['bess_max_power_mw'],
            natural_gas_capacity_mw=inputs['natural_gas_capacity_mw'],
            generator_type=inputs['generator_type'],
            solar_capex=capex['solar'],
            bess_capex=capex['bess'],
            generator_capex=capex['generator'],
            system_integration_capex=capex['system_integration'],
            soft_costs_capex=capex['soft_costs'],
            solar_om_fixed_dollar_per_kw=inputs['solar_om_fixed_dollar_per_kw'],
            bess_om_fixed_dollar_per_kw=inputs['bess_om_fixed_dollar_per_kw'],
            generator_om_fixed_dollar_per_kw=inputs['generator_om_fixed_dollar_per_kw'],
            generator_om_variable_dollar_per_kwh=inputs['generator_om_variable_dollar_per_kwh'],
            fuel_price_dollar_per_mmbtu=inputs['fuel_price_dollar_per_mmbtu'],
            fuel_escalator_pct=inputs['fuel_escalator_pct'],
            bos_om_fixed_dollar_per_kw_load=inputs['bos_om_fixed_dollar_per_kw_load'],
            soft_om_pct=inputs['soft_om_pct'],
            om_escalator_pct=inputs['om_escalator_pct'],
            debt_term_years=inputs['debt_term_years'],
            leverage_pct=inputs['leverage_pct'],
            cost_of_debt_pct=inputs['cost_of_debt_pct'],
            combined_tax_rate_pct=inputs['combined_tax_rate_pct'],
            lcoe_dollar_per_mwh=inputs['lcoe_dollar_per_mwh'],
            investment_tax_credit_pct=inputs['investment_tax_credit_pct'],
            depreciation_schedule=inputs['depreciation_schedule']
        )
        
        if pro_forma is not None:
            formatted_proforma = format_proforma(pro_forma)
            display_proforma(formatted_proforma)
        else:
            st.error("Failed to generate pro forma. Please check your inputs.")

if __name__ == "__main__":
    main()
