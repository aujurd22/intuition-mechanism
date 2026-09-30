"""README figures: four publication-style panels from archived artifacts."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    "figure.dpi": 150, "font.size": 9, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.alpha": 0.25,
})
C = {"blue": "#2563eb", "red": "#dc2626", "green": "#059669",
     "gray": "#6b7280", "orange": "#d97706"}

# ---------------------------------------------------------------- Fig 1
# Six-row theorem: 1/x6 values + census
d_locus = [1, 3, 5, 7, 13, 17]
vals = [8, 12, 20, 32, 104, 200]
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.2))
ax1.bar([str(d) for d in d_locus], vals, color=C["blue"], alpha=0.85)
for d, v in zip(d_locus, vals):
    ax1.text(str(d), v + 4, str(v), ha="center", fontsize=8, fontweight="bold")
ax1.set_xlabel("d")
ax1.set_ylabel("1/x$_6$(i√(d/6))  (exact integer)")
ax1.set_title("Six-row rationality locus (P79/P121)", fontsize=10)
ax1.set_ylim(0, 230)

ax2.barh([0], [100], color=C["green"], alpha=0.85, height=0.5)
ax2.barh([0], [300], color="none", edgecolor=C["gray"], height=0.5)
ax2.axvline(77, color=C["red"], ls="--", lw=1)
ax2.text(78, 0.42, "2-elementary locus closes at d=77", color=C["red"], fontsize=8)
for x, lab in [(1, "1"), (3, "3"), (5, "5"), (7, "7"), (13, "13"), (17, "17")]:
    ax2.plot(x, 0, "o", color=C["blue"], ms=7)
ax2.set_xlim(0, 300)
ax2.set_ylim(-0.6, 0.8)
ax2.set_yticks([])
ax2.set_xlabel("d  (census range)")
ax2.set_title("Census d∈[1,300]: 6 hits, 294 non-hits, 0 errors (P121)", fontsize=10)
fig.tight_layout()
fig.savefig("docs/fig_sixrow.png", bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- Fig 2
# Prefix injection curve (P120) + dose-response (P122-b)
p120 = json.load(open("p120_prefix_sweep.json", encoding="utf-8"))
pf = p120["prefix_first"]
Ls = [50, 100, 200, 400]
y_pf = [pf[str(L)]["top1"] for L in Ls]
y_qf = [p120["question_first"][str(L)]["top1"] for L in Ls]
y_po = [p120["prefix_only"][str(L)]["top1"] for L in Ls]

p122b = json.load(open("p122b_dose_response.json", encoding="utf-8"))
doses = [0.0, 0.2, 0.4, 0.6, 0.8]
lab = ["0", "0.2", "0.4", "0.6", "0.8"]
y_bare = [p122b["q_alone"][str(x)]["top1"] for x in doses]
y_hqq = [p122b["hyb_q_hit"][str(x)]["top1"] for x in doses]
y_hph = [p122b["hyb_pre_hit"][str(x)]["top1"] for x in doses]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.2))
ax1.plot(Ls, y_qf, "s-", color=C["gray"], label="question first")
ax1.plot(Ls, y_po, "^-", color=C["orange"], label="prefix only")
ax1.plot(Ls, y_pf, "o-", color=C["blue"], lw=2, label="prefix first")
ax1.axhline(49.8, color=C["red"], ls=":", lw=1)
ax1.text(405, 46, "bare question\n49.8", color=C["red"], fontsize=7, va="top", ha="right")
ax1.set_xscale("log")
ax1.set_xticks(Ls, ["50", "100", "200", "400"])
ax1.minorticks_off()
ax1.set_xlabel("prefix length (chars)")
ax1.set_ylabel("top-1 retrieval (%)")
ax1.set_title("Context-prefix injection, n=2823 (P120)", fontsize=10)
ax1.legend(fontsize=8, loc="lower right")

ax2.plot(doses, y_hqq, "o-", color=C["green"], label="prefix intact, question hit")
ax2.plot(doses, y_hph, "s-", color=C["orange"], label="prefix hit, question intact")
ax2.plot(doses, y_bare, "d-", color=C["red"], lw=2, label="bare question")
ax2.set_xticks(doses, lab)
ax2.set_xlabel("word-substitution dose")
ax2.set_ylabel("top-1 retrieval (%)")
ax2.set_title("Dose-response: the prefix is the load-bearing asset (P122-b)", fontsize=10)
ax2.legend(fontsize=8, loc="center left")
fig.tight_layout()
fig.savefig("docs/fig_rag.png", bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- Fig 3
# Judge landscape (P131 consolidated)
land = json.load(open("p131_landscape_consolidated.json", encoding="utf-8"))
cells = [
    ("v4.1\nforced", land["v4.1_forced"]["rate"], land["v4.1_forced"]["p"], "carrier"),
    ("v4.1\nabsolute", None, None, "null"),
    ("v4-flash\nforced", land["v4flash_forced"]["rate"], land["v4flash_forced"]["p"], "weak"),
    ("v4-flash\nabsolute", None, None, "carrier"),   # rho 0.609/0.447
    ("doubao\nforced", land["doubao_forced"]["rate"], land["doubao_forced"]["p"], "carrier"),
    ("doubao\nabsolute", None, None, "null"),
    ("kimi\nforced", land["kimi_forced"]["rate"], land["kimi_forced"]["p"], "floor"),
    ("kimi\nabsolute", None, None, "null"),
    ("minimax\nforced", land["minimax_forced"]["rate"], land["minimax_forced"]["p"], "floor"),
    ("minimax\nabsolute", None, None, "null"),
]
fig, ax = plt.subplots(figsize=(9, 3.2))
COLMAP = {"carrier": C["green"], "weak": C["orange"], "floor": C["gray"],
          "null": C["red"]}
xs = np.arange(len(cells))
for i, (lab, rate, p, kind) in enumerate(cells):
    if rate is not None:
        ax.bar(i, rate, color=COLMAP[kind], alpha=0.88, width=0.62)
        ax.text(i, rate + 2, f"{rate:.0f}%", ha="center", fontsize=8,
                fontweight="bold")
    else:
        ax.bar(i, 50, color=COLMAP[kind], alpha=0.25, width=0.62, hatch="//")
        ax.text(i, 53, "ns", ha="center", fontsize=8, color=C["red"])
ax.axhline(50, color="black", lw=1, ls="-")
ax.axhspan(79, 90, color=C["green"], alpha=0.08)
ax.text(9.45, 84.5, "carrier band", fontsize=7, color=C["green"], ha="right")
ax.set_xticks(xs, [c[0] for c in cells], fontsize=7.5)
ax.set_ylim(0, 100)
ax.set_ylabel("gdepth-agreement rate (%)")
ax.set_title("Judge landscape: structural signal is model × format (P128-c/P130/P131)", fontsize=10)
fig.tight_layout()
fig.savefig("docs/fig_landscape.png", bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- Fig 4
# Memory geometry: eviction policies + coverage boundary
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.2))
pol = ["core-first", "LRU", "random", "fringe-first"]
twoscale = [100, 92.4, 92.4, 53.6]
squad = [42.5, 30.0, 38.2, 30.0]
x = np.arange(4)
ax1.bar(x - 0.18, twoscale, 0.36, label="synthetic twoscale (P72)", color=C["blue"], alpha=0.85)
ax1.bar(x + 0.18, squad, 0.36, label="SQuAD (P90)", color=C["orange"], alpha=0.85)
ax1.set_xticks(x, pol)
ax1.set_ylabel("retention accuracy (%)")
ax1.set_title("Eviction laws on two substrates (L6)", fontsize=10)
ax1.legend(fontsize=8)

# coverage boundary: STR vs R/mind (P52/P65 reading)
rm = np.array([0.0, 0.25, 0.45, 0.50, 0.55, 0.65, 0.85, 1.0])
strv = np.array([0.0, 92.3, 47.9, 50.0, 14.0, 0.6, 0.0, 0.0])
ax2.plot(rm, strv, "o-", color=C["blue"], lw=2)
ax2.axvline(0.5, color=C["red"], ls="--", lw=1)
ax2.text(0.505, 80, "R/mind = 0.500\nviability boundary", color=C["red"], fontsize=8)
ax2.set_xlabel("R / mind  (resource ratio)")
ax2.set_ylabel("STR (%)")
ax2.set_title("Coverage law: prototype viability boundary (P52/P65)", fontsize=10)
ax2.set_ylim(-5, 100)
fig.tight_layout()
fig.savefig("docs/fig_geometry.png", bbox_inches="tight")
plt.close(fig)

print("figures written: docs/fig_sixrow.png, fig_rag.png, fig_landscape.png, fig_geometry.png")
