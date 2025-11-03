# LLM Verification System - MVP Implementation

A two-layer blockchain framework for traceable and immutable LLM outputs. This repository contains the Minimum Viable Prototype (MVP) for the research paper "Traceable and Immutable LLM Generated Contents through Blockchain Framework."

## Overview

This framework addresses LLM output provenance verification through:

1. **Off-chain PoA Layer**: Consensus filtering using 5 independent LLMs (GPT, Claude, Gemini, Llama, DeepSeek)
2. **On-chain Anchoring Layer**: Immutable storage on Ethereum Sepolia testnet

### Key Results

- **85.36%** consensus accuracy (vs. 76.65% single model average)
- **10.17s** average blockchain commit latency
- **0.41s** verification latency

---

## Project Structure

```
llm_verification/
│
├── backend/                          # Flask API Server
│   ├── app/services/
│   │   ├── consensus_service.py      # Algorithm 1: k-of-n PoA Consensus
│   │   ├── hash_service.py           # Algorithm 2: Canonicalization & HMAC Hash
│   │   ├── blockchain_service.py     # Algorithm 3: Anchoring Workflow
│   │   │                             # Contract Interface 1 & 2
│   │   └── llm_service.py            # LLM API Integration (OpenRouter)
│   ├── app/routes/
│   │   ├── llm_routes.py             # /generate, /consensus
│   │   └── verification_routes.py    # /verify
│   ├── app.py                        # Entry point
│   └── config.py
│
├── frontend/                         # Next.js/React UI
│   └── src/
│       ├── components/
│       │   ├── GenerateSection.tsx
│       │   ├── VerificationSection.tsx
│       │   └── ConsensusDisplay.tsx
│       └── pages/index.tsx
│
├── smart-contracts/
│   ├── contracts/
│   │   └── LLMVerification.sol       # Smart contract (storeLLMRecord, getLLMRecord)
│   └── artifacts/                    # Compiled ABIs
│
├── analysis/
│   ├── experiment_runner.py          # Algorithm 5: Consensus Performance Evaluation
│   ├── result_analyzer.py            # Statistical analysis
│   └── data_loader.py                # WildJailbreak dataset (2,500 samples)
│
└── test_blockchain_performance.py    # Algorithm 6: Blockchain Performance Test
```

---

## Installation

### Prerequisites

- Python 3.8+, Node.js 16+
- Ethereum wallet with Sepolia testnet ETH ([faucet](https://sepoliafaucet.com/))

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
```

Create `.env`:
```env
OPENROUTER_API_KEY=your_key
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
PRIVATE_KEY=your_wallet_private_key
CONTRACT_ADDRESS=deployed_contract_address
HMAC_SECRET_KEY=your_secret
```

### 2. Smart Contracts

```bash
cd smart-contracts
npm install
npx hardhat compile
npx hardhat run scripts/deploy.js --network sepolia
```

### 3. Frontend

```bash
cd frontend
npm install
```

Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:5001
```

---

## Usage

```bash
# Terminal 1: Backend
cd backend
python app.py --port 5001

# Terminal 2: Frontend
cd frontend
npm run dev
```

Open http://localhost:3000

### Workflow

1. User enters prompt → Select LLM provider/model
2. **PoA Layer**: 5 models vote (3-of-5 threshold)
3. **Anchoring**: HMAC-SHA256 hash → Blockchain commit
4. **Verification**: Transaction hash → Integrity check

---

## Algorithm Implementations

### Algorithm 1: k-of-n Consensus
**File**: `backend/app/services/consensus_service.py`
- Parallel calls to 5 LLMs via ThreadPoolExecutor
- Safety prompt template with True/False response
- 3-of-5 threshold, 60s timeout

### Algorithm 2: Canonicalization & Hash
**File**: `backend/app/services/hash_service.py`
- HMAC-SHA256 with secret key (security enhancement over plain SHA256)
- Canonicalized JSON (`sort_keys=True`)
- Includes: provider, model, prompt, response, parameters, timestamp, consensus votes

### Algorithm 3: Anchoring Workflow
**File**: `backend/app/services/blockchain_service.py` → `commit_hash()`
- Gas estimation with 20% buffer
- Dynamic gas price adjustment for Sepolia
- Latency tracking: submission + confirmation

### Contract Interface 1: On-Chain Commit
**File**: `smart-contracts/contracts/LLMVerification.sol` → `storeLLMRecord()`
- Stores: hash, prompt, response, provider, model, timestamp, parameters, consensus_votes
- Emits `LLMRecordStored` event

### Contract Interface 2: On-Chain Verification
**File**: `backend/app/services/blockchain_service.py` → `verify_transaction_hash()`
- Fetches transaction via Web3 RPC
- Decodes input data using ABI
- Recalculates HMAC hash → Compares with original

### Algorithm 5: Consensus Evaluation
**File**: `analysis/experiment_runner.py`
- WildJailbreak dataset (2,500 samples)
- Metrics: Accuracy, Precision, Recall, F1
- Confusion matrices per model

### Algorithm 6: Blockchain Performance
**File**: `test_blockchain_performance.py`
- 75 transactions on Sepolia
- Tracks: submission time, confirmation time, gas usage

---

## Performance Results

### Consensus Layer

| Model | Accuracy | Precision | Recall | F1 |
|-------|----------|-----------|--------|-----|
| **Consensus (5 models)** | **85.36%** | **92.58%** | **76.88%** | **84.00%** |
| DeepSeek Chat | 84.68% | 93.39% | 74.64% | 82.97% |
| Claude 3 Haiku | 82.64% | 78.86% | 84.32% | 81.49% |
| Gemini 2.5 Flash | 81.64% | 93.22% | 68.24% | 78.90% |
| GPT-3.5 Turbo | 75.76% | 59.70% | 98.00% | 74.20% |
| Llama 3.1 8B | 58.52% | 96.18% | 38.24% | 54.66% |

**Improvement**: 8.71pp over single model average (76.65% → 85.36%)

### Blockchain Layer

- **Average commit latency**: 10.17s (median: 11.08s)
- **Verification latency**: 0.41s (mean)
- **Gas usage**: ~200,000 gas per transaction

---

## API Endpoints

### POST /api/llm/generate
Generate LLM response with consensus validation and blockchain anchoring.

**Request**:
```json
{
  "prompt": "Your question",
  "provider": "openai",
  "model": "gpt-3.5-turbo"
}
```

**Response**:
```json
{
  "response": "LLM output",
  "transaction_hash": "0x...",
  "hash": "abc123...",
  "consensus": {
    "passed": true,
    "safe_votes": 4,
    "harmful_votes": 1
  }
}
```

### POST /api/verification/verify
Verify transaction hash and check data integrity.

**Request**:
```json
{
  "transaction_hash": "0x..."
}
```

**Response**:
```json
{
  "verified": true,
  "block_number": 12345,
  "hash_verification": {
    "verified": true,
    "original_hash": "abc123...",
    "calculated_hash": "abc123..."
  }
}
```

---

## Security Features

- **HMAC-SHA256**: Secret key prevents unauthorized hash generation
- **Immutable Storage**: Blockchain prevents tampering
- **Multi-Model Consensus**: Reduces single-point failure
- **Public Auditability**: Etherscan verification

---

## Limitations

1. Relies on LLM API providers (OpenRouter)
2. Single-generation scope (multi-turn requires external storage)
3. On-chain plain text storage (privacy concern)

**Future Work**: Layer-2 integration, IPFS storage, adaptive thresholding

---

## License

MIT License

## Contact

Sungheon Lee - spl5637@psu.edu
Pennsylvania State University
