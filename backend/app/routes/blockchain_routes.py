from flask import Blueprint, request, jsonify
from app.services.blockchain_service import BlockchainService
from config import Config

blockchain_bp = Blueprint('blockchain', __name__)

@blockchain_bp.route('/status', methods=['GET'])
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

@blockchain_bp.route('/verify/<hash_value>', methods=['GET'])
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

@blockchain_bp.route('/commit', methods=['POST'])
def commit_hash_to_blockchain():
    """
    해시를 블록체인에 수동 커밋
    """
    try:
        data = request.get_json()
        
        if 'hash_value' not in data or 'verification_record_id' not in data:
            return jsonify({
                'error': '해시값과 검증 기록 ID가 필요합니다'
            }), 400
        
        if not Config.CONTRACT_ADDRESS:
            return jsonify({
                'error': '블록체인 설정이 완료되지 않았습니다'
            }), 400
        
        blockchain_service = BlockchainService(
            Config.ETHEREUM_RPC_URL,
            Config.PRIVATE_KEY,
            Config.CONTRACT_ADDRESS
        )
        
        result = blockchain_service.commit_hash(
            data['hash_value'],
            data['verification_record_id']
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
