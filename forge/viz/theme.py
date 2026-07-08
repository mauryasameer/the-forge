import matplotlib as mpl

FORGE_BG     = "#0a0a0a"
FORGE_PANEL  = "#111111"
FORGE_BORDER = "#1e1e1e"
FORGE_TEXT   = "#e8e4dc"
FORGE_MUTED  = "#a09994"
FORGE_ACCENT = "#c8a96e"
FORGE_CYBER  = "#00e5cc"

PALETTE = [FORGE_CYBER, FORGE_ACCENT, "#a78bfa", "#f472b6", "#34d399", "#38bdf8", "#fb923c"]


def apply_forge_theme() -> None:
    """Apply the Forge dark theme to all subsequent matplotlib / seaborn figures."""
    mpl.rcParams.update({
        "figure.facecolor":   FORGE_BG,
        "axes.facecolor":     FORGE_PANEL,
        "axes.edgecolor":     FORGE_BORDER,
        "axes.labelcolor":    FORGE_TEXT,
        "axes.titlecolor":    FORGE_TEXT,
        "axes.grid":          True,
        "axes.prop_cycle":    mpl.cycler(color=PALETTE),
        "grid.color":         FORGE_BORDER,
        "grid.linewidth":     0.6,
        "xtick.color":        FORGE_MUTED,
        "ytick.color":        FORGE_MUTED,
        "text.color":         FORGE_TEXT,
        "lines.color":        FORGE_CYBER,
        "patch.edgecolor":    FORGE_BORDER,
        "figure.titlesize":   14,
        "axes.titlesize":     12,
        "axes.labelsize":     10,
        "xtick.labelsize":    9,
        "ytick.labelsize":    9,
        "legend.facecolor":   FORGE_PANEL,
        "legend.edgecolor":   FORGE_BORDER,
        "legend.labelcolor":  FORGE_TEXT,
        "font.family":        "monospace",
        "savefig.facecolor":  FORGE_BG,
        "savefig.dpi":        150,
    })
