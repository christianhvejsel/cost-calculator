import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Solar Datacenter LCOE Calculator - Single Case", layout="wide")

st.title("Solar Datacenter LCOE Calculator")
st.header("Single Case Analysis")

# Configuration Inputs (always expanded)
st.header("Configuration")

# System Capacity Inputs
col1, col2, col3, col4 = st.columns(4)
with col1:
    datacenter_demand = st.number_input("Data Center Demand (MW)", 
                                      value=100.0, 
                                      min_value=0.0, 
                                      step=100.0)
with col2:
    solar_pv_capacity = st.number_input("Solar PV Capacity (MW-DC, 1.2 ILR)", 
                                      value=50.0, 
                                      min_value=0.0, 
                                      step=50.0)
with col3:
    bess_max_power = st.number_input("BESS Max Power (MW)", 
                                    value=100.0, 
                                    min_value=0.0, 
                                    step=50.0)
with col4:
    natural_gas_capacity = st.number_input("Natural Gas Capacity (MW)", 
                                         value=125.0, 
                                         min_value=0.0, 
                                         step=25.0)

# Capacity Visualization
colors = ['#1f77b4', '#ffd700', '#ff7f0e', '#808080']  # Blue, Yellow, Orange, Grey
fig = go.Figure(data=[
    go.Bar(name='Capacity (MW)', 
           x=['Data Center', 'Solar PV', 'BESS', 'Natural Gas'],
           y=[datacenter_demand, solar_pv_capacity, bess_max_power, natural_gas_capacity],
           text=[f'{val:.0f} MW' for val in [datacenter_demand, solar_pv_capacity, bess_max_power, natural_gas_capacity]],
           textposition='auto',
           marker_color=colors)
])
fig.update_layout(
    title='System Capacity Overview',
    height=300,
    showlegend=False,
    margin=dict(t=30, b=0, l=0, r=0)
)
st.plotly_chart(fig, use_container_width=True)

# Non-megawatt configuration inputs
col1, col2 = st.columns(2)
with col1:
    location = st.text_input("Location (City, State)", value="El Paso, TX")
with col2:
    gen_type = st.selectbox("Generators or Turbines?", ["GEN", "GT"], index=0)

# Financial Inputs (in dropdown)
with st.expander("Financial Inputs"):
    col1, col2 = st.columns(2)
    with col1:
        cost_of_debt = st.number_input("Cost of Debt (%)", value=7.5, min_value=0.0, max_value=100.0)
        leverage = st.number_input("Leverage (%)", value=70.0, min_value=0.0, max_value=100.0)
        debt_term = st.number_input("Debt Term (years)", value=20, min_value=1)
    with col2:
        cost_of_equity = st.number_input("Cost of Equity (%)", value=11.0, min_value=0.0, max_value=100.0)
        investment_tax_credit = st.number_input("Investment Tax Credit (%)", value=30.0, min_value=0.0, max_value=100.0)
        combined_tax_rate = st.number_input("Combined Tax Rate (%)", value=21.0, min_value=0.0, max_value=100.0)

# CAPEX Inputs (in dropdown)
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

# O&M Inputs (in dropdown)
with st.expander("O&M Inputs"):
    col1, col2 = st.columns(2)
    with col1:
        solar_om_fixed = st.number_input("Solar Fixed O&M ($/kW)", value=11, format="%d")
        bess_om_fixed = st.number_input("BESS Fixed O&M ($/kW)", value=2, format="%d")
        om_escalator = st.number_input("O&M Escalator (% p.a.)", value=2.50, min_value=0.0)
    with col2:
        fuel_price = st.number_input("Fuel Price ($/MMBtu)", value=5.00, min_value=0.0)
        fuel_escalator = st.number_input("Fuel Escalator (% p.a.)", value=3.00, min_value=0.0)

# Calculate button
if st.button("Calculate LCOE"):
    st.info("LCOE calculation will be implemented soon.")
