import pandas as pd
import altair as alt
from dash import Dash, html, dcc, Input, Output
from ctypes import pointer
import dash_bootstrap_components as dbc

# Data wrangling
colony = pd.read_csv(
    "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-01-11/colony.csv",
)


colony["start_month"] = colony["months"].str.split('-', 1, expand=True)[0]
colony["year"] = colony["year"].astype("str")
colony["time"] = colony[['year', 'start_month']].agg('-'.join, axis=1)
colony["time"] = pd.to_datetime(colony["time"])
colony = colony.drop(["year", "months", "start_month"], axis=1)
colony["period"] = pd.PeriodIndex(pd.to_datetime(colony["time"]), freq='Q').astype("str")

# Dash app
app = Dash(__name__)
server = app.server

app.layout = html.Div(
    [
        html.Iframe(
            id='ncolony_chart',
            style={"border-width": "0", "width": "100%", "height": "400px"}
        ),
        dcc.Dropdown(
            id='state-widget',
            value="Alabama",
            options=[
                {'label': state, 'value': state} for state in colony['state'].unique()
            ],
            placeholder="Select a state..."
        ),
        dcc.Dropdown(
            id='start-date-widget',
            value="2015Q1",
            options=[
                {'label': start_date, 'value': start_date} for start_date in colony['period'].unique()
            ],
            placeholder="Select a start date..."
        ),
        dcc.Dropdown(
            id='end-date-widget',
            value="2015Q4",
            options=[
                {'label': end_date, 'value': end_date} for end_date in colony['period'].unique()
            ],
            placeholder="Select an end date..."
        )
    ]
)

@app.callback(
    Output("ncolony_chart", "srcDoc"),
    Input("state-widget", "value"),
    Input("start-date-widget", "value"),
    Input("end-date-widget", "value")
)
def plot_altair(state_arg, start_date, end_date):
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
        .configure_axis(titleFontSize=20, labelFontSize=14, grid=False)
        .configure_title(fontSize=20)
        .configure_legend(titleFontSize=20, labelFontSize=14)
        .configure_view(strokeWidth=0)
        .properties(width=500, height=250)
    )
    
    return colony_chart.to_html()


if __name__ == '__main__':
    app.run_server(
        port = 8070,
        debug=True)