from ctypes import pointer
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import altair as alt
import pandas as pd
from vega_datasets import data

# Read in global data
colony = pd.read_csv("data/colony.csv")
stressor = pd.read_csv("data/stressor.csv")
state_info = pd.read_csv("data/state_info.csv")
state_map = alt.topo_feature(data.us_10m.url, "states")

# Wrangle data
colony["start_month"] = colony["months"].str.split("-", 1, expand=True)[0]
colony["year"] = colony["year"].astype("str")
colony["time"] = colony[["year", "start_month"]].agg("-".join, axis=1)
colony["time"] = pd.to_datetime(colony["time"])
colony["period"] = pd.PeriodIndex(pd.to_datetime(colony["time"]), freq="Q").astype(
    "str"
)

stressor["start_month"] = stressor["months"].str.split("-", 1, expand=True)[0]
stressor["year"] = stressor["year"].astype("str")
stressor["time"] = stressor[["year", "start_month"]].agg("-".join, axis=1)
stressor["time"] = pd.to_datetime(stressor["time"])
stressor = stressor.drop(["year", "months", "start_month"], axis=1)
stressor["period"] = pd.PeriodIndex(pd.to_datetime(stressor["time"]), freq="Q").astype(
    "str"
)
stressor.loc[stressor["stressor"] == "Disesases", "stressor"] = "Diseases"
stressor.loc[stressor["stressor"] == "Unknown", "stressor"] = "Other"

# Setup app and layout/frontend
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Bee Colony Loss in U.S."
server = app.server
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        # App title
                        html.H1(
                            "Bee Colony Dashboard",
                            style={
                                "backgroundColor": "#E9AB17",
                                "font-family": "Roboto",
                                "textAlign": "center",
                                "font-weight": "800",
                                "border": "2px solid #000000",
                                "border-radius": "5px",
                            },
                        ),
                        # Time period dropdowm menu for map and stressor charts
                        html.H4(
                            "Select the period for the map and stressors...",
                            style={"font-family": "Roboto", "font-weight": "600"},
                        ),
                        dbc.Row(
                            dcc.Dropdown(
                                id="period-widget",
                                value="2020Q1",
                                options=[
                                    {"label": period, "value": period}
                                    for period in colony["period"].unique()
                                ],
                                style={
                                    "height": "50px",
                                    "vertical-align": "middle",
                                    "font-family": "Roboto",
                                    "font-size": "28px",
                                    "textAlign": "center",
                                    "border-radius": "10px",
                                },
                                placeholder="Select a period",
                            )
                        ),
                        html.Br(),
                        # State selection dropdown menu for time-series and stressor charts
                        html.H4(
                            "Select states for the time-series and stressors...",
                            style={"font-family": "Roboto", "font-weight": "600"},
                        ),
                        dbc.Row(
                            dcc.Dropdown(
                                id="state-widget",
                                value=["Alabama", "Arizona"],
                                multi=True,
                                options=[
                                    {"label": state, "value": state}
                                    for state in colony["state"].unique()
                                ],
                                style={
                                    "height": "50px",
                                    "vertical-align": "middle",
                                    "font-family": "Roboto",
                                    "font-size": "28px",
                                    "textAlign": "center",
                                    "border-radius": "10px",
                                },
                                placeholder="Select a state",
                            )
                        ),
                        html.Br(),
                        # Slider for time range of the time-series chart
                        html.H4(
                            "Select the period for the time-series...",
                            style={"font-family": "Roboto", "font-weight": "600"},
                        ),
                        dbc.Row(
                             dcc.RangeSlider(
                                id='time-slider',
                                min=(pd.to_datetime(min(colony["period"])) - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s'),
                                max=(pd.to_datetime(max(colony["period"])) - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s'),
                                marks={
                                        (pd.to_datetime(min(colony["period"])) - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s'): "2015Q1",
                                        (pd.to_datetime("2015-10-01") - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s'): "2015Q4",
                                        (pd.to_datetime("2016-10-01") - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s'): "2016Q4",
                                        (pd.to_datetime("2017-10-01") - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s'): "2017Q4",
                                        (pd.to_datetime("2018-07-01") - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s'): "2018Q3",
                                        (pd.to_datetime("2019-07-01") - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s'): "2019Q3",
                                        (pd.to_datetime("2020-07-01") - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s'): "2020Q3",     
                                        (pd.to_datetime(max(colony["period"])) - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s'): "2021Q2"
                                },
                                value=[
                                    (pd.to_datetime("2017-10-01") - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s'),
                                    (pd.to_datetime("2018-07-01") - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')
                                ]
                            ),
                            className="g-0",
                        ),
                    ],
                    md=6,
                    align="start",
                ),
                html.Br(),
                dbc.Col(
                    # Map of loss percentages
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                [
                                    html.H4(
                                        "Bee Colony Loss Percentages by State",
                                        style={
                                            "font-family": "Roboto",
                                            "font-weight": "600",
                                            "textAlign": "center",
                                            "vertical-align": "middle"
                                        },
                                    ),
                                ],
                            ),
                            dbc.CardBody(
                                dcc.Loading(
                                    html.Iframe(
                                        id="map", 
                                        style={"width": "100%", "height": "320px"}
                                    )
                                )
                            ),
                        ],
                        style={
                            "width": "100%",
                            "height": "400px",
                            "backgroundColor": "#FBE7A1",
                            "border": "2px solid #000000",
                            "border-radius": "5px",
                        },
                    )
                ),
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        # Time-series of number of colonies
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    html.H4(
                                        "Number of Bee Colonies Over Time",
                                        style={
                                            "font-family": "Roboto",
                                            "font-weight": "600",
                                            "textAlign": "center",
                                            "vertical-align": "middle"
                                        },
                                    )
                                ),
                                dbc.CardBody(
                                    dcc.Loading(
                                        html.Iframe(
                                            id="ncolony_chart",
                                            style={"width": "100%", "height": "320px"},
                                        )
                                    )
                                ),
                            ],
                            style={
                                "width": "100%",
                                "height": "400px",
                                "backgroundColor": "#FBE7A1",
                                "border": "2px solid #000000",
                                "border-radius": "5px",
                            },
                        )
                    ],
                    md=6,
                ),
                dbc.Col(
                    [
                        # Stressor bar chart
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    [
                                        html.H4(
                                            "Bee Colony Stressors by State",
                                            style={
                                                "font-family": "Roboto",
                                                "font-weight": "600",
                                                "textAlign": "center",
                                                "vertical-align": "middle"
                                            },
                                        ),
                                    ]
                                ),
                                dbc.CardBody(
                                    [
                                        dcc.Loading(
                                            html.Iframe(
                                                id="stressor_chart",
                                                style={"width": "100%", "height": "320px"},
                                            )
                                        )
                                    ]
                                ),
                            ],
                            style={
                                "width": "100%",
                                "height": "400px",
                                "backgroundColor": "#FBE7A1",
                                "border": "2px solid #000000",
                                "border-radius": "5px",
                            },
                        )
                    ]
                ),
            ]
        ),
        html.Div(
            dbc.Alert(
                [ 
                    html.Hr(),
                    "For more info please visit: ",
                    html.A("Github", href="https://github.com/UBC-MDS/Bee_Colony_Dashboard", className="alert-link"),
                    ],
            color="None"
                )
        )
    ],
    style={"backgroundColor": "#FFF8DC"},
)


# Plot the map
@app.callback(Output("map", "srcDoc"), Input("period-widget", "value"))
def plot_map(period):
    df = colony[colony["period"] == period]
    target_df = pd.merge(state_info, df, how="left", on="state")
    target_df.fillna(0, inplace=True)
    target_df = target_df[
        [
            "abbr",
            "lon",
            "lat",
            "state",
            "id",
            "year",
            "months",
            "colony_n",
            "colony_max",
            "colony_lost",
            "colony_lost_pct",
            "colony_added",
            "colony_reno",
            "colony_reno_pct",
        ]
    ]

    background = (
        alt.Chart(state_map, title='Time Period: ' + period)
        .mark_geoshape(stroke="#706545", strokeWidth=1)
        .transform_lookup(
            lookup="id",
            from_=alt.LookupData(target_df, "id", ["colony_lost_pct", "colony_max"]),
        )
        .encode(
            color=alt.Color(
                "colony_lost_pct:Q", legend=alt.Legend(title="Loss %", padding=10)
            )
        )
        .project(type="albersUsa")
    )

    text = (
        alt.Chart(target_df)
        .mark_text()
        .encode(
            longitude="lon:Q",
            latitude="lat:Q",
            color=alt.value("orange"),
            text="colony_lost_pct:Q",
            tooltip=["state:N", "colony_lost_pct:Q", "colony_max:Q"],
        )
    )

    map_chart = (
        (background + text)
        .configure(background="#fffadc", padding=10)
        .configure_axis(titleFontSize=14, labelFontSize=12, grid=False)
        .configure_title(fontSize=14, align="center", anchor="middle")
        .configure_legend(titleFontSize=14, labelFontSize=12)
        .configure_view(strokeWidth=0)
        .properties(width=400, height=250)
    )

    return map_chart.to_html()


# Plot the time series
@app.callback(
    Output("ncolony_chart", "srcDoc"),
    Input("state-widget", "value"),
    Input("time-slider", "value")
)
def plot_timeseries(state_arg, time_range):# start_date, end_date):
    start_date = pd.to_datetime(time_range[0], unit="s")
    end_date = pd.to_datetime(time_range[1], unit="s")
    colony_chart_line = (
        alt.Chart(
            colony[
                (colony['state'].isin(state_arg))
                & (colony["time"] >= start_date)
                & (colony["time"] <= end_date)
            ]
        )
        .mark_line(
            size=4
        )
        .encode(
            x=alt.X("time", title="Time", axis=alt.Axis(format="%b %Y", labelAngle=30)),
            y=alt.Y(
                "colony_n",
                title="Count",
                axis=alt.Axis(format="s"),
                scale=alt.Scale(zero=False),
            ),
            color=alt.Color("state", legend=None),
            tooltip=alt.Tooltip(["colony_n"], title="Count"),
        )
    )

    colony_chart_point = colony_chart_line.mark_point(
        opacity=1,
        size=50
    ).encode(fill=alt.Fill("state", title="State"))

    colony_chart = (
        (colony_chart_line + colony_chart_point)
        .configure(background="#fffadc", padding=10)
        .configure_axis(titleFontSize=14, labelFontSize=12, grid=False)
        .configure_title(fontSize=14)
        .configure_legend(titleFontSize=14, labelFontSize=12)
        .configure_view(strokeWidth=0)
        .properties(width=400, height=190)
    )

    return colony_chart.to_html()


# Plot the stressors
@app.callback(
    Output("stressor_chart", "srcDoc"),
    Input("state-widget", "value"),
    Input("period-widget", "value")
)
def plot_altair(state_arg, period):
    stressor_chart = (
        alt.Chart(
            stressor[
                (stressor['state'].isin(state_arg))
                & (stressor["period"] == period)
            ],
            title="Time Period: " + period
        )
        .mark_bar()
        .encode(
            x=alt.X(
                "stressor",
                title=None,
                axis=alt.Axis(labelAngle=30),
                sort=["Diseases", "Pesticides", "Varroa mites", "Other pests/parasites", "Other"]
            ),
            y=alt.Y(
                "stress_pct", title="Impacted colonies (%)", axis=alt.Axis(format="s")
            ),
            color=alt.Color("stressor", title="Stressor", legend=None),
            tooltip=[
                alt.Tooltip("stressor", title="Stressor"),
                alt.Tooltip("stress_pct", title="Impacted colonies(%)"),
            ],
            column=alt.Column("state", title=None, header=alt.Header(titleFontSize=14, labelFontSize=12))
        )
        .configure(background="#fffadc", padding=10)
        .configure_axis(titleFontSize=14, labelFontSize=12, grid=False)
        .configure_title(fontSize=14, align="center", anchor="middle")
        .configure_legend(titleFontSize=14, labelFontSize=12)
        .configure_view(strokeWidth=0)
        .properties(width=150, height=140)
    )
    return stressor_chart.to_html()


if __name__ == "__main__":
    app.run_server(port=8070, debug=True)