from flask import Blueprint, request, jsonify
from app.services.blockchain_service import BlockchainService
from app.services.hash_service import HashService
from config import Config
import hashlib
import json
import requests
from web3 import Web3

verification_bp = Blueprint('verification', __name__)

@verification_bp.route('/verify', methods=['POST'])
def verify_hash():
    """
    트랜잭션 해시를 통한 LLM 출력 검증 (Etherscan API 사용)
    """
    try:
        data = request.get_json()
        
        if 'hash_value' not in data:
            return jsonify({'error': '해시값이 필요합니다'}), 400
        
        hash_value = data['hash_value']
        
        # Etherscan API를 통한 트랜잭션 검증
        blockchain_service = BlockchainService(
            Config.ETHEREUM_RPC_URL,
            Config.PRIVATE_KEY,
            Config.CONTRACT_ADDRESS
        )
        
        # 트랜잭션 해시 검증
        verification_result = blockchain_service.verify_transaction_hash(hash_value)
        
        # 기본 검증 (트랜잭션 존재 및 성공 여부)
        basic_verified = verification_result.get('exists', False) and verification_result.get('is_success', False)
        
        # 출처 검증 (from 주소가 우리 공식 주소와 일치하는지 확인)
        from_address = verification_result.get('from_address', '')
        our_official_address = "0xaCE2981d41Dce58E6e27a3A04621194Eca44ea65"
        our_official_address_lower = our_official_address.lower()  # UI 표시용 소문자 주소
        origin_verified = from_address.lower() == our_official_address_lower if from_address else False
        
        # 해시 검증 결과
        hash_verification = verification_result.get('hash_verification', {})
        hash_verified = hash_verification.get('verified', False) if hash_verification else False
        
        # 최종 검증 (기본 검증, 출처 검증, 해시 검증 모두 통과해야 함)
        verified = basic_verified and origin_verified and hash_verified
        
        # 응답 메시지 생성
        if verified:
            message = '✅ 검증 완료: 트랜잭션 존재, 출처 일치, 데이터 무결성 확인'
        elif not basic_verified:
            message = '❌ 트랜잭션을 찾을 수 없거나 실패했습니다'
        elif not origin_verified:
            message = '❌ 출처가 일치하지 않습니다'
        elif not hash_verified:
            message = '❌ 해시가 일치하지 않습니다. 데이터가 변조되었을 수 있습니다'
        else:
            message = '❌ 검증 실패'
        
        return jsonify({
            'verified': verified,
            'transaction_hash': hash_value,
            'blockchain_info': verification_result,
            'origin_verification': {
                'from_address': from_address,
                'our_official_address': our_official_address_lower,  # UI에 소문자로 표시
                'origin_verified': origin_verified
            },
            'hash_verification': hash_verification,
            'input_data': verification_result.get('input_data'),
            'message': message
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@verification_bp.route('/verify-input-data', methods=['POST'])
def verify_from_input_data():
    """
    Etherscan Input Data로부터 해시 역계산 및 검증
    
    Input Data 형식:
    {
        "input_data": "hash\nprompt\nresponse\nllm_provider\nmodel_name\ntimestamp\nconsensus_votes"
    }
    또는
    {
        "hash": "...",
        "prompt": "...",
        "response": "...",
        "llm_provider": "...",
        "model_name": "...",
        "timestamp": "...",
        "consensus_votes": "...",
        "parameters": {...}
    }
    """
    try:
        data = request.get_json()
        
        # 두 가지 입력 형식 지원
        if 'input_data' in data:
            # UTF-8 문자열로 받은 경우 파싱
            lines = data['input_data'].strip().split('\n')
            if len(lines) < 7:
                return jsonify({'error': 'Input Data 형식이 올바르지 않습니다 (최소 7개 필드 필요)'}), 400
            
            extracted_data = {
                'hash': lines[0].strip(),
                'prompt': lines[1].strip(),
                'response': lines[2].strip(),
                'llm_provider': lines[3].strip(),
                'model_name': lines[4].strip(),
                'timestamp': lines[5].strip(),
                'consensus_votes': lines[6].strip() if len(lines) > 6 else ''
            }
        else:
            # JSON 객체로 받은 경우
            required_fields = ['hash', 'prompt', 'response', 'llm_provider', 'model_name', 'timestamp']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'필수 필드가 누락되었습니다: {field}'}), 400
            
            extracted_data = {
                'hash': data['hash'],
                'prompt': data['prompt'],
                'response': data['response'],
                'llm_provider': data['llm_provider'],
                'model_name': data['model_name'],
                'timestamp': data['timestamp'],
                'consensus_votes': data.get('consensus_votes', ''),
                'parameters': data.get('parameters', {})
            }
        
        # 해시 재계산을 위한 데이터 구성 (HashService 방식)
        hash_data = {
            'llm_provider': extracted_data['llm_provider'],
            'model_name': extracted_data['model_name'],
            'prompt': extracted_data['prompt'],
            'response': extracted_data['response'],
            'parameters': extracted_data.get('parameters', {}),
            'timestamp': extracted_data['timestamp']
        }
        
        # consensus_votes 추가 (있는 경우)
        if extracted_data.get('consensus_votes'):
            hash_data['consensus_votes'] = extracted_data['consensus_votes']
        
        # JSON 문자열로 변환 (HashService와 동일한 방식)
        json_string = json.dumps(hash_data, sort_keys=True, ensure_ascii=False)
        
        # SHA-256 해시 계산
        calculated_hash = hashlib.sha256(json_string.encode('utf-8')).hexdigest()
        
        # 원본 해시와 비교
        original_hash = extracted_data['hash']
        hash_matches = calculated_hash == original_hash
        
        # 로그 출력
        print("=" * 80)
        print("🔍 HASH VERIFICATION FROM INPUT DATA")
        print("=" * 80)
        print(f"원본 해시:   {original_hash}")
        print(f"계산된 해시: {calculated_hash}")
        print(f"일치 여부:   {'✅ 일치' if hash_matches else '❌ 불일치'}")
        print("=" * 80)
        
        return jsonify({
            'verified': hash_matches,
            'original_hash': original_hash,
            'calculated_hash': calculated_hash,
            'extracted_data': {
                'prompt': extracted_data['prompt'],
                'response': extracted_data['response'],
                'llm_provider': extracted_data['llm_provider'],
                'model_name': extracted_data['model_name'],
                'timestamp': extracted_data['timestamp'],
                'consensus_votes': extracted_data.get('consensus_votes', ''),
                'parameters': hash_data.get('parameters', {})
            },
            'hash_calculation': {
                'json_string': json_string,
                'json_length': len(json_string)
            },
            'message': '해시가 일치합니다. 데이터 무결성이 확인되었습니다.' if hash_matches else '해시가 일치하지 않습니다. 데이터가 변조되었을 수 있습니다.'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


#not used for now network check
@verification_bp.route('/status', methods=['GET'])
def get_blockchain_status():
    """
    블록체인 네트워크 상태 조회
    """
    try:
        if not Config.CONTRACT_ADDRESS:
            return jsonify({
                'status': 'not_configured',
                'message': '블록체인 설정이 완료되지 않았습니다'
            }), 200
        
        blockchain_service = BlockchainService(
            Config.ETHEREUM_RPC_URL,
            Config.PRIVATE_KEY,
            Config.CONTRACT_ADDRESS
        )
        
        network_info = blockchain_service.get_network_info()
        return jsonify(network_info), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error_message': str(e)
        }), 500

