#!/usr/bin/env python3
"""
Generate model accuracy comparison figure replacing OpenAI (lowest accuracy)
with Granite 3.2 2B, using the CORRECT paper dataset (2500 balanced samples).

Uses REAL per-sample Granite predictions from:
  wildguard_vs_premium_full_report.json
which ran Granite on the exact same 2500 prompts — no simulation needed.
"""

import os
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

BASE = os.path.dirname(__file__)

# Load the CORRECT paper dataset (2500 balanced samples)
with open(os.path.join(BASE, "results/paper_used_data/premium_models_2500_samples_clean.json")) as f:
    paper = json.load(f)

# Load real Granite per-sample predictions
with open(os.path.join(BASE, "results/reports/wildguard_vs_premium_full_report.json")) as f:
    granite_report = json.load(f)

OUT_DIR = os.path.join(BASE, "results/visualizations")
os.makedirs(OUT_DIR, exist_ok=True)

paper_results = paper["results"]
granite_results = granite_report["results"]

# Align by prompt — build lookup from granite report
granite_by_prompt = {}
for r in granite_results:
    granite_by_prompt[r["prompt"][:150]] = r

# --- Compute original paper metrics ---
y_true = []
y_preds = {"openai": [], "claude": [], "gemini": [], "llama": [], "deepseek": []}
y_cons_orig = []
granite_preds = []
matched = 0

for pr in paper_results:
    key = pr["prompt"][:150]
    gr = granite_by_prompt.get(key)
    if gr is None:
        continue  # skip unmatched (only ~3 prompts)

    matched += 1
    gt = pr["ground_truth"]
    y_true.append(gt)
    y_cons_orig.append(pr["consensus_prediction"])

    for m in y_preds:
        y_preds[m].append(pr["model_results"][m]["is_harmful"])

    # Real Granite prediction
    granite_preds.append(gr["our_prediction"] == "harmful")

print(f"Matched prompts: {matched} / {len(paper_results)}")

# Original metrics
labels = {"openai": "OPENAI", "claude": "CLAUDE", "gemini": "GEMINI",
          "llama": "LLAMA", "deepseek": "DEEPSEEK"}
metrics = {}
for m, label in labels.items():
    metrics[label] = {
        "accuracy": accuracy_score(y_true, y_preds[m]),
        "precision": precision_score(y_true, y_preds[m]),
        "recall": recall_score(y_true, y_preds[m]),
        "f1": f1_score(y_true, y_preds[m]),
    }

metrics["Consensus\n(5 models)"] = {
    "accuracy": accuracy_score(y_true, y_cons_orig),
}

# Granite metrics (real)
granite_acc = accuracy_score(y_true, granite_preds)
granite_prec = precision_score(y_true, granite_preds)
granite_rec = recall_score(y_true, granite_preds)
granite_f1 = f1_score(y_true, granite_preds)

print(f"\n=== Original Paper Metrics ===")
for name in ["Consensus\n(5 models)", "OPENAI", "CLAUDE", "GEMINI", "LLAMA", "DEEPSEEK"]:
    print(f"  {name.replace(chr(10), ' ')}: accuracy={metrics[name]['accuracy']:.4f}")

print(f"\n=== Granite 3.2 2B (REAL per-sample) ===")
print(f"  accuracy={granite_acc:.4f}, precision={granite_prec:.4f}, "
      f"recall={granite_rec:.4f}, f1={granite_f1:.4f}")

orig_cons_acc = metrics["Consensus\n(5 models)"]["accuracy"]

# --- New consensus: replace LLAMA with Granite (majority vote 3/5) ---
new_consensus = []
for i in range(matched):
    votes_harmful = 0
    # 4 remaining original models (excluding LLAMA)
    for m in ["openai", "claude", "gemini", "deepseek"]:
        if y_preds[m][i]:
            votes_harmful += 1
    # Granite vote
    if granite_preds[i]:
        votes_harmful += 1
    new_consensus.append(votes_harmful >= 3)

new_cons_acc = accuracy_score(y_true, new_consensus)
new_cons_prec = precision_score(y_true, new_consensus)
new_cons_rec = recall_score(y_true, new_consensus)
new_cons_f1 = f1_score(y_true, new_consensus)

delta = new_cons_acc - orig_cons_acc

print(f"\n=== New Consensus (Granite replaces LLAMA) ===")
print(f"  accuracy={new_cons_acc:.4f} (was {orig_cons_acc:.4f}, delta={delta:+.4f})")
print(f"  precision={new_cons_prec:.4f}, recall={new_cons_rec:.4f}, f1={new_cons_f1:.4f}")

# ================================================================
# Figure: Model Accuracy — New Consensus (Granite replaces LLAMA)
# ================================================================
fig, ax = plt.subplots(figsize=(12, 6))

bar_order = ["New\nConsensus", "OPENAI", "CLAUDE", "GEMINI", "DEEPSEEK", "GRANITE\n3.2 2B"]
accuracies = [
    new_cons_acc,
    metrics["OPENAI"]["accuracy"],
    metrics["CLAUDE"]["accuracy"],
    metrics["GEMINI"]["accuracy"],
    metrics["DEEPSEEK"]["accuracy"],
    granite_acc,
]

colors = ["#2ecc71"] + ["#3498db"] * 4 + ["#e74c3c"]
bars = ax.bar(bar_order, accuracies, color=colors, alpha=0.85, edgecolor="black", linewidth=0.8)

bars[0].set_edgecolor("#f39c12")
bars[0].set_linewidth(3)
bars[-1].set_edgecolor("#c0392b")
bars[-1].set_linewidth(3)

for bar, acc in zip(bars, accuracies):
    ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.01,
            f"{acc:.4f}", ha="center", va="bottom", fontsize=11, fontweight="bold")

arrow_color = "#27ae60" if delta >= 0 else "#e74c3c"
box_color = "#eafaf1" if delta >= 0 else "#fdedec"
ax.annotate(
    f"Consensus: {orig_cons_acc:.4f} \u2192 {new_cons_acc:.4f} ({delta:+.4f})",
    xy=(0, new_cons_acc), xytext=(3.5, 0.95),
    fontsize=10, fontweight="bold", color=arrow_color,
    arrowprops=dict(arrowstyle="->", color=arrow_color, lw=1.5),
    bbox=dict(boxstyle="round,pad=0.3", facecolor=box_color, edgecolor=arrow_color),
)

ax.set_xlabel("Model", fontsize=12, fontweight="bold")
ax.set_ylabel("Accuracy", fontsize=12, fontweight="bold")
ax.set_title("Model Accuracy: New Consensus (Granite replaces LLAMA)",
             fontsize=14, fontweight="bold", pad=15)
ax.set_ylim(0, 1.1)
ax.grid(axis="y", alpha=0.3, linestyle="--")

plt.tight_layout()
out_path = os.path.join(OUT_DIR, "beaver_granite_replace_llama_consensus.png")
plt.savefig(out_path, dpi=300, bbox_inches="tight")
plt.close()
print(f"\nSaved: {out_path}")
