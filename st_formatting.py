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

def calculate_npv(values: pd.Series, discount_rate: float) -> float:
    """Calculate NPV of a series of cash flows."""
    years = values.index.astype(float)
    return sum(values / (1 + discount_rate/100)**(years))

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
                    'Units': {
                        'Solar Output - Net (MWh)': 'MWh',
                        'BESS Net Output (MWh)': 'MWh',
                        'Generator Output (MWh)': 'MWh',
                        'Generator Fuel Input (MMBtu)': 'MMBtu',
                        'Load Served (MWh)': 'MWh',
                        'Fuel Unit Cost': '$/MMBtu',
                        'Solar Fixed O&M Rate': '$/kW',
                        'Battery Fixed O&M Rate': '$/kW',
                        'Generator Fixed O&M Rate': '$/kW',
                        'Generator Variable O&M Rate': '$/kWh',
                        'BOS Fixed O&M Rate': '$/kW-load',
                        'Soft O&M Rate': '%',
                        'LCOE': '$/MWh',
                        'Revenue': '$M',
                        'Fuel Cost': '$M',
                        'Fixed O&M Cost': '$M',
                        'Variable O&M Cost': '$M',
                        'Total Operating Costs': '$M',
                        'EBITDA': '$M',
                        'Debt Outstanding, Yr Start': '$M',
                        'Interest Expense': '$M',
                        'Principal Payment': '$M',
                        'Debt Service': '$M',
                        'Depreciation Schedule': '%',
                        'Depreciation (MACRS)': '$M',
                        'Interest Expense (Tax)': '$M',
                        'Taxable Income': '$M',
                        'Federal ITC': '$M',
                        'Tax Benefit (Liability)': '$M',
                        'Capital Expenditure': '$M',
                        'Debt Contribution': '$M',
                        'Equity Capex': '$M',
                        'After-Tax Net Equity Cash Flow': '$M'
                    }.get(metric, ''),
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