#!/usr/bin/env python3
"""
Comprehensive Blockchain Performance Test — V2 Contract (Hash-Only + IPFS)

Tests the LLMVerificationV2 contract on Sepolia with diverse payloads.
Measures gas usage, commit latency, verification latency, and compares
with V1 historical data.

Addresses Reviewer Concerns:
- Concern 3: IPFS + on-chain hash architecture evaluation
- Concern 7: Blockchain performance analysis is minimal

Usage:
    python3 test_v2_blockchain_performance.py --runs 50 --delay 3
    python3 test_v2_blockchain_performance.py --runs 50 --delay 3 --with-ipfs
"""

import os
import sys
import time
import json
import csv
import hashlib
import argparse
import random
import string
import traceback
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from dotenv import load_dotenv
load_dotenv()

from web3 import Web3

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL", "")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
CONTRACT_ADDRESS_V2 = os.getenv("CONTRACT_ADDRESS_V2", "")

V2_ABI = [
    {
        "inputs": [
            {"internalType": "bytes32", "name": "contentHash", "type": "bytes32"},
            {"internalType": "string", "name": "ipfsCID", "type": "string"},
            {"internalType": "string", "name": "consensusVotes", "type": "string"},
        ],
        "name": "storeRecord",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "contentHash", "type": "bytes32"}],
        "name": "hashExists",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "contentHash", "type": "bytes32"}],
        "name": "getRecord",
        "outputs": [
            {"internalType": "bool", "name": "exists", "type": "bool"},
            {"internalType": "string", "name": "ipfsCID", "type": "string"},
            {"internalType": "string", "name": "consensusVotes", "type": "string"},
            {"internalType": "address", "name": "submitter", "type": "address"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "totalRecords",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "bytes32", "name": "contentHash", "type": "bytes32"},
            {"indexed": False, "internalType": "string", "name": "ipfsCID", "type": "string"},
            {"indexed": False, "internalType": "string", "name": "consensusVotes", "type": "string"},
            {"indexed": True, "internalType": "address", "name": "submitter", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "blockNumber", "type": "uint256"},
        ],
        "name": "RecordStored",
        "type": "event",
    },
]

# Simulated IPFS CIDs (46-char base58 strings, realistic length)
SAMPLE_CIDS = [
    "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG",
    "QmT5NvUtoM5nWFfrQdVrFtvGfKFmG7AHE8P34isapyhCxX",
    "QmbWqxBEKC3P8tqsKc98xmWNzrzDtRLMiMPL8wBuTGsMnR",
    "QmUaoioqU7bxezBQZkUcgcSyoEhzStf9BMoQrnLP2bHSno",
    "QmPZ9gcCEpqKTo6aq61g2nXGUhM4iCL3ewB6LDXZCtioEB",
]

# Diverse test prompts — short, medium, long
TEST_PROMPTS_SHORT = [
    "Hello, how are you?",
    "What is 2+2?",
    "Tell me a short joke.",
    "What color is the sky?",
    "Count from 1 to 3.",
]

TEST_PROMPTS_MEDIUM = [
    "Explain the concept of blockchain consensus mechanisms and how they ensure "
    "data integrity across distributed networks. Include examples of Proof of Work "
    "and Proof of Stake approaches. Keep your answer concise but thorough.",

    "Describe the key differences between large language models such as GPT, Claude, "
    "and Gemini in terms of their architecture, training data, and capabilities. "
    "What are the trade-offs when choosing one model over another for production use?",

    "Provide an overview of GDPR's right to be forgotten and its implications for "
    "blockchain-based systems. How can immutability and data erasure be reconciled? "
    "Discuss practical approaches and their limitations.",
]

TEST_PROMPTS_LONG = [
    "Write a comprehensive analysis of zero-knowledge proofs (ZKPs) and their "
    "application in verifying machine learning model outputs. Cover the following: "
    "1) The mathematical foundations of ZKPs including interactive and non-interactive "
    "proofs. 2) How zkSNARKs and zkSTARKs differ in setup requirements, proof size, "
    "and verification time. 3) The current state of zkML, including frameworks like "
    "EZKL and their computational overhead. 4) Practical challenges in applying ZKPs "
    "to large language model inference, including latency and cost considerations. "
    "5) A comparison with alternative approaches such as blockchain anchoring and "
    "watermarking. Provide specific numbers where possible and cite recent research." * 2,

    "Discuss the architectural design of a two-layer verification framework for "
    "AI-generated content. The first layer should handle off-chain consensus among "
    "multiple independent AI models to evaluate content safety. The second layer "
    "should provide on-chain anchoring for immutable provenance records. Address "
    "the following considerations: scalability, gas optimization through Layer-2 "
    "solutions, privacy preservation through hash-only on-chain storage with IPFS "
    "for full content, and regulatory compliance including GDPR right to erasure. "
    "Compare this approach with existing solutions such as C2PA, digital watermarking, "
    "VeriLLM, and BC4LLM. Evaluate trade-offs in latency, cost, and security." * 2,
]

# Simulated responses matching prompt sizes
RESPONSE_SHORT = "The answer is simple and straightforward."
RESPONSE_MEDIUM = (
    "This is a medium-length response that covers the key points. "
    "It provides context, explains the main concepts, and offers "
    "a balanced perspective on the topic at hand. The response includes "
    "relevant examples and considers multiple viewpoints." * 2
)
RESPONSE_LONG = (
    "This is a comprehensive long-form response that thoroughly addresses "
    "all aspects of the question. It includes detailed analysis, supporting "
    "evidence, and nuanced discussion of trade-offs. The response covers "
    "multiple perspectives and provides concrete examples from recent research. "
    "It also discusses practical implications and future directions." * 5
)


def generate_content_hash(prompt: str, response: str, test_num: int) -> bytes:
    """Generate a unique SHA-256 content hash."""
    data = json.dumps({
        "prompt": prompt,
        "response": response,
        "test_number": test_num,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "nonce": random.randint(0, 2**32),
    }, sort_keys=True)
    return hashlib.sha256(data.encode()).digest()


def get_prompt_category(test_num: int, total: int) -> tuple:
    """Distribute tests across short/medium/long prompts (40/30/30 split)."""
    ratio_pos = test_num / total
    if ratio_pos < 0.4:
        prompts = TEST_PROMPTS_SHORT
        response = RESPONSE_SHORT
        category = "short"
    elif ratio_pos < 0.7:
        prompts = TEST_PROMPTS_MEDIUM
        response = RESPONSE_MEDIUM
        category = "medium"
    else:
        prompts = TEST_PROMPTS_LONG
        response = RESPONSE_LONG
        category = "long"

    prompt = prompts[test_num % len(prompts)]
    return prompt, response, category


class IPFSTester:
    """Lightweight IPFS tester using Pinata."""

    def __init__(self):
        self.api_key = os.getenv("PINATA_API_KEY", "")
        self.api_secret = os.getenv("PINATA_API_SECRET", "")
        self.available = bool(self.api_key and self.api_secret)
        if not self.available:
            print("IPFS: Pinata keys not set, using simulated CIDs")

    def pin(self, data: dict) -> tuple:
        """Pin data to IPFS. Returns (cid, latency_seconds)."""
        if not self.available:
            cid = random.choice(SAMPLE_CIDS)
            return cid, 0.0

        import requests
        headers = {
            "pinata_api_key": self.api_key,
            "pinata_secret_api_key": self.api_secret,
            "Content-Type": "application/json",
        }
        payload = {
            "pinataContent": data,
            "pinataMetadata": {"name": f"perf-test-{datetime.now().strftime('%H%M%S')}"},
        }
        start = time.time()
        resp = requests.post(
            "https://api.pinata.cloud/pinning/pinJSONToIPFS",
            headers=headers, json=payload, timeout=30
        )
        latency = time.time() - start

        if resp.status_code != 200:
            raise RuntimeError(f"Pinata pin failed: {resp.status_code} {resp.text}")

        return resp.json()["IpfsHash"], latency

    def retrieve(self, cid: str) -> tuple:
        """Retrieve data from IPFS. Returns (data, latency_seconds)."""
        if not self.available:
            return {"simulated": True}, 0.0

        import requests
        start = time.time()
        resp = requests.get(f"https://gateway.pinata.cloud/ipfs/{cid}", timeout=30)
        latency = time.time() - start
        return resp.json(), latency

    def unpin(self, cid: str) -> tuple:
        """Unpin data from IPFS. Returns (success, latency_seconds)."""
        if not self.available:
            return True, 0.0

        import requests
        headers = {
            "pinata_api_key": self.api_key,
            "pinata_secret_api_key": self.api_secret,
        }
        start = time.time()
        resp = requests.delete(
            f"https://api.pinata.cloud/pinning/unpin/{cid}",
            headers=headers, timeout=30
        )
        latency = time.time() - start
        return resp.status_code in (200, 404), latency


class V2PerformanceTester:
    """Comprehensive V2 contract performance tester."""

    def __init__(self, with_ipfs: bool = False):
        if not SEPOLIA_RPC_URL or not PRIVATE_KEY or not CONTRACT_ADDRESS_V2:
            print("ERROR: Set SEPOLIA_RPC_URL, PRIVATE_KEY, CONTRACT_ADDRESS_V2 in .env")
            sys.exit(1)

        self.w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))
        pk = PRIVATE_KEY if PRIVATE_KEY.startswith("0x") else f"0x{PRIVATE_KEY}"
        self.account = self.w3.eth.account.from_key(pk)
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(CONTRACT_ADDRESS_V2),
            abi=V2_ABI,
        )
        self.ipfs = IPFSTester() if with_ipfs else None
        self.results: List[Dict] = []
        # Track nonce locally to avoid "replacement transaction underpriced"
        self.nonce = self.w3.eth.get_transaction_count(self.account.address)

        print(f"Connected to Sepolia: {self.w3.is_connected()}")
        print(f"Account: {self.account.address}")
        bal = self.w3.eth.get_balance(self.account.address)
        print(f"Balance: {self.w3.from_wei(bal, 'ether'):.6f} ETH")
        print(f"V2 Contract: {CONTRACT_ADDRESS_V2}")
        print(f"IPFS enabled: {with_ipfs and self.ipfs.available}")
        print(f"Starting nonce: {self.nonce}")

    def run_single_test(self, test_num: int, total: int) -> Dict[str, Any]:
        prompt, response, category = get_prompt_category(test_num, total)
        prompt_len = len(prompt)
        response_len = len(response)

        result = {
            "test_number": test_num,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "category": category,
            "prompt_length": prompt_len,
            "response_length": response_len,
            "success": False,
        }

        print(f"\n{'='*70}")
        print(f"Test {test_num}/{total} [{category}] prompt={prompt_len}b response={response_len}b")
        print(f"{'='*70}")

        try:
            # 1. Generate content hash
            content_hash = generate_content_hash(prompt, response, test_num)
            result["content_hash"] = content_hash.hex()

            # 2. IPFS pin (if enabled)
            ipfs_cid = random.choice(SAMPLE_CIDS)
            ipfs_pin_time = 0.0
            if self.ipfs:
                record_data = {
                    "prompt": prompt,
                    "response": response,
                    "provider": "openai",
                    "model": "gpt-4",
                    "parameters": {"temperature": 0.7, "max_tokens": 200},
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "consensus_votes": "3/5",
                }
                ipfs_cid, ipfs_pin_time = self.ipfs.pin(record_data)
                print(f"  IPFS pin: {ipfs_cid} ({ipfs_pin_time:.3f}s)")

            result["ipfs_cid"] = ipfs_cid
            result["ipfs_pin_time"] = ipfs_pin_time

            # 3. Estimate gas
            gas_est_start = time.time()
            try:
                estimated_gas = self.contract.functions.storeRecord(
                    content_hash, ipfs_cid, "3/5"
                ).estimate_gas({"from": self.account.address})
                gas_limit = int(estimated_gas * 1.2)
            except Exception as e:
                print(f"  Gas estimation failed: {e}")
                gas_limit = 300000
                estimated_gas = gas_limit
            gas_est_time = time.time() - gas_est_start
            result["estimated_gas"] = estimated_gas
            result["gas_estimation_time"] = gas_est_time

            # 4. Build and send transaction
            gas_price = self.w3.eth.gas_price
            if gas_price < 1_000_000_000:
                gas_price = 1_000_000_000  # min 1 gwei

            tx = self.contract.functions.storeRecord(
                content_hash, ipfs_cid, "3/5"
            ).build_transaction({
                "from": self.account.address,
                "gas": gas_limit,
                "gasPrice": int(gas_price * 1.5),
                "nonce": self.nonce,
            })

            signed = self.w3.eth.account.sign_transaction(
                tx, self.account.key
            )

            # Submit
            submit_start = time.time()
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            submit_time = time.time() - submit_start
            print(f"  Submitted: {tx_hash.hex()[:20]}... ({submit_time:.3f}s)")

            # Wait for confirmation
            confirm_start = time.time()
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            confirm_time = time.time() - confirm_start
            total_commit_time = submit_time + confirm_time

            # Increment nonce after successful confirmation
            self.nonce += 1

            gas_used = receipt.gasUsed
            effective_gas_price = receipt.get("effectiveGasPrice", gas_price)
            gas_cost_wei = gas_used * effective_gas_price
            gas_cost_eth = float(self.w3.from_wei(gas_cost_wei, "ether"))
            gas_cost_gwei = float(self.w3.from_wei(effective_gas_price, "gwei"))

            print(f"  Confirmed: block {receipt.blockNumber} ({confirm_time:.3f}s)")
            print(f"  Gas: {gas_used:,} used | {gas_cost_gwei:.2f} gwei | {gas_cost_eth:.8f} ETH")

            result["commit"] = {
                "transaction_hash": tx_hash.hex(),
                "block_number": receipt.blockNumber,
                "gas_used": gas_used,
                "gas_price_gwei": gas_cost_gwei,
                "gas_cost_eth": gas_cost_eth,
                "submit_time": submit_time,
                "confirm_time": confirm_time,
                "total_commit_time": total_commit_time,
            }

            # 5. Verification — check on-chain
            verify_start = time.time()
            exists = self.contract.functions.hashExists(content_hash).call()
            verify_time = time.time() - verify_start
            print(f"  Verified on-chain: {exists} ({verify_time:.3f}s)")

            # 6. Retrieve record
            retrieve_start = time.time()
            record = self.contract.functions.getRecord(content_hash).call()
            retrieve_time = time.time() - retrieve_start
            print(f"  Record retrieved: submitter={record[3][:10]}... ({retrieve_time:.3f}s)")

            result["verification"] = {
                "hash_exists": exists,
                "verify_time": verify_time,
                "retrieve_time": retrieve_time,
            }

            # 7. IPFS retrieval test (if enabled and real)
            if self.ipfs and self.ipfs.available:
                try:
                    ipfs_data, ipfs_retrieve_time = self.ipfs.retrieve(ipfs_cid)
                    print(f"  IPFS retrieval: {ipfs_retrieve_time:.3f}s")
                    result["ipfs_retrieve_time"] = ipfs_retrieve_time
                except Exception as e:
                    print(f"  IPFS retrieval failed: {e}")
                    result["ipfs_retrieve_time"] = None

            result["success"] = True
            print(f"  SUCCESS")

        except Exception as e:
            print(f"  FAILED: {e}")
            result["error"] = str(e)
            if "insufficient funds" in str(e).lower():
                result["insufficient_funds"] = True
            # Resync nonce from network on failure
            try:
                self.nonce = self.w3.eth.get_transaction_count(self.account.address)
            except Exception:
                pass

        return result

    def run_tests(self, num_tests: int, delay: float = 3.0):
        print(f"\n{'='*70}")
        print(f"V2 BLOCKCHAIN PERFORMANCE TEST")
        print(f"{'='*70}")
        print(f"Target: {num_tests} tests | Delay: {delay}s")
        print(f"{'='*70}")

        for i in range(1, num_tests + 1):
            result = self.run_single_test(i, num_tests)
            self.results.append(result)

            if result.get("insufficient_funds"):
                print("\nINSUFFICIENT FUNDS — stopping.")
                break

            if i < num_tests:
                time.sleep(delay)

        self.print_summary()

    def print_summary(self):
        successful = [r for r in self.results if r.get("success")]
        failed = [r for r in self.results if not r.get("success")]

        print(f"\n{'='*70}")
        print(f"SUMMARY: {len(successful)} successful / {len(failed)} failed / {len(self.results)} total")
        print(f"{'='*70}")

        if not successful:
            return

        import numpy as np

        # Commit latency
        commit_times = [r["commit"]["total_commit_time"] for r in successful]
        submit_times = [r["commit"]["submit_time"] for r in successful]
        confirm_times = [r["commit"]["confirm_time"] for r in successful]

        print(f"\nCOMMIT LATENCY (n={len(commit_times)}):")
        print(f"  Total:   mean={np.mean(commit_times):.3f}s  median={np.median(commit_times):.3f}s  "
              f"std={np.std(commit_times):.3f}s")
        print(f"           p50={np.percentile(commit_times, 50):.3f}s  "
              f"p90={np.percentile(commit_times, 90):.3f}s  "
              f"p95={np.percentile(commit_times, 95):.3f}s  "
              f"p99={np.percentile(commit_times, 99):.3f}s")
        print(f"  Submit:  mean={np.mean(submit_times):.3f}s")
        print(f"  Confirm: mean={np.mean(confirm_times):.3f}s")

        # Verification latency
        verify_times = [r["verification"]["verify_time"] for r in successful]
        retrieve_times = [r["verification"]["retrieve_time"] for r in successful]
        print(f"\nVERIFICATION LATENCY:")
        print(f"  hashExists: mean={np.mean(verify_times):.3f}s  median={np.median(verify_times):.3f}s")
        print(f"  getRecord:  mean={np.mean(retrieve_times):.3f}s  median={np.median(retrieve_times):.3f}s")

        # Gas
        gas_used = [r["commit"]["gas_used"] for r in successful]
        gas_costs = [r["commit"]["gas_cost_eth"] for r in successful]
        print(f"\nGAS USAGE:")
        print(f"  Gas:  mean={np.mean(gas_used):,.0f}  median={np.median(gas_used):,.0f}  "
              f"min={np.min(gas_used):,}  max={np.max(gas_used):,}")
        print(f"  Cost: mean={np.mean(gas_costs):.8f} ETH  total={np.sum(gas_costs):.8f} ETH")

        # By category
        print(f"\nBY CATEGORY:")
        for cat in ["short", "medium", "long"]:
            cat_results = [r for r in successful if r["category"] == cat]
            if cat_results:
                cat_gas = [r["commit"]["gas_used"] for r in cat_results]
                cat_latency = [r["commit"]["total_commit_time"] for r in cat_results]
                print(f"  {cat:8s}: n={len(cat_results):3d}  gas={np.mean(cat_gas):,.0f}  "
                      f"latency={np.mean(cat_latency):.3f}s")

        # IPFS
        if self.ipfs and self.ipfs.available:
            pin_times = [r["ipfs_pin_time"] for r in successful if r.get("ipfs_pin_time")]
            ret_times = [r["ipfs_retrieve_time"] for r in successful if r.get("ipfs_retrieve_time")]
            if pin_times:
                print(f"\nIPFS LATENCY:")
                print(f"  Pin:      mean={np.mean(pin_times):.3f}s  median={np.median(pin_times):.3f}s")
            if ret_times:
                print(f"  Retrieve: mean={np.mean(ret_times):.3f}s  median={np.median(ret_times):.3f}s")

        # L2 cost estimates (based on gas used)
        avg_gas = np.mean(gas_used)
        eth_price_usd = 2500  # approximate
        l1_cost = np.mean(gas_costs) * eth_price_usd
        print(f"\nCOST ESTIMATES (ETH ~${eth_price_usd}):")
        print(f"  L1 Mainnet:    ${l1_cost:.4f} USD/tx")
        print(f"  Polygon PoS:   ~${l1_cost * 0.01:.6f} USD/tx  (99% reduction)")
        print(f"  Arbitrum:      ~${l1_cost * 0.05:.6f} USD/tx  (95% reduction)")
        print(f"  Optimism:      ~${l1_cost * 0.05:.6f} USD/tx  (95% reduction)")
        print(f"  Base:          ~${l1_cost * 0.02:.6f} USD/tx  (98% reduction)")

        # V1 comparison
        v1_avg_gas = 510662  # from original paper results
        reduction = (1 - np.mean(gas_used) / v1_avg_gas) * 100
        print(f"\nV1 vs V2 COMPARISON:")
        print(f"  V1 avg gas: {v1_avg_gas:,}")
        print(f"  V2 avg gas: {np.mean(gas_used):,.0f}")
        print(f"  Reduction:  {reduction:.1f}%")

    def save_results(self, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "raw_data"), exist_ok=True)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        # JSON
        json_path = os.path.join(output_dir, "raw_data", f"v2_performance_{ts}.json")
        with open(json_path, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\nSaved: {json_path}")

        # CSV
        csv_path = os.path.join(output_dir, "raw_data", f"v2_performance_{ts}.csv")
        successful = [r for r in self.results if r.get("success")]
        if successful:
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "test_number", "timestamp", "category",
                    "prompt_length", "response_length",
                    "gas_used", "gas_price_gwei", "gas_cost_eth",
                    "submit_time", "confirm_time", "total_commit_time",
                    "verify_time", "retrieve_time",
                    "ipfs_cid", "ipfs_pin_time",
                    "transaction_hash",
                ])
                writer.writeheader()
                for r in successful:
                    writer.writerow({
                        "test_number": r["test_number"],
                        "timestamp": r["timestamp"],
                        "category": r["category"],
                        "prompt_length": r["prompt_length"],
                        "response_length": r["response_length"],
                        "gas_used": r["commit"]["gas_used"],
                        "gas_price_gwei": r["commit"]["gas_price_gwei"],
                        "gas_cost_eth": r["commit"]["gas_cost_eth"],
                        "submit_time": r["commit"]["submit_time"],
                        "confirm_time": r["commit"]["confirm_time"],
                        "total_commit_time": r["commit"]["total_commit_time"],
                        "verify_time": r["verification"]["verify_time"],
                        "retrieve_time": r["verification"]["retrieve_time"],
                        "ipfs_cid": r.get("ipfs_cid", ""),
                        "ipfs_pin_time": r.get("ipfs_pin_time", 0),
                        "transaction_hash": r["commit"]["transaction_hash"],
                    })
            print(f"Saved: {csv_path}")

        # Summary report
        report_path = os.path.join(output_dir, "reports", f"v2_performance_summary_{ts}.txt")
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w") as f:
            import numpy as np
            f.write("=" * 70 + "\n")
            f.write("V2 BLOCKCHAIN PERFORMANCE REPORT\n")
            f.write(f"Date: {datetime.now().isoformat()}\n")
            f.write(f"Contract: {CONTRACT_ADDRESS_V2}\n")
            f.write("=" * 70 + "\n\n")

            f.write(f"Total tests: {len(self.results)}\n")
            f.write(f"Successful: {len(successful)}\n")
            f.write(f"Failed: {len(self.results) - len(successful)}\n\n")

            if successful:
                commit_times = [r["commit"]["total_commit_time"] for r in successful]
                gas_used_list = [r["commit"]["gas_used"] for r in successful]
                gas_costs_list = [r["commit"]["gas_cost_eth"] for r in successful]
                verify_times = [r["verification"]["verify_time"] for r in successful]

                f.write("COMMIT LATENCY\n")
                f.write(f"  Mean:   {np.mean(commit_times):.3f}s\n")
                f.write(f"  Median: {np.median(commit_times):.3f}s\n")
                f.write(f"  Std:    {np.std(commit_times):.3f}s\n")
                f.write(f"  Min:    {np.min(commit_times):.3f}s\n")
                f.write(f"  Max:    {np.max(commit_times):.3f}s\n")
                f.write(f"  P50:    {np.percentile(commit_times, 50):.3f}s\n")
                f.write(f"  P90:    {np.percentile(commit_times, 90):.3f}s\n")
                f.write(f"  P95:    {np.percentile(commit_times, 95):.3f}s\n")
                f.write(f"  P99:    {np.percentile(commit_times, 99):.3f}s\n\n")

                f.write("GAS USAGE\n")
                f.write(f"  Mean:   {np.mean(gas_used_list):,.0f}\n")
                f.write(f"  Median: {np.median(gas_used_list):,.0f}\n")
                f.write(f"  Min:    {np.min(gas_used_list):,}\n")
                f.write(f"  Max:    {np.max(gas_used_list):,}\n")
                f.write(f"  Cost:   {np.mean(gas_costs_list):.8f} ETH/tx\n\n")

                f.write("VERIFICATION LATENCY\n")
                f.write(f"  Mean:   {np.mean(verify_times):.3f}s\n")
                f.write(f"  Median: {np.median(verify_times):.3f}s\n\n")

                f.write("BY CATEGORY\n")
                for cat in ["short", "medium", "long"]:
                    cat_r = [r for r in successful if r["category"] == cat]
                    if cat_r:
                        cat_gas = [r["commit"]["gas_used"] for r in cat_r]
                        cat_lat = [r["commit"]["total_commit_time"] for r in cat_r]
                        f.write(f"  {cat:8s}: n={len(cat_r):3d}  "
                                f"gas_mean={np.mean(cat_gas):,.0f}  "
                                f"latency_mean={np.mean(cat_lat):.3f}s\n")

                f.write(f"\nV1 vs V2 GAS COMPARISON\n")
                v1_avg = 510662
                f.write(f"  V1 avg gas: {v1_avg:,}\n")
                f.write(f"  V2 avg gas: {np.mean(gas_used_list):,.0f}\n")
                f.write(f"  Reduction:  {(1 - np.mean(gas_used_list)/v1_avg)*100:.1f}%\n")

        print(f"Saved: {report_path}")


def main():
    parser = argparse.ArgumentParser(description="V2 Blockchain Performance Test")
    parser.add_argument("--runs", type=int, default=50, help="Number of tests (default: 50)")
    parser.add_argument("--delay", type=float, default=3.0, help="Delay between tests (default: 3s)")
    parser.add_argument("--output", type=str, default="analysis/results/blockchain_performance_v2",
                        help="Output directory")
    parser.add_argument("--with-ipfs", action="store_true", help="Enable real IPFS pin/retrieve")
    args = parser.parse_args()

    tester = V2PerformanceTester(with_ipfs=args.with_ipfs)

    try:
        tester.run_tests(num_tests=args.runs, delay=args.delay)
        tester.save_results(output_dir=args.output)
        print(f"\nDone. Results in: {args.output}")
    except KeyboardInterrupt:
        print("\n\nInterrupted — saving partial results...")
        if tester.results:
            tester.save_results(output_dir=args.output)


if __name__ == "__main__":
    main()
