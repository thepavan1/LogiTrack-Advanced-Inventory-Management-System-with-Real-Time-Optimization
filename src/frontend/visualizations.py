import plotly.graph_objects as go
import plotly.express as px
import folium
import pandas as pd
from typing import Dict
from src.config import VIS_SETTINGS  

def create_distribution_map(warehouses: pd.DataFrame,
                          sales: pd.DataFrame,
                          allocation: Dict) -> go.Figure:
    # Create base map
    fig = go.Figure()

    # Add warehouses
    fig.add_trace(go.Scattergeo(
        lon=warehouses['longitude'],
        lat=warehouses['latitude'],
        text=warehouses['warehouse_id'],
        mode='markers',
        marker=dict(
            size=10,
            color=VIS_SETTINGS['COLORS']['primary'],
            symbol='square'
        ),
        name='Warehouses'
    ))

    # Add demand regions
    fig.add_trace(go.Scattergeo(
        lon=sales['longitude'],
        lat=sales['latitude'],
        text=sales['region'],
        mode='markers',
        marker=dict(
            size=8,
            color=VIS_SETTINGS['COLORS']['secondary'],
            symbol='circle'
        ),
        name='Demand Regions'
    ))

    # Add allocation lines
    for (w, r), units in allocation.items():
        if units > 0:
            w_data = warehouses[warehouses['warehouse_id'] == w].iloc[0]
            r_data = sales[sales['region'] == r].iloc[0]
            
            fig.add_trace(go.Scattergeo(
                lon=[w_data['longitude'], r_data['longitude']],
                lat=[w_data['latitude'], r_data['latitude']],
                mode='lines',
                line=dict(
                    width=1,
                    color=VIS_SETTINGS['COLORS']['success']
                ),
                opacity=0.5,
                showlegend=False
            ))

    # Update layout
    fig.update_layout(
        title='Inventory Distribution Network',
        geo=dict(
            scope='usa',
            showland=True,
            showlakes=True,
            showcountries=True,
            showsubunits=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
            subunitcolor='rgb(204, 204, 204)',
            center=dict(
                lat=VIS_SETTINGS['MAP_CENTER'][0],
                lon=VIS_SETTINGS['MAP_CENTER'][1]
            ),
            projection_scale=VIS_SETTINGS['MAP_ZOOM']
        )
    )

    return fig

def create_cost_comparison_chart(results: Dict) -> go.Figure:
    categories = ['Original Cost', 'Optimized Cost']
    values = [results['original_cost'], results['objective_value']]
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=values,
            marker_color=[
                VIS_SETTINGS['COLORS']['warning'],
                VIS_SETTINGS['COLORS']['success']
            ]
        )
    ])
    
    fig.update_layout(
        title='Cost Comparison',
        yaxis_title='Cost ($)',
        showlegend=False
    )
    
    return fig

def create_utilization_chart(warehouses: pd.DataFrame,
                           allocation: Dict) -> go.Figure:
    # Calculate utilization for each warehouse
    utilization = {}
    for w in warehouses['warehouse_id']:
        capacity = warehouses[warehouses['warehouse_id'] == w]['capacity'].iloc[0]
        used = sum(units for (wh, _), units in allocation.items() if wh == w)
        utilization[w] = (used / capacity) * 100

    fig = go.Figure(data=[
        go.Pie(
            labels=list(utilization.keys()),
            values=list(utilization.values()),
            hole=0.4,
            marker_colors=[VIS_SETTINGS['COLORS']['primary'],
                          VIS_SETTINGS['COLORS']['secondary'],
                          VIS_SETTINGS['COLORS']['success']]
        )
    ])

    fig.update_layout(
        title='Warehouse Utilization (%)'
    )

    return fig