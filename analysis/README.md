# LLM Consensus Layer Analysis

논문 게재를 위한 Consensus Layer (5개 LLM 모델) vs 단일 모델 성능 비교 분석 도구

## 📋 개요

이 분석 도구는 다음을 수행합니다:
- **5개의 다른 LLM 모델**을 사용한 Consensus 방식의 정확도 측정
- **개별 모델**의 성능과 비교
- **WildJailbreak 데이터셋** 사용 (1:1:4:4 비율)
  - Vanilla Harmful : Vanilla Benign : Adversarial Harmful : Adversarial Benign
- 논문 게재를 위한 **시각화 및 통계 분석**

## 🏗️ 프로젝트 구조

```
analysis/
├── config.py                  # 설정 파일 (모델, 데이터셋, 경로)
├── data_loader.py            # WildJailbreak 데이터셋 로더
├── experiment_runner.py      # 실험 실행기 (5개 모델 테스트)
├── result_analyzer.py        # 결과 분석 및 시각화
├── run_full_experiment.py    # 전체 실험 자동화 스크립트
├── requirements.txt          # Python 패키지 요구사항
├── README.md                 # 이 파일
└── results/                  # 결과 저장 디렉토리
    ├── raw_data/            # 원본 실험 데이터 (JSON)
    ├── visualizations/      # 시각화 이미지 (PNG, HTML)
    └── reports/             # 분석 보고서 (CSV, TXT)
```

## 🚀 설치 및 설정

### 1. 패키지 설치

```bash
cd analysis
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일에 다음 API 키가 설정되어 있어야 합니다:
```bash
OPENROUTER_API_KEY=your_openrouter_api_key
OPENAI_API_KEY=your_openai_api_key
```

## 📊 사용 방법

### 방법 1: 전체 실험 자동 실행 (추천)

```bash
# 기본 설정 (200개 샘플, free models)
python run_full_experiment.py

# 샘플 수 지정
python run_full_experiment.py --samples 200

# Premium 모델 사용
python run_full_experiment.py --model-set premium

# 커스텀 실험 이름
python run_full_experiment.py --name "my_experiment_v1"
```

### 방법 2: 단계별 실행

#### Step 1: 데이터 로드 테스트
```bash
python data_loader.py
```

#### Step 2: 실험 실행
```python
from data_loader import WildJailbreakLoader
from experiment_runner import ExperimentRunner

# 데이터 로드
loader = WildJailbreakLoader()
df = loader.load_and_sample(total_samples=200)

# 실험 실행
runner = ExperimentRunner()
results = runner.run_experiment(df, experiment_name="free_models_200")
```

#### Step 3: 결과 분석
```bash
python result_analyzer.py results/raw_data/free_models_200.json
```

## 📈 생성되는 결과물

### 1. 시각화 (Visualizations)
- **accuracy_comparison.png**: 모델별 정확도 막대 그래프
- **metrics_radar.html**: 다중 메트릭 레이더 차트 (Accuracy, Precision, Recall, F1)
- **confusion_matrices.png**: 각 모델별 Confusion Matrix
- **category_performance.png**: 카테고리별 성능 비교

### 2. 보고서 (Reports)
- **comparison_table.csv**: 모델 성능 비교 표 (논문 Table용)
- **report.txt**: 전체 실험 결과 텍스트 보고서

### 3. 원본 데이터 (Raw Data)
- **experiment_name.json**: 모든 프롬프트에 대한 상세 결과
  - 각 모델의 개별 판단
  - Consensus 결과
  - 응답 시간
  - 오류 정보

## 🔬 실험 설정

### 현재 사용 중인 Free Models
```python
FREE_MODELS = {
    'openai': 'openai/gpt-5-mini',
    'grok': 'meta-llama/llama-3.3-70b-instruct:free',
    'claude': 'anthropic/claude-3.7-sonnet',
    'gemini': 'google/gemini-2.5-flash-lite',
    'deepseek': 'deepseek/deepseek-chat-v3.1:free'
}
```

### Consensus 규칙
- **5개 모델** 중 **3개 이상**이 동의하면 해당 판단 채택
- 각 모델은 프롬프트를 "harmful" 또는 "safe"로 분류
- 병렬 처리로 속도 최적화

### 데이터셋 샘플링
- **총 200개 샘플** (기본값)
- **비율**: Vanilla Harmful (20) : Vanilla Benign (20) : Adversarial Harmful (80) : Adversarial Benign (80)

## 📊 평가 지표

각 모델 및 Consensus에 대해 다음 지표를 계산합니다:
- **Accuracy**: 전체 정확도
- **Precision**: 정밀도 (False Positive 최소화)
- **Recall**: 재현율 (False Negative 최소화)
- **F1 Score**: Precision과 Recall의 조화 평균
- **Confusion Matrix**: TP, TN, FP, FN
- **Response Time**: 평균 응답 시간

## 🎯 주요 비교 지표

1. **Consensus vs 개별 모델 정확도**
2. **Consensus vs 최고 성능 개별 모델**
3. **카테고리별 성능 (Vanilla vs Adversarial)**
4. **모델별 강점/약점 분석**

## 🔧 설정 커스터마이징

`config.py`에서 다음을 수정할 수 있습니다:
- `TOTAL_SAMPLES`: 총 샘플 수
- `SAMPLE_RATIO`: 카테고리별 비율
- `CONSENSUS_THRESHOLD`: Consensus 임계값 (기본 3/5)
- `TIMEOUT`: API 호출 타임아웃
- `FREE_MODELS` / `PREMIUM_MODELS`: 테스트할 모델

## 📝 실험 확장

향후 실험을 위한 확장 가능한 구조:
- ✅ 다른 모델 세트 추가 (Premium models)
- ✅ 샘플 수 변경
- ✅ 다른 데이터셋 사용
- ✅ Consensus 임계값 변경 (3/5, 4/5 등)
- ✅ 추가 평가 지표

## 🐛 문제 해결

### API 오류
- OpenRouter API 키 확인
- Rate limit 초과 시 샘플 수 줄이기
- 타임아웃 설정 증가 (`config.py`의 `TIMEOUT`)

### 데이터셋 로드 오류
```bash
# datasets 캐시 클리어
rm -rf ~/.cache/huggingface/datasets
```

### 메모리 부족
- 샘플 수 줄이기
- 중간 저장 활용 (10개마다 자동 저장)

## 📚 참고 자료

- **WildJailbreak Dataset**: https://huggingface.co/datasets/allenai/wildjailbreak
- **OpenRouter API**: https://openrouter.ai/docs
- **Scikit-learn Metrics**: https://scikit-learn.org/stable/modules/model_evaluation.html

## 📧 문의

실험 관련 문의나 버그 리포트는 이슈로 등록해주세요.

---

**Note**: 이 분석 도구는 기존 LLM Verification 프로젝트와 완전히 독립적으로 실행됩니다.






