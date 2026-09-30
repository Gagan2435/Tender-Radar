"""Matplotlib charts rendered to PNG bytes (Figure API, so it is safe inside a web server)."""
from io import BytesIO

from matplotlib.figure import Figure

BLUE = "#3b6fd4"


def _png(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight")
    return buf.getvalue()


def _empty(ax):
    ax.text(0.5, 0.5, "No data yet", ha="center", va="center")
    ax.axis("off")


def bar_png(labels, values, title):
    fig = Figure(figsize=(6.4, 3.4))
    ax = fig.subplots()
    if labels:
        ax.barh([l or "Unknown" for l in labels][::-1], list(values)[::-1], color=BLUE)
        ax.set_title(title)
        ax.spines[["top", "right"]].set_visible(False)
    else:
        _empty(ax)
    return _png(fig)


def line_png(xs, ys, title):
    fig = Figure(figsize=(6.4, 3.4))
    ax = fig.subplots()
    if xs:
        ax.plot([str(x) for x in xs], ys, marker="o", color=BLUE)
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=60, labelsize=7)
        ax.spines[["top", "right"]].set_visible(False)
    else:
        _empty(ax)
    return _png(fig)
