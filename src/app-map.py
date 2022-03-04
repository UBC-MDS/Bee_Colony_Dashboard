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

# Wrangle data
colony["start_month"] = colony["months"].str.split('-', 1, expand=True)[0]
colony["year"] = colony["year"].astype("str")
colony["time"] = colony[['year', 'start_month']].agg('-'.join, axis=1)
colony["time"] = pd.to_datetime(colony["time"])
colony["period"] = pd.PeriodIndex(pd.to_datetime(colony["time"]), freq='Q').astype("str")

# Setup app and layout/frontend
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([
    html.H1('Bee Colony Dashboard',
    style={'backgroundColor': '#E9AB17', 'font-family':'Roboto', 'textAlign': 'center', 'font-weight':'800'}),
    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id='map-widget',
                value='2020Q1', 
                options=[{'label': period, 'value':  period} for period in colony['period'].unique()],
                placeholder="Select a period")),     
        dbc.Col(
            html.Iframe(
                id='map',
                style={'width': '100%', 'height': '400px', 
                'backgroundColor': '#FBE7A1', 'border': '3px solid #000000', 'border-radius': '10px'}))])
], style={'backgroundColor': '#FFF8DC'})

# Plot the map
@app.callback(
    Output('map', 'srcDoc'),
    Input('map-widget', 'value'))
def plot_altair(period):
    df = colony[colony['period'] == period]
    target_df = pd.merge(state_info, df, how="left", on="state")
    target_df.fillna(0, inplace=True)
    target_df = target_df[['abbr', 'lon', 'lat', 'state', 'id', 'year', 'months', 'colony_n',
       'colony_max', 'colony_lost', 'colony_lost_pct', 'colony_added',
       'colony_reno', 'colony_reno_pct']]
       
    background = alt.Chart(state_map).mark_geoshape(stroke='#706545', strokeWidth=1).transform_lookup(
        lookup='id',
        from_=alt.LookupData(target_df, 'id', ['colony_lost_pct', 'colony_max'])
        ).encode(color='colony_lost_pct:Q').project(type='albersUsa').properties(
            width=400,
            height=300)

    text = alt.Chart(target_df).mark_text().encode(
        longitude='lon:Q',
        latitude='lat:Q',
        color=alt.value('orange'),
        text='colony_lost_pct:Q',
        tooltip=['state:N', 'colony_lost_pct:Q', 'colony_max:Q']
    )

    return (background + text).to_html()
    
if __name__ == '__main__':
    app.run_server(debug=True)