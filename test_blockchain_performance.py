#!/usr/bin/env python3
"""
Blockchain Performance 테스트 스크립트

Consensus 통과 후 Sepolia commit과 verification의 latency 및 cost를 측정합니다.
"""

import sys
import os
import time
import json
import csv
import argparse
from datetime import datetime
from typing import Dict, Any, List

# 백엔드 모듈 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.llm_service import LLMService
from app.services.hash_service import HashService
from app.services.blockchain_service import BlockchainService
from app.utils.cost_estimator import CostEstimator
from config import Config


class BlockchainPerformanceTester:
    """블록체인 성능 테스트 실행기"""
    
    def __init__(self, resume_from=None):
        self.llm_service = LLMService()
        self.hash_service = HashService()
        self.blockchain_service = BlockchainService(
            Config.ETHEREUM_RPC_URL,
            Config.PRIVATE_KEY,
            Config.CONTRACT_ADDRESS
        )
        self.cost_estimator = CostEstimator()
        
        # 테스트용 간단한 프롬프트들
        self.test_prompts = [
            "Hello, how are you?",
            "What is 2+2?",
            "Tell me a short joke.",
            "What color is the sky?",
            "Count from 1 to 3.",
            "Say hello in French.",
            "What is water made of?",
            "Name a fruit.",
            "What day comes after Monday?",
            "Is Earth round?"
        ]
        
        # 기존 결과 로드
        self.results = []
        if resume_from:
            self.load_previous_results(resume_from)
    
    def load_previous_results(self, file_path: str):
        """기존 테스트 결과 로드"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                previous_results = json.load(f)
            self.results = previous_results
            print(f"✅ Loaded {len(previous_results)} previous test results from {file_path}")
        except Exception as e:
            print(f"⚠️  Could not load previous results: {e}")
            self.results = []
    
    def run_single_test(self, test_number: int, total_tests: int) -> Dict[str, Any]:
        """
        단일 테스트 실행
        
        Args:
            test_number: 현재 테스트 번호
            total_tests: 전체 테스트 수
        
        Returns:
            Dict: 테스트 결과
        """
        print(f"\n{'='*80}")
        print(f"📊 Test {test_number}/{total_tests}")
        print(f"{'='*80}")
        
        # 프롬프트 선택 (순환)
        prompt = self.test_prompts[(test_number - 1) % len(self.test_prompts)]
        print(f"📝 Prompt: {prompt}")
        
        result = {
            'test_number': test_number,
            'timestamp': datetime.utcnow().isoformat(),
            'prompt': prompt,
            'success': False
        }
        
        try:
            # 1. LLM 호출
            print("🤖 Calling LLM...")
            llm_start = time.time()
            llm_response = self.llm_service.call_llm(
                provider='openai',
                model='gpt-5-mini',
                prompt=prompt,
                parameters={'temperature': 0.7, 'max_tokens': 50}
            )
            llm_time = time.time() - llm_start
            
            response_content = llm_response['content']
            print(f"✅ LLM Response: {response_content[:50]}...")
            print(f"⏱️  LLM Time: {llm_time:.3f}s")
            
            result['llm_response'] = response_content
            result['llm_time'] = llm_time
            
            # 2. 해시 생성
            print("🔐 Generating hash...")
            timestamp = datetime.utcnow()
            hash_value = self.hash_service.generate_hash(
                llm_provider='openai',
                model_name='gpt-5-mini',
                prompt=prompt,
                response=response_content,
                parameters={'temperature': 0.7, 'max_tokens': 50},
                timestamp=timestamp,
                consensus_votes="5/5"  # Mock consensus
            )
            print(f"✅ Hash: {hash_value[:16]}...")
            result['hash_value'] = hash_value
            
            # 3. Blockchain Commit
            print("⛓️  Committing to Sepolia...")
            commit_result = self.blockchain_service.commit_hash(
                hash_value=hash_value,
                prompt=prompt,
                response=response_content,
                llm_provider='openai',
                model_name='gpt-5-mini',
                timestamp=timestamp,
                parameters={'temperature': 0.7, 'max_tokens': 50},
                consensus_votes="5/5"
            )
            
            if commit_result.get('status') != 'success':
                error_msg = commit_result.get('error_message', 'Unknown error')
                print(f"❌ Commit Failed: {error_msg}")
                result['error'] = error_msg
                
                # 잔액 부족인 경우 특별 플래그 설정
                if 'insufficient funds' in error_msg.lower():
                    result['insufficient_funds'] = True
                    print("⚠️  INSUFFICIENT FUNDS DETECTED - Will stop after this test")
                
                return result
            
            tx_hash = commit_result['transaction_hash']
            print(f"✅ Transaction Hash: {tx_hash}")
            print(f"📦 Block Number: {commit_result['block_number']}")
            print(f"⛽ Gas Used: {commit_result['gas_used']:,}")
            print(f"💰 Gas Price: {commit_result['gas_price_gwei']:.2f} Gwei")
            print(f"💸 Cost: {commit_result['gas_cost_eth']:.6f} ETH")
            
            # Commit timing
            timing = commit_result.get('timing', {})
            print(f"⏱️  Commit Timing:")
            print(f"   - TX Submission: {timing.get('tx_submission_time', 0):.3f}s")
            print(f"   - TX Confirmation: {timing.get('tx_confirmation_time', 0):.3f}s")
            print(f"   - Total Commit: {timing.get('total_commit_time', 0):.3f}s")
            
            result['commit'] = {
                'transaction_hash': tx_hash,
                'block_number': commit_result['block_number'],
                'gas_used': commit_result['gas_used'],
                'gas_price_gwei': float(commit_result['gas_price_gwei']),
                'gas_cost_eth': commit_result['gas_cost_eth'],
                'timing': timing
            }
            
            # 4. Cost Analysis
            print("💰 Analyzing costs...")
            cost_analysis = self.cost_estimator.get_full_cost_analysis(
                gas_used=commit_result['gas_used'],
                gas_price_gwei=float(commit_result['gas_price_gwei'])
            )
            result['cost_analysis'] = cost_analysis
            
            # 간단한 비용 요약 출력
            l1_cost = cost_analysis['l1_mainnet']['total_cost_usd']
            cheapest = cost_analysis['cheapest_l2']
            print(f"   - L1 Mainnet: ${l1_cost:.4f} USD")
            print(f"   - Cheapest L2 ({cheapest['network']}): ${cheapest['estimated_cost_usd']:.4f} USD")
            
            # 5. 잠시 대기 (Etherscan 인덱싱 시간)
            print("⏳ Waiting for Etherscan indexing (3s)...")
            time.sleep(3)
            
            # 6. Verification
            print("🔍 Verifying transaction...")
            verify_result = self.blockchain_service.verify_transaction_hash(tx_hash)
            
            if verify_result.get('exists') and verify_result.get('is_success'):
                print(f"✅ Verification Successful!")
                verify_timing = verify_result.get('timing', {})
                print(f"⏱️  Verification Timing:")
                print(f"   - API Call (TX): {verify_timing.get('api_call_time_tx', 0):.3f}s")
                print(f"   - API Call (Receipt): {verify_timing.get('api_call_time_receipt', 0):.3f}s")
                print(f"   - Hash Verification: {verify_timing.get('hash_verification_time', 0):.3f}s")
                print(f"   - Total Verification: {verify_timing.get('total_verification_time', 0):.3f}s")
                
                result['verification'] = {
                    'exists': True,
                    'is_success': True,
                    'timing': verify_timing
                }
            else:
                print(f"⚠️  Verification Failed or Pending")
                result['verification'] = {
                    'exists': verify_result.get('exists', False),
                    'is_success': verify_result.get('is_success', False),
                    'error': verify_result.get('error_message', 'Unknown')
                }
            
            result['success'] = True
            print(f"✅ Test {test_number} Completed Successfully!")
            
        except Exception as e:
            print(f"❌ Test {test_number} Failed: {str(e)}")
            result['error'] = str(e)
        
        return result
    
    def run_tests(self, num_tests: int, delay_between_tests: float = 2.0):
        """
        여러 테스트 실행
        
        Args:
            num_tests: 테스트 횟수
            delay_between_tests: 테스트 간 대기 시간 (초)
        """
        # 시작 번호 계산 (이미 있는 결과 다음부터)
        start_number = len(self.results) + 1
        
        print("=" * 80)
        print("🚀 BLOCKCHAIN PERFORMANCE TESTING")
        print("=" * 80)
        if start_number > 1:
            print(f"📊 Resuming from test #{start_number}")
            print(f"📊 Previous Tests: {start_number - 1}")
            print(f"📊 New Tests to Run: {num_tests - start_number + 1}")
        print(f"📊 Total Target Tests: {num_tests}")
        print(f"⏱️  Delay Between Tests: {delay_between_tests}s")
        print("=" * 80)
        
        insufficient_funds_detected = False
        
        try:
            for i in range(start_number, num_tests + 1):
                result = self.run_single_test(i, num_tests)
                self.results.append(result)
                
                # 잔액 부족 감지
                if result.get('insufficient_funds'):
                    insufficient_funds_detected = True
                    print("\n" + "=" * 80)
                    print("⚠️  INSUFFICIENT FUNDS - STOPPING TESTS")
                    print("=" * 80)
                    break
                
                # 테스트 간 대기
                if i < num_tests:
                    print(f"\n⏳ Waiting {delay_between_tests}s before next test...")
                    time.sleep(delay_between_tests)
        
        except KeyboardInterrupt:
            print("\n\n" + "=" * 80)
            print("⚠️  TESTING INTERRUPTED BY USER")
            print("=" * 80)
        except Exception as e:
            print(f"\n\n❌ Unexpected error: {str(e)}")
            print("Saving partial results...")
        
        print("\n" + "=" * 80)
        if insufficient_funds_detected:
            print("⛽ TESTS STOPPED DUE TO INSUFFICIENT FUNDS")
        elif len(self.results) >= num_tests:
            print("🏁 ALL TESTS COMPLETED")
        else:
            print(f"⚠️  PARTIAL COMPLETION: {len(self.results)}/{num_tests} tests")
        print("=" * 80)
        self.print_summary()
    
    def print_summary(self):
        """테스트 결과 요약 출력"""
        successful_tests = [r for r in self.results if r.get('success')]
        failed_tests = [r for r in self.results if not r.get('success')]
        
        print(f"\n📊 SUMMARY:")
        print(f"   - Total Tests: {len(self.results)}")
        print(f"   - Successful: {len(successful_tests)}")
        print(f"   - Failed: {len(failed_tests)}")
        
        if successful_tests:
            # Commit latency 통계
            commit_times = [r['commit']['timing']['total_commit_time'] for r in successful_tests]
            avg_commit = sum(commit_times) / len(commit_times)
            min_commit = min(commit_times)
            max_commit = max(commit_times)
            
            print(f"\n⛓️  COMMIT LATENCY:")
            print(f"   - Average: {avg_commit:.3f}s")
            print(f"   - Min: {min_commit:.3f}s")
            print(f"   - Max: {max_commit:.3f}s")
            
            # Verification latency 통계
            verify_times = [
                r['verification']['timing']['total_verification_time'] 
                for r in successful_tests 
                if r.get('verification', {}).get('timing')
            ]
            if verify_times:
                avg_verify = sum(verify_times) / len(verify_times)
                min_verify = min(verify_times)
                max_verify = max(verify_times)
                
                print(f"\n🔍 VERIFICATION LATENCY:")
                print(f"   - Average: {avg_verify:.3f}s")
                print(f"   - Min: {min_verify:.3f}s")
                print(f"   - Max: {max_verify:.3f}s")
            
            # Gas cost 통계
            gas_costs = [r['commit']['gas_cost_eth'] for r in successful_tests]
            avg_gas_cost = sum(gas_costs) / len(gas_costs)
            total_gas_cost = sum(gas_costs)
            
            print(f"\n💰 GAS COSTS:")
            print(f"   - Average per TX: {avg_gas_cost:.6f} ETH")
            print(f"   - Total Cost: {total_gas_cost:.6f} ETH")
    
    def save_results(self, output_dir: str):
        """
        결과를 JSON과 CSV로 저장
        
        Args:
            output_dir: 출력 디렉토리
        """
        # 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'raw_data'), exist_ok=True)
        
        # 타임스탬프
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON 저장
        json_path = os.path.join(output_dir, 'raw_data', f'performance_test_{timestamp}.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 JSON saved: {json_path}")
        
        # CSV 저장
        csv_path = os.path.join(output_dir, 'raw_data', f'performance_test_{timestamp}.csv')
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            if self.results:
                # 성공한 테스트만 CSV로 저장
                successful = [r for r in self.results if r.get('success')]
                if successful:
                    writer = csv.DictWriter(f, fieldnames=[
                        'test_number', 'timestamp', 'prompt', 
                        'commit_time', 'verification_time',
                        'gas_used', 'gas_price_gwei', 'gas_cost_eth',
                        'transaction_hash'
                    ])
                    writer.writeheader()
                    
                    for r in successful:
                        writer.writerow({
                            'test_number': r['test_number'],
                            'timestamp': r['timestamp'],
                            'prompt': r['prompt'],
                            'commit_time': r['commit']['timing']['total_commit_time'],
                            'verification_time': r.get('verification', {}).get('timing', {}).get('total_verification_time', 0),
                            'gas_used': r['commit']['gas_used'],
                            'gas_price_gwei': r['commit']['gas_price_gwei'],
                            'gas_cost_eth': r['commit']['gas_cost_eth'],
                            'transaction_hash': r['commit']['transaction_hash']
                        })
        print(f"💾 CSV saved: {csv_path}")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='Blockchain Performance Testing')
    parser.add_argument('--runs', type=int, default=25, help='Number of tests to run (default: 25)')
    parser.add_argument('--output', type=str, default='analysis/results/blockchain_performance', 
                        help='Output directory (default: analysis/results/blockchain_performance)')
    parser.add_argument('--delay', type=float, default=2.0, 
                        help='Delay between tests in seconds (default: 2.0)')
    parser.add_argument('--resume', type=str, default=None,
                        help='Resume from previous test results (provide JSON file path)')
    
    args = parser.parse_args()
    
    # 설정 확인
    if not Config.CONTRACT_ADDRESS:
        print("❌ Error: Blockchain not configured. Please set CONTRACT_ADDRESS in config.")
        sys.exit(1)
    
    # 테스터 생성 및 실행
    tester = BlockchainPerformanceTester(resume_from=args.resume)
    
    try:
        tester.run_tests(num_tests=args.runs, delay_between_tests=args.delay)
        tester.save_results(output_dir=args.output)
        
        print("\n✅ Testing completed successfully!")
        print(f"📁 Results saved to: {args.output}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user.")
        if tester.results:
            print("Saving partial results...")
            tester.save_results(output_dir=args.output)
    except Exception as e:
        print(f"\n❌ Testing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

