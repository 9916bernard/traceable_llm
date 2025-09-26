from web3 import Web3
import requests
import json
import os
from typing import Dict, Any, Optional
from config import Config

class BlockchainService:
    """블록체인 연동 서비스"""
#region 생성자
    def __init__(self, rpc_url: str, private_key: str, contract_address: str):
        # 우리가 Web3 HTTP 사용해서 rpc_url: sepolia testnet 에 연결해서 반환하는 w3 객체 생성
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        # 개인키 정리 (0x 접두사 제거 후 다시 추가) 자꾸 해시 포멧 안맞는다해서 넣음
        if private_key.startswith('0x'):
            private_key = private_key[2:]
        self.private_key = '0x' + private_key
        self.contract_address = contract_address
        # 계정 객체 생성 (지갑)
        self.account = self.w3.eth.account.from_key(self.private_key)
        
        # 컴파일된 ABI 파일에서 로드
        self.contract_abi = self._load_contract_abi()
        
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=self.contract_abi
        )
#endregion

#region 컨트랙트 ABI 로드
    def _load_contract_abi(self) -> list:
        """
        컴파일된 ABI 파일에서 ABI 로드
        
        Returns:
            list: 컨트랙트 ABI
        """
        try:
            # ABI 파일 경로 설정 (프로젝트 루트 기준)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            abi_file_path = os.path.join(
                project_root,
                '..',
                'smart-contracts',
                'artifacts',
                'contracts',
                'LLMVerification.sol',
                'LLMVerification.json'
            )
            abi_file_path = os.path.abspath(abi_file_path)
            
            # ABI 파일이 존재하는지 확인
            if not os.path.exists(abi_file_path):
                raise FileNotFoundError(f"ABI 파일을 찾을 수 없습니다: {abi_file_path}")
            
            # ABI 파일 로드
            with open(abi_file_path, 'r', encoding='utf-8') as f:
                contract_json = json.load(f)
                return contract_json['abi']
                
        except Exception as e:
            print(f"ABI 로드 실패: {e}")
            # 폴백: 기본 ABI 사용 (기존 하드코딩된 ABI)
            return self._get_fallback_abi()
#endregion

#region 컨트랙트 함수 호출
    # def _get_fallback_abi(self) -> list:
    #     """
    #     폴백 ABI (기존 하드코딩된 ABI)
        
    #     Returns:
    #         list: 기본 ABI
    #     """
    #     return [
    #         {
    #             "inputs": [],
    #             "stateMutability": "nonpayable",
    #             "type": "constructor"
    #         },
    #         {
    #             "anonymous": False,
    #             "inputs": [
    #                 {
    #                     "indexed": True,
    #                     "internalType": "string",
    #                     "name": "hash",
    #                     "type": "string"
    #                 },
    #                 {
    #                     "indexed": False,
    #                     "internalType": "string",
    #                     "name": "prompt",
    #                     "type": "string"
    #                 },
    #                 {
    #                     "indexed": False,
    #                     "internalType": "string",
    #                     "name": "response",
    #                     "type": "string"
    #                 },
    #                 {
    #                     "indexed": False,
    #                     "internalType": "string",
    #                     "name": "llm_provider",
    #                     "type": "string"
    #                 },
    #                 {
    #                     "indexed": False,
    #                     "internalType": "string",
    #                     "name": "model_name",
    #                     "type": "string"
    #                 },
    #                 {
    #                     "indexed": False,
    #                     "internalType": "uint256",
    #                     "name": "timestamp",
    #                     "type": "uint256"
    #                 },
    #                 {
    #                     "indexed": True,
    #                     "internalType": "address",
    #                     "name": "submitter",
    #                     "type": "address"
    #                 },
    #                 {
    #                     "indexed": False,
    #                     "internalType": "uint256",
    #                     "name": "blockNumber",
    #                     "type": "uint256"
    #                 }
    #             ],
    #             "name": "LLMRecordStored",
    #             "type": "event"
    #         },
    #         {
    #             "inputs": [
    #                 {
    #                     "internalType": "string",
    #                     "name": "hash",
    #                     "type": "string"
    #                 },
    #                 {
    #                     "internalType": "string",
    #                     "name": "prompt",
    #                     "type": "string"
    #                 },
    #                 {
    #                     "internalType": "string",
    #                     "name": "response",
    #                     "type": "string"
    #                 },
    #                 {
    #                     "internalType": "string",
    #                     "name": "llm_provider",
    #                     "type": "string"
    #                 },
    #                 {
    #                     "internalType": "string",
    #                     "name": "model_name",
    #                     "type": "string"
    #                 },
    #                 {
    #                     "internalType": "uint256",
    #                     "name": "timestamp",
    #                     "type": "uint256"
    #                 }
    #             ],
    #             "name": "storeLLMRecord",
    #             "outputs": [],
    #             "stateMutability": "nonpayable",
    #             "type": "function"
    #         },
    #         {
    #             "inputs": [
    #                 {
    #                     "internalType": "string",
    #                     "name": "hash",
    #                     "type": "string"
    #                 }
    #             ],
    #             "name": "getLLMRecord",
    #             "outputs": [
    #                 {
    #                     "internalType": "bool",
    #                     "name": "exists",
    #                     "type": "bool"
    #                 },
    #                 {
    #                     "internalType": "string",
    #                     "name": "prompt",
    #                     "type": "string"
    #                 },
    #                 {
    #                     "internalType": "string",
    #                     "name": "response",
    #                     "type": "string"
    #                 },
    #                 {
    #                     "internalType": "string",
    #                     "name": "llm_provider",
    #                     "type": "string"
    #                 },
    #                 {
    #                     "internalType": "string",
    #                     "name": "model_name",
    #                     "type": "string"
    #                 },
    #                 {
    #                     "internalType": "uint256",
    #                     "name": "timestamp",
    #                     "type": "uint256"
    #                 },
    #                 {
    #                     "internalType": "address",
    #                     "name": "submitter",
    #                     "type": "address"
    #                 }
    #             ],
    #             "stateMutability": "view",
    #             "type": "function"
    #         },
    #         {
    #             "inputs": [
    #                 {
    #                     "internalType": "string",
    #                     "name": "hash",
    #                     "type": "string"
    #                 }
    #             ],
    #             "name": "hashExists",
    #             "outputs": [
    #                 {
    #                     "internalType": "bool",
    #                     "name": "exists",
    #                     "type": "bool"
    #                 }
    #             ],
    #             "stateMutability": "view",
    #             "type": "function"
    #         }
    #     ]

    #region commit hash
    def commit_hash(self, hash_value: str, prompt: str, response: str, llm_provider: str, model_name: str) -> Dict[str, Any]:
        """
        LLM 기록을 블록체인에 커밋
        
        Args:
            hash_value: 커밋할 해시값
            prompt: 원본 프롬프트
            response: LLM 응답
            llm_provider: LLM 제공자
            model_name: 모델명
        
        Returns:
            Dict: 트랜잭션 정보
        """
        try:
            # 현재 타임스탬프
            timestamp = int(self.w3.eth.get_block('latest')['timestamp'])
            
            # 가스 추정 - 우리 LLMRecord 컨트렉트 함수의 저장 사이즈에 기반해서 web3 의 가스 추정 함수를 사용해서 추정하는듯 - Limit 을 추정하기 위함임
            try:
                estimated_gas = self.contract.functions.storeLLMRecord(
                    hash_value, prompt, response, llm_provider, model_name, timestamp
                ).estimate_gas({'from': self.account.address})
                gas_limit = int(estimated_gas * 1.2)  # 20% 여유분 추가
            except Exception as e:
                # 가스 추정 실패시 기본값 사용 (텍스트 저장으로 인해 더 많은 가스 필요)
                gas_limit = 500000
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
            
            # 문자열을 안전하게 처리 (UTF-8 인코딩)
            # 한글 등 유니코드 문자가 깨지지 않도록 보장
            safe_prompt = prompt.encode('utf-8', errors='ignore').decode('utf-8')
            safe_response = response.encode('utf-8', errors='ignore').decode('utf-8')
            safe_llm_provider = llm_provider.encode('utf-8', errors='ignore').decode('utf-8')
            safe_model_name = model_name.encode('utf-8', errors='ignore').decode('utf-8')
            
            # 트랜잭션 구성 ! 여기서 nounce 생성 ! 
            transaction = self.contract.functions.storeLLMRecord(
                hash_value, safe_prompt, safe_response, safe_llm_provider, safe_model_name, timestamp
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
            
            # DB 업데이트 로직 제거됨 - Etherscan 전용 시스템
            
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
    #endregion

    
# 지금은 쓰이지 않음. 나중에 더 세세한 정보가 필요하면 사용
    # def verify_llm_record(self, hash_value: str) -> Dict[str, Any]:
    #     """
    #     블록체인에서 LLM 기록 검증
        
    #     Args:
    #         hash_value: 검증할 해시값
        
    #     Returns:
    #         Dict: 검증 결과 (프롬프트, 응답, 모델 정보 포함)
    #     """
    #     try:
    #         # 블록체인에서 LLM 기록 조회
    #         result = self.contract.functions.getLLMRecord(hash_value).call()
            
    #         exists = result[0]
    #         if not exists:
    #             return {
    #                 'exists': False,
    #                 'status': 'error',
    #                 'error_message': 'LLM 기록을 찾을 수 없습니다'
    #             }
            
    #         # UTF-8 문자열 안전하게 처리 (한글 깨짐 방지)
    #         prompt = result[1] if result[1] else ""
    #         response = result[2] if result[2] else ""
    #         llm_provider = result[3] if result[3] else ""
    #         model_name = result[4] if result[4] else ""
    #         timestamp = result[5]
    #         submitter = result[6]
            
    #         return {
    #             'exists': True,
    #             'hash_value': hash_value,
    #             'prompt': prompt,
    #             'response': response,
    #             'llm_provider': llm_provider,
    #             'model_name': model_name,
    #             'timestamp': timestamp,
    #             'submitter': submitter,
    #             'status': 'success'
    #         }
            
    #     except Exception as e:
    #         return {
    #             'exists': False,
    #             'status': 'error',
    #             'error_message': str(e)
    #         }

    #region verify hash
    
    def verify_transaction_hash(self, transaction_hash: str) -> Dict[str, Any]:
        """
        Etherscan API를 통해 트랜잭션 해시 검증
        
        Args:
            transaction_hash: 검증할 트랜잭션 해시
        
        Returns:
            Dict: 검증 결과
        """
        try:
            # Sepolia Etherscan API URL
            etherscan_url = "https://api-sepolia.etherscan.io/api"
            api_key = Config.ETHERSCAN_API_KEY or ''
            
            # 트랜잭션 정보 조회
            params = {
                'module': 'proxy',
                'action': 'eth_getTransactionByHash',
                'txhash': transaction_hash,
                'apikey': api_key
            }
            
            response = requests.get(etherscan_url, params=params, timeout=20)  # 10초 → 20초 (200% 증가)
            response.raise_for_status()
            data = response.json()
            
            # 디버깅을 위한 로그 (개발 환경에서만)
            print(f"Etherscan API 응답 (트랜잭션): {data}")
            
            if 'error' in data:
                error_msg = data['error']
                if isinstance(error_msg, dict):
                    error_message = error_msg.get('message', str(error_msg))
                else:
                    error_message = str(error_msg)
                return {
                    'exists': False,
                    'status': 'error',
                    'error_message': error_message
                }
            
            # 트랜잭션이 존재하는지 확인
            if data['result'] is None:
                return {
                    'exists': False,
                    'status': 'error',
                    'error_message': '트랜잭션을 찾을 수 없습니다'
                }
            
            # 트랜잭션 영수증 조회
            receipt_params = {
                'module': 'proxy',
                'action': 'eth_getTransactionReceipt',
                'txhash': transaction_hash,
                'apikey': api_key
            }
            
            receipt_response = requests.get(etherscan_url, params=receipt_params, timeout=20)  # 10초 → 20초 (200% 증가)
            receipt_response.raise_for_status()
            receipt_data = receipt_response.json()
            
            # 디버깅을 위한 로그 (개발 환경에서만)
            print(f"Etherscan API 응답 (영수증): {receipt_data}")
            
            if 'error' in receipt_data:
                error_msg = receipt_data['error']
                if isinstance(error_msg, dict):
                    error_message = error_msg.get('message', str(error_msg))
                else:
                    error_message = str(error_msg)
                return {
                    'exists': False,
                    'status': 'error',
                    'error_message': error_message
                }
            
            receipt = receipt_data['result']
            
            # 트랜잭션 영수증이 없는 경우
            if receipt is None:
                return {
                    'exists': False,
                    'status': 'error',
                    'error_message': '트랜잭션 영수증을 찾을 수 없습니다'
                }
            
            # 트랜잭션 성공 여부 확인
            status = receipt.get('status', '0x0')
            is_success = status == '0x1'
            
            # 트랜잭션 정보 안전하게 접근
            tx_result = data['result']
            
            return {
                'exists': True,
                'transaction_hash': transaction_hash,
                'block_number': int(receipt['blockNumber'], 16) if receipt.get('blockNumber') else None,
                'gas_used': int(receipt['gasUsed'], 16) if receipt.get('gasUsed') else None,
                'status': 'success' if is_success else 'failed',
                'is_success': is_success,
                'from_address': tx_result.get('from'),
                'to_address': tx_result.get('to'),
                'value': tx_result.get('value'),
                'etherscan_url': f"https://sepolia.etherscan.io/tx/{transaction_hash}"
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'exists': False,
                'status': 'error',
                'error_message': f'Etherscan API 요청 실패: {str(e)}'
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
