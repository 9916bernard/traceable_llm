#!/usr/bin/env python3
"""
V2 Blockchain Performance Analysis & Visualization

Generates publication-quality figures comparing V1 and V2 contract
performance, including latency distributions, gas usage, and L2 cost
projections.

Usage:
    python3 analyze_v2_blockchain_performance.py
"""

import os
import sys
import json
import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Paths
V1_DATA_DIR = "analysis/results/blockchain_performance/raw_data"
V2_DATA_DIR = "analysis/results/blockchain_performance_v2/raw_data"
VIS_DIR = "analysis/results/visualizations"
REPORTS_DIR = "analysis/results/reports"


def load_v1_data() -> list:
    """Load V1 performance test results."""
    # Use the largest V1 dataset
    files = sorted(glob.glob(os.path.join(V1_DATA_DIR, "*.json")))
    if not files:
        print("Warning: No V1 data found")
        return []
    # Pick the file with most results
    best = None
    best_count = 0
    for f in files:
        with open(f) as fh:
            data = json.load(fh)
        if isinstance(data, list) and len(data) > best_count:
            best = data
            best_count = len(data)
    print(f"V1: Loaded {best_count} results")
    return best or []


def load_v2_data() -> list:
    """Load V2 performance test results."""
    files = sorted(glob.glob(os.path.join(V2_DATA_DIR, "*.json")))
    if not files:
        print("Warning: No V2 data found")
        return []
    # Use the latest file
    with open(files[-1]) as f:
        data = json.load(f)
    print(f"V2: Loaded {len(data)} results from {os.path.basename(files[-1])}")
    return data


def extract_v1_metrics(data: list) -> dict:
    """Extract key metrics from V1 results."""
    successful = [r for r in data if r.get("success")]
    if not successful:
        return {}

    commit_times = [r["commit"]["timing"]["total_commit_time"] for r in successful]
    gas_used = [r["commit"]["gas_used"] for r in successful]
    gas_costs = [r["commit"]["gas_cost_eth"] for r in successful]

    verify_times = []
    for r in successful:
        vt = r.get("verification", {}).get("timing", {})
        if vt and "total_verification_time" in vt:
            verify_times.append(vt["total_verification_time"])

    return {
        "commit_times": commit_times,
        "gas_used": gas_used,
        "gas_costs": gas_costs,
        "verify_times": verify_times,
        "n": len(successful),
    }


def extract_v2_metrics(data: list) -> dict:
    """Extract key metrics from V2 results."""
    successful = [r for r in data if r.get("success")]
    if not successful:
        return {}

    commit_times = [r["commit"]["total_commit_time"] for r in successful]
    gas_used = [r["commit"]["gas_used"] for r in successful]
    gas_costs = [r["commit"]["gas_cost_eth"] for r in successful]
    verify_times = [r["verification"]["verify_time"] for r in successful]
    retrieve_times = [r["verification"]["retrieve_time"] for r in successful]
    categories = [r["category"] for r in successful]
    prompt_lengths = [r["prompt_length"] for r in successful]

    return {
        "commit_times": commit_times,
        "gas_used": gas_used,
        "gas_costs": gas_costs,
        "verify_times": verify_times,
        "retrieve_times": retrieve_times,
        "categories": categories,
        "prompt_lengths": prompt_lengths,
        "n": len(successful),
    }


def plot_latency_comparison(v1: dict, v2: dict):
    """Box plot comparing V1 and V2 commit latency."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Commit latency box plot
    data_commit = []
    labels_commit = []
    if v1.get("commit_times"):
        data_commit.append(v1["commit_times"])
        labels_commit.append(f'V1 Plaintext\n(n={v1["n"]})')
    if v2.get("commit_times"):
        data_commit.append(v2["commit_times"])
        labels_commit.append(f'V2 Hash+IPFS\n(n={v2["n"]})')

    bp = ax1.boxplot(data_commit, labels=labels_commit, patch_artist=True,
                      widths=0.5, showmeans=True,
                      meanprops=dict(marker='D', markerfacecolor='red', markersize=8))
    colors = ['#3498db', '#2ecc71']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax1.set_ylabel('Latency (seconds)', fontsize=12, fontweight='bold')
    ax1.set_title('Commit Latency: V1 vs V2', fontsize=13, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3, linestyle='--')

    # Add stats annotation
    for i, (d, label) in enumerate(zip(data_commit, labels_commit)):
        mean = np.mean(d)
        median = np.median(d)
        ax1.annotate(f'mean={mean:.2f}s\nmedian={median:.2f}s',
                     xy=(i + 1, np.max(d)), xytext=(0, 10),
                     textcoords='offset points', ha='center', fontsize=9,
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

    # Verification latency
    data_verify = []
    labels_verify = []
    if v1.get("verify_times"):
        data_verify.append(v1["verify_times"])
        labels_verify.append(f'V1\n(n={len(v1["verify_times"])})')
    if v2.get("verify_times"):
        data_verify.append(v2["verify_times"])
        labels_verify.append(f'V2\n(n={len(v2["verify_times"])})')

    if data_verify:
        bp2 = ax2.boxplot(data_verify, labels=labels_verify, patch_artist=True,
                           widths=0.5, showmeans=True,
                           meanprops=dict(marker='D', markerfacecolor='red', markersize=8))
        for patch, color in zip(bp2['boxes'], colors[:len(data_verify)]):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

    ax2.set_ylabel('Latency (seconds)', fontsize=12, fontweight='bold')
    ax2.set_title('Verification Latency: V1 vs V2', fontsize=13, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()
    path = os.path.join(VIS_DIR, "v1_v2_latency_comparison.png")
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_gas_comparison(v1: dict, v2: dict):
    """Bar chart and distribution of gas usage V1 vs V2."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Bar chart: average gas
    labels = []
    means = []
    stds = []
    colors = []

    if v1.get("gas_used"):
        labels.append(f'V1 Plaintext\n(n={v1["n"]})')
        means.append(np.mean(v1["gas_used"]))
        stds.append(np.std(v1["gas_used"]))
        colors.append('#3498db')
    if v2.get("gas_used"):
        labels.append(f'V2 Hash+IPFS\n(n={v2["n"]})')
        means.append(np.mean(v2["gas_used"]))
        stds.append(np.std(v2["gas_used"]))
        colors.append('#2ecc71')

    bars = ax1.bar(labels, means, yerr=stds, color=colors, alpha=0.8,
                    edgecolor='black', capsize=5)
    for i, (bar, mean) in enumerate(zip(bars, means)):
        ax1.text(bar.get_x() + bar.get_width() / 2., mean / 2,
                f'{mean:,.0f}', ha='center', va='center', fontsize=13,
                fontweight='bold', color='white')

    if len(means) == 2:
        reduction = (1 - means[1] / means[0]) * 100
        ax1.annotate(f'{reduction:.1f}% reduction',
                     xy=(0.5, max(means) * 0.85), fontsize=14,
                     fontweight='bold', color='red', ha='center',
                     transform=ax1.get_xaxis_transform())

    ax1.set_ylabel('Gas Used', fontsize=12, fontweight='bold')
    ax1.set_title('Average Gas Usage: V1 vs V2', fontsize=13, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3, linestyle='--')

    # Distribution
    if v1.get("gas_used"):
        ax2.hist(v1["gas_used"], bins=20, alpha=0.6, color='#3498db',
                 label=f'V1 (n={v1["n"]})', edgecolor='black')
    if v2.get("gas_used"):
        ax2.hist(v2["gas_used"], bins=20, alpha=0.6, color='#2ecc71',
                 label=f'V2 (n={v2["n"]})', edgecolor='black')

    ax2.set_xlabel('Gas Used', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Frequency', fontsize=12, fontweight='bold')
    ax2.set_title('Gas Usage Distribution', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()
    path = os.path.join(VIS_DIR, "v1_v2_gas_comparison.png")
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_v2_latency_distribution(v2: dict):
    """V2 commit latency histogram with percentile markers."""
    if not v2.get("commit_times"):
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    times = v2["commit_times"]
    ax.hist(times, bins=20, color='#2ecc71', alpha=0.7, edgecolor='black')

    # Percentile lines
    percentiles = {50: 'blue', 90: 'orange', 95: 'red'}
    for p, color in percentiles.items():
        val = np.percentile(times, p)
        ax.axvline(val, color=color, linestyle='--', linewidth=2,
                   label=f'P{p}={val:.2f}s')

    # Mean line
    mean = np.mean(times)
    ax.axvline(mean, color='black', linestyle='-', linewidth=2,
               label=f'Mean={mean:.2f}s')

    ax.set_xlabel('Commit Latency (seconds)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
    ax.set_title(f'V2 Commit Latency Distribution (n={v2["n"]})', fontsize=13, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()
    path = os.path.join(VIS_DIR, "v2_commit_latency_distribution.png")
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_l2_cost_comparison(v1: dict, v2: dict):
    """Bar chart comparing costs across L1 and L2 networks."""
    eth_price = 2500  # USD

    networks = ['L1\nMainnet', 'Polygon\nPoS', 'Arbitrum', 'Optimism', 'Base']
    multipliers = [1.0, 0.01, 0.05, 0.05, 0.02]

    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(networks))
    width = 0.35

    if v1.get("gas_costs"):
        v1_base = np.mean(v1["gas_costs"]) * eth_price
        v1_costs = [v1_base * m for m in multipliers]
        bars1 = ax.bar(x - width/2, v1_costs, width, label='V1 (Plaintext)',
                       color='#3498db', alpha=0.8, edgecolor='black')

    if v2.get("gas_costs"):
        v2_base = np.mean(v2["gas_costs"]) * eth_price
        v2_costs = [v2_base * m for m in multipliers]
        bars2 = ax.bar(x + width/2, v2_costs, width, label='V2 (Hash+IPFS)',
                       color='#2ecc71', alpha=0.8, edgecolor='black')

    ax.set_xlabel('Network', fontsize=12, fontweight='bold')
    ax.set_ylabel('Cost per Transaction (USD)', fontsize=12, fontweight='bold')
    ax.set_title('Transaction Cost: V1 vs V2 Across Networks', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(networks)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Use log scale if the range is large
    if v1.get("gas_costs") and v2.get("gas_costs"):
        ax.set_yscale('log')
        ax.set_ylabel('Cost per Transaction (USD, log scale)', fontsize=12, fontweight='bold')

    plt.tight_layout()
    path = os.path.join(VIS_DIR, "l2_cost_comparison_v1_v2.png")
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_latency_over_time(v2: dict):
    """V2 commit and verification latency over sequential tests."""
    if not v2.get("commit_times"):
        return

    fig, ax = plt.subplots(figsize=(12, 5))

    x = range(1, len(v2["commit_times"]) + 1)
    ax.plot(x, v2["commit_times"], 'b-o', markersize=4, alpha=0.7,
            label='Commit latency', linewidth=1.5)

    if v2.get("verify_times"):
        ax.plot(x[:len(v2["verify_times"])], v2["verify_times"], 'g-s',
                markersize=4, alpha=0.7, label='Verification latency', linewidth=1.5)

    ax.set_xlabel('Test Number', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latency (seconds)', fontsize=12, fontweight='bold')
    ax.set_title(f'V2 Latency Over Time (n={v2["n"]})', fontsize=13, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')

    plt.tight_layout()
    path = os.path.join(VIS_DIR, "v2_latency_over_time.png")
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def generate_comparison_report(v1: dict, v2: dict):
    """Generate a comprehensive comparison report."""
    path = os.path.join(REPORTS_DIR, "v1_v2_comparison_report.txt")

    with open(path, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("V1 vs V2 BLOCKCHAIN PERFORMANCE COMPARISON REPORT\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write("=" * 70 + "\n\n")

        f.write("SUMMARY\n")
        f.write("-" * 50 + "\n")
        f.write(f"{'Metric':<30} {'V1 (Plaintext)':>18} {'V2 (Hash+IPFS)':>18}\n")
        f.write("-" * 70 + "\n")

        if v1.get("commit_times") and v2.get("commit_times"):
            f.write(f"{'Transactions':<30} {v1['n']:>18} {v2['n']:>18}\n")
            f.write(f"{'Commit Latency (mean)':<30} {np.mean(v1['commit_times']):>17.3f}s {np.mean(v2['commit_times']):>17.3f}s\n")
            f.write(f"{'Commit Latency (median)':<30} {np.median(v1['commit_times']):>17.3f}s {np.median(v2['commit_times']):>17.3f}s\n")
            f.write(f"{'Commit Latency (p90)':<30} {np.percentile(v1['commit_times'], 90):>17.3f}s {np.percentile(v2['commit_times'], 90):>17.3f}s\n")
            f.write(f"{'Commit Latency (p95)':<30} {np.percentile(v1['commit_times'], 95):>17.3f}s {np.percentile(v2['commit_times'], 95):>17.3f}s\n")

        if v1.get("gas_used") and v2.get("gas_used"):
            v1_gas = np.mean(v1["gas_used"])
            v2_gas = np.mean(v2["gas_used"])
            reduction = (1 - v2_gas / v1_gas) * 100
            f.write(f"{'Gas Used (mean)':<30} {v1_gas:>18,.0f} {v2_gas:>18,.0f}\n")
            f.write(f"{'Gas Reduction':<30} {'':>18} {reduction:>17.1f}%\n")

            eth_price = 2500
            v1_cost = np.mean(v1["gas_costs"]) * eth_price
            v2_cost = np.mean(v2["gas_costs"]) * eth_price
            cost_reduction = (1 - v2_cost / v1_cost) * 100
            f.write(f"{'L1 Cost/tx (USD)':<30} ${v1_cost:>17.4f} ${v2_cost:>17.4f}\n")
            f.write(f"{'Cost Reduction':<30} {'':>18} {cost_reduction:>17.1f}%\n")

        if v1.get("verify_times") and v2.get("verify_times"):
            f.write(f"{'Verify Latency (mean)':<30} {np.mean(v1['verify_times']):>17.3f}s {np.mean(v2['verify_times']):>17.3f}s\n")

        f.write("\n")

        # V2 category breakdown
        if v2.get("categories"):
            f.write("\nV2 PERFORMANCE BY PROMPT CATEGORY\n")
            f.write("-" * 50 + "\n")
            successful_v2 = list(zip(v2["categories"], v2["gas_used"], v2["commit_times"]))
            for cat in ["short", "medium", "long"]:
                cat_data = [(g, t) for c, g, t in successful_v2 if c == cat]
                if cat_data:
                    gases, times = zip(*cat_data)
                    f.write(f"  {cat:8s}: n={len(cat_data):3d}  "
                            f"gas={np.mean(gases):>10,.0f}  "
                            f"latency={np.mean(times):.3f}s\n")

        # L2 projections
        if v2.get("gas_costs"):
            eth_price = 2500
            v2_base = np.mean(v2["gas_costs"]) * eth_price
            f.write(f"\nV2 L2 COST PROJECTIONS (ETH ~${eth_price})\n")
            f.write("-" * 50 + "\n")
            for name, mult in [("L1 Mainnet", 1.0), ("Polygon PoS", 0.01),
                               ("Arbitrum", 0.05), ("Optimism", 0.05), ("Base", 0.02)]:
                f.write(f"  {name:15s}: ${v2_base * mult:.6f} USD/tx\n")

        f.write("\n" + "=" * 70 + "\n")

    print(f"Saved: {path}")


def main():
    os.makedirs(VIS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    print("Loading performance data...")
    v1_data = load_v1_data()
    v2_data = load_v2_data()

    v1 = extract_v1_metrics(v1_data)
    v2 = extract_v2_metrics(v2_data)

    if not v1 and not v2:
        print("ERROR: No data to analyze")
        sys.exit(1)

    print("\nGenerating visualizations...")
    plot_latency_comparison(v1, v2)
    plot_gas_comparison(v1, v2)
    plot_v2_latency_distribution(v2)
    plot_l2_cost_comparison(v1, v2)
    plot_latency_over_time(v2)

    print("\nGenerating comparison report...")
    generate_comparison_report(v1, v2)

    print("\n=== Analysis Complete ===")


if __name__ == "__main__":
    main()
