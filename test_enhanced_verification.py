#!/usr/bin/env python3
"""
향상된 Verification API 테스트 (자동 해시 검증 포함)
"""

import requests

# 백엔드 URL
BACKEND_URL = "http://localhost:5000"

def test_verification_with_hash():
    """트랜잭션 해시로 검증 (자동으로 Input Data 가져오기 + 해시 검증)"""
    
    print("🧪 트랜잭션 해시 검증 테스트 (향상된 버전)")
    print("=" * 60)
    
    # 실제 트랜잭션 해시 입력
    transaction_hash = input("트랜잭션 해시를 입력하세요: ").strip()
    
    if not transaction_hash:
        print("트랜잭션 해시가 입력되지 않았습니다.")
        return
    
    print(f"\n🔍 검증 중: {transaction_hash}")
    print()
    
    # API 요청
    response = requests.post(
        f"{BACKEND_URL}/api/verification/verify",
        json={"hash_value": transaction_hash}
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print("=" * 60)
        print("📊 검증 결과")
        print("=" * 60)
        print(f"✅ 최종 검증 결과: {'✅ 성공' if result['verified'] else '❌ 실패'}")
        print(f"💬 메시지: {result['message']}")
        print()
        
        # 기본 정보
        print("📋 트랜잭션 정보:")
        blockchain_info = result.get('blockchain_info', {})
        print(f"  - 존재 여부: {'✅ 존재' if blockchain_info.get('exists') else '❌ 없음'}")
        print(f"  - 상태: {blockchain_info.get('status')}")
        print(f"  - 블록 번호: {blockchain_info.get('block_number')}")
        print(f"  - 가스 사용량: {blockchain_info.get('gas_used')}")
        print()
        
        # 출처 검증
        print("🔐 출처 검증:")
        origin_info = result.get('origin_verification', {})
        print(f"  - From 주소: {origin_info.get('from_address')}")
        print(f"  - 공식 주소: {origin_info.get('our_official_address')}")
        print(f"  - 출처 일치: {'✅ 일치' if origin_info.get('origin_verified') else '❌ 불일치'}")
        print()
        
        # 해시 검증
        print("🔐 해시 무결성 검증:")
        hash_info = result.get('hash_verification', {})
        if hash_info:
            print(f"  - 원본 해시:   {hash_info.get('original_hash', '')[:50]}...")
            print(f"  - 계산된 해시: {hash_info.get('calculated_hash', '')[:50]}...")
            print(f"  - 검증 결과:   {'✅ 일치' if hash_info.get('verified') else '❌ 불일치'}")
            print(f"  - 메시지: {hash_info.get('message')}")
        else:
            print("  - 해시 검증 정보 없음")
        print()
        
        # Input Data
        input_data = result.get('input_data')
        if input_data:
            print("📝 Input Data:")
            print(f"  - Hash: {input_data.get('hash', '')[:50]}...")
            print(f"  - Prompt: {input_data.get('prompt', '')[:50]}...")
            print(f"  - Response: {input_data.get('response', '')[:50]}...")
            print(f"  - Provider: {input_data.get('llm_provider')}")
            print(f"  - Model: {input_data.get('model_name')}")
            print(f"  - Timestamp: {input_data.get('timestamp')}")
            print(f"  - Consensus Votes: {input_data.get('consensus_votes')}")
        else:
            print("📝 Input Data: 없음")
        print()
        
        print(f"🌐 Etherscan 링크: {blockchain_info.get('etherscan_url')}")
        
    else:
        print(f"❌ API 오류: {response.status_code}")
        print(f"  {response.text}")
    
    print()

if __name__ == "__main__":
    print("🚀 향상된 Verification API 테스트")
    print("=" * 60)
    print("이제 트랜잭션 해시만 입력하면:")
    print("  1. 트랜잭션 존재 여부 확인")
    print("  2. 출처(from 주소) 검증")
    print("  3. Input Data 자동 추출")
    print("  4. 해시 역계산 및 무결성 검증")
    print("=" * 60)
    print()
    
    try:
        test_verification_with_hash()
        print("🏁 테스트 완료!")
    except requests.exceptions.ConnectionError:
        print("❌ 백엔드 서버에 연결할 수 없습니다.")
        print("   백엔드가 실행 중인지 확인해주세요: http://localhost:5000")
    except Exception as e:
        print(f"❌ 테스트 오류: {str(e)}")

