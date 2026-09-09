"""
pages/causes.py — Delay Causes page (registered at "/causes")

The question this page answers:
    "When flights are delayed at this airport, whose fault is it —
    the airline itself, weather, air-traffic congestion, or a chain
    reaction from a late incoming aircraft?"

Visualization: stacked/pie breakdown of total delay-minutes by cause.

Note on the underlying data: the five *_ct columns (carrier_ct,
weather_ct, etc.) are fractional flight-counts assigned by a
BTS-published proration formula, so they will not sum to a whole
number of flights - only the *_delay minute columns are used here to
avoid presenting fractional "flights" as if they were a real count.
"""

import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

from utils.data_loader import load_clean_data, airport_options, carrier_options, CAUSE_COLS
from utils.chart_theme import transparent_bg

dash.register_page(__name__, path="/causes", name="Delay Causes", order=3)

df = load_clean_data()
AIRPORT_OPTIONS = airport_options(df)
CARRIER_OPTIONS = [{"label": "All carriers", "value": "ALL"}] + carrier_options(df)
DEFAULT_AIRPORT = "ATL" if "ATL" in df["airport"].unique() else df["airport"].iloc[0]
MIN_YEAR, MAX_YEAR = int(df["year"].min()), int(df["year"].max())

layout = dbc.Container(
    [
        html.H2("When flights are delayed here, who's responsible?"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Airport"),
                        dcc.Dropdown(
                            id="cause-airport-dropdown",
                            options=AIRPORT_OPTIONS,
                            value=DEFAULT_AIRPORT,
                            clearable=False,
                        ),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        html.Label("Carrier"),
                        dcc.Dropdown(
                            id="cause-carrier-dropdown",
                            options=CARRIER_OPTIONS,
                            value="ALL",
                            clearable=False,
                        ),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        html.Label("Year range"),
                        dcc.RangeSlider(
                            id="cause-year-range",
                            min=MIN_YEAR,
                            max=MAX_YEAR,
                            step=1,
                            value=[MIN_YEAR, MAX_YEAR],
                            marks={y: str(y) for y in range(MIN_YEAR, MAX_YEAR + 1)},
                        ),
                    ],
                    md=4,
                ),
            ],
            className="mb-3 g-3",
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="cause-pie-chart"), md=5),
                dbc.Col(dcc.Graph(id="cause-bar-chart"), md=7),
            ]
        ),
    ],
    fluid=True,
)


@callback(
    Output("cause-pie-chart", "figure"),
    Output("cause-bar-chart", "figure"),
    Input("cause-airport-dropdown", "value"),
    Input("cause-carrier-dropdown", "value"),
    Input("cause-year-range", "value"),
)
def update_causes(airport, carrier, year_range):
    lo, hi = year_range
    subset = df[(df["airport"] == airport) & (df["year"] >= lo) & (df["year"] <= hi)]
    if carrier != "ALL":
        subset = subset[subset["carrier"] == carrier]

    if subset.empty or subset[list(CAUSE_COLS.keys())].sum().sum() == 0:
        empty = go.Figure()
        empty.add_annotation(text="No delay data for this selection", showarrow=False, font=dict(size=18))
        empty = transparent_bg(empty)
        return empty, empty

    totals = subset[list(CAUSE_COLS.keys())].sum().rename(index=CAUSE_COLS).reset_index()
    totals.columns = ["cause", "minutes"]

    pie_fig = px.pie(
        totals, names="cause", values="minutes",
        title="Share of total delay minutes",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Safe,
    )

    monthly = (
        subset.groupby("date", as_index=False)[list(CAUSE_COLS.keys())]
        .sum()
        .rename(columns=CAUSE_COLS)
        .sort_values("date")
    )
    long_monthly = monthly.melt(id_vars="date", var_name="cause", value_name="minutes")
    bar_fig = px.bar(
        long_monthly,
        x="date",
        y="minutes",
        color="cause",
        title="Delay minutes by month, stacked by cause",
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    bar_fig.update_layout(barmode="stack", xaxis_title="Month", yaxis_title="Total delay minutes")
    bar_fig.update_xaxes(gridcolor="#e0e0e0")
    bar_fig.update_yaxes(gridcolor="#e0e0e0")

    return transparent_bg(pie_fig), transparent_bg(bar_fig)