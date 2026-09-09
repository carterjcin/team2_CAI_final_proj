"""
utils/chart_theme.py — shared Plotly styling helper.

Keeps every chart's background transparent so it blends into the
page/card behind it instead of showing Plotly's default pale
lavender plot area.
"""


def transparent_bg(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig
