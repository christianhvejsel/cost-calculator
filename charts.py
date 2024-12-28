"""Module for chart generation functions."""

import plotly.graph_objects as go
from typing import Dict

def create_capex_chart(capex: Dict[str, float], total_capex: float) -> go.Figure:
    """Create a stacked horizontal bar chart showing CAPEX breakdown."""
    fig = go.Figure(data=[
        go.Bar(
            name='Solar',
            x=[capex['solar']],
            y=[''],  # Empty label
            orientation='h',
            marker_color='#ffd700',  # yellow
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
            marker_color='#ff7f0e',  # orange
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
            marker_color='#808080',  # gray
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
            marker_color='#1f77b4',  # blue
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
            marker_color='#2ca02c',  # green
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
    total_energy = energy_mix['solar_twh'] + energy_mix['bess_twh'] + energy_mix['generator_twh']
    
    fig = go.Figure(data=[
        go.Bar(
            name='Solar',
            x=[energy_mix['solar_twh']],
            y=[''],  # Empty label
            orientation='h',
            marker_color='#ffd700',  # yellow
            text=f"{energy_mix['solar_twh']:,.1f} TWh",
            textposition='inside',
            hovertemplate="Solar: %{x:.1f} TWh<br>%{customdata:.1f}% of Total Energy<extra></extra>",
            customdata=[(energy_mix['solar_twh']/total_energy)*100]
        ),
        go.Bar(
            name='BESS',
            x=[energy_mix['bess_twh']],
            y=[''],  # Empty label
            orientation='h',
            marker_color='#ff7f0e',  # orange
            text=f"{energy_mix['bess_twh']:,.1f} TWh",
            textposition='inside',
            hovertemplate="BESS: %{x:.1f} TWh<br>%{customdata:.1f}% of Total Energy<extra></extra>",
            customdata=[(energy_mix['bess_twh']/total_energy)*100]
        ),
        go.Bar(
            name='Generator',
            x=[energy_mix['generator_twh']],
            y=[''],  # Empty label
            orientation='h',
            marker_color='#808080',  # gray
            text=f"{energy_mix['generator_twh']:,.1f} TWh",
            textposition='inside',
            hovertemplate="Generator: %{x:.1f} TWh<br>%{customdata:.1f}% of Total Energy<extra></extra>",
            customdata=[(energy_mix['generator_twh']/total_energy)*100]
        )
    ])

    fig.update_layout(
        title='Lifetime Energy Mix',
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
                         bess_max_power: float, natural_gas_capacity: float) -> go.Figure:
    """Create a bar chart showing system capacity overview."""
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