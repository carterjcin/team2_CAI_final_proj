"""
pages/home.py — Landing page (registered at "/")

A short welcome/hero page introducing the app, linking into the
Overview page where the actual choropleth map lives.
"""

import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/", name="Home", order=0)

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
                html.Img(src="/assets/plane3.png", className="hero-plane"),
            ],
            className="hero-landing",
        ),
    ],
    fluid=True,
)