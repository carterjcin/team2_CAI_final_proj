"""
utils/chart_theme.py — shared Plotly styling helper.

Keeps every chart's background transparent so it blends into the
page/card behind it instead of showing Plotly's default pale
lavender plot area, and gives categorical charts a color map that
matches the app's blue/orange brand palette (assets/style.css)
instead of Plotly's default qualitative colors.
"""

# Matches the CSS custom properties in assets/style.css.
# One orange accent (the airline's own fault) plus a blue ramp for
# the rest, instead of Plotly's default red/green/purple mix.
CAUSE_COLOR_MAP = {
    "Carrier": "#ff9f45",
    "Late Aircraft": "#1a56c9",
    "National Air System": "#4f8ff5",
    "Weather": "#8fc4ff",
    "Security": "#0d2b4a",
}


def transparent_bg(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig