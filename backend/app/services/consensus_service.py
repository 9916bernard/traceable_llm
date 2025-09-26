import asyncio
import time
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.services.llm_service import LLMService

class ConsensusService:
    """LLM Consensus 검증 서비스"""
    
    def __init__(self):
        self.llm_service = LLMService()
        # 5개의 LLM 모델 정의
        self.consensus_models = [
            {'provider': 'openai', 'model': 'gpt-5-mini'},
            {'provider': 'grok', 'model': 'llama-3.3-70b-instruct:free'},
            {'provider': 'claude', 'model': 'claude-3.7-sonnet'},
            {'provider': 'gemini', 'model': 'gemini-2.5-flash-lite'},
            {'provider': 'deepseek', 'model': 'deepseek-chat-v3.1:free'}
        ]
        self.consensus_threshold = 3  # 3명 이상 동의 필요
        self.consensus_timeout = 60  # 30초 → 60초 (200% 증가)
    
    def create_consensus_prompt(self, original_prompt: str) -> str:
        """Consensus 검증을 위한 프롬프트 생성"""
        return f"""You are a content safety evaluator. Please analyze the following prompt and determine if it contains harmful, inappropriate, or manipulative content.

Prompt to evaluate: "{original_prompt}"

Please respond with ONLY "True" if the prompt is harmful, inappropriate, or manipulative, or "False" if the prompt is safe and appropriate.

Your response should be exactly "True" or "False" with no additional text or explanation."""

    def parse_consensus_response(self, response: str) -> bool:
        """LLM 응답을 True/False로 파싱"""
        response = response.strip().lower()
        if 'true' in response:
            return True
        elif 'false' in response:
            return False
        else:
            # 응답이 명확하지 않은 경우 기본적으로 False (안전하다고 가정)
            return False
    
    def call_single_consensus_model(self, model_info: Dict[str, str], prompt: str) -> Tuple[str, bool, float]:
        """단일 모델에 대한 consensus 호출"""
        try:
            start_time = time.time()
            response = self.llm_service.call_llm(
                provider=model_info['provider'],
                model=model_info['model'],
                prompt=prompt,
                parameters={'temperature': 0.1, 'max_tokens': 10}
            )
            response_time = time.time() - start_time
            
            is_harmful = self.parse_consensus_response(response['content'])
            return model_info['provider'], is_harmful, response_time
            
        except Exception as e:
            # 오류 발생 시 기본적으로 False (안전하다고 가정)
            return model_info['provider'], False, 0.0
    
    def run_consensus_validation(self, original_prompt: str) -> Dict[str, Any]:
        """Consensus 검증 실행"""
        consensus_prompt = self.create_consensus_prompt(original_prompt)
        
        # 병렬로 모든 모델에 요청
        results = []
        model_responses = {}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            # 모든 모델에 동시 요청
            future_to_model = {
                executor.submit(self.call_single_consensus_model, model, consensus_prompt): model
                for model in self.consensus_models
            }
            
            # 결과 수집 (타임아웃 적용)
            try:
                for future in as_completed(future_to_model, timeout=self.consensus_timeout):
                    model = future_to_model[future]
                    try:
                        provider, is_harmful, response_time = future.result()
                        model_responses[provider] = {
                            'is_harmful': is_harmful,
                            'response_time': response_time,
                            'model': model['model']
                        }
                    except Exception as e:
                        # 오류 발생 시 기본값으로 처리
                        model_responses[model['provider']] = {
                            'is_harmful': False,
                            'response_time': 0.0,
                            'model': model['model'],
                            'error': str(e)
                        }
            except TimeoutError:
                # 타임아웃 발생 시 미완료된 모델들을 기본값으로 처리
                for future, model in future_to_model.items():
                    if not future.done():
                        model_responses[model['provider']] = {
                            'is_harmful': False,
                            'response_time': 0.0,
                            'model': model['model'],
                            'error': 'Consensus timeout'
                        }
        
        # 결과 분석
        harmful_count = sum(1 for response in model_responses.values() if response['is_harmful'])
        safe_count = len(model_responses) - harmful_count
        
        consensus_passed = safe_count >= self.consensus_threshold
        
        return {
            'consensus_passed': consensus_passed,
            'total_models': len(self.consensus_models),
            'harmful_votes': harmful_count,
            'safe_votes': safe_count,
            'threshold': self.consensus_threshold,
            'model_responses': model_responses,
            'consensus_message': self._generate_consensus_message(
                consensus_passed, harmful_count, safe_count
            )
        }
    
    def _generate_consensus_message(self, passed: bool, harmful_count: int, safe_count: int) -> str:
        """Consensus 결과에 따른 메시지 생성"""
        if passed:
            return f"Consensus validation passed. {safe_count} out of 5 models agreed that the prompt is safe."
        else:
            return f"The prompt has been rejected by consensus validation. {harmful_count} out of 5 models identified this as an inappropriate prompt."
