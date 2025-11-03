import hashlib
import hmac
import json
from datetime import datetime
from typing import Dict, Any
from config import Config

class HashService:
    """
    HMAC 기반 보안 해시 생성 및 검증 서비스
    
    보안 강화:
    - 기존: SHA256(content) - 공격자가 (content', SHA256(content')) 쌍을 만들어 주입 가능
    - 개선: HMAC-SHA256(secret_key, content) - secret_key 없이는 올바른 HMAC 생성 불가
    
    이를 통해 네트워크 중간에서 데이터와 해시를 함께 수정하는 공격을 방지합니다.
    """
    
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
        LLM 파라미터와 타임스탬프를 이용한 HMAC-SHA256 보안 해시 생성
        
        보안 메커니즘:
        - HMAC (Hash-based Message Authentication Code) 사용
        - Secret key 없이는 올바른 해시를 생성할 수 없음
        - 네트워크 중간 공격(MITM)으로 데이터와 해시를 함께 수정하는 것 방지
        
        Args:
            llm_provider: LLM 제공자 (openai, anthropic 등)
            model_name: 모델 이름
            prompt: 입력 프롬프트
            response: LLM 응답
            parameters: LLM 파라미터 (temperature, max_tokens 등)
            timestamp: 타임스탬프 (기본값: 현재 시간)
            consensus_votes: Consensus 투표 결과 (예: "3/5")
        
        Returns:
            str: HMAC-SHA256 해시값 (64자 16진수 문자열)
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
        print("🔍 HMAC HASH GENERATION DEBUG LOG")
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
        
        # HMAC secret key 가져오기
        secret_key = Config.HMAC_SECRET_KEY
        if not secret_key:
            raise ValueError("HMAC_SECRET_KEY가 설정되지 않았습니다. 환경변수를 확인해주세요.")
        
        # 🔐 HMAC-SHA256 해시 생성 (보안 강화)
        # secret_key를 모르면 올바른 해시를 생성할 수 없음
        calculated_hash = hmac.new(
            key=secret_key.encode('utf-8'),
            msg=json_string.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        print(f"🔐 생성된 HMAC-SHA256 해시:")
        print(f"  {calculated_hash}")
        print(f"🔑 보안: Secret key로 서명됨 (네트워크 중간 공격 방지)")
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
        timestamp: datetime,
        consensus_votes: str = None
    ) -> bool:
        """
        HMAC 해시값 검증
        
        보안 메커니즘:
        - Secret key를 사용하여 HMAC 재계산
        - 계산된 HMAC과 원본 해시 비교
        - Secret key가 없으면 검증 불가능 (보안 강화)
        
        Args:
            hash_value: 검증할 HMAC 해시값
            llm_provider: LLM 제공자
            model_name: 모델 이름
            prompt: 입력 프롬프트
            response: LLM 응답
            parameters: LLM 파라미터
            timestamp: 타임스탬프
            consensus_votes: Consensus 투표 결과 (예: "3/5")
        
        Returns:
            bool: HMAC 해시값이 일치하면 True, 아니면 False
        """
        expected_hash = HashService.generate_hash(
            llm_provider, model_name, prompt, response, parameters, timestamp, consensus_votes
        )
        return hash_value == expected_hash
