// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title LLMVerificationV2
 * @dev Hash-only on-chain storage with IPFS CID reference.
 *
 * V2 stores only a content hash and an IPFS CID on-chain.
 * Full plaintext (prompt, response, parameters) lives off-chain on IPFS.
 * This reduces gas cost by ~85% compared to V1 and enables GDPR
 * compliance via IPFS unpinning (right to be forgotten).
 *
 * Verification flow:
 *   1. Retrieve IPFS CID from on-chain record
 *   2. Fetch full JSON from IPFS using the CID
 *   3. Recompute SHA-256 hash from the JSON
 *   4. Compare with on-chain contentHash
 */
contract LLMVerificationV2 {
    struct LLMRecord {
        bool exists;
        bytes32 contentHash;       // SHA-256 hash of the canonicalized record
        string ipfsCID;            // IPFS Content Identifier for off-chain data
        string consensusVotes;     // e.g. "3/5"
        address submitter;
        uint256 timestamp;         // block.timestamp at commit time
    }

    // Content hash => record
    mapping(bytes32 => LLMRecord) private records;

    // List of all content hashes for enumeration
    bytes32[] private allHashes;

    event RecordStored(
        bytes32 indexed contentHash,
        string ipfsCID,
        string consensusVotes,
        address indexed submitter,
        uint256 timestamp,
        uint256 blockNumber
    );

    constructor() {}

    /**
     * @dev Store a hash-only LLM record on-chain.
     * @param contentHash SHA-256 hash of the canonicalized LLM record (32 bytes)
     * @param ipfsCID IPFS Content Identifier where the full record is stored
     * @param consensusVotes Consensus vote result (e.g. "3/5")
     */
    function storeRecord(
        bytes32 contentHash,
        string calldata ipfsCID,
        string calldata consensusVotes
    ) external {
        require(contentHash != bytes32(0), "Invalid content hash");
        require(bytes(ipfsCID).length > 0, "Invalid IPFS CID");
        require(!records[contentHash].exists, "Record already exists");

        records[contentHash] = LLMRecord({
            exists: true,
            contentHash: contentHash,
            ipfsCID: ipfsCID,
            consensusVotes: consensusVotes,
            submitter: msg.sender,
            timestamp: block.timestamp
        });

        allHashes.push(contentHash);

        emit RecordStored(
            contentHash,
            ipfsCID,
            consensusVotes,
            msg.sender,
            block.timestamp,
            block.number
        );
    }

    /**
     * @dev Check if a content hash exists on-chain.
     */
    function hashExists(bytes32 contentHash) external view returns (bool) {
        return records[contentHash].exists;
    }

    /**
     * @dev Retrieve an LLM record by content hash.
     */
    function getRecord(bytes32 contentHash) external view returns (
        bool exists,
        string memory ipfsCID,
        string memory consensusVotes,
        address submitter,
        uint256 timestamp
    ) {
        LLMRecord storage r = records[contentHash];
        return (r.exists, r.ipfsCID, r.consensusVotes, r.submitter, r.timestamp);
    }

    /**
     * @dev Get total number of stored records.
     */
    function totalRecords() external view returns (uint256) {
        return allHashes.length;
    }
}
