"""Module for chart generation functions."""

import plotly.graph_objects as go
from typing import Dict

# Global color constants
SOLAR_COLOR = '#ffd700'  # yellow
BESS_COLOR = '#ff7f0e'   # orange
GENERATOR_COLOR = '#808080'  # gray
SYSTEM_INTEGRATION_COLOR = '#1f77b4'  # blue
SOFT_COSTS_COLOR = '#2ca02c'  # green
DATACENTER_COLOR = '#1f77b4'  # blue

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