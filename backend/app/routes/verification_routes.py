from flask import Blueprint, request, jsonify
from app.services.blockchain_service import BlockchainService
from config import Config

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
        
        # 최종 검증 (기본 검증과 출처 검증 모두 통과해야 함)
        verified = basic_verified and origin_verified
        
        return jsonify({
            'verified': verified,
            'transaction_hash': hash_value,
            'blockchain_info': verification_result,
            'origin_verification': {
                'from_address': from_address,
                'our_official_address': our_official_address_lower,  # UI에 소문자로 표시
                'origin_verified': origin_verified
            },
            'message': '검증 완료' if verified else '트랜잭션을 찾을 수 없거나 출처가 일치하지 않습니다'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@verification_bp.route('/verify/<hash_value>', methods=['GET'])
def verify_hash_on_blockchain(hash_value):
    """
    블록체인에서 해시 검증
    """
    try:
        if not Config.CONTRACT_ADDRESS:
            return jsonify({
                'error': '블록체인 설정이 완료되지 않았습니다'
            }), 400
        
        blockchain_service = BlockchainService(
            Config.ETHEREUM_RPC_URL,
            Config.PRIVATE_KEY,
            Config.CONTRACT_ADDRESS
        )
        
        result = blockchain_service.verify_hash(hash_value)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
