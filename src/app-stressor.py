import pandas as pd
import altair as alt
from dash import Dash, html, dcc, Input, Output

# Data wrangling
stressor = pd.read_csv(
    "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-01-11/stressor.csv")

stressor["start_month"] = stressor["months"].str.split('-', 1, expand=True)[0]
stressor["year"] = stressor["year"].astype("str")
stressor["time"] = stressor[['year', 'start_month']].agg('-'.join, axis=1)
stressor["time"] = pd.to_datetime(stressor["time"])
stressor = stressor.drop(["year", "months", "start_month"], axis=1)
stressor["period"] = pd.PeriodIndex(pd.to_datetime(stressor["time"]), freq='Q').astype("str")

# Dash app
app = Dash(__name__)
server = app.server

app.layout = html.Div(
    [
        html.Iframe(
            id='stressor_chart',
            style={"border-width": "0", "width": "100%", "height": "400px"}
        ),
        html.P('State'),
        dcc.Dropdown(
            id='state-widget',
            value="Alabama",
            options=[
                {'label': state, 'value': state} for state in stressor['state'].unique()
            ],
            placeholder="Select a state..."
        ),
        html.P('Start time'),
        dcc.Dropdown(
            id='starttime-widget',
            value="2015Q1",
            options=[
                {'label': start_date, 'value': start_date} for start_date in stressor['period'].unique()
            ],
            placeholder="Select start time period"
        ),
        html.P('End time'),
        dcc.Dropdown(
            id='endtime-widget',
            value="2016Q1",
            options=[
                {'label': end_date, 'value': end_date} for end_date in stressor['period'].unique()
            ],
            placeholder="Select end time period"
        )
    ]
)

@app.callback(
    Output("stressor_chart", "srcDoc"),
    Input("state-widget", "value"),
    Input("starttime-widget", "value"),
    Input("endtime-widget", "value"))
    
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
        .configure_axis(titleFontSize=14, labelFontSize=14, grid=False)
        .configure_legend(titleFontSize=14, labelFontSize=14)
        .properties(width=500)
    )
    return stressor_chart.to_html()


if __name__ == '__main__':
    app.run_server(
        port = 8070,
        debug=True)