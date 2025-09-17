from flask import Blueprint, request, jsonify
from datetime import datetime
from app.services.llm_service import LLMService
from app.services.hash_service import HashService
from app.services.blockchain_service import BlockchainService
from app.models.verification_record import VerificationRecord
from app import db
from config import Config

llm_bp = Blueprint('llm', __name__)

@llm_bp.route('/generate', methods=['POST'])
def generate_with_verification():
    """
    LLM 응답 생성 및 검증 해시 커밋
    """
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['provider', 'model', 'prompt']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'필수 필드가 누락되었습니다: {field}'}), 400
        
        provider = data['provider']
        model = data['model']
        prompt = data['prompt']
        parameters = data.get('parameters', {})
        commit_to_blockchain = data.get('commit_to_blockchain', True)
        
        # LLM 서비스 호출
        llm_service = LLMService()
        llm_response = llm_service.call_llm(provider, model, prompt, parameters)
        
        # 해시 생성
        hash_service = HashService()
        hash_value = hash_service.generate_hash(
            llm_provider=provider,
            model_name=model,
            prompt=prompt,
            response=llm_response['content'],
            parameters=parameters,
            timestamp=datetime.utcnow()
        )
        
        # 검증 기록 생성
        verification_record = VerificationRecord(
            hash_value=hash_value,
            llm_provider=provider,
            model_name=model,
            prompt=prompt,
            response=llm_response['content'],
            parameters=parameters,
            timestamp=datetime.utcnow()
        )
        db.session.add(verification_record)
        db.session.commit()
        
        result = {
            'request_id': llm_response['request_id'],
            'content': llm_response['content'],
            'hash_value': hash_value,
            'verification_record_id': verification_record.id,
            'response_time': llm_response['response_time'],
            'model': model,
            'provider': provider
        }
        
        # 블록체인에 커밋
        if commit_to_blockchain and Config.CONTRACT_ADDRESS:
            blockchain_service = BlockchainService(
                Config.ETHEREUM_RPC_URL,
                Config.PRIVATE_KEY,
                Config.CONTRACT_ADDRESS
            )
            commit_result = blockchain_service.commit_hash(
                hash_value, 
                prompt, 
                llm_response['content'], 
                provider, 
                model, 
                verification_record.id
            )
            result['blockchain_commit'] = commit_result
            
            # 성공적으로 커밋된 경우, 로컬 해시 대신 트랜잭션 해시를 반환
            if commit_result.get('status') == 'success' and commit_result.get('transaction_hash'):
                result['hash_value'] = commit_result['transaction_hash']
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@llm_bp.route('/models', methods=['GET'])
def get_available_models():
    """
    사용 가능한 LLM 모델 목록 조회 (저가 모델만)
    """
    models = {
        'openai': ['gpt-5-mini'],
        'grok': ['llama-3.3-70b-instruct:free'],
        'claude': ['claude-3.7-sonnet'],
        'gemini': ['gemini-2.5-flash-lite'],
        'deepseek': ['deepseek-chat-v3.1:free']
    }
    
    return jsonify(models), 200

@llm_bp.route('/test', methods=['POST'])
def test_openrouter_connection():
    """
    OpenRouter API 연결 테스트 (사용자 입력 프롬프트 사용)
    """
    try:
        from app.services.llm_service import LLMService
        
        data = request.get_json() or {}
        
        # 사용자가 입력한 프롬프트 사용, 없으면 기본값
        test_prompt = data.get('prompt', "안녕하세요! 간단한 인사말을 해주세요.")
        provider = data.get('provider', 'openai')
        model = data.get('model', 'gpt-5-mini')
        
        llm_service = LLMService()
        
        # OpenRouter를 통한 API 호출 테스트
        result = llm_service.call_llm(
            provider=provider,
            model=model,
            prompt=test_prompt,
            parameters={
                'temperature': 0.7,
                'max_tokens': 500
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'OpenRouter API 연결 성공!',
            'response': result['content'],
            'model': result['model'],
            'provider': result['provider'],
            'prompt': test_prompt
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'OpenRouter API 연결 실패: {str(e)}',
            'error': str(e)
        }), 500

@llm_bp.route('/health', methods=['GET'])
def health_check():
    """
    LLM 서비스 상태 확인
    """
    try:
        llm_service = LLMService()
        
        # 간단한 테스트 요청
        test_response = llm_service.call_llm(
            provider='openai',
            model='gpt-5-mini',
            prompt='Hello',
            parameters={'max_tokens': 10}
        )
        
        return jsonify({
            'status': 'healthy',
            'test_response': test_response['content'][:50] + '...' if len(test_response['content']) > 50 else test_response['content']
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
