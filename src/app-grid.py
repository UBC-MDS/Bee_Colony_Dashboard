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
    
    dbc.Row([
        dbc.Col([
            html.H1('Bee Colony Dashboard',
                    style={'backgroundColor': '#E9AB17', 'font-family':'Roboto', 'textAlign': 'center', 'font-weight':'800', 'border': '2px solid #000000','border-radius': '5px'}),
            html.H4("Select a state...",
                style={'font-family':'Roboto', 'font-weight':'600'}),
            dbc.Row(dcc.Dropdown(
                id='state-widget',
                value='Alabama', 
                options=[{'label': state, 'value':  state} for state in colony['state'].unique()],
                style={'height': '50px', 'vertical-align': 'middle', 'font-family':'Roboto', 
                'font-size':'28px', 'textAlign': 'center', 
                'border-radius': '10px'}, placeholder="Select a state")),
            html.Br(), 
            html.H4("Select the time period...",
                style={'font-family':'Roboto', 'font-weight':'600'}),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(
                        id='start-date-widget',
                        value='2015Q1', 
                        options=[
                {'label': start_date, 'value': start_date} for start_date in colony['period'].unique()
            ],
                        style={'height': '50px', 'vertical-align': 'middle', 'font-family':'Roboto', 
                    'font-size':'28px', 'textAlign': 'center',
                    'border-radius': '10px'}, placeholder="Select a year")),
                dbc.Col(
                    dcc.Dropdown(
                        id='end-date-widget',
                        value='2015Q4', 
                        options=[
                {'label': end_date, 'value': end_date} for end_date in colony['period'].unique()
            ],
                        style={'height': '50px', 'vertical-align': 'middle', 'font-family':'Roboto', 
                    'font-size':'28px', 'textAlign': 'center',
                    'border-radius': '10px'},  placeholder="Select a time period")),
            ], className="g-0"),
            html.Br(), 
            html.H4("Select the indicator...",
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
        html.Br(),                
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(
                    html.H4("Distribution by state",
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
                )], align="start"),
    html.Br(), 
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    html.H4("Number of bee colonies over time",
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
                    html.H4("Stressor of the bee colonies' lost",
                        style={'font-family':'Roboto',  'font-weight':'600'})
                        ),
                dbc.CardBody(
                    html.Iframe(
                        id='stressor_chart',
                        style={'width': '100%', 'height': '320px' 
                    }))],
                        style={'width': '100%', 'height': '400px', 
                        'backgroundColor': '#FBE7A1', 'border': '2px solid #000000', 'border-radius': '5px', 
                    })
                ])
    ], align="end")
], style={'backgroundColor': '#FFF8DC'})
 

# Plot the map
@app.callback(
    Output('map', 'srcDoc'),
    Input('start-date-widget', 'value'),
    Input('end-date-widget', 'value'),
    Input('indicator-widget', 'value'))
def plot_map(year, month, indicator):
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
    Input("state-widget", "value"),
    Input("start-date-widget", "value"),
    Input("end-date-widget", "value")
)
def plot_timeseries(state_arg, start_date, end_date):
    colony_chart_line = (
        alt.Chart(
            colony[
                (colony["state"] == state_arg)
                & (colony["period"] >= start_date)
                & (colony["period"] <= end_date)
            ],
            title="Number of Colonies"
        )
        .mark_line(size=4, color="black")
        .encode(
            x=alt.X("time", title="Time", axis=alt.Axis(format="%b %Y", labelAngle=30)),
            y=alt.Y("colony_n", title="Count", axis=alt.Axis(format="s"), scale=alt.Scale(zero=False)),
            tooltip=alt.Tooltip(["colony_n"], title="Count")
        )
    )
    
    colony_chart_point = colony_chart_line.mark_point(color="black", fill="black", size=50)
    
    colony_chart = (
        (
            colony_chart_line + colony_chart_point
        )
        .configure(background='#fffadc', padding=20)
        .configure_axis(titleFontSize=14, labelFontSize=12, grid=False)
        .configure_title(fontSize=14)
        .configure_legend(titleFontSize=14, labelFontSize=12)
        .configure_view(strokeWidth=0)
        .properties(width=400, height=180)
    )
    
    return colony_chart.to_html()


# Plot the stressor
@app.callback(
    Output("stressor_chart", "srcDoc"),
    Input("state-widget", "value"),
    Input("start-date-widget", "value"),
    Input("end-date-widget", "value"))
def plot_altair(state_arg, start_date, end_date):
    stressor_chart = (
        alt.Chart(
            stressor[
                (stressor["state"] == state_arg)
                & (stressor["period"] >= start_date)
                & (stressor["period"] <= end_date)
            ], title="Colony Stressors")
        .mark_bar()
        .encode(
            x=alt.X("period", title="Time period"),
            y=alt.Y("stress_pct", title="Impacted colonies (%)", axis=alt.Axis(format="s")),
            color=alt.Color("stressor", title="Stressor"),
            tooltip = [alt.Tooltip('stressor', title = 'Stressor'), alt.Tooltip('stress_pct', title = 'Impacted colonies(%)')]
        )
        .configure(background='#fffadc', padding=20)
        .configure_axis(titleFontSize=14, labelFontSize=12, grid=False)
        .configure_title(fontSize=14)
        .configure_legend(titleFontSize=14, labelFontSize=12)
        .configure_view(strokeWidth=0)
        .properties(width=400, height=180)
    )
    return stressor_chart.to_html()





if __name__ == '__main__':
    app.run_server(
        port = 8070,
        debug=True)