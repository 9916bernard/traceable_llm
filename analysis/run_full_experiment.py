"""
Full Experiment Runner
전체 실험 실행 및 분석 자동화
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv('../backend/.env')

from data_loader import WildJailbreakLoader
from experiment_runner import ExperimentRunner
from result_analyzer import ResultAnalyzer
from config import FREE_MODELS, PREMIUM_MODELS, TOTAL_SAMPLES, RAW_DATA_DIR


def run_full_experiment(
    total_samples: int = TOTAL_SAMPLES,
    models: dict = FREE_MODELS,
    experiment_name: str = None
):
    """
    전체 실험 실행 (데이터 로드 → 실험 → 분석)
    
    Args:
        total_samples: 총 샘플 수
        models: 사용할 모델 딕셔너리
        experiment_name: 실험 이름
    """
    if experiment_name is None:
        experiment_name = f"free_models_{total_samples}_samples_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print("\n" + "="*80)
    print("LLM CONSENSUS LAYER ANALYSIS - FULL EXPERIMENT")
    print("="*80)
    print(f"Experiment Name: {experiment_name}")
    print(f"Total Samples: {total_samples}")
    print(f"Models: {list(models.keys())}")
    print("="*80 + "\n")
    
    # Step 1: 데이터 로드
    print("\n[STEP 1/3] Loading and sampling dataset...")
    print("-" * 80)
    loader = WildJailbreakLoader()
    df = loader.load_and_sample(total_samples=total_samples)
    
    print(f"\nDataset loaded successfully!")
    print(f"  Total samples: {len(df)}")
    print(f"  Category distribution:")
    print(df['category'].value_counts().to_string())
    print(f"  Harmful/Benign distribution:")
    print(df['is_harmful'].value_counts().to_string())
    
    # Step 2: 실험 실행
    print("\n[STEP 2/3] Running experiment...")
    print("-" * 80)
    runner = ExperimentRunner(models=models)
    experiment_data = runner.run_experiment(df, experiment_name=experiment_name)
    
    # Step 3: 결과 분석
    print("\n[STEP 3/3] Analyzing results...")
    print("-" * 80)
    result_file = os.path.join(RAW_DATA_DIR, f"{experiment_name}.json")
    analyzer = ResultAnalyzer(result_file)
    analyzer.generate_full_report()
    
    print("\n" + "="*80)
    print("EXPERIMENT COMPLETED SUCCESSFULLY!")
    print("="*80)
    print(f"\nResults Location:")
    print(f"  Raw Data: {RAW_DATA_DIR}/{experiment_name}.json")
    print(f"  Visualizations: analysis/results/visualizations/")
    print(f"  Reports: analysis/results/reports/")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run LLM Consensus Analysis Experiment')
    parser.add_argument('--samples', type=int, default=TOTAL_SAMPLES,
                       help=f'Total number of samples (default: {TOTAL_SAMPLES})')
    parser.add_argument('--model-set', type=str, default='free',
                       choices=['free', 'premium'],
                       help='Model set to use: free or premium (default: free)')
    parser.add_argument('--name', type=str, default=None,
                       help='Custom experiment name')
    
    args = parser.parse_args()
    
    # 모델 선택
    if args.model_set == 'free':
        models = FREE_MODELS
        print("Using FREE models for cost optimization")
    else:
        models = PREMIUM_MODELS
        print("Using PREMIUM models for best performance")
    
    # 실험 실행
    run_full_experiment(
        total_samples=args.samples,
        models=models,
        experiment_name=args.name
    )






