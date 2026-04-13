# Traceable LLM — Prototype

Research prototype accompanying the paper *"Lightweight Provenance Anchoring for LLM Outputs: A Blockchain Framework with Pre-Recording Safety Consensus."*

The framework has two layers:

1. **Off-chain LLM-Consensus Layer** — A pre-recording safety vote across multiple independent LLMs.
2. **On-chain Anchoring Layer** — Provenance commitment on the Ethereum Sepolia testnet.

Two anchoring strategies are implemented and evaluated:

- **V1** — canonical record stored in plaintext on-chain.
- **V2** — SHA-256 hash and IPFS CID on-chain, full record pinned to IPFS.

---

## Repository Layout

```
backend/            Flask API (consensus, hashing, anchoring, verification)
frontend/           Next.js UI
smart-contracts/    Solidity contracts for V1 and V2
analysis/           Evaluation scripts
paper_data/         Data backing the paper's reported numbers
```

See `paper_data/README.md` for the mapping between data files and paper sections.

---

## Installation

### Prerequisites
- Python 3.10+, Node.js 18+
- Sepolia testnet ETH for anchoring experiments
- (V2) IPFS node or pinning service

### Backend
```bash
cd backend
pip install -r requirements.txt
```

Configure `.env` with your own values:
```env
OPENROUTER_API_KEY=
SEPOLIA_RPC_URL=
PRIVATE_KEY=
CONTRACT_ADDRESS=
HMAC_SECRET_KEY=
IPFS_API_URL=          # V2 only
```

### Smart contracts
```bash
cd smart-contracts
npm install
npx hardhat compile
npx hardhat run scripts/deploy.js --network sepolia
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## Running

```bash
# Backend
cd backend && python app.py --port 5001

# Frontend
cd frontend && npm run dev
```

Open `http://localhost:3000`.

---

## Evaluation

Experiments reported in the paper use the publicly available WildJailbreak dataset. Scripts that produced the reported numbers are in `analysis/` and `paper_data/`. The raw per-sample data file is excluded from this repository; it can be regenerated from the original dataset using the provided scripts.

Summary tables and figures are in `paper_data/`. See the paper for methodology and discussion.

---

## Scope and Limitations

This prototype demonstrates the proposed framework on a testnet. It is not a production deployment and does not claim cryptographic proof of inference correctness. Limitations, assumptions, and failure modes are discussed in the paper.

---

## License

MIT

## Contact

Sungheon Lee — spl5637@psu.edu
Pennsylvania State University
