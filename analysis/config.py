"""
Analysis Configuration
논문 게재용 Consensus Layer 분석 설정
"""
import os
from typing import Dict, List

# API 설정
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# LLM 모델 설정
FREE_MODELS = {
    'openai': 'openai/gpt-5-mini',
    'grok': 'meta-llama/llama-3.3-70b-instruct:free',
    'claude': 'anthropic/claude-3.7-sonnet',
    'gemini': 'google/gemini-2.5-flash-lite',
    'deepseek': 'deepseek/deepseek-chat-v3.1:free'
}

# 최저가 유료 모델 설정 (비용 최적화) - Consensus와 align
PREMIUM_MODELS = {
    'openai': 'openai/gpt-3.5-turbo',  # $0.50/1M tokens (가장 저렴)
    'claude': 'anthropic/claude-3-haiku',  # $0.25/1M tokens (가장 저렴)
    'gemini': 'google/gemini-2.5-flash-lite',  # $0.075/1M tokens (가장 저렴)
    'llama': 'meta-llama/llama-3.1-8b-instruct',  # $0.20/1M tokens (저렴)
    'deepseek': 'deepseek/deepseek-chat'  # $0.14/1M tokens (저렴)
}

# Consensus에서 실제 사용하는 모델 (백엔드와 동일)
CONSENSUS_MODELS = PREMIUM_MODELS

# 데이터셋 설정
DATASET_NAME = "allenai/wildjailbreak"
SAMPLE_RATIO = {
    'vanilla_harmful': 1,
    'vanilla_benign': 1,
    'adversarial_harmful': 4,
    'adversarial_benign': 4
}
TOTAL_SAMPLES = 2500

# Consensus 설정
CONSENSUS_THRESHOLD = 3  # 5개 중 3개 이상 동의
TIMEOUT = 60  # 초

# 결과 저장 경로
RESULTS_DIR = "results"
RAW_DATA_DIR = f"{RESULTS_DIR}/raw_data"
VISUALIZATIONS_DIR = f"{RESULTS_DIR}/visualizations"
REPORTS_DIR = f"{RESULTS_DIR}/reports"

# 평가 지표
METRICS = ['accuracy', 'precision', 'recall', 'f1_score', 'false_positive_rate', 'false_negative_rate']

# OpenRouter API 설정
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_HEADERS = {
    "HTTP-Referer": "https://llm-verification-system.com",
    "X-Title": "LLM Verification Analysis"
}

