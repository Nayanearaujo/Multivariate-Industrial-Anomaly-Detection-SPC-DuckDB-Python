"""Export process-context and lineage figures for Notebook 01."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "images"
IMAGES.mkdir(parents=True, exist_ok=True)

NAVY = "#14213D"
TEAL = "#2A9D8F"
GUAVA = "#F08FA0"
SAND = "#F6F1EC"
AMBER = "#E9C46A"
STEEL = "#607A80"


def box(ax, x, y, width, height, label, colour, text_colour="white"):
    patch = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.02,rounding_size=0.04",
        linewidth=1.2, edgecolor=colour, facecolor=colour,
    )
    ax.add_patch(patch)
    ax.text(x + width / 2, y + height / 2, label, ha="center", va="center",
            color=text_colour, weight="bold", fontsize=11)


def arrow(ax, start, end, colour=STEEL, style="->"):
    ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": style, "color": colour, "lw": 2})


def process_context() -> None:
    fig, ax = plt.subplots(figsize=(12, 5.3))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5)
    ax.axis("off")
    ax.set_title("Simplified Tennessee Eastman process context", loc="left", color=NAVY, weight="bold", fontsize=17)

    box(ax, 0.3, 2.0, 1.4, 0.85, "Feeds\nA, C, D, E", GUAVA)
    box(ax, 2.3, 2.0, 1.5, 0.85, "Reactor", TEAL)
    box(ax, 4.4, 2.0, 1.5, 0.85, "Condenser", TEAL)
    box(ax, 6.5, 2.0, 1.6, 0.85, "Separator", TEAL)
    box(ax, 9.1, 2.0, 1.5, 0.85, "Stripper", TEAL)
    box(ax, 9.1, 0.4, 1.5, 0.72, "Products\nG and H", NAVY)
    box(ax, 6.5, 3.55, 1.6, 0.72, "Recycle\ncompressor", AMBER, NAVY)

    arrow(ax, (1.7, 2.43), (2.3, 2.43))
    arrow(ax, (3.8, 2.43), (4.4, 2.43))
    arrow(ax, (5.9, 2.43), (6.5, 2.43))
    arrow(ax, (8.1, 2.43), (9.1, 2.43))
    arrow(ax, (9.85, 2.0), (9.85, 1.12))
    arrow(ax, (7.3, 2.85), (7.3, 3.55))
    ax.annotate("", xy=(3.05, 2.85), xytext=(7.3, 3.91),
                arrowprops={"arrowstyle": "->", "color": STEEL, "lw": 2, "connectionstyle": "arc3,rad=0.12"})

    ax.text(0.3, 0.35, "Monitoring challenge", color=NAVY, weight="bold", fontsize=12)
    ax.text(0.3, 0.05, "Interacting units, feedback control and correlated measurements can distribute one disturbance across many signals.", color=STEEL, fontsize=10.5)
    fig.tight_layout()
    fig.savefig(IMAGES / "01_process_context.png", dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def data_lineage() -> None:
    fig, ax = plt.subplots(figsize=(12, 3.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 3.2)
    ax.axis("off")
    ax.set_title("From publisher source to operating decision", loc="left", color=NAVY, weight="bold", fontsize=17)

    stages = [
        ("Harvard\nDataverse", GUAVA),
        ("RData\nraw layer", STEEL),
        ("Python\nvalidation", TEAL),
        ("Parquet +\nDuckDB", TEAL),
        ("Monitoring\nKPIs", AMBER),
        ("Power BI\ncontrol view", NAVY),
    ]
    x_positions = [0.25, 2.25, 4.25, 6.25, 8.25, 10.25]
    for index, ((label, colour), x) in enumerate(zip(stages, x_positions, strict=True)):
        box(ax, x, 1.25, 1.45, 0.85, label, colour, NAVY if colour == AMBER else "white")
        if index < len(stages) - 1:
            arrow(ax, (x + 1.45, 1.68), (x_positions[index + 1], 1.68))
    ax.text(0.25, 0.45, "Control principle", color=NAVY, weight="bold", fontsize=11)
    ax.text(1.8, 0.45, "Source evidence and transformation logic remain separate from dashboard presentation.", color=STEEL, fontsize=10.5)
    fig.tight_layout()
    fig.savefig(IMAGES / "01_data_to_decision_lineage.png", dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    process_context()
    data_lineage()
    print("Exported Notebook 01 context figures")
