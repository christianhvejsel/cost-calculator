"""Main Streamlit entrypoint."""

import streamlit as st
from typing import Dict
import time

from data_loader import get_unique_values
from calculations import DataCenter
from st_output_components import (
    format_proforma, display_proforma, create_capex_chart,
    create_energy_mix_chart, create_capacity_chart
)
from st_inputs import create_input_sections, calculate_capex_subtotals


def display_capex_breakdown(capex_subtotals: Dict[str, Dict[str, float]]) -> None:
    """Display CAPEX breakdown with metric and chart side by side."""
    st.subheader("CAPEX Breakdown")
    col1, col2 = st.columns([1, 3])
    with col1:
        total_capex = sum(component['absolute'] for component in capex_subtotals.values())
        st.metric("Total CAPEX", f"${total_capex:,.1f}M")
    with col2:
        absolute_values = {k: v['absolute'] for k, v in capex_subtotals.items()}
        st.plotly_chart(create_capex_chart(absolute_values, total_capex), use_container_width=True)

def display_energy_mix(energy_mix: Dict[str, float]) -> None:
    """Display energy mix with metric and chart side by side."""
    st.subheader("Energy Mix")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("Renewable %", f"{energy_mix['renewable_percentage']:.1f}%")
    with col2:
        st.plotly_chart(create_energy_mix_chart(energy_mix), use_container_width=True)

def main():
    """Main application."""
    st.set_page_config(layout="wide", page_title="LCOE Calculator")
    
    unique_values = get_unique_values()
    
    # Create input sections
    inputs = create_input_sections(unique_values)
    
    # Calculate CAPEX subtotals for each system component
    capex_subtotals = calculate_capex_subtotals(inputs)
    
    display_capex_breakdown(capex_subtotals)
    
    try:
        # Create DataCenter instance (this will also load and filter simulation data)
        data_center = DataCenter(
            location=inputs['location'],
            solar_pv_capacity_mw=inputs['solar_pv_capacity_mw'],
            bess_max_power_mw=inputs['bess_max_power_mw'],
            generator_capacity_mw=inputs['generator_capacity_mw'],
            generator_type=inputs['generator_type'],
            solar_capex_total_dollar_per_w=capex_subtotals['solar']['rate'],
            bess_capex_total_dollar_per_kwh=capex_subtotals['bess']['rate'],
            generator_capex_total_dollar_per_kw=capex_subtotals['generator']['rate'],
            system_integration_capex_total_dollar_per_kw=capex_subtotals['system_integration']['rate'],
            soft_costs_capex_total_pct=capex_subtotals['soft_costs']['rate'],
            om_solar_fixed_dollar_per_kw=inputs['solar_om_fixed_dollar_per_kw'],
            om_bess_fixed_dollar_per_kw=inputs['bess_om_fixed_dollar_per_kw'],
            om_generator_fixed_dollar_per_kw=inputs['generator_om_fixed_dollar_per_kw'],
            om_generator_variable_dollar_per_kwh=inputs['generator_om_variable_dollar_per_kwh'],
            fuel_price_dollar_per_mmbtu=inputs['fuel_price_dollar_per_mmbtu'],
            fuel_escalator_pct=inputs['fuel_escalator_pct'],
            om_bos_fixed_dollar_per_kw_load=inputs['bos_om_fixed_dollar_per_kw_load'],
            om_soft_pct=inputs['soft_om_pct'],
            om_escalator_pct=inputs['om_escalator_pct'],
            debt_term_years=inputs['debt_term_years'],
            leverage_pct=inputs['leverage_pct'],
            cost_of_debt_pct=inputs['cost_of_debt_pct'],
            combined_tax_rate_pct=inputs['combined_tax_rate_pct'],
            investment_tax_credit_pct=inputs['investment_tax_credit_pct'],
            depreciation_schedule=inputs['depreciation_schedule']
        )
    except ValueError as e:
        st.error(str(e))
        st.stop()
    
    # Calculate and display Energy Mix
    energy_mix = data_center.calculate_energy_mix()
    display_energy_mix(energy_mix)

    # Calculate LCOE
    start_time = time.time()
    lcoe, pro_forma = data_center.calculate_lcoe()
    calculation_time = time.time() - start_time
    
    # Display LCOE  
    st.subheader("LCOE")
    st.metric("Calculated LCOE", f"${lcoe:.2f}/MWh")
    st.text(f"(Ran in {calculation_time*1000:.0f} ms)")
    
    # Display Proforma
    st.subheader("Proforma")
    formatted_proforma = format_proforma(pro_forma)
    display_proforma(formatted_proforma)

    
if __name__ == "__main__":
    main()
