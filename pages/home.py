"""
pages/home.py — Landing page (registered at "/")

A short welcome/hero page introducing the app, linking into the
Overview page where the actual choropleth map lives.
"""

import dash
from dash import html
import dash_bootstrap_components as dbc

from utils.data_loader import load_clean_data

dash.register_page(__name__, path="/", name="Home", order=0)

df = load_clean_data()

# A curated set of recognizable mainline carriers mapped to their logo
# file directly under assets/.
_CARRIER_LOGOS = {
    "Delta Air Lines Network": "delta.png",
    "American Airlines Network": "american.png",
    "United Air Lines Network": "united.png",
    "Southwest Airlines": "southwest.png",
    "Alaska Airlines Network": "alaska.png",
    "JetBlue Airways": "jetblue.png",
    "Spirit Airlines": "spirit.png",
    "Frontier Airlines": "frontier.png",
    "Hawaiian Airlines Network": "hawaiian.png",
    "Allegiant Air": "allegiant.png",
}
_AVAILABLE = set(df["carrier_name"].unique())
TICKER_LOGOS = [(name, file) for name, file in _CARRIER_LOGOS.items() if name in _AVAILABLE]
#Claude provided the code for the moving banner

layout = dbc.Container(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.H1("Flight Delay Explorer"),
                        html.P(
                            "Which airline should you actually book, and is on-time "
                            "performance at your airport getting better or worse? "
                            "Explore three years of US DOT delay-cause data by "
                            "airport, carrier, and cause."
                        ),
                        dbc.Button(
                            "See the Overview",
                            href="/overview",
                            color="warning",
                            size="lg",
                            className="mt-3",
                        ),
                    ],
                    className="hero-text",
                ),
                html.Img(src="/assets/plane.png", className="hero-plane"),
            ],
            className="hero-landing",
        ),
        html.Div(
            html.Div(
                [
                    html.Img(
                        src=f"/assets/{file}",
                        alt="",
                        title=name,
                        className="ticker-logo",
                    )
                    for name, file in TICKER_LOGOS * 2
                ],
                className="ticker-track",
            ),
            className="ticker-wrap",
        ),
    ],
    fluid=True,
)