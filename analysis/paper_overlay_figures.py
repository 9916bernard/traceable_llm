#!/usr/bin/env python3
"""
Overlay V2 data onto existing V1-style paper figures.
Matches the style of the original paper's Figure 10 and Figure 11.
"""

import os
import json
import glob
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

V1_DATA = "results/blockchain_performance/raw_data"
V2_DATA = "results/blockchain_performance_v2_final/raw_data"
OUT_DIR = "results/visualizations"
os.makedirs(OUT_DIR, exist_ok=True)


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
v1_commit = [r["commit"]["timing"]["total_commit_time"] for r in v1]
v1_verify = [r["verification"]["timing"]["total_verification_time"]
             for r in v1 if r.get("verification", {}).get("timing")]
v1_gas = [r["commit"]["gas_used"] for r in v1]

# V2 metrics
v2_commit = [r["commit"]["total_commit_time"] for r in v2]
v2_verify = [r["verification"]["verify_time"] for r in v2]
v2_gas = [r["commit"]["gas_used"] for r in v2]


# ================================================================
# Figure 1: Commit Latency Distribution — V1 and V2 side by side
# (Original: Figure 10 in paper)
# ================================================================
PAPER_DIR = os.path.join(os.path.dirname(__file__), '..', 'paper', 'Images')
os.makedirs(PAPER_DIR, exist_ok=True)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

bins = 20
props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)

# V1
ax1.hist(v1_commit, bins=bins, color='#4E79A7', alpha=0.7, edgecolor='black', linewidth=0.8)
v1_stats = f'Mean: {np.mean(v1_commit):.3f}\nMedian: {np.median(v1_commit):.3f}\nStd: {np.std(v1_commit):.3f}'
ax1.text(0.95, 0.95, v1_stats, transform=ax1.transAxes, fontsize=10,
         verticalalignment='top', horizontalalignment='right', bbox=props)
ax1.set_xlabel('Commit Time (seconds)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Frequency', fontsize=12, fontweight='bold')
ax1.set_title(f'V1 Plaintext (n={len(v1_commit)})', fontsize=13, fontweight='bold')
ax1.grid(axis='y', alpha=0.3, linestyle='--')

# V2
ax2.hist(v2_commit, bins=bins, color='#59A14F', alpha=0.7, edgecolor='black', linewidth=0.8)
v2_stats = f'Mean: {np.mean(v2_commit):.3f}\nMedian: {np.median(v2_commit):.3f}\nStd: {np.std(v2_commit):.3f}'
ax2.text(0.95, 0.95, v2_stats, transform=ax2.transAxes, fontsize=10,
         verticalalignment='top', horizontalalignment='right', bbox=props)
ax2.set_xlabel('Commit Time (seconds)', fontsize=12, fontweight='bold')
ax2.set_title(f'V2 Hash+IPFS (n={len(v2_commit)})', fontsize=13, fontweight='bold')
ax2.grid(axis='y', alpha=0.3, linestyle='--')

fig.suptitle('Commit Latency Distribution', fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
path = os.path.join(PAPER_DIR, "commit_latency_v1_v2_side_by_side.png")
plt.savefig(path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved: {path}")


# ================================================================
# Figure 2: Latency Over Time — V1 and V2 side by side
# (Original: Figure 11 in paper)
# ================================================================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=False, sharey=True)

# V1 panel
x_v1 = range(1, len(v1_commit) + 1)
ax1.plot(x_v1, v1_commit, 'o-', color='#4E79A7', markersize=4, linewidth=1.2,
         alpha=0.8, label='Commit Latency')
ax1.plot(x_v1[:len(v1_verify)], v1_verify, 's-', color='#E15759', markersize=4,
         linewidth=1.2, alpha=0.8, label='Verification Latency')
ax1.set_ylabel('Time (seconds)', fontsize=12, fontweight='bold')
ax1.set_title(f'V1 Plaintext On-Chain (n={len(v1_commit)})', fontsize=13, fontweight='bold')
ax1.legend(fontsize=10, loc='upper right')
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.set_xlabel('Test Number', fontsize=12, fontweight='bold')

# V2 panel
x_v2 = range(1, len(v2_commit) + 1)
ax2.plot(x_v2, v2_commit, 'o-', color='#59A14F', markersize=4, linewidth=1.2,
         alpha=0.8, label='Commit Latency')
ax2.plot(x_v2[:len(v2_verify)], v2_verify, 's-', color='#E15759', markersize=4,
         linewidth=1.2, alpha=0.8, label='Verification Latency')
ax2.set_xlabel('Test Number', fontsize=12, fontweight='bold')
ax2.set_ylabel('Time (seconds)', fontsize=12, fontweight='bold')
ax2.set_title(f'V2 Hash + IPFS (n={len(v2_commit)})', fontsize=13, fontweight='bold')
ax2.legend(fontsize=10, loc='upper right')
ax2.grid(True, alpha=0.3, linestyle='--')

plt.tight_layout()
path = os.path.join(OUT_DIR, "paper_latency_over_time_v1_v2.png")
plt.savefig(path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved: {path}")


# ================================================================
# Figure 3: Gas Usage Distribution — V1 and V2 overlaid
# (New figure, same style as Figure 10)
# ================================================================
fig, ax = plt.subplots(figsize=(10, 6))

# V1 gas has wide variance, V2 is nearly constant
# Use shared bins across full range
all_gas = v1_gas + v2_gas
gas_min = min(all_gas) - 20000
gas_max = max(all_gas) + 20000
bins_gas = np.linspace(gas_min, gas_max, 25)

ax.hist(v1_gas, bins=bins_gas, alpha=0.6, color='#4E79A7', edgecolor='black',
        linewidth=0.8, label=f'V1 Plaintext (n={len(v1_gas)})')
ax.hist(v2_gas, bins=bins_gas, alpha=0.6, color='#59A14F', edgecolor='black',
        linewidth=0.8, label=f'V2 Hash+IPFS (n={len(v2_gas)})')

# Stats box
v1_g_text = f'V1 — Mean: {np.mean(v1_gas):,.0f}\n      Std: {np.std(v1_gas):,.0f}'
v2_g_text = f'V2 — Mean: {np.mean(v2_gas):,.0f}\n      Std: {np.std(v2_gas):,.0f}'
reduction = (1 - np.mean(v2_gas) / np.mean(v1_gas)) * 100

props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
ax.text(0.98, 0.98, v1_g_text + '\n' + v2_g_text + f'\nReduction: {reduction:.1f}%',
        transform=ax.transAxes, fontsize=10, verticalalignment='top',
        horizontalalignment='right', bbox=props)

ax.set_xlabel('Gas Used', fontsize=13, fontweight='bold')
ax.set_ylabel('Frequency', fontsize=13, fontweight='bold')
ax.set_title('Gas Usage Distribution', fontsize=15, fontweight='bold')
ax.legend(fontsize=11, loc='upper left')
ax.grid(axis='y', alpha=0.3, linestyle='--')

plt.tight_layout()
path = os.path.join(OUT_DIR, "paper_gas_distribution_v1_v2_overlay.png")
plt.savefig(path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved: {path}")


print("\n=== All overlay figures generated ===")
