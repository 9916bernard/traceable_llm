#!/usr/bin/env python3
"""Inter-model error correlation analysis for the Multi-LLM Agreement layer.

Addresses Reviewer 2 (BLC-2025-11-0234.R1) comments 3.4 and suggestion #2:
quantify whether the independent LLMs make *correlated* errors, which bears
directly on the model-diversity assumption underlying majority-vote consensus.

Data source (tracked in repo):
    analysis/results/paper_used_data/premium_models_2500_samples_clean.json
    -> 2,500 WildJailbreak prompts x 5 models, with per-model correctness.

Method:
    For each prompt i and model m define an *error indicator*
        e_{i,m} = 1 if model m's harmful/safe prediction is wrong, else 0.
    The pairwise error correlation is the phi coefficient (Pearson on the
    binary error vectors). High positive phi => the two models tend to fail on
    the same prompts (redundant, weak diversity); phi near 0 => independent
    failures (the regime majority voting relies on).

Outputs:
    - Figure 20 heatmap (PNG) -> paper_data/figures/ and paper/Images/
    - text + CSV report with the full matrix and summary statistics
"""
import json
import os
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DATA = os.path.join(ROOT, "analysis", "results", "paper_used_data",
                    "premium_models_2500_samples_clean.json")
FIG_DIR = os.path.join(ROOT, "paper_data", "figures")
PAPER_IMG = os.path.join(ROOT, "paper", "Images")

# Display order / labels matching the manuscript
MODEL_ORDER = ["openai", "claude", "gemini", "llama", "deepseek"]
LABELS = {
    "openai": "GPT-3.5",
    "claude": "Claude 3 Haiku",
    "gemini": "Gemini 2.5\nFlash-Lite",
    "llama": "Llama 3.1 8B",
    "deepseek": "DeepSeek",
}


def load_error_matrix(path):
    d = json.load(open(path))
    models = [m for m in MODEL_ORDER if m in d["models"]]
    results = d["results"]
    n = len(results)
    # E[i, j] = 1 if model j wrong on prompt i
    E = np.zeros((n, len(models)), dtype=float)
    for i, r in enumerate(results):
        ia = r["individual_accuracy"]
        for j, m in enumerate(models):
            # individual_accuracy True == correct -> error = not correct
            E[i, j] = 0.0 if ia.get(m) else 1.0
    return models, E, d


def phi_matrix(E):
    """Pairwise phi (Pearson) correlation of binary error vectors."""
    k = E.shape[1]
    C = np.eye(k)
    for a in range(k):
        for b in range(a + 1, k):
            xa, xb = E[:, a], E[:, b]
            # guard against zero variance
            if xa.std() == 0 or xb.std() == 0:
                r = 0.0
            else:
                r = float(np.corrcoef(xa, xb)[0, 1])
            C[a, b] = C[b, a] = r
    return C


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    models, E, d = load_error_matrix(DATA)
    err_rate = E.mean(axis=0)
    C = phi_matrix(E)

    # summary stats over off-diagonal entries
    k = len(models)
    off = [C[a, b] for a in range(k) for b in range(a + 1, k)]
    off = np.array(off)

    # ---- heatmap (Figure 20) ----
    disp = [LABELS[m] for m in models]
    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    # diverging map centred at 0: blue = anti-correlated (diverse errors, good),
    # red = positively correlated (redundant failures, weak diversity)
    im = ax.imshow(C, cmap="RdBu_r", vmin=-1.0, vmax=1.0)
    ax.set_xticks(range(k)); ax.set_yticks(range(k))
    ax.set_xticklabels(disp, rotation=30, ha="right", fontsize=9)
    ax.set_yticklabels(disp, fontsize=9)
    for a in range(k):
        for b in range(k):
            val = C[a, b]
            ax.text(b, a, f"{val:.2f}", ha="center", va="center",
                    color="white" if abs(val) > 0.6 else "black", fontsize=10)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Error correlation ($\\phi$)", fontsize=10)
    ax.set_title("Inter-model error correlation\n(2,500 WildJailbreak prompts)",
                 fontsize=11)
    fig.tight_layout()
    for outdir in (FIG_DIR, PAPER_IMG):
        os.makedirs(outdir, exist_ok=True)
        fig.savefig(os.path.join(outdir, "Figure 20.png"), dpi=300,
                    bbox_inches="tight")
    plt.close(fig)

    # ---- text + CSV report ----
    rep = os.path.join(HERE, "inter_model_error_correlation_report.txt")
    with open(rep, "w") as f:
        f.write("Inter-Model Error Correlation Analysis\n")
        f.write("=" * 50 + "\n")
        f.write(f"source: {os.path.relpath(DATA, ROOT)}\n")
        f.write(f"samples: {E.shape[0]}   models: {models}\n\n")
        f.write("Per-model error rate (1 - accuracy):\n")
        for m, e in zip(models, err_rate):
            f.write(f"  {m:10s} {100*e:5.2f}%\n")
        f.write("\nPairwise error correlation (phi):\n      ")
        f.write("".join(f"{m[:7]:>9s}" for m in models) + "\n")
        for a, m in enumerate(models):
            f.write(f"{m[:6]:>6s}" + "".join(f"{C[a,b]:9.3f}" for b in range(k)) + "\n")
        f.write("\nOff-diagonal summary:\n")
        f.write(f"  mean phi   = {off.mean():.3f}\n")
        f.write(f"  median phi = {np.median(off):.3f}\n")
        f.write(f"  min phi    = {off.min():.3f}\n")
        f.write(f"  max phi    = {off.max():.3f}\n")
        # identify most/least correlated pair
        amax = max(((a, b) for a in range(k) for b in range(a+1, k)),
                   key=lambda ab: C[ab[0], ab[1]])
        amin = min(((a, b) for a in range(k) for b in range(a+1, k)),
                   key=lambda ab: C[ab[0], ab[1]])
        f.write(f"  most correlated pair : {models[amax[0]]}-{models[amax[1]]} "
                f"({C[amax[0],amax[1]]:.3f})\n")
        f.write(f"  least correlated pair: {models[amin[0]]}-{models[amin[1]]} "
                f"({C[amin[0],amin[1]]:.3f})\n")

    csvp = os.path.join(HERE, "inter_model_error_correlation_matrix.csv")
    with open(csvp, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([""] + models)
        for a, m in enumerate(models):
            w.writerow([m] + [f"{C[a,b]:.4f}" for b in range(k)])

    print(open(rep).read())
    print(f"figure -> {os.path.join(FIG_DIR, 'Figure 20.png')}")
    print(f"figure -> {os.path.join(PAPER_IMG, 'Figure 20.png')}")


if __name__ == "__main__":
    main()
