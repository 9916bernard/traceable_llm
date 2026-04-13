"""
IPFS Service using Pinata API

Provides off-chain storage for LLM records via IPFS.
Full record JSON is pinned to IPFS; only the content hash and
IPFS CID are stored on-chain (V2 contract).

This enables:
- ~85% gas cost reduction (no plaintext on-chain)
- GDPR compliance via unpinning (right to be forgotten)
- Decentralized, content-addressed storage
"""

import os
import json
import requests
from typing import Dict, Any, Optional


class IPFSService:
    """IPFS pinning/retrieval via Pinata API."""

    PINATA_PIN_URL = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    PINATA_UNPIN_URL = "https://api.pinata.cloud/pinning/unpin"
    IPFS_GATEWAY_URL = "https://gateway.pinata.cloud/ipfs"

    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key or os.getenv("PINATA_API_KEY", "")
        self.api_secret = api_secret or os.getenv("PINATA_API_SECRET", "")

        if not self.api_key or not self.api_secret:
            print("Warning: PINATA_API_KEY or PINATA_API_SECRET not set. "
                  "IPFS operations will fail.")

    def _headers(self) -> dict:
        return {
            "pinata_api_key": self.api_key,
            "pinata_secret_api_key": self.api_secret,
            "Content-Type": "application/json",
        }

    def pin_to_ipfs(self, data: Dict[str, Any], name: str = "llm-record") -> Dict[str, Any]:
        """
        Pin a JSON record to IPFS via Pinata.

        Args:
            data: The LLM record dict to store (prompt, response, parameters, etc.)
            name: A human-readable name for the pin (shown in Pinata dashboard)

        Returns:
            Dict with 'cid' (IPFS CID), 'size', and 'gateway_url'
        """
        payload = {
            "pinataContent": data,
            "pinataMetadata": {
                "name": name,
            },
        }

        response = requests.post(
            self.PINATA_PIN_URL,
            headers=self._headers(),
            json=payload,
            timeout=30,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Pinata pin failed (HTTP {response.status_code}): {response.text}"
            )

        result = response.json()
        cid = result["IpfsHash"]

        return {
            "cid": cid,
            "size": result.get("PinSize", 0),
            "gateway_url": f"{self.IPFS_GATEWAY_URL}/{cid}",
            "timestamp": result.get("Timestamp", ""),
        }

    def retrieve_from_ipfs(self, cid: str) -> Dict[str, Any]:
        """
        Retrieve a JSON record from IPFS by CID.

        Args:
            cid: IPFS Content Identifier

        Returns:
            The stored JSON record as a dict
        """
        url = f"{self.IPFS_GATEWAY_URL}/{cid}"
        response = requests.get(url, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(
                f"IPFS retrieval failed (HTTP {response.status_code}): {response.text}"
            )

        return response.json()

    def unpin_from_ipfs(self, cid: str) -> bool:
        """
        Unpin a record from IPFS (enables right-to-be-forgotten).

        After unpinning, the content will eventually be garbage collected
        by IPFS nodes, making the data effectively deleted. The on-chain
        hash becomes a meaningless 32-byte value without the off-chain data.

        Args:
            cid: IPFS Content Identifier to unpin

        Returns:
            True if unpinning succeeded
        """
        url = f"{self.PINATA_UNPIN_URL}/{cid}"
        response = requests.delete(url, headers=self._headers(), timeout=30)

        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            # Already unpinned
            return True
        else:
            raise RuntimeError(
                f"Pinata unpin failed (HTTP {response.status_code}): {response.text}"
            )

    def test_connection(self) -> bool:
        """Test Pinata API connectivity."""
        url = "https://api.pinata.cloud/data/testAuthentication"
        try:
            response = requests.get(url, headers=self._headers(), timeout=10)
            return response.status_code == 200
        except Exception:
            return False
