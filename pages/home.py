"""
pages/home.py — Overview page (registered at "/")

The question this page answers:
    "Which states have the worst flight delays right now, and does
    picking a specific airline change the answer?"

Visualization: choropleth map of the US, colored by average arrival
delay rate, filterable by year and carrier.
"""

import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

from utils.data_loader import load_clean_data, carrier_options, year_options

dash.register_page(__name__, path="/", name="Overview")

df = load_clean_data()
CARRIER_OPTIONS = carrier_options(df)
YEAR_OPTIONS = year_options(df)
MIN_YEAR = int(df["year"].min())
MAX_YEAR = int(df["year"].max())

layout = dbc.Container(
    [
        html.H2("Which states have the worst flight delays?"),
        html.P(
            "Arrival delay rate = share of flights that landed 15+ minutes late, "
            "aggregated by the state the destination airport is in. "
            "Data: US DOT / Bureau of Transportation Statistics, Airline Delay Cause "
            f"file, {MIN_YEAR}\u2013{MAX_YEAR}.",
            className="text-muted",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Year range"),
                        dcc.RangeSlider(
                            id="home-year-range",
                            min=MIN_YEAR,
                            max=MAX_YEAR,
                            step=1,
                            value=[MIN_YEAR, MAX_YEAR],
                            marks={y: str(y) for y in range(MIN_YEAR, MAX_YEAR + 1)},
                        ),
                    ],
                    md=7,
                ),
                dbc.Col(
                    [
                        html.Label("Carrier"),
                        dcc.Dropdown(
                            id="home-carrier-dropdown",
                            options=[{"label": "All carriers", "value": "ALL"}] + CARRIER_OPTIONS,
                            value="ALL",
                            clearable=False,
                        ),
                    ],
                    md=5,
                ),
            ],
            className="mb-3 g-3",
        ),
        dbc.Row(id="home-kpi-row", className="mb-3 g-3"),
        dcc.Graph(id="home-choropleth", style={"height": "65vh"}),
    ],
    fluid=True,
)


def _kpi_card(title, value, subtitle=""):
    return dbc.Col(
        dbc.Card(
            dbc.CardBody(
                [
                    html.H6(title, className="card-subtitle text-muted"),
                    html.H3(value, className="card-title"),
                    html.Small(subtitle, className="text-muted"),
                ]
            )
        ),
        md=4,
    )


def _filtered(year_range, carrier):
    lo, hi = year_range
    filtered = df[(df["year"] >= lo) & (df["year"] <= hi)]
    if carrier != "ALL":
        filtered = filtered[filtered["carrier"] == carrier]
    return filtered


@callback(
    Output("home-choropleth", "figure"),
    Input("home-year-range", "value"),
    Input("home-carrier-dropdown", "value"),
)
def update_map(year_range, carrier):
    filtered = _filtered(year_range, carrier)

    if filtered.empty:
        empty_fig = go.Figure(go.Choropleth(locationmode="USA-states"))
        empty_fig.update_layout(
            geo=dict(scope="usa"),
            annotations=[dict(text="No data for this selection", showarrow=False, font_size=18)],
        )
        return empty_fig

    state_stats = (
        filtered.groupby("state", as_index=False)
        .agg(total_flights=("arr_flights", "sum"), total_delayed=("arr_del15", "sum"))
    )
    state_stats["delay_rate"] = (state_stats["total_delayed"] / state_stats["total_flights"]).round(4)

    fig = px.choropleth(
        state_stats,
        locations="state",
        locationmode="USA-states",
        color="delay_rate",
        scope="usa",
        color_continuous_scale="OrRd",
        range_color=(state_stats["delay_rate"].min(), state_stats["delay_rate"].max()),
        labels={"delay_rate": "Delay rate"},
        hover_data={"total_flights": True, "delay_rate": ":.1%"},
    )
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), coloraxis_colorbar=dict(tickformat=".0%"))
    return fig


@callback(
    Output("home-kpi-row", "children"),
    Input("home-year-range", "value"),
    Input("home-carrier-dropdown", "value"),
)
def update_kpis(year_range, carrier):
    filtered = _filtered(year_range, carrier)

    if filtered.empty:
        return [
            _kpi_card("Total flights", "—"),
            _kpi_card("Avg delay rate", "—"),
            _kpi_card("Most delayed state", "—"),
        ]

    state_stats = (
        filtered.groupby("state", as_index=False)
        .agg(total_flights=("arr_flights", "sum"), total_delayed=("arr_del15", "sum"))
    )
    state_stats["delay_rate"] = (state_stats["total_delayed"] / state_stats["total_flights"]).round(4)

    total_flights = int(filtered["arr_flights"].sum())
    overall_rate = filtered["arr_del15"].sum() / filtered["arr_flights"].sum()
    worst_state = state_stats.sort_values("delay_rate", ascending=False).iloc[0]

    return [
        _kpi_card("Total flights", f"{total_flights:,}"),
        _kpi_card("Avg delay rate", f"{overall_rate:.1%}"),
        _kpi_card("Most delayed state", worst_state["state"], f"{worst_state['delay_rate']:.1%} of flights"),
    ]