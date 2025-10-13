#!/usr/bin/env python3
"""
LLM Verification System - Flask 애플리케이션 진입점
"""

import os
import argparse
from app import create_app

# 환경 변수에서 설정 로드
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Flask application')
    parser.add_argument('--port', type=int, default=5001, help='Port to run the server on (default: 5001)')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to run the server on (default: 0.0.0.0)')
    args = parser.parse_args()
    
    app.run(debug=True, host=args.host, port=args.port)
