from ctypes import pointer
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import altair as alt
import pandas as pd
from vega_datasets import data

# Read in global data
colony = pd.read_csv('data/colony.csv')
stressor = pd.read_csv('data/stressor.csv')
state_info = pd.read_csv('data/state_info.csv')
state_map = alt.topo_feature(data.us_10m.url, 'states')
# state_pop = data.population_engineers_hurricanes()[['state', 'id', 'population']]

# Setup app and layout/frontend
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.layout = dbc.Container([
    html.H1('Bee Informer'),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='year-widget',
                value='2021', 
                options=[{'label': col, 'value': col} for col in colony['year'].unique()]),
            dcc.Dropdown(
                id='month-widget',
                value='January-March', 
                options=[{'label': col, 'value': col} for col in colony['months'].unique()]),
            dcc.Dropdown(
                id='indicator-widget',
                value='colony_lost_pct', 
                options=[{'label': col, 'value': col} for col in list(set(colony.columns) - set(['year', 'months', 'state']))]),                
                ]),                
        dbc.Col(
            html.Iframe(
                id='scatter',
                style={'border-width': '0', 'width': '90%', 'height': '400px'}))]),
    dbc.Row([
        dbc.Col([
            html.Iframe(
                id='scatter1',
                style={'border-width': '0', 'width': '90%', 'height': '400px'})
        ]),                
        dbc.Col([
            html.Iframe(
                id='scatter2',
                style={'border-width': '0', 'width': '90%', 'height': '400px'})])
    ])
])
 

# Set up callbacks/backend
@app.callback(
    Output('scatter', 'srcDoc'),
    Input('year-widget', 'value'),
    Input('month-widget', 'value'),
    Input('indicator-widget', 'value'))
def plot_altair(year, month, indicator):
    df = colony.query(f"year == {year} & months == '{month}'")
    # capital = pd.merge(state_info, df, how="left", on="state")
    target_df = pd.merge(state_info, df, how="left", on="state")
    target_df.fillna(0, inplace=True)
    background = alt.Chart(state_map).mark_geoshape(stroke='#706545', strokeWidth=1).transform_lookup(
        lookup='id',
        from_=alt.LookupData(target_df, 'id', [indicator])
    ).encode(color=(indicator + ':Q')).project(type='albersUsa').properties(
        width=400,
        height=300
    )

    text = alt.Chart(target_df).mark_text().encode(
        longitude='lon:Q',
        latitude='lat:Q',
        color=alt.value('orange'),
        text=indicator + ':Q',
        tooltip=['state:N', 'colony_max:Q', 'colony_lost_pct:Q']
    )
    return (background + text).to_html()

@app.callback(
    Output('scatter1', 'srcDoc'),
    Input('year-widget', 'value'),
    Input('month-widget', 'value'),
    Input('indicator-widget', 'value'))
def plot_altair(year, month, indicator):
    df = colony.query(f"year == {year} & months == '{month}'")
    # capital = pd.merge(state_info, df, how="left", on="state")
    target_df = pd.merge(state_info, df, how="left", on="state")
    target_df.fillna(0, inplace=True)
    background = alt.Chart(state_map).mark_geoshape(stroke='#706545', strokeWidth=1).transform_lookup(
        lookup='id',
        from_=alt.LookupData(target_df, 'id', [indicator])
    ).encode(color=(indicator + ':Q')).project(type='albersUsa').properties(
        width=400,
        height=300
    )

    text = alt.Chart(target_df).mark_text().encode(
        longitude='lon:Q',
        latitude='lat:Q',
        color=alt.value('orange'),
        text=indicator + ':Q',
        tooltip=['state:N', 'colony_max:Q', 'colony_lost_pct:Q']
    )
    return (background + text).to_html()

@app.callback(
    Output('scatter2', 'srcDoc'),
    Input('year-widget', 'value'),
    Input('month-widget', 'value'),
    Input('indicator-widget', 'value'))
def plot_altair(year, month, indicator):
    df = colony.query(f"year == {year} & months == '{month}'")
    # capital = pd.merge(state_info, df, how="left", on="state")
    target_df = pd.merge(state_info, df, how="left", on="state")
    target_df.fillna(0, inplace=True)
    background = alt.Chart(state_map).mark_geoshape(stroke='#706545', strokeWidth=1).transform_lookup(
        lookup='id',
        from_=alt.LookupData(target_df, 'id', [indicator])
    ).encode(color=(indicator + ':Q')).project(type='albersUsa').properties(
        width=400,
        height=300
    )

    text = alt.Chart(target_df).mark_text().encode(
        longitude='lon:Q',
        latitude='lat:Q',
        color=alt.value('orange'),
        text=indicator + ':Q',
        tooltip=['state:N', 'colony_max:Q', 'colony_lost_pct:Q']
    )
    return (background + text).to_html()

    
if __name__ == '__main__':
    app.run_server(debug=True)