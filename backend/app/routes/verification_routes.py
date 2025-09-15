from flask import Blueprint, request, jsonify
from app.models.verification_record import VerificationRecord
from app.services.blockchain_service import BlockchainService
from app import db
from config import Config
from datetime import datetime

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
        
        verified = verification_result.get('exists', False) and verification_result.get('is_success', False)
        
        return jsonify({
            'verified': verified,
            'transaction_hash': hash_value,
            'blockchain_info': verification_result,
            'message': '검증 완료' if verified else '트랜잭션을 찾을 수 없거나 실패했습니다'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@verification_bp.route('/record/<int:record_id>', methods=['GET'])
def get_verification_record(record_id):
    """
    특정 검증 기록 조회
    """
    try:
        verification_record = VerificationRecord.query.get_or_404(record_id)
        return jsonify(verification_record.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@verification_bp.route('/records', methods=['GET'])
def list_verification_records():
    """
    검증 기록 목록 조회
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        provider = request.args.get('provider')
        verified = request.args.get('verified')
        
        query = VerificationRecord.query
        
        if provider:
            query = query.filter_by(llm_provider=provider)
        
        if verified is not None:
            query = query.filter_by(verified=verified.lower() == 'true')
        
        records = query.order_by(VerificationRecord.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'records': [record.to_dict() for record in records.items],
            'total': records.total,
            'pages': records.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@verification_bp.route('/search', methods=['POST'])
def search_by_content():
    """
    내용으로 검증 기록 검색
    """
    try:
        data = request.get_json()
        
        if 'query' not in data:
            return jsonify({'error': '검색 쿼리가 필요합니다'}), 400
        
        query = data['query']
        search_type = data.get('type', 'both')  # 'prompt', 'response', 'both'
        
        search_query = VerificationRecord.query
        
        if search_type in ['prompt', 'both']:
            search_query = search_query.filter(VerificationRecord.prompt.contains(query))
        
        if search_type in ['response', 'both']:
            search_query = search_query.filter(VerificationRecord.response.contains(query))
        
        records = search_query.order_by(VerificationRecord.created_at.desc()).limit(50).all()
        
        return jsonify({
            'records': [record.to_dict() for record in records],
            'total': len(records)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
