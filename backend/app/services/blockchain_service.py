from web3 import Web3
import json
from typing import Dict, Any, Optional
from app import db
from app.models.verification_record import VerificationRecord

class BlockchainService:
    """블록체인 연동 서비스"""
    
    def __init__(self, rpc_url: str, private_key: str, contract_address: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.private_key = private_key
        self.contract_address = contract_address
        self.account = self.w3.eth.account.from_key(private_key)
        
        # 컨트랙트 ABI (실제 배포 후 업데이트 필요)
        self.contract_abi = [
            {
                "inputs": [
                    {"internalType": "string", "name": "hash", "type": "string"},
                    {"internalType": "uint256", "name": "timestamp", "type": "uint256"}
                ],
                "name": "storeHash",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "string", "name": "hash", "type": "string"}
                ],
                "name": "verifyHash",
                "outputs": [
                    {"internalType": "bool", "name": "", "type": "bool"},
                    {"internalType": "uint256", "name": "", "type": "uint256"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=self.contract_abi
        )
    
    def commit_hash(self, hash_value: str, verification_record_id: int) -> Dict[str, Any]:
        """
        해시를 블록체인에 커밋
        
        Args:
            hash_value: 커밋할 해시값
            verification_record_id: 검증 기록 ID
        
        Returns:
            Dict: 트랜잭션 정보
        """
        try:
            # 현재 타임스탬프
            timestamp = int(self.w3.eth.get_block('latest')['timestamp'])
            
            # 트랜잭션 구성
            transaction = self.contract.functions.storeHash(
                hash_value, timestamp
            ).build_transaction({
                'from': self.account.address,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
            })
            
            # 트랜잭션 서명
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            
            # 트랜잭션 전송
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # 트랜잭션 영수증 대기
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # 검증 기록 업데이트
            verification_record = VerificationRecord.query.get(verification_record_id)
            if verification_record:
                verification_record.transaction_hash = tx_hash.hex()
                verification_record.block_number = tx_receipt.blockNumber
                verification_record.verified = True
                db.session.commit()
            
            return {
                'transaction_hash': tx_hash.hex(),
                'block_number': tx_receipt.blockNumber,
                'gas_used': tx_receipt.gasUsed,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error_message': str(e)
            }
    
    def verify_hash(self, hash_value: str) -> Dict[str, Any]:
        """
        블록체인에서 해시 검증
        
        Args:
            hash_value: 검증할 해시값
        
        Returns:
            Dict: 검증 결과
        """
        try:
            # 컨트랙트에서 해시 검증
            result = self.contract.functions.verifyHash(hash_value).call()
            exists, timestamp = result
            
            return {
                'exists': exists,
                'timestamp': timestamp,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'exists': False,
                'status': 'error',
                'error_message': str(e)
            }
    
    def get_network_info(self) -> Dict[str, Any]:
        """네트워크 정보 조회"""
        try:
            latest_block = self.w3.eth.get_block('latest')
            return {
                'network_id': self.w3.eth.chain_id,
                'latest_block': latest_block.number,
                'gas_price': self.w3.eth.gas_price,
                'account_balance': self.w3.eth.get_balance(self.account.address),
                'status': 'connected'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error_message': str(e)
            }
