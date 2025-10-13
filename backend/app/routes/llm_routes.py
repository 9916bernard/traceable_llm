from flask import Blueprint, request, jsonify
from datetime import datetime
from app.services.llm_service import LLMService
from app.services.hash_service import HashService
from app.services.blockchain_service import BlockchainService
from app.services.consensus_service import ConsensusService
from config import Config

llm_bp = Blueprint('llm', __name__)

@llm_bp.route('/generate', methods=['POST'])
def generate_with_verification():
    """
    LLM 응답 생성 및 검증 해시 커밋 (Consensus 검증 포함)
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
        
        # 1. Consensus 검증 실행
        consensus_service = ConsensusService()
        consensus_result = consensus_service.run_consensus_validation(prompt)
        
        # Consensus 검증 실패 시 에러 반환
        if not consensus_result['consensus_passed']:
            return jsonify({
                'success': False,
                'error': 'Consensus validation failed',
                'consensus_result': consensus_result,
                'message': consensus_result['consensus_message']
            }), 400
        
        # 2. LLM 서비스 호출
        llm_service = LLMService()
        llm_response = llm_service.call_llm(provider, model, prompt, parameters)
        
        # 3. 해시 생성 (consensus 정보 포함)
        hash_service = HashService()
        timestamp = datetime.utcnow()  # timestamp 변수로 저장
        hash_value = hash_service.generate_hash(
            llm_provider=provider,
            model_name=model,
            prompt=prompt,
            response=llm_response['content'],
            parameters=parameters,
            timestamp=timestamp,
            consensus_votes=f"{consensus_result['safe_votes']}/{consensus_result['total_models']}"
        )
        
        result = {
            'request_id': llm_response['request_id'],
            'content': llm_response['content'],
            'hash_value': hash_value,
            'response_time': llm_response['response_time'],
            'model': model,
            'provider': provider,
            'consensus_result': consensus_result
        }
        
        # 4. 블록체인에 커밋
        if commit_to_blockchain and Config.CONTRACT_ADDRESS:
            blockchain_service = BlockchainService(
                Config.ETHEREUM_RPC_URL,
                Config.PRIVATE_KEY,
                Config.CONTRACT_ADDRESS
            )
            # 해시 생성 시 사용된 정확한 timestamp와 consensus_votes 전달
            # timestamp를 그대로 전달 (마이크로초 포함)
            consensus_votes_str = f"{consensus_result['safe_votes']}/{consensus_result['total_models']}"
            
            commit_result = blockchain_service.commit_hash(
                hash_value, 
                prompt, 
                llm_response['content'], 
                provider, 
                model,
                timestamp,  # datetime 객체 그대로 전달
                parameters,  # 파라미터 전달
                consensus_votes_str,
                wait_for_confirmation=False  # TX submission만, confirmation은 대기하지 않음
            )
            result['blockchain_commit'] = commit_result
            
            # 성공적으로 커밋된 경우 (pending 포함), 로컬 해시 대신 트랜잭션 해시를 반환
            if commit_result.get('status') in ['success', 'pending'] and commit_result.get('transaction_hash'):
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



#여기는 테스트
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
            parameters={}
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
            parameters={}
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
