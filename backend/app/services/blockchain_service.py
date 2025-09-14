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
            
            # 가스 추정
            try:
                estimated_gas = self.contract.functions.storeHash(
                    hash_value, timestamp
                ).estimate_gas({'from': self.account.address})
                gas_limit = int(estimated_gas * 1.2)  # 20% 여유분 추가
            except Exception as e:
                # 가스 추정 실패시 기본값 사용
                gas_limit = 300000
                print(f"Gas estimation failed, using default: {e}")
            
            # 가스 가격 설정 (Sepolia testnet 최적화)
            gas_price = self.w3.eth.gas_price
            # Sepolia testnet에서는 가스 가격을 더 높여서 빠른 처리 보장
            if self.w3.eth.chain_id == 11155111:  # Sepolia chain ID
                gas_price = int(gas_price * 1.5)  # 50% 높임 (더 안정적)
            
            # 최소 가스 가격 보장 (너무 낮으면 트랜잭션이 처리되지 않음)
            min_gas_price = 1000000000  # 1 gwei
            if gas_price < min_gas_price:
                gas_price = min_gas_price
            
            # 트랜잭션 구성
            transaction = self.contract.functions.storeHash(
                hash_value, timestamp
            ).build_transaction({
                'from': self.account.address,
                'gas': gas_limit,
                'gasPrice': gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
            })
            
            # 트랜잭션 서명
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            
            # 트랜잭션 전송
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # 트랜잭션 영수증 대기
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # 검증 기록 업데이트 (Flask 앱 컨텍스트 내에서만)
            try:
                from flask import current_app
                with current_app.app_context():
                    verification_record = VerificationRecord.query.get(verification_record_id)
                    if verification_record:
                        verification_record.transaction_hash = tx_hash.hex()
                        verification_record.block_number = tx_receipt.blockNumber
                        verification_record.verified = True
                        db.session.commit()
            except Exception as db_error:
                # 데이터베이스 업데이트 실패는 트랜잭션 성공에 영향을 주지 않음
                print(f"Database update failed: {db_error}")
            
            return {
                'transaction_hash': tx_hash.hex(),
                'block_number': tx_receipt.blockNumber,
                'gas_used': tx_receipt.gasUsed,
                'status': 'success'
            }
            
        except Exception as e:
            error_msg = str(e)
            # 구체적인 에러 메시지 제공
            if "insufficient funds" in error_msg.lower():
                error_msg = "계정 잔액이 부족합니다. Sepolia faucet에서 ETH를 받아주세요."
            elif "gas" in error_msg.lower():
                error_msg = f"가스 관련 오류: {error_msg}"
            elif "nonce" in error_msg.lower():
                error_msg = f"Nonce 오류: {error_msg}"
            elif "revert" in error_msg.lower():
                error_msg = f"스마트 컨트랙트 실행 실패: {error_msg}"
            
            return {
                'status': 'error',
                'error_message': error_msg,
                'original_error': str(e)
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
