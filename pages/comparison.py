"""
pages/comparison.py — Comparison page (registered at "/comparison")

The question this page answers:
    "Out of the airlines that fly out of my airport, which one should
    I actually book to minimize the chance of a late arrival?"

Visualization: a ranked horizontal bar chart.
"""

import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

from utils.data_loader import load_clean_data, airport_options, year_options
from utils.chart_theme import transparent_bg

dash.register_page(__name__, path="/comparison", name="Comparison", order=2)

df = load_clean_data()
AIRPORT_OPTIONS = airport_options(df)
YEAR_OPTIONS = [{"label": "All years", "value": "ALL"}] + year_options(df)
DEFAULT_AIRPORT = "ATL" if "ATL" in df["airport"].unique() else df["airport"].iloc[0]

METRIC_MAP = {
    "delay_rate": ("Delay rate", ".1%"),
    "cancellation_rate": ("Cancellation rate", ".1%"),
    "avg_arr_delay_min": ("Avg arrival delay (minutes)", ".1f"),
}

layout = dbc.Container(
    [
        html.H2("Which Carrier Should You Fly?"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Airport"),
                        dcc.Dropdown(
                            id="cmp-airport-dropdown",
                            options=AIRPORT_OPTIONS,
                            value=DEFAULT_AIRPORT,
                            clearable=False,
                        ),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        html.Label("Year"),
                        dcc.Dropdown(
                            id="cmp-year-dropdown",
                            options=YEAR_OPTIONS,
                            value="ALL",
                            clearable=False,
                        ),
                    ],
                    md=3,
                ),
                dbc.Col(
                    [
                        html.Label("Rank carriers by"),
                        dcc.RadioItems(
                            id="cmp-metric-radio",
                            options=[{"label": f" {v[0]}", "value": k} for k, v in METRIC_MAP.items()],
                            value="delay_rate",
                            inline=False,
                        ),
                    ],
                    md=5,
                ),
            ],
            className="mb-3 g-3",
        ),
        dcc.Graph(id="cmp-bar-chart"),
    ],
    fluid=True,
)


@callback(
    Output("cmp-bar-chart", "figure"),
    Input("cmp-airport-dropdown", "value"),
    Input("cmp-year-dropdown", "value"),
    Input("cmp-metric-radio", "value"),
)
def update_comparison(airport, year, metric):
    subset = df[df["airport"] == airport]
    if year != "ALL":
        subset = subset[subset["year"] == year]

    if subset.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data for this selection", showarrow=False, font=dict(size=18))
        return transparent_bg(fig)

    metric_label, fmt = METRIC_MAP[metric]

    ranked = (
        subset.groupby("carrier_name", as_index=False)
        .agg(
            arr_flights=("arr_flights", "sum"),
            arr_del15=("arr_del15", "sum"),
            arr_cancelled=("arr_cancelled", "sum"),
            arr_delay=("arr_delay", "sum"),
        )
    )
    ranked["delay_rate"] = ranked["arr_del15"] / ranked["arr_flights"]
    ranked["cancellation_rate"] = ranked["arr_cancelled"] / ranked["arr_flights"]
    ranked["avg_arr_delay_min"] = ranked["arr_delay"] / ranked["arr_flights"]
    ranked = ranked.sort_values(metric, ascending=True)

    fig = px.bar(
        ranked,
        x=metric,
        y="carrier_name",
        orientation="h",
        text_auto=fmt,
        labels={metric: metric_label, "carrier_name": "Carrier"},
        title=f"{metric_label} by carrier",
    )
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    fig.update_xaxes(gridcolor="#e0e0e0")
    fig.update_yaxes(gridcolor="#e0e0e0")

    return transparent_bg(fig)