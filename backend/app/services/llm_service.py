import requests
import time
import uuid
import os
from typing import Dict, Any, Optional

class LLMService:
    """LLM API 호출 서비스 - OpenRouter 통합"""
    
    def __init__(self):
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY가 설정되지 않았습니다")
        
        # 저가 모델 매핑 (실제 OpenRouter API 모델 ID 사용)
        self.model_mapping = {
            'openai': 'openai/gpt-5-mini',  # 가장 저렴한 OpenAI 모델
            'grok': 'meta-llama/llama-3.3-70b-instruct:free',  # Llama 3.3 70B (무료, 간단한 응답)
            'claude': 'anthropic/claude-3.7-sonnet',  # Claude 3.7 Sonnet
            'gemini': 'google/gemini-2.5-flash-lite',  # Gemini 2.5 Flash Lite
            'deepseek': 'deepseek/deepseek-chat-v3.1:free'  # DeepSeek 무료 모델
        }
    
    def call_llm(
        self,
        provider: str,
        model: str,
        prompt: str,
        parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        OpenRouter를 통한 LLM API 호출
        
        Args:
            provider: LLM 제공자 ('openai', 'grok', 'claude', 'gemini', 'deepseek')
            model: 모델 이름 (실제로는 provider에 따라 자동 매핑됨)
            prompt: 입력 프롬프트
            parameters: LLM 파라미터
        
        Returns:
            Dict: 응답 데이터
        """
        if parameters is None:
            parameters = {}
        
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # OpenRouter를 통한 API 호출
            response = self._call_openrouter(provider, prompt, parameters)
            
            response_time = time.time() - start_time
            
            return {
                'request_id': request_id,
                'content': response['content'],
                'model': self.model_mapping.get(provider, model),
                'provider': provider,
                'response_time': response_time,
                'parameters': parameters
            }
            
        except Exception as e:
            raise e
    
    def _call_openrouter(self, provider: str, prompt: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """OpenRouter API 호출"""
        if provider not in self.model_mapping:
            raise ValueError(f"지원하지 않는 LLM 제공자: {provider}")
        
        model = self.model_mapping[provider]
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://llm-verification-system.com",  # OpenRouter 요구사항
            "X-Title": "LLM Verification System"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 200
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                error_msg = f"OpenRouter API 오류: {response.status_code}"
                if response.text:
                    try:
                        error_data = response.json()
                        error_msg += f" - {error_data.get('error', {}).get('message', response.text)}"
                    except:
                        error_msg += f" - {response.text}"
                raise Exception(error_msg)
            
            data = response.json()
            
            if 'choices' not in data or not data['choices']:
                raise Exception("OpenRouter API 응답에 choices가 없습니다")
            
            message = data['choices'][0]['message']
            content = message.get('content', '')
            
            # Grok 모델의 경우 reasoning 필드에서 응답을 가져옴
            if not content and 'reasoning' in message and message['reasoning']:
                content = message['reasoning']
            
            return {
                'content': content,
                'usage': data.get('usage', {})
            }
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"OpenRouter API 요청 실패: {str(e)}")
        except Exception as e:
            raise Exception(f"OpenRouter API 호출 중 오류: {str(e)}")
