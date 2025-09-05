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
            commit_result = blockchain_service.commit_hash(hash_value, verification_record.id)
            result['blockchain_commit'] = commit_result
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@llm_bp.route('/models', methods=['GET'])
def get_available_models():
    """
    사용 가능한 LLM 모델 목록 조회
    """
    models = {
        'openai': [
            'gpt-5-mini',
            'gpt-5-turbo',
            'gpt-4',
            'gpt-4-turbo',
            'gpt-3.5-turbo',
            'gpt-3.5-turbo-16k'
        ],
        'anthropic': [
            'claude-3-opus-20240229',
            'claude-3-sonnet-20240229',
            'claude-3-haiku-20240307'
        ]
    }
    
    return jsonify(models), 200

@llm_bp.route('/test', methods=['POST'])
def test_openai_connection():
    """
    OpenAI API 연결 테스트
    """
    try:
        from app.services.llm_service import LLMService
        
        llm_service = LLMService()
        
        # 간단한 테스트 프롬프트
        test_prompt = "안녕하세요! 간단한 인사말을 해주세요."
        
        # OpenAI API 호출 테스트
        result = llm_service.call_llm(
            provider='openai',
            model='gpt-3.5-turbo',  # 안정적인 모델 사용
            prompt=test_prompt,
            parameters={
                'temperature': 0.7,
                'max_tokens': 100
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'OpenAI API 연결 성공!',
            'response': result['content'],
            'model': 'gpt-3.5-turbo',
            'prompt': test_prompt
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'OpenAI API 연결 실패: {str(e)}',
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
            model='gpt-3.5-turbo',
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
