import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """기본 설정 클래스"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # LLM API 설정
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    
    # 블록체인 설정
    ETHEREUM_RPC_URL = os.environ.get('ETHEREUM_RPC_URL') or 'https://sepolia.infura.io/v3/YOUR_PROJECT_ID'
    PRIVATE_KEY = os.environ.get('PRIVATE_KEY')
    CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS')
    ETHERSCAN_API_KEY = os.environ.get('ETHERSCAN_API_KEY')
    
    # HMAC 보안 해시 설정
    # HMAC secret key - 별도 설정이 없으면 PRIVATE_KEY 사용 (보안 강화)
    # 공격자가 네트워크 중간에서 데이터와 해시를 함께 수정하는 것을 방지
    HMAC_SECRET_KEY = os.environ.get('HMAC_SECRET_KEY') or os.environ.get('PRIVATE_KEY')
    
    # CORS 설정
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')

class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True

class ProductionConfig(Config):
    """프로덕션 환경 설정"""
    DEBUG = False

class TestingConfig(Config):
    """테스트 환경 설정"""
    TESTING = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
