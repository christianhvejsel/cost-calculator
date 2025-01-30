"""Module for handling user inputs in the Streamlit app."""

import streamlit as st
import pandas as pd
from typing import Dict
from streamlit_folium import folium_static, st_folium
import folium

from st_output_components import create_capacity_chart
from defaults import (
    DATACENTER_DEMAND_MW, BESS_HRS_STORAGE, DEFAULTS_GENERATORS,
    DEFAULTS_SOLAR_CAPEX, DEFAULTS_BESS_CAPEX, DEFAULTS_SYSTEM_INTEGRATION_CAPEX,
    DEFAULTS_SOFT_COSTS_CAPEX, DEFAULTS_OM, DEFAULTS_FINANCIAL,
    DEFAULTS_DEPRECIATION_SCHEDULE
)


MAP_INITIAL_LAT = 51.5074
MAP_INITIAL_LONG = -0.1278


def calculate_capex_subtotals(inputs: Dict) -> Dict[str, Dict[str, float]]:
    """Calculate CAPEX subtotals for each system component.
    
    Returns:
        Dict with both unit rates and absolute totals for each component:
        {
            'solar': {'rate': $/W, 'absolute': $M},
            'bess': {'rate': $/kWh, 'absolute': $M},
            'generator': {'rate': $/kW, 'absolute': $M},
            'system_integration': {'rate': $/kW, 'absolute': $M},
            'soft_costs': {'rate': %, 'absolute': $M}
        }
    """
    # Calculate Solar unit rate and absolute CAPEX
    solar_rate = (
        inputs['capex_pv_modules'] + 
        inputs['capex_pv_inverters'] + 
        inputs['capex_pv_racking'] + 
        inputs['capex_pv_balance_system'] + 
        inputs['capex_pv_labor']
    )
    solar_absolute = inputs['solar_pv_capacity_mw'] * 1_000_000 * solar_rate
    
    # Calculate BESS unit rate and absolute CAPEX
    bess_rate = (
        inputs['capex_bess_units'] + 
        inputs['capex_bess_balance_of_system'] + 
        inputs['capex_bess_labor']
    )
    bess_system_mwh = inputs['bess_max_power_mw'] * BESS_HRS_STORAGE
    bess_absolute = bess_system_mwh * 1000 * bess_rate
    
    # Calculate Generator unit rate and absolute CAPEX
    generator_rate = (
        inputs['capex_gensets'] + 
        inputs['capex_gen_balance_of_system'] + 
        inputs['capex_gen_labor']
    )
    generator_absolute = inputs['generator_capacity_mw'] * 1000 * generator_rate
    
    # Calculate System Integration unit rate and absolute CAPEX
    system_integration_rate = (
        inputs['capex_si_microgrid'] + 
        inputs['capex_si_controls'] + 
        inputs['capex_si_labor']
    )
    system_integration_absolute = inputs['datacenter_load_mw'] * 1000 * system_integration_rate
    
    # Calculate total hard costs
    total_hard_costs = (
        solar_absolute +
        bess_absolute +
        generator_absolute +
        system_integration_absolute
    )
    
    # Calculate soft costs rate and absolute
    soft_costs_rate = (
        inputs['capex_soft_costs_general_conditions'] +
        inputs['capex_soft_costs_epc_overhead'] +
        inputs['capex_soft_costs_design_engineering'] +
        inputs['capex_soft_costs_permitting'] +
        inputs['capex_soft_costs_startup'] +
        inputs['capex_soft_costs_insurance'] +
        inputs['capex_soft_costs_taxes']
    )
    soft_costs_absolute = total_hard_costs * soft_costs_rate / 100
    
    # Return both rates and absolute values (absolute in millions)
    return {
        'solar': {
            'rate': solar_rate,
            'absolute': solar_absolute / 1_000_000
        },
        'bess': {
            'rate': bess_rate,
            'absolute': bess_absolute / 1_000_000
        },
        'generator': {
            'rate': generator_rate,
            'absolute': generator_absolute / 1_000_000
        },
        'system_integration': {
            'rate': system_integration_rate,
            'absolute': system_integration_absolute / 1_000_000
        },
        'soft_costs': {
            'rate': soft_costs_rate,
            'absolute': soft_costs_absolute / 1_000_000
        }
    }

def create_input_sections(unique_values) -> Dict:
    """Create all input sections in the Streamlit app."""
    st.title("Solar Datacenter LCOE Calculator", anchor=False)

    preset_location_tab, custom_location_tab = st.tabs(['Preset locations', 'Custom location'])

    with preset_location_tab:
        location = st.selectbox("Location", options=unique_values['locations'])

    with custom_location_tab:
        if "custom_lat_long" not in st.session_state:
            st.session_state.custom_lat_long = None
        
        if st.session_state.custom_lat_long is None:
            st.write("Click on the map to build your datacenter 🏗️")
        
        # Create a Folium map centered on default coordinates
        m = folium.Map(location=[MAP_INITIAL_LAT, MAP_INITIAL_LONG], zoom_start=3, tiles="CartoDB Positron")

        # Add a click handler to the map
        m.add_child(folium.LatLngPopup())

        # Display the map and capture user clicks
        map_data = st_folium(m, width=700, height=500, key="map")

        # Check if the user has clicked on the map
        if map_data.get("last_clicked"):
            # Get the latitude and longitude of the clicked point
            custom_lat = map_data["last_clicked"]["lat"]
            custom_long = map_data["last_clicked"]["lng"]
            
            # Store the coordinates in session state
            st.session_state.custom_lat_long = (custom_lat, custom_long)
    
    # System Capacity Inputs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Data Center Demand", "100 MW")
        datacenter_load = DATACENTER_DEMAND_MW
    with col2:
        solar_pv_capacity = st.selectbox(
            "Solar PV Capacity (MW-DC)",
            options=unique_values['solar_capacities'],
            index=2
        )
    with col3:
        bess_max_power = st.selectbox(
            "BESS Max Power (MW), 4h store",
            options=unique_values['bess_capacities'],
            index=2
        )
    with col4:
        generator_capacity = st.selectbox(
            "Generator Capacity (MW)",
            options=unique_values['generator_capacities'],
            index=2
        )
    
    # Display capacity chart
    st.plotly_chart(
        create_capacity_chart(datacenter_load, solar_pv_capacity, bess_max_power, generator_capacity),
        use_container_width=True
    )
    
    # Non-megawatt configuration inputs
    col1, col2 = st.columns(2)
    with col1:
        # location = st.selectbox("Location", options=unique_values['locations'])
        st.write("placeholder")
    with col2:
        generator_type = st.selectbox("Generator Type", ["Gas Engine", "Gas Turbine"], index=0)
    
    # Get generator configuration based on selection
    gen_config = DEFAULTS_GENERATORS[generator_type]

    # Financial Inputs
    with st.expander("Financial Inputs"):
        col1, col2 = st.columns(2)
        with col1:
            cost_of_debt = st.number_input("Cost of Debt (%)", value=DEFAULTS_FINANCIAL['cost_of_debt_pct'], min_value=0.0, max_value=100.0)
            leverage = st.number_input("Leverage (%)", value=DEFAULTS_FINANCIAL['leverage_pct'], min_value=0.0, max_value=100.0)
            debt_term = st.number_input("Debt Term (years)", value=DEFAULTS_FINANCIAL['debt_term_years'], min_value=1)
            cost_of_equity = st.number_input("Cost of Equity (%)", value=DEFAULTS_FINANCIAL['cost_of_equity_pct'], min_value=0.0, max_value=100.0)
            investment_tax_credit_pct = st.number_input("Investment Tax Credit (%)", value=DEFAULTS_FINANCIAL['investment_tax_credit_pct'], min_value=0.0, max_value=100.0)
            combined_tax_rate = st.number_input("Combined Tax Rate (%)", value=DEFAULTS_FINANCIAL['combined_tax_rate_pct'], min_value=0.0, max_value=100.0)
        
        with col2:
            # Create default MACRS depreciation schedule (20 years)
            if 'depreciation_schedule' not in st.session_state:
                st.session_state.depreciation_schedule = pd.DataFrame({
                    'Year': range(1, 21),
                    'Depreciation (%)': DEFAULTS_DEPRECIATION_SCHEDULE
                })
            
            # Display editable depreciation schedule
            edited_depreciation = st.data_editor(
                st.session_state.depreciation_schedule,
                column_config={
                    "Year": st.column_config.NumberColumn(
                        "Year",
                        help="Year of depreciation",
                        min_value=1,
                        max_value=20,
                        step=1,
                        disabled=True
                    ),
                    "Depreciation (%)": st.column_config.NumberColumn(
                        "Depreciation (%)",
                        help="Percentage of total CAPEX to depreciate in this year",
                        min_value=0.0,
                        max_value=100.0,
                        step=0.1,
                        format="%.1f%%"
                    )
                },
                hide_index=True,
                width=400
            )
            
            # Update session state with edited values
            st.session_state.depreciation_schedule = edited_depreciation
    
    # CAPEX Inputs
    with st.expander("CAPEX Inputs"):
        # TODO: make this dynamic
        # construction_time = st.number_input("Construction Time (years)", value=DEFAULTS_FINANCIAL['construction_time_years'], min_value=1)
        construction_time = DEFAULTS_FINANCIAL['construction_time_years']
        
        # Solar PV
        st.subheader("Solar PV")
        col1, col2 = st.columns(2)
        with col1:
            pv_modules = st.number_input("Modules ($/W)", value=DEFAULTS_SOLAR_CAPEX['modules'], format="%.3f")
            pv_inverters = st.number_input("Inverters ($/W)", value=DEFAULTS_SOLAR_CAPEX['inverters'], format="%.3f")
            pv_racking = st.number_input("Racking and Foundations ($/W)", value=DEFAULTS_SOLAR_CAPEX['racking'], format="%.3f")
        with col2:
            pv_balance_system = st.number_input("Balance of System ($/W)", value=DEFAULTS_SOLAR_CAPEX['balance_of_system'], format="%.3f")
            pv_labor = st.number_input("Labor ($/W)", value=DEFAULTS_SOLAR_CAPEX['labor'], format="%.3f")
    
        # BESS
        st.subheader("Battery Energy Storage System")
        col1, col2 = st.columns(2)
        with col1:
            bess_units = st.number_input("BESS Units ($/kWh)", value=DEFAULTS_BESS_CAPEX['units'], format="%d")
            bess_balance_of_system = st.number_input("Balance of System ($/kWh)", value=DEFAULTS_BESS_CAPEX['balance_of_system'], format="%d")
        with col2:
            bess_labor = st.number_input("Labor ($/kWh)", value=DEFAULTS_BESS_CAPEX['labor'], format="%d")

        # Generators
        st.subheader("Generators")
        col1, col2 = st.columns(2)
        with col1:
            gensets = st.number_input(
                "Gensets ($/kW)", 
                value=gen_config['capex']['gensets'],
                format="%d"
            )
            gen_balance_of_system = st.number_input(
                "Balance of System ($/kW)", 
                value=gen_config['capex']['balance_of_system'],
                format="%d"
            )
        with col2:
            gen_labor = st.number_input(
                "Labor ($/kW)", 
                value=gen_config['capex']['labor'],
                format="%d"
            )

        # System Integration
        st.subheader("System Integration")
        col1, col2 = st.columns(2)
        with col1:
            si_microgrid = st.number_input("Microgrid Switchgear, Transformers, etc. ($/kW)", value=DEFAULTS_SYSTEM_INTEGRATION_CAPEX['microgrid'], format="%d")
            si_controls = st.number_input("Controls ($/kW)", value=DEFAULTS_SYSTEM_INTEGRATION_CAPEX['controls'], format="%d")
        with col2:
            si_labor = st.number_input("System Integration Labor ($/kW)", value=DEFAULTS_SYSTEM_INTEGRATION_CAPEX['labor'], format="%d")

        # Soft Costs
        st.subheader("Soft Costs (CAPEX)")
        col1, col2 = st.columns(2)
        with col1:
            soft_costs_general_conditions = st.number_input("General Conditions (%)", value=DEFAULTS_SOFT_COSTS_CAPEX['general_conditions'], format="%.2f")
            soft_costs_epc_overhead = st.number_input("EPC Overhead (%)", value=DEFAULTS_SOFT_COSTS_CAPEX['epc_overhead'], format="%.2f")
            soft_costs_design_engineering = st.number_input("Design, Engineering, and Surveys (%)", value=DEFAULTS_SOFT_COSTS_CAPEX['design_engineering'], format="%.2f")
        with col2:
            soft_costs_permitting = st.number_input("Permitting & Inspection (%)", value=DEFAULTS_SOFT_COSTS_CAPEX['permitting'], format="%.2f")
            soft_costs_startup = st.number_input("Startup & Commissioning (%)", value=DEFAULTS_SOFT_COSTS_CAPEX['startup'], format="%.2f")
            soft_costs_insurance = st.number_input("Insurance (%)", value=DEFAULTS_SOFT_COSTS_CAPEX['insurance'], format="%.2f")
            soft_costs_taxes = st.number_input("Taxes (%)", value=DEFAULTS_SOFT_COSTS_CAPEX['taxes'], format="%.2f")
    
    # O&M Inputs
    with st.expander("O&M Inputs"):
        col1, col2 = st.columns(2)
        
        # Column 1: Asset-specific O&M
        with col1:
            st.subheader("Operations and Maintenance")
            fuel_price = st.number_input("Fuel Price ($/MMBtu)", value=DEFAULTS_OM['fuel_price_dollar_per_mmbtu'], format="%.2f")
            solar_om_fixed = st.number_input("Solar Fixed O&M ($/kW)", value=DEFAULTS_OM['solar_fixed_dollar_per_kw'], format="%d")
            bess_om_fixed = st.number_input("BESS Fixed O&M ($/kW)", value=DEFAULTS_OM['bess_fixed_dollar_per_kw'], format="%.1f")
            generator_om_fixed = st.number_input(
                "Generator Fixed O&M ($/kW)", 
                value=gen_config['opex']['fixed_om'],
                format="%.2f"
            )
            generator_om_variable = st.number_input(
                "Generator Variable O&M ($/kWh)", 
                value=gen_config['opex']['variable_om'],
                format="%.3f"
            )
            bos_om_fixed = st.number_input("Balance of System Fixed O&M ($/kW-load)", value=DEFAULTS_OM['bos_fixed_dollar_per_kw_load'], format="%.1f")
            soft_om_pct = st.number_input("Soft O&M (% of hard capex)", value=DEFAULTS_OM['soft_pct'], format="%.2f")
            
        # Column 2: System-wide O&M and Escalators
        with col2:
            st.subheader("Escalators")
            om_escalator = st.number_input("O&M Escalator (% p.a.)", value=DEFAULTS_OM['escalator_pct'], format="%.2f")
            fuel_escalator = st.number_input("Fuel Escalator (% p.a.)", value=DEFAULTS_OM['fuel_escalator_pct'], format="%.2f")

    return {
        'location': location,
        'custom_lat_long': st.session_state.custom_lat_long,
        'datacenter_load_mw': datacenter_load,
        'solar_pv_capacity_mw': solar_pv_capacity,
        'bess_max_power_mw': bess_max_power,
        'generator_capacity_mw': generator_capacity,
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
        'cost_of_debt_pct': cost_of_debt,
        'leverage_pct': leverage,
        'debt_term_years': debt_term,
        'cost_of_equity_pct': cost_of_equity,
        'investment_tax_credit_pct': investment_tax_credit_pct,
        'combined_tax_rate_pct': combined_tax_rate,
        'construction_time_years': construction_time,
        'depreciation_schedule': edited_depreciation['Depreciation (%)'].tolist(),
        # Solar PV CAPEX
        'capex_pv_modules': pv_modules,
        'capex_pv_inverters': pv_inverters,
        'capex_pv_racking': pv_racking,
        'capex_pv_balance_system': pv_balance_system,
        'capex_pv_labor': pv_labor,
        # BESS CAPEX
        'capex_bess_units': bess_units,
        'capex_bess_balance_of_system': bess_balance_of_system,
        'capex_bess_labor': bess_labor,
        # Generator CAPEX
        'capex_gensets': gensets,
        'capex_gen_balance_of_system': gen_balance_of_system,
        'capex_gen_labor': gen_labor,
        # System Integration CAPEX
        'capex_si_microgrid': si_microgrid,
        'capex_si_controls': si_controls,
        'capex_si_labor': si_labor,
        # Soft Costs
        'capex_soft_costs_general_conditions': soft_costs_general_conditions,
        'capex_soft_costs_epc_overhead': soft_costs_epc_overhead,
        'capex_soft_costs_design_engineering': soft_costs_design_engineering,
        'capex_soft_costs_permitting': soft_costs_permitting,
        'capex_soft_costs_startup': soft_costs_startup,
        'capex_soft_costs_insurance': soft_costs_insurance,
        'capex_soft_costs_taxes': soft_costs_taxes
    } 