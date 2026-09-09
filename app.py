"""
app.py — Flight Delay Explorer

--------------------------------------------------------------------
Used Claude to: brainstorm the dataset/page structure, scaffold the
Dash multi-page layout and callbackw, and draft the data
cleaning steps in utils/data_loader.py. All code was reviewed, run,
and edited by the team; callback logic, chart choices, and the
written analysis/narrative were verified against the actual data
before submission.
--------------------------------------------------------------------

"""

import dash
from dash import Dash, html
import dash_bootstrap_components as dbc

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True,
    title="Flight Delay Explorer",
)

# exposed for gunicorn / Render deployment: `gunicorn app:server`
server = app.server

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink(page["name"], href=page["path"]))
        for page in dash.page_registry.values()
    ],
    brand="Flight Delay Explorer",
    brand_href="/",
    color="primary",
    dark=True,
    className="mb-3",
)

app.layout = html.Div(
    [
        navbar,
        dbc.Container(dash.page_container, fluid=True, className="pb-5"),
    ]
)

if __name__ == "__main__":
    app.run(debug=True)
