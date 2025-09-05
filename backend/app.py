#!/usr/bin/env python3
"""
LLM Verification System - Flask 애플리케이션 진입점
"""

import os
from app import create_app, db
from app.models import VerificationRecord, LLMRequest

# 환경 변수에서 설정 로드
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

@app.shell_context_processor
def make_shell_context():
    """Flask shell 컨텍스트"""
    return {
        'db': db,
        'VerificationRecord': VerificationRecord,
        'LLMRequest': LLMRequest
    }

@app.cli.command()
def init_db():
    """데이터베이스 초기화"""
    db.create_all()
    print("데이터베이스가 초기화되었습니다.")

@app.cli.command()
def reset_db():
    """데이터베이스 리셋"""
    db.drop_all()
    db.create_all()
    print("데이터베이스가 리셋되었습니다.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
