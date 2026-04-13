# Paper Data

Backing data for all claims in the paper. Organized by paper section.

## Folder Structure

### `consensus_evaluation/` (Section 7.1)
Core 2,500-prompt evaluation with 5 LLMs (OpenAI, Claude, Gemini, Llama, DeepSeek).
- `premium_models_2500_samples_clean.json` — Full per-sample results (2,500 prompts, 5 models each)
- `premium_models_2500_samples_clean_comparison_table.csv` — Model accuracy comparison table
- `premium_models_2500_samples_clean_report.txt` — Summary report with all metrics

Key numbers from this data:
- Consensus accuracy: 85.36%
- Best individual model (DeepSeek): 84.68%
- Improvement over average: 8.71 percentage points

### `threshold_sensitivity/` (Section 7.2)
Threshold sensitivity analysis across k=1 to k=5.
- `threshold_sensitivity_report.txt` — Full report with all thresholds, weighted voting, Bayesian analysis
- `threshold_sensitivity_report.csv` — CSV with per-threshold metrics
- `threshold_sensitivity_analysis.py` — Script that generated the analysis

Key numbers from this data:
- k=3 accuracy: 0.7212, precision: 0.9862, recall: 0.6840, F1: 0.8077
- Bayesian P(majority correct) at k=3: 0.8244
- Weighted voting best F1: 0.9278 (at k=1, did not improve over uniform)

### `fine_tuned_model/` (Section 7.3)
Fine-tuned IBM Granite 3.2 2B replacing Llama in consensus.
- `generate_beaver_granite_consensus.py` — Script for Granite consensus evaluation
- `paper_granite_figures.py` — Figure generation script
- `wildguard_vs_premium_full_report.json` — Full comparison report

Key numbers from this data:
- Granite accuracy: 83.24%, precision: 81.74%, recall: 85.60%, F1: 83.63%
- New consensus accuracy: 85.89% (up from 85.36%)
- New consensus F1: 85.62% (up from 84.00%)

### `blockchain_v1/` (Section 7.4 — V1 plaintext)
75 transactions on Ethereum Sepolia testnet with full plaintext on-chain.
- `performance_test_20251009_175753.json` — Raw transaction data
- `performance_test_20251009_175753.csv` — CSV format
- `performance_summary.txt` — Summary statistics

Key numbers: mean latency 10.17s, mean gas 510,662

### `blockchain_v2/` (Section 7.4 — V2 hash+IPFS)
75 transactions on Ethereum Sepolia testnet with hash+IPFS on-chain.
- `v2_performance_20260402_133907.json` — Raw transaction data
- `v2_performance_20260402_133907.csv` — CSV format
- `v2_performance_summary_20260402_133907.txt` — Summary statistics
- `v1_v2_comparison_report.txt` — Head-to-head V1 vs V2 comparison

Key numbers: mean latency 8.74s, mean gas 234,022, 54.2% gas reduction

### `figures/`
Key figures used in the paper (Figures 10, 11, 16-19).
