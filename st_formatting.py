"""Module for Streamlit-specific formatting functions."""

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Optional

# Global units definition
METRIC_UNITS = {
    'Operating Year': 'years',
    'Solar Output - Raw (MWh)': 'MWh',
    'Solar Output - Net (MWh)': 'MWh',
    'BESS Throughput (MWh)': 'MWh',
    'BESS Net Output (MWh)': 'MWh',
    'Generator Output (MWh)': 'MWh',
    'Generator Fuel Input (MMBtu)': 'MMBtu',
    'Load Served (MWh)': 'MWh',
    'Fuel Unit Cost': '$/MMBtu',
    'Solar Fixed O&M Rate': '$/kW',
    'Battery Fixed O&M Rate': '$/kW',
    'Generator Fixed O&M Rate': '$/kW',
    'Generator Variable O&M Rate': '$/MWh',
    'BOS Fixed O&M Rate': '$/kW-load',
    'Soft O&M Rate': '% of hard capex',
    'LCOE': '$/MWh',
    'Revenue': '$, Millions',
    'Fuel Cost': '$, Millions',
    'Fixed O&M Cost': '$, Millions',
    'Variable O&M Cost': '$, Millions',
    'Total Operating Costs': '$, Millions',
    'EBITDA': '$, Millions',
    'Debt Outstanding - Start of Period': '$, Millions',
    'Interest Expense': '$, Millions',
    'Principal Payment': '$, Millions',
    'Debt Service': '$, Millions',
    'Depreciation Schedule': '%',
    'Depreciation (MACRS)': '$, Millions',
    'Taxable Income': '$, Millions',
    'Federal ITC': '$, Millions',
    'Tax Benefit (Liability)': '$, Millions',
    'Capital Expenditure': '$, Millions',
    'Debt Contribution': '$, Millions',
    'Equity Capex': '$, Millions',
    'After-Tax Net Equity Cash Flow': '$, Millions'
}

def create_capacity_chart(datacenter_demand: float, solar_pv_capacity: float, 
                         bess_max_power: float, natural_gas_capacity: float) -> go.Figure:
    """
    Create a bar chart showing system capacity overview.
    
    Args:
        datacenter_demand (float): Data center demand in MW
        solar_pv_capacity (float): Solar PV capacity in MW-DC
        bess_max_power (float): Battery storage power capacity in MW
        natural_gas_capacity (float): Natural gas generator capacity in MW
    
    Returns:
        go.Figure: Plotly figure object with the capacity chart
    """
    colors = ['#1f77b4', '#ffd700', '#ff7f0e', '#808080']  # Blue, Yellow, Orange, Grey
    fig = go.Figure(data=[
        go.Bar(name='Capacity (MW)', 
               x=['Data Center', 'Solar PV', 'BESS', 'Natural Gas'],
               y=[datacenter_demand, solar_pv_capacity, bess_max_power, natural_gas_capacity],
               text=[f'{int(val)} MW' for val in [datacenter_demand, solar_pv_capacity, bess_max_power, natural_gas_capacity]],
               textposition='auto',
               marker_color=colors)
    ])
    fig.update_layout(
        title='System Capacity Overview',
        height=300,
        showlegend=False,
        margin=dict(t=30, b=0, l=0, r=0)
    )
    return fig

def format_proforma(proforma: pd.DataFrame) -> pd.DataFrame:
    """
    Format proforma with years as columns and metrics as rows.
    
    Args:
        proforma (pd.DataFrame): Raw proforma data
    
    Returns:
        pd.DataFrame: Formatted proforma with proper structure and grouping
    """
    # Define row groups and their metrics
    row_groups = {
        'Consumption': [
            'Solar Output - Raw (MWh)',
            'Solar Output - Net (MWh)',
            'BESS Throughput (MWh)',
            'BESS Net Output (MWh)',
            'Generator Output (MWh)',
            'Generator Fuel Input (MMBtu)',
            'Load Served (MWh)'
        ],
        'Rates': [
            'Fuel Unit Cost',
            'Solar Fixed O&M Rate',
            'Battery Fixed O&M Rate',
            'Generator Fixed O&M Rate',
            'Generator Variable O&M Rate',
            'BOS Fixed O&M Rate',
            'Soft O&M Rate'
        ],
        'Earnings': [
            'LCOE',
            'Revenue',
            'Fuel Cost',
            'Fixed O&M Cost',
            'Variable O&M Cost',
            'Total Operating Costs',
            'EBITDA'
        ],
        'Debt': [
            'Debt Outstanding - Start of Period',
            'Interest Expense',
            'Principal Payment',
            'Debt Service'
        ],
        'Tax': [
            'Depreciation Schedule',
            'Depreciation (MACRS)',
            'Interest Expense',
            'Taxable Income',
            'Federal ITC',
            'Tax Benefit (Liability)'
        ],
        'Capital': [
            'Capital Expenditure',
            'Debt Contribution',
            'Equity Capex'
        ],
        'Returns': [
            'After-Tax Net Equity Cash Flow'
        ]
    }
    
    # Create rows for the formatted dataframe
    rows = []
    
    # Add header row
    rows.append({
        'Group': 'Year',
        'Metric': '',
        'Units': '',
        **{str(year): year for year in proforma.index}
    })
    
    # Add metrics by group
    for group, metrics in row_groups.items():
        # Add group header
        rows.append({
            'Group': group,
            'Metric': '',
            'Units': '',
            **{str(year): '' for year in proforma.index}
        })
        
        # Add metrics in the group
        for metric in metrics:
            if metric in proforma.columns:
                rows.append({
                    'Group': '',
                    'Metric': metric,
                    'Units': METRIC_UNITS.get(metric, ''),
                    **{str(year): proforma.loc[year, metric] if year in proforma.index else None 
                       for year in proforma.index}
                })
    
    # Create DataFrame
    display_df = pd.DataFrame(rows)
    
    return display_df

def display_proforma(proforma: Optional[pd.DataFrame]) -> None:
    """
    Display proforma in Streamlit with proper formatting and styling.
    
    Args:
        proforma (Optional[pd.DataFrame]): Proforma data to display
    """
    if proforma is None:
        st.error("No matching simulation data found for the selected inputs.")
        return
    
    # Define groups and their metrics
    groups = {
        'Consumption': [
            'Operating Year',
            'Solar Output - Raw (MWh)',
            'Solar Output - Net (MWh)',
            'BESS Throughput (MWh)',
            'BESS Net Output (MWh)',
            'Generator Output (MWh)',
            'Generator Fuel Input (MMBtu)',
            'Load Served (MWh)'
        ],
        'Rates': [
            'Fuel Unit Cost',
            'Solar Fixed O&M Rate',
            'Battery Fixed O&M Rate',
            'Generator Fixed O&M Rate',
            'Generator Variable O&M Rate',
            'BOS Fixed O&M Rate',
            'Soft O&M Rate'
        ],
        'Earnings': [
            'LCOE',
            'Revenue',
            'Fuel Cost',
            'Fixed O&M Cost',
            'Variable O&M Cost',
            'Total Operating Costs',
            'EBITDA'
        ],
        'Debt': [
            'Debt Outstanding - Start of Period',
            'Interest Expense',
            'Principal Payment',
            'Debt Service'
        ],
        'Tax': [
            'Depreciation Schedule',
            'Depreciation (MACRS)',
            'Interest Expense',
            'Taxable Income',
            'Federal ITC',
            'Tax Benefit (Liability)'
        ],
        'Capital': [
            'Capital Expenditure',
            'Debt Contribution',
            'Equity Capex'
        ],
        'Returns': [
            'After-Tax Net Equity Cash Flow'
        ]
    }
    
    # Create the display DataFrame with groups
    rows = []
    
    # Add header row
    rows.append({
        'Group': 'Year',
        'Metric': '',
        'Units': '',
        **{str(year): year for year in proforma.index}
    })
    
    # Add metrics by group
    for group, metrics in groups.items():
        # Add group header
        rows.append({
            'Group': group,
            'Metric': '',
            'Units': '',
            **{str(year): '' for year in proforma.index}
        })
        
        # Add metrics in the group
        for metric in metrics:
            if metric in proforma.columns:
                rows.append({
                    'Group': '',
                    'Metric': metric,
                    'Units': METRIC_UNITS.get(metric, ''),
                    **{str(year): proforma.loc[year, metric] if year in proforma.index else None 
                       for year in proforma.index}
                })
    
    # Create DataFrame
    display_df = pd.DataFrame(rows)
    
    # Create a style function for negative numbers
    def style_negative(val):
        try:
            if isinstance(val, (int, float)) and val < 0:
                return 'color: red; font-weight: bold;'
        except:
            pass
        return ''
    
    # Format numbers with units and handle negatives
    def format_numbers(val):
        if pd.isna(val) or val == '' or not isinstance(val, (int, float)):
            return val
        
        # Find the row containing this value
        mask = display_df.iloc[:, 3:].isin([val]).any(axis=1)  # Skip Group, Metric, Units columns
        if not mask.any():
            return val
            
        row_idx = mask.idxmax()
        unit = display_df.loc[row_idx, 'Units']
        
        is_negative = val < 0
        abs_val = abs(val)
        
        # Format based on unit type
        if unit in ['MWh', 'MMBtu']:
            formatted = f"{abs_val:,.0f}"
        elif unit.startswith('$'):
            formatted = f"${abs_val:,.2f}"
        elif unit.startswith('%'):
            formatted = f"{abs_val:,.2f}%"
        else:
            formatted = f"{abs_val:,.2f}"
        
        # Add brackets for negative values
        if is_negative:
            return f"({formatted})"
        return formatted
    
    # Apply styling and formatting
    styled_df = display_df.style.map(style_negative).format(format_numbers)
    
    # Add group styling
    def highlight_groups(x):
        return ['background-color: #f0f2f6' if x['Group'] != '' else '' for _ in x]
    
    styled_df = styled_df.apply(highlight_groups, axis=1)
    
    # Format the DataFrame
    st.dataframe(
        styled_df,
        column_config={
            "Group": st.column_config.Column(
                width="small",
            ),
            "Metric": st.column_config.Column(
                width="medium",
            ),
            "Units": st.column_config.Column(
                width="small",
            ),
        },
        hide_index=True,
        height=1000,
        use_container_width=True
    ) 