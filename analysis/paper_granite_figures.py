#!/usr/bin/env python3
"""
Generate paper figures with Granite 3.2 2B added to existing model comparisons.
Matches the style of the original paper's Figure 4, 5, and 8.
"""

import os
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

OUT_DIR = "results/visualizations"
os.makedirs(OUT_DIR, exist_ok=True)

# Load existing experiment data
with open("results/premium_models_2500_samples/premium_models_2500_samples.json") as f:
    data = json.load(f)

results = data["results"]
models = list(data["models"].keys())
y_true = [r["ground_truth"] for r in results]

# Compute existing metrics
metrics = {}

# Consensus
y_cons = [r["consensus_prediction"] for r in results]
metrics["Consensus\n(5 models)"] = {
    "accuracy": accuracy_score(y_true, y_cons),
    "precision": precision_score(y_true, y_cons),
    "recall": recall_score(y_true, y_cons),
    "f1": f1_score(y_true, y_cons),
}

# Individual models
model_labels = {
    "openai": "OPENAI",
    "claude": "CLAUDE",
    "gemini": "GEMINI",
    "llama": "LLAMA",
    "deepseek": "DEEPSEEK",
}
for m in models:
    y_m = [r["model_results"][m]["is_harmful"] for r in results]
    metrics[model_labels[m]] = {
        "accuracy": accuracy_score(y_true, y_m),
        "precision": precision_score(y_true, y_m),
        "recall": recall_score(y_true, y_m),
        "f1": f1_score(y_true, y_m),
    }

# Granite 3.2 2B results
metrics["Granite\n3.2 2B"] = {
    "accuracy": 0.832,
    "precision": 0.833,
    "recall": 0.832,
    "f1": 0.832,
}

# Category data for existing models
categories = ["adversarial_harmful", "adversarial_benign", "vanilla_harmful", "vanilla_benign"]
cat_data_existing = {
    "adversarial_harmful": {
        "Consensus\n(5 models)": 0.6530,
        "OPENAI": 0.9720, "CLAUDE": 0.7250, "GEMINI": 0.5420,
        "LLAMA": 0.2230, "DEEPSEEK": 0.6600,
    },
    "adversarial_benign": {
        "Consensus\n(5 models)": 0.9429,
        "OPENAI": 0.2476, "CLAUDE": 0.7952, "GEMINI": 0.9524,
        "LLAMA": 0.9952, "DEEPSEEK": 0.9619,
    },
    "vanilla_harmful": {
        "Consensus\n(5 models)": 0.8080,
        "OPENAI": 0.9120, "CLAUDE": 0.8400, "GEMINI": 0.8000,
        "LLAMA": 0.7000, "DEEPSEEK": 0.8080,
    },
    "vanilla_benign": {
        "Consensus\n(5 models)": None,  # not in dataset
        "OPENAI": None, "CLAUDE": None, "GEMINI": None,
        "LLAMA": None, "DEEPSEEK": None,
    },
}

# Add Granite category data
granite_cat = {
    "adversarial_harmful": 0.848,
    "adversarial_benign": 0.778,
    "vanilla_harmful": 0.888,
    "vanilla_benign": 0.932,
}

# ================================================================
# Figure 1: Accuracy Bar Chart (like Figure 4)
# ================================================================
fig, ax = plt.subplots(figsize=(14, 6))

bar_order = ["Consensus\n(5 models)", "OPENAI", "CLAUDE", "GEMINI", "LLAMA", "DEEPSEEK", "Granite\n3.2 2B"]
accuracies = [metrics[m]["accuracy"] for m in bar_order]

colors = ["#2ecc71"] + ["#3498db"] * 5 + ["#e74c3c"]
bars = ax.bar(bar_order, accuracies, color=colors, alpha=0.8, edgecolor="black", linewidth=0.8)

# Highlight consensus and granite with border
bars[0].set_edgecolor("#f39c12")
bars[0].set_linewidth(3)
bars[-1].set_edgecolor("#e74c3c")
bars[-1].set_linewidth(3)

for bar, acc in zip(bars, accuracies):
    ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.01,
            f"{acc:.4f}", ha="center", va="bottom", fontsize=10, fontweight="bold")

ax.set_xlabel("Model", fontsize=12, fontweight="bold")
ax.set_ylabel("Accuracy", fontsize=12, fontweight="bold")
ax.set_title("Model Accuracy Comparison: Consensus vs Individual Models vs Granite 3.2 2B",
             fontsize=13, fontweight="bold", pad=15)
ax.set_ylim(0, 1.1)
ax.grid(axis="y", alpha=0.3, linestyle="--")

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "paper_accuracy_with_granite.png"), dpi=300, bbox_inches="tight")
plt.close()
print("Saved: paper_accuracy_with_granite.png")


# ================================================================
# Figure 2: Radar Chart (matplotlib version, like Figure 5)
# ================================================================
metric_names = ["Accuracy", "Precision", "Recall", "F1 Score"]

radar_order = ["Consensus\n(5 models)", "OPENAI", "CLAUDE", "GEMINI", "LLAMA", "DEEPSEEK", "Granite\n3.2 2B"]
radar_colors_mpl = {
    "Consensus\n(5 models)": ("#2ecc71", 0.25),
    "OPENAI": ("#3498db", 0.10),
    "CLAUDE": ("#27ae60", 0.10),
    "GEMINI": ("#9b59b6", 0.10),
    "LLAMA": ("#f1c40f", 0.10),
    "DEEPSEEK": ("#1abc9c", 0.10),
    "Granite\n3.2 2B": ("#e74c3c", 0.25),
}

angles = np.linspace(0, 2 * np.pi, len(metric_names), endpoint=False).tolist()
angles += angles[:1]  # close the polygon

fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))

for m in radar_order:
    vals = [metrics[m]["accuracy"], metrics[m]["precision"],
            metrics[m]["recall"], metrics[m]["f1"]]
    vals += vals[:1]
    color, alpha = radar_colors_mpl[m]
    lw = 2.5 if m in ["Consensus\n(5 models)", "Granite\n3.2 2B"] else 1.2
    label = m.replace("\n", " ")
    ax.plot(angles, vals, linewidth=lw, label=label, color=color)
    ax.fill(angles, vals, alpha=alpha, color=color)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(metric_names, fontsize=14, fontweight="bold")
ax.set_ylim(0, 1)
ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], fontsize=10)
ax.set_title("Model Performance Metrics Comparison", fontsize=16, fontweight="bold", pad=20)
ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), fontsize=10)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "paper_radar_with_granite.png"), dpi=300, bbox_inches="tight")
plt.close()
print("Saved: paper_radar_with_granite.png")


# ================================================================
# Figure 3: Category Breakdown (like Figure 8)
# ================================================================
fig, ax = plt.subplots(figsize=(14, 6))

# Only use categories that exist in both datasets
cats_to_plot = ["adversarial_harmful", "adversarial_benign", "vanilla_harmful", "vanilla_benign"]
cat_labels_display = {
    "adversarial_harmful": "adversarial\nharmful",
    "adversarial_benign": "adversarial\nbenign",
    "vanilla_harmful": "vanilla\nharmful",
    "vanilla_benign": "vanilla\nbenign",
}

bar_models = ["Consensus\n(5 models)", "OPENAI", "CLAUDE", "GEMINI", "LLAMA", "DEEPSEEK", "Granite\n3.2 2B"]
bar_colors_cat = {
    "Consensus\n(5 models)": "#2ecc71",
    "OPENAI": "#f39c12",
    "CLAUDE": "#27ae60",
    "GEMINI": "#e74c3c",
    "LLAMA": "#9b59b6",
    "DEEPSEEK": "#95a5a6",
    "Granite\n3.2 2B": "#c0392b",
}

x = np.arange(len(cats_to_plot))
n_models = len(bar_models)
width = 0.11

for idx, m in enumerate(bar_models):
    accs = []
    for cat in cats_to_plot:
        if m == "Granite\n3.2 2B":
            accs.append(granite_cat.get(cat, 0))
        else:
            val = cat_data_existing.get(cat, {}).get(m)
            accs.append(val if val is not None else 0)

    offset = width * (idx - n_models / 2 + 0.5)
    label = m.replace("\n", " ")
    edgewidth = 2.5 if m in ["Consensus\n(5 models)", "Granite\n3.2 2B"] else 0.5
    edgecolor = "#f39c12" if m == "Consensus\n(5 models)" else ("#c0392b" if m == "Granite\n3.2 2B" else "black")

    bars = ax.bar(x + offset, accs, width, label=label, color=bar_colors_cat[m],
                  alpha=0.8, edgecolor=edgecolor, linewidth=edgewidth)

ax.set_xlabel("Category", fontsize=12, fontweight="bold")
ax.set_ylabel("Accuracy", fontsize=12, fontweight="bold")
ax.set_title("Accuracy by Prompt Category", fontsize=14, fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels([cat_labels_display[c] for c in cats_to_plot])
ax.legend(loc="upper right", fontsize=9, ncol=2)
ax.grid(axis="y", alpha=0.3, linestyle="--")
ax.set_ylim(0, 1.1)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "paper_category_with_granite.png"), dpi=300, bbox_inches="tight")
plt.close()
print("Saved: paper_category_with_granite.png")


print("\n=== All Granite comparison figures generated ===")
