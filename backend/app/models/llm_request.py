from datetime import datetime
from app import db

class LLMRequest(db.Model):
    """LLM 요청 로그 모델"""
    __tablename__ = 'llm_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.String(36), unique=True, nullable=False, index=True)  # UUID
    llm_provider = db.Column(db.String(50), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    parameters = db.Column(db.JSON, nullable=True)
    response = db.Column(db.Text, nullable=True)
    response_time = db.Column(db.Float, nullable=True)  # 응답 시간 (초)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, success, error
    error_message = db.Column(db.Text, nullable=True)
    verification_record_id = db.Column(db.Integer, db.ForeignKey('verification_records.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    verification_record = db.relationship('VerificationRecord', backref=db.backref('llm_requests', lazy=True))
    
    def __repr__(self):
        return f'<LLMRequest {self.request_id}>'
    
    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'request_id': self.request_id,
            'llm_provider': self.llm_provider,
            'model_name': self.model_name,
            'prompt': self.prompt,
            'parameters': self.parameters,
            'response': self.response,
            'response_time': self.response_time,
            'status': self.status,
            'error_message': self.error_message,
            'verification_record_id': self.verification_record_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
