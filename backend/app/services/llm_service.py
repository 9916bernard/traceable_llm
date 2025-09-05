import openai
import anthropic
import time
import uuid
import os
from typing import Dict, Any, Optional
from datetime import datetime
from app.models.llm_request import LLMRequest
from app import db

class LLMService:
    """LLM API 호출 서비스"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        
        # OpenAI 클라이언트 초기화
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            self.openai_client = openai.OpenAI(api_key=openai_api_key)
        
        # Anthropic 클라이언트 초기화
        anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
    
    def call_llm(
        self,
        provider: str,
        model: str,
        prompt: str,
        parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        LLM API 호출
        
        Args:
            provider: LLM 제공자 ('openai', 'anthropic')
            model: 모델 이름
            prompt: 입력 프롬프트
            parameters: LLM 파라미터
        
        Returns:
            Dict: 응답 데이터
        """
        if parameters is None:
            parameters = {}
        
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # 요청 로그 생성
        llm_request = LLMRequest(
            request_id=request_id,
            llm_provider=provider,
            model_name=model,
            prompt=prompt,
            parameters=parameters,
            status='pending'
        )
        db.session.add(llm_request)
        db.session.commit()
        
        try:
            if provider == 'openai':
                response = self._call_openai(model, prompt, parameters)
            elif provider == 'anthropic':
                response = self._call_anthropic(model, prompt, parameters)
            else:
                raise ValueError(f"지원하지 않는 LLM 제공자: {provider}")
            
            response_time = time.time() - start_time
            
            # 요청 로그 업데이트
            llm_request.response = response['content']
            llm_request.response_time = response_time
            llm_request.status = 'success'
            llm_request.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'request_id': request_id,
                'content': response['content'],
                'model': model,
                'provider': provider,
                'response_time': response_time,
                'parameters': parameters
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            
            # 에러 로그 업데이트
            llm_request.response_time = response_time
            llm_request.status = 'error'
            llm_request.error_message = str(e)
            llm_request.updated_at = datetime.utcnow()
            db.session.commit()
            
            raise e
    
    def _call_openai(self, model: str, prompt: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """OpenAI API 호출"""
        if not self.openai_client:
            raise ValueError("OpenAI API 키가 설정되지 않았습니다")
        
        # 새로운 API 형식 지원 (gpt-5-mini 등)
        if model in ['gpt-5-mini', 'gpt-5-turbo']:
            # 새로운 responses API 사용
            response = self.openai_client.responses.create(
                model=model,
                input=prompt
            )
            return {
                'content': response.output_text,
                'usage': None  # 새로운 API에서는 usage 정보가 다를 수 있음
            }
        else:
            # 기존 chat completions API 사용
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=parameters.get('temperature', 0.7),
                max_tokens=parameters.get('max_tokens', 1000)
            )
            return {
                'content': response.choices[0].message.content,
                'usage': response.usage.dict() if response.usage else None
            }
    
    def _call_anthropic(self, model: str, prompt: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Anthropic API 호출"""
        if not self.anthropic_client:
            raise ValueError("Anthropic API 키가 설정되지 않았습니다")
        
        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=parameters.get('max_tokens', 1000),
            temperature=parameters.get('temperature', 0.7),
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            'content': response.content[0].text,
            'usage': response.usage.dict() if response.usage else None
        }
