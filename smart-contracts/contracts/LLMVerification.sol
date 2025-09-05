// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title LLMVerification
 * @dev LLM 출력의 진위를 검증하기 위한 스마트 컨트랙트
 * @author LLM Verification System
 */
contract LLMVerification is Ownable, ReentrancyGuard {
    // 해시 저장을 위한 구조체
    struct HashRecord {
        string hash;
        uint256 timestamp;
        address submitter;
        bool exists;
    }

    // 이벤트 정의
    event HashStored(
        string indexed hash,
        uint256 timestamp,
        address indexed submitter,
        uint256 blockNumber
    );
    
    event HashVerified(
        string indexed hash,
        bool verified,
        uint256 timestamp
    );

    // 해시 저장소
    mapping(string => HashRecord) private hashRecords;
    
    // 제출된 해시 목록 (인덱싱용)
    string[] private submittedHashes;
    
    // 통계 정보
    uint256 public totalHashes;
    uint256 public totalVerifications;

    // 생성자
    constructor() Ownable(msg.sender) {}

    /**
     * @dev 해시를 블록체인에 저장
     * @param hash 저장할 해시값
     * @param timestamp 해시 생성 시점의 타임스탬프
     */
    function storeHash(
        string memory hash,
        uint256 timestamp
    ) external nonReentrant {
        require(bytes(hash).length == 64, "Invalid hash length");
        require(timestamp > 0, "Invalid timestamp");
        require(!hashRecords[hash].exists, "Hash already exists");

        // 해시 기록 생성
        hashRecords[hash] = HashRecord({
            hash: hash,
            timestamp: timestamp,
            submitter: msg.sender,
            exists: true
        });

        // 목록에 추가
        submittedHashes.push(hash);
        totalHashes++;

        // 이벤트 발생
        emit HashStored(hash, timestamp, msg.sender, block.number);
    }

    /**
     * @dev 해시의 존재 여부와 정보를 반환
     * @param hash 검증할 해시값
     * @return exists 해시 존재 여부
     * @return timestamp 해시 생성 시점
     * @return submitter 제출자 주소
     */
    function verifyHash(
        string memory hash
    ) external view returns (
        bool exists,
        uint256 timestamp,
        address submitter
    ) {
        HashRecord memory record = hashRecords[hash];
        exists = record.exists;
        timestamp = record.timestamp;
        submitter = record.submitter;

        // 검증 통계 업데이트 (읽기 전용이므로 실제로는 증가하지 않음)
        // 이는 로그 목적으로만 사용
        emit HashVerified(hash, exists, block.timestamp);
    }

    /**
     * @dev 해시의 상세 정보를 반환
     * @param hash 조회할 해시값
     * @return record 해시 기록
     */
    function getHashRecord(
        string memory hash
    ) external view returns (HashRecord memory record) {
        require(hashRecords[hash].exists, "Hash does not exist");
        return hashRecords[hash];
    }

    /**
     * @dev 제출된 해시 목록을 반환 (페이지네이션)
     * @param offset 시작 인덱스
     * @param limit 반환할 개수
     * @return hashes 해시 배열
     * @return total 전체 개수
     */
    function getSubmittedHashes(
        uint256 offset,
        uint256 limit
    ) external view returns (
        string[] memory hashes,
        uint256 total
    ) {
        total = submittedHashes.length;
        
        if (offset >= total) {
            return (new string[](0), total);
        }

        uint256 end = offset + limit;
        if (end > total) {
            end = total;
        }

        uint256 length = end - offset;
        hashes = new string[](length);

        for (uint256 i = 0; i < length; i++) {
            hashes[i] = submittedHashes[offset + i];
        }
    }

    /**
     * @dev 컨트랙트 통계 정보를 반환
     * @return _totalHashes 총 해시 개수
     * @return _totalVerifications 총 검증 횟수
     * @return contractBalance 컨트랙트 잔액
     */
    function getStats() external view returns (
        uint256 _totalHashes,
        uint256 _totalVerifications,
        uint256 contractBalance
    ) {
        return (totalHashes, totalVerifications, address(this).balance);
    }

    /**
     * @dev 해시 존재 여부만 확인 (가스 효율적)
     * @param hash 확인할 해시값
     * @return exists 존재 여부
     */
    function hashExists(string memory hash) external view returns (bool exists) {
        return hashRecords[hash].exists;
    }

    /**
     * @dev 컨트랙트에 ETH 입금 (필요시)
     */
    receive() external payable {
        // ETH 수신 허용
    }

    /**
     * @dev 컨트랙트에서 ETH 출금 (소유자만)
     * @param amount 출금할 금액
     */
    function withdraw(uint256 amount) external onlyOwner {
        require(amount <= address(this).balance, "Insufficient balance");
        payable(owner()).transfer(amount);
    }

    /**
     * @dev 컨트랙트 소유권 이전
     * @param newOwner 새로운 소유자 주소
     */
    function transferOwnership(address newOwner) public override onlyOwner {
        require(newOwner != address(0), "New owner is the zero address");
        _transferOwnership(newOwner);
    }
}
