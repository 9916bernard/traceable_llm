#!/usr/bin/env python3
"""
LLM Verification System - Flask 애플리케이션 진입점
"""

import os
from app import create_app

# 환경 변수에서 설정 로드
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
