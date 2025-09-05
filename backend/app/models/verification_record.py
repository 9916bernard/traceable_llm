from datetime import datetime
from app import db

class VerificationRecord(db.Model):
    """LLM 검증 기록 모델"""
    __tablename__ = 'verification_records'
    
    id = db.Column(db.Integer, primary_key=True)
    hash_value = db.Column(db.String(64), unique=True, nullable=False, index=True)
    llm_provider = db.Column(db.String(50), nullable=False)  # 'openai', 'anthropic', etc.
    model_name = db.Column(db.String(100), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    parameters = db.Column(db.JSON, nullable=True)  # temperature, max_tokens, etc.
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    transaction_hash = db.Column(db.String(66), nullable=True)  # 블록체인 트랜잭션 해시
    block_number = db.Column(db.Integer, nullable=True)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<VerificationRecord {self.hash_value}>'
    
    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'hash_value': self.hash_value,
            'llm_provider': self.llm_provider,
            'model_name': self.model_name,
            'prompt': self.prompt,
            'response': self.response,
            'parameters': self.parameters,
            'timestamp': self.timestamp.isoformat(),
            'transaction_hash': self.transaction_hash,
            'block_number': self.block_number,
            'verified': self.verified,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
