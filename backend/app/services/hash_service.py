import hashlib
import json
from datetime import datetime
from typing import Dict, Any

class HashService:
    """해시 생성 및 검증 서비스"""
    
    @staticmethod
    def generate_hash(
        llm_provider: str,
        model_name: str,
        prompt: str,
        response: str,
        parameters: Dict[str, Any],
        timestamp: datetime = None,
        consensus_votes: str = None
    ) -> str:
        """
        LLM 파라미터와 타임스탬프를 이용한 SHA-256 해시 생성
        
        Args:
            llm_provider: LLM 제공자 (openai, anthropic 등)
            model_name: 모델 이름
            prompt: 입력 프롬프트
            response: LLM 응답
            parameters: LLM 파라미터 (temperature, max_tokens 등)
            timestamp: 타임스탬프 (기본값: 현재 시간)
            consensus_votes: Consensus 투표 결과 (예: "3/5")
        
        Returns:
            str: SHA-256 해시값
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        # 해시 생성을 위한 데이터 구성
        hash_data = {
            'llm_provider': llm_provider,
            'model_name': model_name,
            'prompt': prompt,
            'response': response,
            'parameters': parameters,
            'timestamp': timestamp.isoformat()
        }
        
        # Consensus 투표 결과가 있으면 추가
        if consensus_votes:
            hash_data['consensus_votes'] = consensus_votes
        
        # 🔍 로그: 해시 생성 과정 출력
        print("=" * 80)
        print("🔍 HASH GENERATION DEBUG LOG")
        print("=" * 80)
        print("📊 hash_data 구조:")
        for key, value in hash_data.items():
            if len(str(value)) > 100:
                print(f"  {key}: {str(value)[:100]}... (길이: {len(str(value))})")
            else:
                print(f"  {key}: {repr(value)}")
        print()
        
        # JSON 문자열로 변환 (정렬된 키 순서로)
        json_string = json.dumps(hash_data, sort_keys=True, ensure_ascii=False)
        
        print("🔤 JSON 문자열 (정렬된 키):")
        print(json_string)
        print()
        print(f"📏 JSON 길이: {len(json_string)} bytes")
        print()
        
        # !!!SHA-256 해시 생성!!!
        hash_object = hashlib.sha256(json_string.encode('utf-8'))
        calculated_hash = hash_object.hexdigest()
        
        print(f"🔐 생성된 SHA-256 해시:")
        print(f"  {calculated_hash}")
        print("=" * 80)
        print()
        
        return calculated_hash
    
    @staticmethod
    def verify_hash(
        hash_value: str,
        llm_provider: str,
        model_name: str,
        prompt: str,
        response: str,
        parameters: Dict[str, Any],
        timestamp: datetime
    ) -> bool:
        """
        해시값 검증
        
        Args:
            hash_value: 검증할 해시값
            llm_provider: LLM 제공자
            model_name: 모델 이름
            prompt: 입력 프롬프트
            response: LLM 응답
            parameters: LLM 파라미터
            timestamp: 타임스탬프
        
        Returns:
            bool: 해시값이 일치하면 True, 아니면 False
        """
        expected_hash = HashService.generate_hash(
            llm_provider, model_name, prompt, response, parameters, timestamp
        )
        return hash_value == expected_hash
