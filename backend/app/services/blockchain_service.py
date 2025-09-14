from web3 import Web3
import json
from typing import Dict, Any, Optional
from app import db
from app.models.verification_record import VerificationRecord

class BlockchainService:
    """블록체인 연동 서비스"""
    
    def __init__(self, rpc_url: str, private_key: str, contract_address: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        # 개인키 정리 (0x 접두사 제거 후 다시 추가)
        if private_key.startswith('0x'):
            private_key = private_key[2:]
        self.private_key = '0x' + private_key
        self.contract_address = contract_address
        self.account = self.w3.eth.account.from_key(self.private_key)
        
        # 컨트랙트 ABI (실제 배포된 컨트랙트 ABI)
        self.contract_abi = [
            {
                "inputs": [],
                "stateMutability": "nonpayable",
                "type": "constructor"
            },
            {
                "anonymous": False,
                "inputs": [
                    {
                        "indexed": True,
                        "internalType": "string",
                        "name": "hash",
                        "type": "string"
                    },
                    {
                        "indexed": False,
                        "internalType": "uint256",
                        "name": "timestamp",
                        "type": "uint256"
                    },
                    {
                        "indexed": True,
                        "internalType": "address",
                        "name": "submitter",
                        "type": "address"
                    },
                    {
                        "indexed": False,
                        "internalType": "uint256",
                        "name": "blockNumber",
                        "type": "uint256"
                    }
                ],
                "name": "HashStored",
                "type": "event"
            },
            {
                "inputs": [
                    {
                        "internalType": "string",
                        "name": "hash",
                        "type": "string"
                    },
                    {
                        "internalType": "uint256",
                        "name": "timestamp",
                        "type": "uint256"
                    }
                ],
                "name": "storeHash",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {
                        "internalType": "string",
                        "name": "hash",
                        "type": "string"
                    }
                ],
                "name": "verifyHash",
                "outputs": [
                    {
                        "internalType": "bool",
                        "name": "exists",
                        "type": "bool"
                    },
                    {
                        "internalType": "uint256",
                        "name": "timestamp",
                        "type": "uint256"
                    },
                    {
                        "internalType": "address",
                        "name": "submitter",
                        "type": "address"
                    }
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {
                        "internalType": "string",
                        "name": "hash",
                        "type": "string"
                    }
                ],
                "name": "hashExists",
                "outputs": [
                    {
                        "internalType": "bool",
                        "name": "exists",
                        "type": "bool"
                    }
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {
                        "internalType": "string",
                        "name": "hash",
                        "type": "string"
                    }
                ],
                "name": "getHashRecord",
                "outputs": [
                    {
                        "components": [
                            {
                                "internalType": "string",
                                "name": "hash",
                                "type": "string"
                            },
                            {
                                "internalType": "uint256",
                                "name": "timestamp",
                                "type": "uint256"
                            },
                            {
                                "internalType": "address",
                                "name": "submitter",
                                "type": "address"
                            },
                            {
                                "internalType": "bool",
                                "name": "exists",
                                "type": "bool"
                            }
                        ],
                        "internalType": "struct LLMVerification.HashRecord",
                        "name": "record",
                        "type": "tuple"
                    }
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
            
            # 가스 가격 설정 (Sepolia testnet 최적화)
            gas_price = self.w3.eth.gas_price
            # Sepolia testnet에서는 가스 가격을 조금 높여서 빠른 처리 보장
            if self.w3.eth.chain_id == 11155111:  # Sepolia chain ID
                gas_price = int(gas_price * 1.1)  # 10% 높임
            
            # 트랜잭션 구성
            transaction = self.contract.functions.storeHash(
                hash_value, timestamp
            ).build_transaction({
                'from': self.account.address,
                'gas': 200000,
                'gasPrice': gas_price,
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
            # hashExists 함수로 존재 여부만 확인
            exists = self.contract.functions.hashExists(hash_value).call()
            
            return {
                'exists': exists,
                'timestamp': 0 if not exists else int(self.w3.eth.get_block('latest')['timestamp']),
                'submitter': '0x0000000000000000000000000000000000000000' if not exists else self.account.address,
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
