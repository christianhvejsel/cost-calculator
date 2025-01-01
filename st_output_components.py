"""Module for Streamlit-specific output components including charts and formatting."""

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Optional

# Global color constants
SOLAR_COLOR = '#ffd700'  # yellow
BESS_COLOR = '#ff7f0e'   # orange
GENERATOR_COLOR = '#808080'  # gray
SYSTEM_INTEGRATION_COLOR = '#1f77b4'  # blue
SOFT_COSTS_COLOR = '#2ca02c'  # green
DATACENTER_COLOR = '#1f77b4'

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
    'Debt Outstanding, Yr Start': '$, Millions',
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

def create_capex_chart(capex: Dict[str, float], total_capex: float) -> go.Figure:
    """Create a stacked horizontal bar chart showing CAPEX breakdown."""
    fig = go.Figure(data=[
        go.Bar(
            name='Solar',
            x=[capex['solar']],
            y=[''],  # Empty label
            orientation='h',
            marker_color=SOLAR_COLOR,
            text=f"${capex['solar']:,.1f}M",
            textposition='inside',
            hovertemplate="Solar CAPEX: $%{x:.1f}M<br>%{customdata:.1f}% of Total CAPEX<extra></extra>",
            customdata=[(capex['solar']/total_capex)*100]
        ),
        go.Bar(
            name='BESS',
            x=[capex['bess']],
            y=[''],  # Empty label
            orientation='h',
            marker_color=BESS_COLOR,
            text=f"${capex['bess']:,.1f}M",
            textposition='inside',
            hovertemplate="BESS CAPEX: $%{x:.1f}M<br>%{customdata:.1f}% of Total CAPEX<extra></extra>",
            customdata=[(capex['bess']/total_capex)*100]
        ),
        go.Bar(
            name='Generator',
            x=[capex['generator']],
            y=[''],  # Empty label
            orientation='h',
            marker_color=GENERATOR_COLOR,
            text=f"${capex['generator']:,.1f}M",
            textposition='inside',
            hovertemplate="Generator CAPEX: $%{x:.1f}M<br>%{customdata:.1f}% of Total CAPEX<extra></extra>",
            customdata=[(capex['generator']/total_capex)*100]
        ),
        go.Bar(
            name='System Integration',
            x=[capex['system_integration']],
            y=[''],  # Empty label
            orientation='h',
            marker_color=SYSTEM_INTEGRATION_COLOR,
            text=f"${capex['system_integration']:,.1f}M",
            textposition='inside',
            hovertemplate="System Integration CAPEX: $%{x:.1f}M<br>%{customdata:.1f}% of Total CAPEX<extra></extra>",
            customdata=[(capex['system_integration']/total_capex)*100]
        ),
        go.Bar(
            name='Soft Costs',
            x=[capex['soft_costs']],
            y=[''],  # Empty label
            orientation='h',
            marker_color=SOFT_COSTS_COLOR,
            text=f"${capex['soft_costs']:,.1f}M",
            textposition='inside',
            hovertemplate="Soft Costs CAPEX: $%{x:.1f}M<br>%{customdata:.1f}% of Total CAPEX<extra></extra>",
            customdata=[(capex['soft_costs']/total_capex)*100]
        )
    ])

    fig.update_layout(
        title=dict(
            text='Breakdown',
            y=0.95  # Move title down slightly
        ),
        xaxis_title='CAPEX Cost ($ Millions)',
        barmode='stack',
        height=150,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.15,  # Move legend up
            xanchor="center",
            x=0.5,
            traceorder="normal"
        ),
        margin=dict(t=50, b=30, l=0, r=0),  # Adjusted top and bottom margins
        yaxis=dict(showticklabels=False)  # Hide y-axis labels
    )

    return fig

def create_energy_mix_chart(energy_mix: Dict[str, float]) -> go.Figure:
    """Create a stacked horizontal bar chart showing energy mix breakdown."""
    total_energy = energy_mix['total_load_twh']
    
    fig = go.Figure(data=[
        go.Bar(
            name='Solar (direct)',
            x=[energy_mix['solar_to_load_twh']],
            y=[''],  # Empty label
            orientation='h',
            marker_color=SOLAR_COLOR,
            text=f"{energy_mix['solar_to_load_twh']:,.1f} TWh",
            textposition='inside',
            hovertemplate="Solar (direct): %{x:.1f} TWh<br>%{customdata:.1f}% of Total Energy<extra></extra>",
            customdata=[(energy_mix['solar_to_load_twh']/total_energy)*100]
        ),
        go.Bar(
            name='Solar (via BESS)',
            x=[energy_mix['bess_to_load_twh']],
            y=[''],  # Empty label
            orientation='h',
            marker_color=BESS_COLOR,
            text=f"{energy_mix['bess_to_load_twh']:,.1f} TWh",
            textposition='inside',
            hovertemplate="Solar (via BESS): %{x:.1f} TWh<br>%{customdata:.1f}% of Total Energy<extra></extra>",
            customdata=[(energy_mix['bess_to_load_twh']/total_energy)*100]
        ),
        go.Bar(
            name='Generator',
            x=[energy_mix['generator_twh']],
            y=[''],  # Empty label
            orientation='h',
            marker_color=GENERATOR_COLOR,
            text=f"{energy_mix['generator_twh']:,.1f} TWh",
            textposition='inside',
            hovertemplate="Generator: %{x:.1f} TWh<br>%{customdata:.1f}% of Total Energy<extra></extra>",
            customdata=[(energy_mix['generator_twh']/total_energy)*100]
        )
    ])

    fig.update_layout(
        title='Lifetime Energy to Load',
        xaxis_title='Energy (TWh)',
        barmode='stack',
        height=150,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            traceorder="normal"
        ),
        margin=dict(t=50, b=30, l=0, r=0),  # Adjusted top and bottom margins
        yaxis=dict(showticklabels=False)  # Hide y-axis labels
    )
    
    return fig

def create_capacity_chart(datacenter_demand: float, solar_pv_capacity: float, 
                         bess_max_power: float, generator_capacity: float) -> go.Figure:
    """Create a bar chart showing system capacity overview."""
    fig = go.Figure(data=[
        go.Bar(name='Capacity (MW)', 
               x=['Data Center', 'Solar PV', 'BESS', 'Generator'],
               y=[datacenter_demand, solar_pv_capacity, bess_max_power, generator_capacity],
               text=[f'{int(val)} MW' for val in [datacenter_demand, solar_pv_capacity, bess_max_power, generator_capacity]],
               textposition='auto',
               marker_color=[DATACENTER_COLOR, SOLAR_COLOR, BESS_COLOR, GENERATOR_COLOR])
    ])
    fig.update_layout(
        title='System Capacity Overview',
        height=300,
        showlegend=False,
        margin=dict(t=30, b=0, l=0, r=0)
    )
    return fig

def format_proforma(proforma: pd.DataFrame) -> pd.DataFrame:
    """Format proforma with years as columns and metrics as rows."""
    # Define row groups and their metrics
    row_groups = {
        'Consumption': [
            'Solar Output - Net (MWh)',
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
            'Debt Outstanding, Yr Start',
            'Interest Expense',
            'Principal Payment',
            'Debt Service'
        ],
        'Tax': [
            'Depreciation Schedule',
            'Depreciation (MACRS)',
            'Interest Expense (Tax)',
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
    
    # Add metrics by group
    for group, metrics in row_groups.items():
        # Add group header
        rows.append({
            'Group': group,
            'Metric': '',
            'Units': '',
            'Totals/NPV': '',
            **{str(year): '' for year in proforma.index if year != 'NPV'}
        })
        
        # Add metrics in the group
        for metric in metrics:
            if metric in proforma.columns:
                rows.append({
                    'Group': '',
                    'Metric': metric,
                    'Units': METRIC_UNITS.get(metric, ''),
                    'Totals/NPV': proforma.loc['NPV', metric] if 'NPV' in proforma.index else '',
                    **{str(year): proforma.loc[year, metric] if year in proforma.index and year != 'NPV' else None 
                       for year in proforma.index if year != 'NPV'}
                })
    
    # Create DataFrame
    display_df = pd.DataFrame(rows)
    
    return display_df

def display_proforma(proforma: Optional[pd.DataFrame]) -> None:
    """Display proforma in Streamlit with proper formatting and styling."""
    if proforma is None:
        st.error("No matching simulation data found for the selected inputs.")
        return
    
    # Create DataFrame
    display_df = proforma
    
    # Create a style function for negative numbers
    def style_negative(val):
        if isinstance(val, (int, float)) and val < 0:
            return 'color: red; font-weight: bold;'
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
    
    # Add Totals/NPV column highlighting
    def highlight_totals_column(x):
        return ['background-color: #e6f3ff' if col == 'Totals/NPV' else '' for col in x.index]
    
    styled_df = (styled_df
                .apply(highlight_groups, axis=1)
                .apply(highlight_totals_column, axis=1))
    
    # Display with frozen columns
    st.dataframe(
        styled_df,
        column_config={
            "Group": st.column_config.Column(
                width="small",
                help="Metric group"
            ),
            "Metric": st.column_config.Column(
                width="medium",
                help="Individual metric"
            ),
            "Units": st.column_config.Column(
                width="small",
                help="Metric units"
            ),
            "Totals/NPV": st.column_config.Column(
                width="small",
                help="Sum for Consumption, NPV for financial metrics"
            )
        },
        hide_index=True,
        use_container_width=True,
        height=1000
    ) 