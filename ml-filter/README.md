# ML Prompt Filter Model

> **목적**: 유해, jailbreak, 조작, 성인 프롬프트를 걸러내는 커스텀 ML 필터 모델 개발

## 📁 프로젝트 구조

```
ml-filter/
├── models/           # 훈련된 모델 저장
├── training/         # 훈련 스크립트
├── datasets/         # 데이터셋 (훈련/검증/테스트)
├── inference/        # 추론 서비스
├── notebooks/        # Jupyter 노트북 (Colab 호환)
└── requirements.txt  # ML 관련 의존성
```

## 🎯 목표

1. **데이터셋 수집**: 유해/정상 프롬프트 데이터셋 구축
2. **모델 선택**: HuggingFace에서 적절한 베이스 모델 선택
3. **훈련 환경**: PyTorch + 로컬 GPU 또는 Google Colab
4. **모델 훈련**: 분류 모델 훈련 및 검증
5. **통합**: 기존 PromptFilterService와 연동

## 🛠️ 기술 스택

- **PyTorch**: 딥러닝 프레임워크
- **Transformers**: HuggingFace 라이브러리
- **scikit-learn**: 데이터 전처리 및 평가
- **pandas**: 데이터 처리
- **Google Colab**: 무료 GPU 환경

## 📊 분류 카테고리

- **APPROPRIATE**: 정상적인 프롬프트
- **JAILBREAK**: AI 조작 시도
- **HARMFUL**: 유해한 내용
- **ADULT**: 성인 콘텐츠
- **MEANINGLESS**: 의미없는 입력

## 🚀 개발 단계

1. [x] 프로젝트 구조 생성
2. [ ] 데이터셋 수집 및 전처리
3. [ ] 베이스 모델 선택
4. [ ] 훈련 환경 구성
5. [ ] 모델 훈련
6. [ ] 성능 평가
7. [ ] 기존 시스템 통합

