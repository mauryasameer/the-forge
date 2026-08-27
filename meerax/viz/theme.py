import matplotlib as mpl

MEERAX_BG     = "#0a0a0a"
MEERAX_PANEL  = "#111111"
MEERAX_BORDER = "#1e1e1e"
MEERAX_TEXT   = "#e8e4dc"
MEERAX_MUTED  = "#a09994"
MEERAX_ACCENT = "#c8a96e"
MEERAX_CYBER  = "#00e5cc"

PALETTE = [MEERAX_CYBER, MEERAX_ACCENT, "#a78bfa", "#f472b6", "#34d399", "#38bdf8", "#fb923c"]


def apply_meerax_theme() -> None:
    """Apply the Forge dark theme to all subsequent matplotlib / seaborn figures."""
    mpl.rcParams.update({
        "figure.facecolor":   MEERAX_BG,
        "axes.facecolor":     MEERAX_PANEL,
        "axes.edgecolor":     MEERAX_BORDER,
        "axes.labelcolor":    MEERAX_TEXT,
        "axes.titlecolor":    MEERAX_TEXT,
        "axes.grid":          True,
        "axes.prop_cycle":    mpl.cycler(color=PALETTE),
        "grid.color":         MEERAX_BORDER,
        "grid.linewidth":     0.6,
        "xtick.color":        MEERAX_MUTED,
        "ytick.color":        MEERAX_MUTED,
        "text.color":         MEERAX_TEXT,
        "lines.color":        MEERAX_CYBER,
        "patch.edgecolor":    MEERAX_BORDER,
        "figure.titlesize":   14,
        "axes.titlesize":     12,
        "axes.labelsize":     10,
        "xtick.labelsize":    9,
        "ytick.labelsize":    9,
        "legend.facecolor":   MEERAX_PANEL,
        "legend.edgecolor":   MEERAX_BORDER,
        "legend.labelcolor":  MEERAX_TEXT,
        "font.family":        "monospace",
        "savefig.facecolor":  MEERAX_BG,
        "savefig.dpi":        150,
    })
