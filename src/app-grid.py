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

# Wrangle data
colony["start_month"] = colony["months"].str.split('-', 1, expand=True)[0]
colony["year"] = colony["year"].astype("str")
colony["time"] = colony[['year', 'start_month']].agg('-'.join, axis=1)
colony["time"] = pd.to_datetime(colony["time"])
colony["period"] = pd.PeriodIndex(pd.to_datetime(colony["time"]), freq='Q').astype("str")

stressor["start_month"] = stressor["months"].str.split('-', 1, expand=True)[0]
stressor["year"] = stressor["year"].astype("str")
stressor["time"] = stressor[['year', 'start_month']].agg('-'.join, axis=1)
stressor["time"] = pd.to_datetime(stressor["time"])
stressor = stressor.drop(["year", "months", "start_month"], axis=1)
stressor["period"] = pd.PeriodIndex(pd.to_datetime(stressor["time"]), freq='Q').astype("str")



# Setup app and layout/frontend
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.layout = dbc.Container([
    html.H1('Bee Colony Dashboard',
    style={'backgroundColor': '#E9AB17', 'font-family':'Roboto', 'textAlign': 'center', 'font-weight':'800'}),
    dbc.Row([
        dbc.Col([
            html.H3("Select a state...",
                style={'font-family':'Roboto', 'font-weight':'600'}),
            dbc.Row(dcc.Dropdown(
                id='state-widget',
                value='Alabama', 
                options=[{'label': state, 'value':  state} for state in colony['state'].unique()],
                style={'height': '50px', 'vertical-align': 'middle', 'font-family':'Roboto', 
                'font-size':'28px', 'textAlign': 'center', 
                'border-radius': '10px'}, placeholder="Select a state")),
            html.H3("Select the time period...",
                style={'font-family':'Roboto', 'font-weight':'600'}),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(
                        id='year-widget',
                        value='2021', 
                        options=[{'label': col, 'value': col} for col in colony['year'].unique()],
                        style={'height': '50px', 'vertical-align': 'middle', 'font-family':'Roboto', 
                    'font-size':'28px', 'textAlign': 'center',
                    'border-radius': '10px'}, placeholder="Select a year")),
                dbc.Col(
                    dcc.Dropdown(
                        id='month-widget',
                        value='January-March', 
                        options=[{'label': col, 'value': col} for col in colony['months'].unique()],
                        style={'height': '50px', 'vertical-align': 'middle', 'font-family':'Roboto', 
                    'font-size':'28px', 'textAlign': 'center',
                    'border-radius': '10px'},  placeholder="Select a time period")),
            ], className="g-0"),
            html.H3("Select the indicator...",
                style={'font-family':'Roboto', 'font-weight':'600'}),
            dbc.Row(dcc.Dropdown(
                id='indicator-widget',
                value='colony_lost_pct', 
                options=[{'label': col, 'value': col} for col in list(set(colony.columns) - set(['year', 'months', 'state']))],
                style={'height': '50px', 'vertical-align': 'middle', 'font-family':'Roboto', 
                'font-size':'28px', 'textAlign': 'center',
                'border-radius': '10px'}, placeholder="Select a indicator")),                
            
                ], 
            md=6, align="start", ),                
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(
                    html.H5("Distribution by state",
                        style={'font-family':'Roboto',  'font-weight':'600'}),
                        ),
                dbc.CardBody(
                    html.Iframe(
                        id='map',
                        style={'width': '100%', 'height': '320px' 
                    }))],
                        style={'width': '100%', 'height': '400px', 
                        'backgroundColor': '#FBE7A1', 'border': '2px solid #000000', 'border-radius': '5px', 
                    })
                )], align="start",),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    html.H5("Number of bee colonies over time",
                        style={'font-family':'Roboto',  'font-weight':'600'})
                        ),
                dbc.CardBody(
                    html.Iframe(
                        id='ncolony_chart',
                        style={'width': '100%', 'height': '320px' 
                    }))],
                        style={'width': '100%', 'height': '400px', 
                        'backgroundColor': '#FBE7A1', 'border': '2px solid #000000', 'border-radius': '5px', 
                    })
        ],
                md=6),                
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    html.H5("Stressor of the bee colonies' lost",
                        style={'font-family':'Roboto',  'font-weight':'600'})
                        ),
                dbc.CardBody(
                    html.Iframe(
                        id='scatter2',
                        style={'width': '100%', 'height': '320px' 
                    }))],
                        style={'width': '100%', 'height': '400px', 
                        'backgroundColor': '#FBE7A1', 'border': '2px solid #000000', 'border-radius': '5px', 
                    })
                ])
    ], align="end",)
], style={'backgroundColor': '#FFF8DC'})
 

# Plot the map
@app.callback(
    Output('map', 'srcDoc'),
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
        height=350
    )

    text = alt.Chart(target_df).mark_text().encode(
        longitude='lon:Q',
        latitude='lat:Q',
        color=alt.value('orange'),
        text=indicator + ':Q',
        tooltip=['state:N', 'colony_max:Q', 'colony_lost_pct:Q']
    )
    return (background + text).to_html()

# Plot the time series
@app.callback(
    Output("ncolony_chart", "srcDoc"),
    Input("state-widget", "value"))
def plot_altair(state_arg):
    colony_chart = (
        alt.Chart(colony[colony["state"].isin([state_arg])], title="Num")
        .mark_line()
        .encode(
            x=alt.X("time", title="Time period"),
            y=alt.Y("colony_n", title="Number of colonies", axis=alt.Axis(format="s")),
            color=alt.Color("state", title="State"),
        )
        .configure_axis(titleFontSize=20, labelFontSize=14, grid=False)
        .configure_legend(titleFontSize=20, labelFontSize=14)
        .properties(width=400,
        height=290)
    )
    return colony_chart.to_html()

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