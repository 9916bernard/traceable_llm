#!/usr/bin/env python3
"""
Paper-quality V1 vs V2 comparison figures.

Generates focused, clean figures for the revised paper section on
hybrid on-chain/off-chain storage architecture.
"""

import os
import json
import glob
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Paths
V1_DATA = "results/blockchain_performance/raw_data"
V2_DATA = "results/blockchain_performance_v2_final/raw_data"
OUT_DIR = "results/visualizations"

os.makedirs(OUT_DIR, exist_ok=True)

# ---------- Load data ----------

def load_successful(data_dir):
    files = sorted(glob.glob(os.path.join(data_dir, "*.json")))
    best, best_n = None, 0
    for f in files:
        with open(f) as fh:
            d = json.load(fh)
        if isinstance(d, list) and len(d) > best_n:
            best, best_n = d, len(d)
    return [r for r in (best or []) if r.get("success")]

v1 = load_successful(V1_DATA)
v2 = load_successful(V2_DATA)
print(f"V1: {len(v1)} txns | V2: {len(v2)} txns")

# V1 metrics
v1_gas = [r["commit"]["gas_used"] for r in v1]
v1_commit = [r["commit"]["timing"]["total_commit_time"] for r in v1]
v1_verify = [r["verification"]["timing"]["total_verification_time"]
             for r in v1 if r.get("verification", {}).get("timing")]
v1_cost_eth = [r["commit"]["gas_cost_eth"] for r in v1]

# V2 metrics
v2_gas = [r["commit"]["gas_used"] for r in v2]
v2_commit = [r["commit"]["total_commit_time"] for r in v2]
v2_verify = [r["verification"]["verify_time"] for r in v2]
v2_cost_eth = [r["commit"]["gas_cost_eth"] for r in v2]
v2_cats = [r["category"] for r in v2]
v2_ipfs_pin = [r["ipfs_pin_time"] for r in v2 if r.get("ipfs_pin_time")]
v2_ipfs_ret = [r["ipfs_retrieve_time"] for r in v2 if r.get("ipfs_retrieve_time")]

# ================================================================
# Figure 1: Gas Usage — V1 vs V2 bar chart (simple, clean)
# ================================================================
fig, ax = plt.subplots(figsize=(7, 5))

means = [np.mean(v1_gas), np.mean(v2_gas)]
stds = [np.std(v1_gas), np.std(v2_gas)]
labels = ['V1\n(Plaintext on-chain)', 'V2\n(Hash + IPFS)']
colors = ['#5B9BD5', '#70AD47']

bars = ax.bar(labels, means, yerr=stds, color=colors, alpha=0.9,
              edgecolor='black', linewidth=0.8, capsize=6, width=0.55)

for bar, m in zip(bars, means):
    ax.text(bar.get_x() + bar.get_width() / 2, m / 2,
            f'{m:,.0f}', ha='center', va='center',
            fontsize=14, fontweight='bold', color='white')

# Reduction arrow
reduction = (1 - means[1] / means[0]) * 100
ax.annotate('', xy=(1, means[1] + stds[1] + 15000),
            xytext=(0, means[0] - stds[0] - 15000),
            arrowprops=dict(arrowstyle='->', color='red', lw=2))
ax.text(0.5, (means[0] + means[1]) / 2,
        f'−{reduction:.1f}%', ha='center', va='center',
        fontsize=15, fontweight='bold', color='red',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='red', alpha=0.9))

ax.set_ylabel('Gas Used per Transaction', fontsize=12, fontweight='bold')
ax.set_title('Gas Usage: V1 vs V2', fontsize=14, fontweight='bold')
ax.set_ylim(0, max(means) * 1.3)
ax.grid(axis='y', alpha=0.3, linestyle='--')
ax.tick_params(axis='x', labelsize=11)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "paper_gas_v1_v2.png"), dpi=300, bbox_inches='tight')
plt.close()
print("Saved: paper_gas_v1_v2.png")


# ================================================================
# Figure 2: V2 Gas by payload size (constant gas proof)
# ================================================================
fig, ax = plt.subplots(figsize=(7, 5))

cat_labels = {'short': 'Short\n(~20 bytes)', 'medium': 'Medium\n(~220 bytes)', 'long': 'Long\n(~1,400 bytes)'}
cat_order = ['short', 'medium', 'long']
cat_colors = ['#5B9BD5', '#FFC000', '#FF6B6B']

cat_means = []
cat_stds = []
for cat in cat_order:
    g = [v2_gas[i] for i in range(len(v2)) if v2_cats[i] == cat]
    cat_means.append(np.mean(g))
    cat_stds.append(np.std(g))

x = np.arange(len(cat_order))
bars = ax.bar(x, cat_means, yerr=cat_stds, color=cat_colors, alpha=0.9,
              edgecolor='black', linewidth=0.8, capsize=6, width=0.55)

for bar, m in zip(bars, cat_means):
    ax.text(bar.get_x() + bar.get_width() / 2, m + 3000,
            f'{m:,.0f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_xticks(x)
ax.set_xticklabels([cat_labels[c] for c in cat_order], fontsize=10)
ax.set_ylabel('Gas Used per Transaction', fontsize=12, fontweight='bold')
ax.set_title('V2 Gas Usage by Prompt Length', fontsize=14, fontweight='bold')
ax.set_ylim(0, max(cat_means) * 1.25)
ax.grid(axis='y', alpha=0.3, linestyle='--')

# Highlight constant line
ax.axhline(y=np.mean(v2_gas), color='red', linestyle='--', linewidth=1.5, alpha=0.7)
ax.text(2.35, np.mean(v2_gas) + 1500, f'Mean: {np.mean(v2_gas):,.0f}',
        fontsize=10, color='red', fontstyle='italic')

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "paper_v2_gas_by_payload.png"), dpi=300, bbox_inches='tight')
plt.close()
print("Saved: paper_v2_gas_by_payload.png")


# ================================================================
# Figure 3: Commit latency comparison (box + histogram combo)
# ================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), gridspec_kw={'width_ratios': [1, 1.3]})

# Left: Box plot
bp = ax1.boxplot([v1_commit, v2_commit],
                  tick_labels=['V1\n(Plaintext)', 'V2\n(Hash + IPFS)'],
                  patch_artist=True, widths=0.45, showmeans=True,
                  meanprops=dict(marker='D', markerfacecolor='red', markersize=7),
                  medianprops=dict(color='black', linewidth=2))

for patch, color in zip(bp['boxes'], ['#5B9BD5', '#70AD47']):
    patch.set_facecolor(color)
    patch.set_alpha(0.8)

for i, (data, label) in enumerate(zip([v1_commit, v2_commit], ['V1', 'V2'])):
    ax1.text(i + 1.25, np.mean(data), f'μ={np.mean(data):.2f}s',
             fontsize=9, va='center', color='red', fontweight='bold')

ax1.set_ylabel('Commit Latency (seconds)', fontsize=12, fontweight='bold')
ax1.set_title('Commit Latency Distribution', fontsize=13, fontweight='bold')
ax1.grid(axis='y', alpha=0.3, linestyle='--')

# Right: V2 histogram with percentile markers
ax2.hist(v2_commit, bins=15, color='#70AD47', alpha=0.8, edgecolor='black', linewidth=0.5)

for p, style, color in [(50, '--', '#5B9BD5'), (90, '--', '#FFC000'), (95, '--', '#FF6B6B')]:
    val = np.percentile(v2_commit, p)
    ax2.axvline(val, color=color, linestyle=style, linewidth=2,
                label=f'P{p} = {val:.1f}s')

mean_val = np.mean(v2_commit)
ax2.axvline(mean_val, color='black', linestyle='-', linewidth=2,
            label=f'Mean = {mean_val:.1f}s')

ax2.set_xlabel('Commit Latency (seconds)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Frequency', fontsize=12, fontweight='bold')
ax2.set_title(f'V2 Commit Latency (n={len(v2_commit)})', fontsize=13, fontweight='bold')
ax2.legend(fontsize=9, loc='upper right')
ax2.grid(axis='y', alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "paper_latency_comparison.png"), dpi=300, bbox_inches='tight')
plt.close()
print("Saved: paper_latency_comparison.png")


# ================================================================
# Figure 4: IPFS lifecycle latency breakdown
# ================================================================
fig, ax = plt.subplots(figsize=(7, 5))

operations = ['Pin\n(store to IPFS)', 'Retrieve\n(fetch from IPFS)', 'Unpin\n(right to erasure)']
means_ipfs = [np.mean(v2_ipfs_pin) if v2_ipfs_pin else 0,
              np.mean(v2_ipfs_ret) if v2_ipfs_ret else 0,
              0.54]  # unpin from our test
stds_ipfs = [np.std(v2_ipfs_pin) if v2_ipfs_pin else 0,
             np.std(v2_ipfs_ret) if v2_ipfs_ret else 0,
             0.0]  # single test
colors_ipfs = ['#70AD47', '#5B9BD5', '#FF6B6B']

bars = ax.barh(operations, means_ipfs, xerr=stds_ipfs, color=colors_ipfs,
               alpha=0.9, edgecolor='black', linewidth=0.8, capsize=4, height=0.5)

for bar, m in zip(bars, means_ipfs):
    ax.text(m + 0.15, bar.get_y() + bar.get_height() / 2,
            f'{m:.2f}s', va='center', fontsize=12, fontweight='bold')

ax.set_xlabel('Latency (seconds)', fontsize=12, fontweight='bold')
ax.set_title('IPFS Operation Latency', fontsize=14, fontweight='bold')
ax.set_xlim(0, max(means_ipfs) * 1.4)
ax.grid(axis='x', alpha=0.3, linestyle='--')
ax.tick_params(axis='y', labelsize=11)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "paper_ipfs_latency.png"), dpi=300, bbox_inches='tight')
plt.close()
print("Saved: paper_ipfs_latency.png")


# ================================================================
# Figure 5: L2 cost projection (V1 vs V2)
# ================================================================
fig, ax = plt.subplots(figsize=(9, 5))

eth_price = 2500
v1_base_usd = np.mean(v1_cost_eth) * eth_price
v2_base_usd = np.mean(v2_cost_eth) * eth_price

networks = ['L1 Mainnet', 'Polygon PoS', 'Arbitrum', 'Optimism', 'Base']
multipliers = [1.0, 0.01, 0.05, 0.05, 0.02]

v1_costs = [v1_base_usd * m for m in multipliers]
v2_costs = [v2_base_usd * m for m in multipliers]

x = np.arange(len(networks))
w = 0.32

bars1 = ax.bar(x - w/2, v1_costs, w, label='V1 (Plaintext)', color='#5B9BD5',
               alpha=0.9, edgecolor='black', linewidth=0.5)
bars2 = ax.bar(x + w/2, v2_costs, w, label='V2 (Hash + IPFS)', color='#70AD47',
               alpha=0.9, edgecolor='black', linewidth=0.5)

# Value labels on L1 bars
for bar, cost in zip(bars1[:1], v1_costs[:1]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f'${cost:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
for bar, cost in zip(bars2[:1], v2_costs[:1]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f'${cost:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Value labels on L2 bars
for bar, cost in zip(bars2[1:], v2_costs[1:]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
            f'${cost:.4f}', ha='center', va='bottom', fontsize=8, rotation=0)

ax.set_ylabel('Cost per Transaction (USD)', fontsize=12, fontweight='bold')
ax.set_title(f'Transaction Cost Across Networks (ETH ≈ ${eth_price})', fontsize=13, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(networks, fontsize=10)
ax.legend(fontsize=10)
ax.set_yscale('log')
ax.set_ylim(0.005, 5)
ax.grid(axis='y', alpha=0.3, linestyle='--', which='both')

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "paper_l2_cost_projection.png"), dpi=300, bbox_inches='tight')
plt.close()
print("Saved: paper_l2_cost_projection.png")


# ================================================================
# Figure 6: End-to-end latency breakdown (stacked bar)
# ================================================================
fig, ax = plt.subplots(figsize=(8, 5))

# V1 breakdown: submit + confirm + verify
v1_submit = [r["commit"]["timing"]["tx_submission_time"] for r in v1]
v1_confirm = [r["commit"]["timing"]["tx_confirmation_time"] for r in v1]

# V2 breakdown: IPFS pin + submit + confirm + verify
v2_submit = [r["commit"]["submit_time"] for r in v2]
v2_confirm = [r["commit"]["confirm_time"] for r in v2]

labels_stack = ['V1 (Plaintext)', 'V2 (Hash + IPFS)']
x_pos = [0, 1]

# Means
v1_stack = [np.mean(v1_submit), np.mean(v1_confirm), np.mean(v1_verify)]
v2_stack = [np.mean(v2_ipfs_pin) if v2_ipfs_pin else 0,
            np.mean(v2_submit), np.mean(v2_confirm), np.mean(v2_verify)]

# V1 stacked bar
bottom = 0
colors_v1 = ['#FFC000', '#5B9BD5', '#70AD47']
labels_v1 = ['TX Submit', 'TX Confirm', 'Verification']
for val, c, lb in zip(v1_stack, colors_v1, labels_v1):
    ax.bar(0, val, bottom=bottom, color=c, edgecolor='black', linewidth=0.5, width=0.5, label=lb)
    if val > 0.3:
        ax.text(0, bottom + val/2, f'{val:.2f}s', ha='center', va='center', fontsize=9, fontweight='bold')
    bottom += val

# V2 stacked bar
bottom = 0
colors_v2 = ['#FF6B6B', '#FFC000', '#5B9BD5', '#70AD47']
labels_v2 = ['IPFS Pin', 'TX Submit', 'TX Confirm', 'Verification']
for val, c, lb in zip(v2_stack, colors_v2, labels_v2):
    lbl = lb if lb == 'IPFS Pin' else None  # avoid duplicate legend
    ax.bar(1, val, bottom=bottom, color=c, edgecolor='black', linewidth=0.5, width=0.5, label=lbl)
    if val > 0.3:
        ax.text(1, bottom + val/2, f'{val:.2f}s', ha='center', va='center', fontsize=9, fontweight='bold')
    bottom += val

# Totals on top
ax.text(0, sum(v1_stack) + 0.3, f'Total: {sum(v1_stack):.2f}s', ha='center', fontsize=10, fontweight='bold')
ax.text(1, sum(v2_stack) + 0.3, f'Total: {sum(v2_stack):.2f}s', ha='center', fontsize=10, fontweight='bold')

ax.set_xticks(x_pos)
ax.set_xticklabels(labels_stack, fontsize=11)
ax.set_ylabel('Latency (seconds)', fontsize=12, fontweight='bold')
ax.set_title('End-to-End Latency Breakdown', fontsize=14, fontweight='bold')
ax.legend(loc='upper right', fontsize=9)
ax.grid(axis='y', alpha=0.3, linestyle='--')
ax.set_xlim(-0.5, 1.7)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "paper_latency_breakdown.png"), dpi=300, bbox_inches='tight')
plt.close()
print("Saved: paper_latency_breakdown.png")

print("\n=== All paper figures generated ===")
