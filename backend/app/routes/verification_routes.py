from flask import Blueprint, request, jsonify
from app.services.blockchain_service import BlockchainService
from app.services.hash_service import HashService
from app.services.ipfs_service import IPFSService
from config import Config
import hashlib
import hmac
import json
import requests
from web3 import Web3

verification_bp = Blueprint('verification', __name__)

@verification_bp.route('/verify', methods=['POST'])
def verify_hash():
    """
    트랜잭션 해시를 통한 LLM 출력 검증 (V1 plaintext / V2 IPFS 자동 감지)
    """
    try:
        data = request.get_json()

        if 'hash_value' not in data:
            return jsonify({'error': 'Hash value is required'}), 400

        hash_value = data['hash_value']

        # --- V2 감지: tx의 to 주소가 V2 컨트랙트인지 확인 ---
        is_v2 = False
        if Config.CONTRACT_ADDRESS_V2:
            try:
                w3 = Web3(Web3.HTTPProvider(Config.ETHEREUM_RPC_URL))
                tx = w3.eth.get_transaction(hash_value)
                to_address = (tx.get('to') or '').lower()
                is_v2 = to_address == Config.CONTRACT_ADDRESS_V2.lower()
            except Exception:
                pass  # tx 조회 실패 시 V1으로 진행

        if is_v2:
            return _verify_v2(hash_value)
        else:
            return _verify_v1(hash_value)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _verify_v1(hash_value: str):
    """V1 검증: on-chain plaintext에서 HMAC 재계산"""
    blockchain_service = BlockchainService(
        Config.ETHEREUM_RPC_URL,
        Config.PRIVATE_KEY,
        Config.CONTRACT_ADDRESS
    )

    verification_result = blockchain_service.verify_transaction_hash(hash_value)

    # 기본 검증 (트랜잭션 존재 및 성공 여부)
    basic_verified = verification_result.get('exists', False) and verification_result.get('is_success', False)

    # 출처 검증
    from_address = verification_result.get('from_address', '')
    our_official_address = "0xaCE2981d41Dce58E6e27a3A04621194Eca44ea65"
    our_official_address_lower = our_official_address.lower()
    origin_verified = from_address.lower() == our_official_address_lower if from_address else False

    # 해시 검증 결과
    hash_verification = verification_result.get('hash_verification', {})
    hash_verified = hash_verification.get('verified', False) if hash_verification else False

    verified = basic_verified and origin_verified and hash_verified

    if verified:
        message = 'Verification complete: Transaction exists, origin matched, data integrity confirmed'
    elif not basic_verified:
        message = 'Transaction not found or failed'
    elif not origin_verified:
        message = 'Origin does not match'
    elif not hash_verified:
        message = 'Hash does not match. Data may have been tampered with'
    else:
        message = 'Verification failed'

    return jsonify({
        'verified': verified,
        'version': 'v1',
        'transaction_hash': hash_value,
        'blockchain_info': verification_result,
        'origin_verification': {
            'from_address': from_address,
            'our_official_address': our_official_address_lower,
            'origin_verified': origin_verified
        },
        'hash_verification': hash_verification,
        'input_data': verification_result.get('input_data'),
        'message': message
    }), 200


def _verify_v2(hash_value: str):
    """V2 검증: on-chain hash + IPFS에서 데이터 검증"""
    blockchain_service = BlockchainService(
        Config.ETHEREUM_RPC_URL,
        Config.PRIVATE_KEY,
        Config.CONTRACT_ADDRESS_V2,
        contract_version='v2'
    )

    verification_result = blockchain_service.verify_transaction_hash_v2(hash_value)

    # 기본 검증
    basic_verified = verification_result.get('exists', False) and verification_result.get('is_success', False)

    # 출처 검증
    from_address = verification_result.get('from_address', '')
    our_official_address = "0xaCE2981d41Dce58E6e27a3A04621194Eca44ea65"
    our_official_address_lower = our_official_address.lower()
    origin_verified = from_address.lower() == our_official_address_lower if from_address else False

    # IPFS 데이터 가져오기 + HMAC 해시 재계산
    ipfs_cid = verification_result.get('ipfs_cid', '')
    content_hash_hex = verification_result.get('content_hash', '')
    ipfs_data = None
    hash_verified = False
    hash_verification = {}

    if ipfs_cid:
        try:
            ipfs_service = IPFSService(Config.PINATA_API_KEY, Config.PINATA_API_SECRET)
            ipfs_data = ipfs_service.retrieve_from_ipfs(ipfs_cid)

            # HMAC-SHA256 재계산
            hash_data = {
                'llm_provider': ipfs_data.get('llm_provider', ''),
                'model_name': ipfs_data.get('model_name', ''),
                'prompt': ipfs_data.get('prompt', ''),
                'response': ipfs_data.get('response', ''),
                'parameters': ipfs_data.get('parameters', {}),
                'timestamp': ipfs_data.get('timestamp', '')
            }
            if ipfs_data.get('consensus_votes'):
                hash_data['consensus_votes'] = ipfs_data['consensus_votes']

            json_string = json.dumps(hash_data, sort_keys=True, ensure_ascii=False)

            secret_key = Config.HMAC_SECRET_KEY
            calculated_hash = hmac.new(
                key=secret_key.encode('utf-8'),
                msg=json_string.encode('utf-8'),
                digestmod=hashlib.sha256
            ).hexdigest()

            hash_verified = calculated_hash == content_hash_hex

            hash_verification = {
                'verified': hash_verified,
                'original_hash': content_hash_hex,
                'calculated_hash': calculated_hash,
                'message': 'HMAC hash matches — data integrity confirmed.' if hash_verified else 'HMAC hash mismatch — data may have been tampered with.'
            }

            print("=" * 80)
            print("🔍 V2 HMAC HASH VERIFICATION (IPFS → on-chain)")
            print("=" * 80)
            print(f"  On-chain hash:   {content_hash_hex}")
            print(f"  Calculated hash: {calculated_hash}")
            print(f"  Match:           {'✅' if hash_verified else '❌'}")
            print("=" * 80)

        except Exception as e:
            print(f"V2 IPFS retrieval/verification error: {e}")
            hash_verification = {
                'verified': False,
                'error': str(e)
            }

    verified = basic_verified and origin_verified and hash_verified

    if verified:
        message = 'V2 Verification complete: Transaction exists, IPFS data retrieved, hash matches, origin confirmed'
    elif not basic_verified:
        message = 'Transaction not found or failed'
    elif not origin_verified:
        message = 'Origin does not match'
    elif not hash_verified:
        message = 'Hash does not match or IPFS data unavailable'
    else:
        message = 'Verification failed'

    # input_data를 V1과 동일한 형태로 매핑 (프론트엔드 호환)
    input_data = None
    if ipfs_data:
        params = ipfs_data.get('parameters', {})
        input_data = {
            'hash': content_hash_hex,
            'prompt': ipfs_data.get('prompt', ''),
            'response': ipfs_data.get('response', ''),
            'llm_provider': ipfs_data.get('llm_provider', ''),
            'model_name': ipfs_data.get('model_name', ''),
            'timestamp': ipfs_data.get('timestamp', ''),
            'consensus_votes': ipfs_data.get('consensus_votes', ''),
            'parameters': json.dumps(params, sort_keys=True, ensure_ascii=False) if isinstance(params, dict) else str(params),
        }

    return jsonify({
        'verified': verified,
        'version': 'v2',
        'transaction_hash': hash_value,
        'blockchain_info': verification_result,
        'origin_verification': {
            'from_address': from_address,
            'our_official_address': our_official_address_lower,
            'origin_verified': origin_verified
        },
        'hash_verification': hash_verification,
        'input_data': input_data,
        'ipfs_cid': ipfs_cid,
        'ipfs_gateway_url': f"https://gateway.pinata.cloud/ipfs/{ipfs_cid}" if ipfs_cid else None,
        'ipfs_data': ipfs_data,
        'message': message
    }), 200


@verification_bp.route('/retrieve-ipfs', methods=['POST'])
def retrieve_ipfs():
    """IPFS CID로 off-chain 레코드 조회"""
    try:
        data = request.get_json()
        cid = data.get('cid')

        if not cid:
            return jsonify({'error': 'CID is required'}), 400

        ipfs_service = IPFSService(Config.PINATA_API_KEY, Config.PINATA_API_SECRET)
        record = ipfs_service.retrieve_from_ipfs(cid)

        return jsonify({
            'cid': cid,
            'gateway_url': f"https://gateway.pinata.cloud/ipfs/{cid}",
            'data': record
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@verification_bp.route('/verify-input-data', methods=['POST'])
def verify_from_input_data():
    """
    Etherscan Input Data로부터 HMAC 해시 역계산 및 검증
    """
    try:
        data = request.get_json()

        # 두 가지 입력 형식 지원
        if 'input_data' in data:
            lines = data['input_data'].strip().split('\n')
            if len(lines) < 7:
                return jsonify({'error': 'Invalid input data format (minimum 7 fields required)'}), 400

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
            required_fields = ['hash', 'prompt', 'response', 'llm_provider', 'model_name', 'timestamp']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Required field is missing: {field}'}), 400

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

        hash_data = {
            'llm_provider': extracted_data['llm_provider'],
            'model_name': extracted_data['model_name'],
            'prompt': extracted_data['prompt'],
            'response': extracted_data['response'],
            'parameters': extracted_data.get('parameters', {}),
            'timestamp': extracted_data['timestamp']
        }

        if extracted_data.get('consensus_votes'):
            hash_data['consensus_votes'] = extracted_data['consensus_votes']

        json_string = json.dumps(hash_data, sort_keys=True, ensure_ascii=False)

        secret_key = Config.HMAC_SECRET_KEY
        if not secret_key:
            return jsonify({'error': 'HMAC_SECRET_KEY is not configured'}), 500

        calculated_hash = hmac.new(
            key=secret_key.encode('utf-8'),
            msg=json_string.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        original_hash = extracted_data['hash']
        hash_matches = calculated_hash == original_hash

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
                'json_length': len(json_string),
                'hash_type': 'HMAC-SHA256'
            },
            'message': 'HMAC hash matches — data integrity confirmed.' if hash_matches else 'HMAC hash mismatch — data may have been tampered with.'
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@verification_bp.route('/status', methods=['GET'])
def get_blockchain_status():
    """블록체인 네트워크 상태 조회"""
    try:
        contract_address = Config.CONTRACT_ADDRESS_V2 or Config.CONTRACT_ADDRESS
        if not contract_address:
            return jsonify({
                'status': 'not_configured',
                'message': 'Blockchain configuration is not complete'
            }), 200

        contract_version = 'v2' if Config.CONTRACT_ADDRESS_V2 else 'v1'
        blockchain_service = BlockchainService(
            Config.ETHEREUM_RPC_URL,
            Config.PRIVATE_KEY,
            contract_address,
            contract_version=contract_version
        )

        network_info = blockchain_service.get_network_info()
        return jsonify(network_info), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error_message': str(e)
        }), 500
