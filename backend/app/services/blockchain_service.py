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
    def commit_hash(self, hash_value: str, prompt: str, response: str, llm_provider: str, model_name: str, timestamp, parameters: dict, consensus_votes: str = "", wait_for_confirmation: bool = True) -> Dict[str, Any]:
        """
        LLM 기록을 블록체인에 커밋
        
        Args:
            hash_value: 커밋할 해시값
            prompt: 원본 프롬프트
            response: LLM 응답
            llm_provider: LLM 제공자
            model_name: 모델명
            timestamp: 해시 생성 시 사용된 정확한 timestamp (datetime 객체)
            parameters: LLM 파라미터 (dict)
            consensus_votes: Consensus 투표 결과 (예: "3/5")
            wait_for_confirmation: True면 블록 confirmation까지 대기, False면 TX submission만 (default: True)
        
        Returns:
            Dict: 트랜잭션 정보 (latency 정보 포함)
        """
        import time
        
        # 전체 커밋 시작 시간
        total_start_time = time.time()
        
        try:
            # 해시 생성 시 사용된 정확한 timestamp를 ISO format string으로 변환
            # 해시 계산에 사용된 것과 동일한 형식
            timestamp_string = timestamp.isoformat()
            
            # parameters를 JSON string으로 변환 (해시 생성과 동일한 방식)
            import json
            parameters_string = json.dumps(parameters, sort_keys=True, ensure_ascii=False)
            
            # 🔍 로그: 블록체인 커밋 데이터 출력
            print("=" * 80)
            print("🔗 BLOCKCHAIN COMMIT DEBUG LOG")
            print("=" * 80)
            print("📤 스마트 컨트랙트에 전달되는 데이터:")
            print(f"  hash_value: {hash_value}")
            print(f"  prompt: {prompt[:50]}..." if len(prompt) > 50 else f"  prompt: {prompt}")
            print(f"  response: {response[:50]}..." if len(response) > 50 else f"  response: {response}")
            print(f"  llm_provider: {llm_provider}")
            print(f"  model_name: {model_name}")
            print(f"  timestamp: {timestamp_string}")
            print(f"  parameters: {parameters_string}")
            print(f"  consensus_votes: {consensus_votes}")
            print("=" * 80)
            print()
            
            # 가스 추정 - 우리 LLMRecord 컨트렉트 함수의 저장 사이즈에 기반해서 web3 의 가스 추정 함수를 사용해서 추정하는듯 - Limit 을 추정하기 위함임
            try:
                estimated_gas = self.contract.functions.storeLLMRecord(
                    hash_value, prompt, response, llm_provider, model_name, timestamp_string, parameters_string, consensus_votes
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
                hash_value, safe_prompt, safe_response, safe_llm_provider, safe_model_name, timestamp_string, parameters_string, consensus_votes
            ).build_transaction({
                'from': self.account.address,
                'gas': gas_limit,
                'gasPrice': gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
            })
            
            # 트랜잭션 서명
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            
            # 트랜잭션 전송 시작 시간
            tx_submission_start = time.time()
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_submission_time = time.time() - tx_submission_start
            
            # wait_for_confirmation이 False면 여기서 바로 리턴 (pending 상태)
            if not wait_for_confirmation:
                total_commit_time = time.time() - total_start_time
                
                # Gas 비용 추정 (실제 사용량은 confirmation 후에 알 수 있음)
                estimated_gas_cost_wei = gas_limit * gas_price
                estimated_gas_cost_eth = self.w3.from_wei(estimated_gas_cost_wei, 'ether')
                
                return {
                    'transaction_hash': tx_hash.hex(),
                    'status': 'pending',
                    'gas_limit': gas_limit,
                    'gas_price': gas_price,
                    'gas_price_gwei': self.w3.from_wei(gas_price, 'gwei'),
                    'estimated_gas_cost_wei': estimated_gas_cost_wei,
                    'estimated_gas_cost_eth': float(estimated_gas_cost_eth),
                    'timing': {
                        'tx_submission_time': tx_submission_time,
                        'total_commit_time': total_commit_time
                    },
                    'message': 'Transaction submitted successfully. Waiting for confirmation...'
                }
            
            # wait_for_confirmation이 True면 confirmation까지 대기
            tx_confirmation_start = time.time()
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            tx_confirmation_time = time.time() - tx_confirmation_start
            
            # DB 업데이트 로직 제거됨 - Etherscan 전용 시스템
            
            # 총 커밋 시간 계산
            total_commit_time = time.time() - total_start_time
            
            # Gas 비용 계산 (ETH 단위)
            gas_cost_wei = tx_receipt.gasUsed * gas_price
            gas_cost_eth = self.w3.from_wei(gas_cost_wei, 'ether')
            
            return {
                'transaction_hash': tx_hash.hex(),
                'block_number': tx_receipt.blockNumber,
                'gas_used': tx_receipt.gasUsed,
                'gas_price': gas_price,
                'gas_price_gwei': self.w3.from_wei(gas_price, 'gwei'),
                'gas_cost_wei': gas_cost_wei,
                'gas_cost_eth': float(gas_cost_eth),
                'status': 'success',
                'timing': {
                    'tx_submission_time': tx_submission_time,
                    'tx_confirmation_time': tx_confirmation_time,
                    'total_commit_time': total_commit_time
                }
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
        Web3를 통해 트랜잭션 해시 검증 (Etherscan API 대신 직접 RPC 사용)
        
        Args:
            transaction_hash: 검증할 트랜잭션 해시
        
        Returns:
            Dict: 검증 결과 (latency 정보 포함)
        """
        import time
        
        # 전체 검증 시작 시간
        total_verification_start = time.time()
        
        try:
            # Web3를 사용하여 트랜잭션 정보 조회
            rpc_call_start = time.time()
            tx = self.w3.eth.get_transaction(transaction_hash)
            rpc_call_time_tx = time.time() - rpc_call_start
            
            # 디버깅을 위한 로그
            print(f"Web3 트랜잭션 조회 성공: {transaction_hash}")
            
            if tx is None:
                return {
                    'exists': False,
                    'status': 'error',
                    'error_message': '트랜잭션을 찾을 수 없습니다'
                }
            
            # 트랜잭션 영수증 조회
            rpc_call_receipt_start = time.time()
            receipt = self.w3.eth.get_transaction_receipt(transaction_hash)
            rpc_call_time_receipt = time.time() - rpc_call_receipt_start
            
            # 디버깅을 위한 로그
            print(f"Web3 영수증 조회 성공")
            
            # 트랜잭션 영수증이 없는 경우 (pending 상태)
            if receipt is None:
                return {
                    'exists': True,
                    'status': 'pending',
                    'error_message': '트랜잭션이 아직 처리되지 않았습니다 (pending 상태)',
                    'transaction_hash': transaction_hash,
                    'from_address': tx.get('from'),
                    'to_address': tx.get('to'),
                    'value': tx.get('value'),
                    'etherscan_url': f"https://sepolia.etherscan.io/tx/{transaction_hash}"
                }
            
            # 트랜잭션 성공 여부 확인
            is_success = receipt.status == 1
            
            # Input Data 추출 및 디코딩
            input_data_hex = tx.get('input', '0x')
            decoded_input_data = None
            hash_verification = None
            hash_verification_time = 0
            
            try:
                if input_data_hex and input_data_hex != '0x':
                    # Web3를 사용하여 Input Data 디코딩
                    decoded_input_data = self._decode_input_data(input_data_hex)
                    
                    # 해시 역계산 검증
                    if decoded_input_data:
                        hash_verification_start = time.time()
                        hash_verification = self._verify_hash_from_input_data(decoded_input_data)
                        hash_verification_time = time.time() - hash_verification_start
            except Exception as e:
                print(f"Input Data 디코딩/검증 오류: {str(e)}")
            
            # 총 검증 시간 계산
            total_verification_time = time.time() - total_verification_start
            
            return {
                'exists': True,
                'transaction_hash': transaction_hash,
                'block_number': receipt.blockNumber,
                'gas_used': receipt.gasUsed,
                'status': 'success' if is_success else 'failed',
                'is_success': is_success,
                'from_address': tx.get('from'),
                'to_address': tx.get('to'),
                'value': tx.get('value'),
                'etherscan_url': f"https://sepolia.etherscan.io/tx/{transaction_hash}",
                'input_data': decoded_input_data,
                'hash_verification': hash_verification,
                'timing': {
                    'rpc_call_time_tx': rpc_call_time_tx,
                    'rpc_call_time_receipt': rpc_call_time_receipt,
                    'hash_verification_time': hash_verification_time,
                    'total_verification_time': total_verification_time
                }
            }
            
        except Exception as e:
            # 트랜잭션을 찾을 수 없는 경우
            error_msg = str(e)
            if "not found" in error_msg.lower() or "unknown" in error_msg.lower():
                return {
                    'exists': False,
                    'status': 'error',
                    'error_message': '트랜잭션을 찾을 수 없습니다'
                }
            return {
                'exists': False,
                'status': 'error',
                'error_message': f'트랜잭션 조회 실패: {error_msg}'
            }
    
    def _decode_input_data(self, input_data_hex: str) -> Dict[str, Any]:
        """
        트랜잭션 Input Data 디코딩
        
        Args:
            input_data_hex: 16진수 형식의 Input Data
        
        Returns:
            Dict: 디코딩된 데이터
        """
        try:
            # Function signature (첫 4바이트)는 제외
            if len(input_data_hex) <= 10:  # '0x' + 8자리 (4바이트)
                return None
            
            # ABI를 사용하여 디코딩
            decoded = self.contract.decode_function_input(input_data_hex)
            function_obj, params = decoded
            
            return {
                'hash': params.get('hash', ''),
                'prompt': params.get('prompt', ''),
                'response': params.get('response', ''),
                'llm_provider': params.get('llm_provider', ''),
                'model_name': params.get('model_name', ''),
                'timestamp': params.get('timestamp', ''),
                'parameters': params.get('parameters', ''),
                'consensus_votes': params.get('consensus_votes', '')
            }
        except Exception as e:
            print(f"Input Data 디코딩 오류: {str(e)}")
            return None
    
    def _verify_hash_from_input_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input Data로부터 HMAC 해시 역계산 및 검증
        
        보안 강화:
        - HMAC-SHA256 방식 사용
        - Secret key 없이는 올바른 해시를 생성할 수 없음
        - 네트워크 중간 공격(MITM)으로 데이터와 해시를 함께 수정하는 것 방지
        
        Args:
            input_data: 디코딩된 Input Data
        
        Returns:
            Dict: 검증 결과
        """
        try:
            import hashlib
            import hmac
            import json
            
            # 해시 재계산을 위한 데이터 구성 (HashService 방식)
            # parameters는 JSON 문자열로 저장되어 있으므로 파싱
            parameters_dict = {}
            if input_data.get('parameters'):
                try:
                    parameters_dict = json.loads(input_data['parameters'])
                except:
                    parameters_dict = {}
            
            hash_data = {
                'llm_provider': input_data['llm_provider'],
                'model_name': input_data['model_name'],
                'prompt': input_data['prompt'],
                'response': input_data['response'],
                'parameters': parameters_dict,
                'timestamp': input_data['timestamp']
            }
            
            # consensus_votes 추가 (있는 경우)
            if input_data.get('consensus_votes'):
                hash_data['consensus_votes'] = input_data['consensus_votes']
            
            # JSON 문자열로 변환 (HashService와 동일한 방식)
            json_string = json.dumps(hash_data, sort_keys=True, ensure_ascii=False)
            
            # HMAC secret key 가져오기
            secret_key = Config.HMAC_SECRET_KEY
            if not secret_key:
                raise ValueError("HMAC_SECRET_KEY가 설정되지 않았습니다. 환경변수를 확인해주세요.")
            
            # 🔐 HMAC-SHA256 해시 계산 (보안 강화)
            calculated_hash = hmac.new(
                key=secret_key.encode('utf-8'),
                msg=json_string.encode('utf-8'),
                digestmod=hashlib.sha256
            ).hexdigest()
            
            # 원본 해시와 비교
            original_hash = input_data['hash']
            hash_matches = calculated_hash == original_hash
            
            # 로그 출력
            print("=" * 80)
            print("🔍 HMAC HASH VERIFICATION FROM BLOCKCHAIN INPUT DATA")
            print("=" * 80)
            print(f"원본 HMAC 해시:   {original_hash}")
            print(f"계산된 HMAC 해시: {calculated_hash}")
            print(f"일치 여부:        {'✅ 일치' if hash_matches else '❌ 불일치'}")
            print(f"🔑 보안:          Secret key로 검증됨 (네트워크 중간 공격 방지)")
            print("=" * 80)
            
            return {
                'verified': hash_matches,
                'original_hash': original_hash,
                'calculated_hash': calculated_hash,
                'message': 'HMAC 해시가 일치합니다. 데이터 무결성과 인증이 확인되었습니다.' if hash_matches else 'HMAC 해시가 일치하지 않습니다. 데이터가 변조되었거나 인증되지 않은 출처입니다.'
            }
        except Exception as e:
            print(f"HMAC 해시 검증 오류: {str(e)}")
            return {
                'verified': False,
                'error': str(e)
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
