// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title LLMVerification
 * @dev LLM 출력의 진위를 검증하기 위한 스마트 컨트랙트
 * @author LLM Verification System
 * 
 * Python ABI와 완전히 호환되도록 설계됨
 * - storeLLMRecord(): LLM 기록 저장
 * - hashExists(): 해시 존재 여부 확인
 * - getLLMRecord(): LLM 기록 조회
 * - LLMRecordStored 이벤트: 기록 저장 시 발생
 */
contract LLMVerification {
    // LLM 기록을 위한 구조체
    struct LLMRecord {
        bool exists;
        string prompt;
        string response;
        string llm_provider;
        string model_name;
        uint256 timestamp;
        address submitter;
    }

    // Python ABI와 정확히 일치하는 이벤트 정의 , 여기서 이벤트란 emit event 해서 올리는거임 모든 사용자에게 알림이 감 ledger
    event LLMRecordStored(
        string indexed hash,
        string prompt,
        string response,
        string llm_provider,
        string model_name,
        uint256 timestamp,
        address indexed submitter,
        uint256 blockNumber
    );

    // 해시별 LLM 기록 이따 storeLLMRecord 에서 쓰임
    mapping(string => LLMRecord) private llmRecords;
    
    // 해시 존재 여부만 확인하는 매핑 (가스 효율적)
    mapping(string => bool) private _hashExists;

    // 생성자 (Python ABI와 일치)
    constructor() {}

    /**
     * @dev LLM 기록을 블록체인에 저장
     * @param hash 해시값
     * @param prompt 원본 프롬프트
     * @param response LLM 응답
     * @param llm_provider LLM 제공자
     * @param model_name 모델명
     * @param timestamp 타임스탬프
     */
    function storeLLMRecord(
        string memory hash,
        string memory prompt,
        string memory response,
        string memory llm_provider,
        string memory model_name,
        uint256 timestamp
    ) external {
        require(bytes(hash).length == 64, "Invalid hash length");
        require(timestamp > 0, "Invalid timestamp");
        require(!llmRecords[hash].exists, "Record already exists");

        // LLM 기록 저장
        llmRecords[hash] = LLMRecord({
            exists: true,
            prompt: prompt,
            response: response,
            llm_provider: llm_provider,
            model_name: model_name,
            timestamp: timestamp,
            submitter: msg.sender
        });

        // 해시 존재 여부도 저장 (가스 효율적 조회용)
        _hashExists[hash] = true;

        // 이벤트 발생
        emit LLMRecordStored(hash, prompt, response, llm_provider, model_name, timestamp, msg.sender, block.number);
    }

    /**
     * @dev LLM 기록 조회
     * @param hash 조회할 해시값
     * @return exists 존재 여부
     * @return prompt 원본 프롬프트
     * @return response LLM 응답
     * @return llm_provider LLM 제공자
     * @return model_name 모델명
     * @return timestamp 타임스탬프
     * @return submitter 제출자 주소
     */
    function getLLMRecord(string memory hash) external view returns (
        bool exists,
        string memory prompt,
        string memory response,
        string memory llm_provider,
        string memory model_name,
        uint256 timestamp,
        address submitter
    ) {
        LLMRecord memory record = llmRecords[hash];
        return (
            record.exists,
            record.prompt,
            record.response,
            record.llm_provider,
            record.model_name,
            record.timestamp,
            record.submitter
        );
    }

    /**
     * @dev 해시 존재 여부만 확인 (가스 효율적)
     * @param hash 확인할 해시값
     * @return exists 존재 여부
     */
    function hashExists(string memory hash) external view returns (bool exists) {
        return _hashExists[hash];
    }
}
