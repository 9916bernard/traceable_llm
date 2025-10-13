"""
Dataset Loader for WildJailbreak
allenai/wildjailbreak 데이터셋 로드 및 샘플링
"""
import random
from typing import Dict, List, Tuple
from datasets import load_dataset
import pandas as pd
from config import DATASET_NAME, SAMPLE_RATIO, TOTAL_SAMPLES


class WildJailbreakLoader:
    """WildJailbreak 데이터셋 로더"""
    
    def __init__(self):
        """데이터셋 초기화"""
        print(f"Loading dataset: {DATASET_NAME}...")
        # Training set 로드 (모든 4개 카테고리 포함: 261K samples)
        dataset = load_dataset(DATASET_NAME, 'train', delimiter="\t", keep_default_na=False)
        self.train_data = dataset['train']
        print(f"Dataset loaded successfully")
        print(f"  - Total samples: {len(self.train_data):,}")
        
        # data_type 분포 확인
        from collections import Counter
        data_types = Counter(self.train_data['data_type'])
        print(f"  - Category distribution:")
        for dtype, count in sorted(data_types.items()):
            print(f"    {dtype}: {count:,}")
        
    def load_and_sample(self, total_samples: int = TOTAL_SAMPLES, 
                       ratio: Dict[str, int] = SAMPLE_RATIO,
                       random_seed: int = 42) -> pd.DataFrame:
        """
        데이터셋에서 지정된 비율로 샘플링
        
        Args:
            total_samples: 총 샘플 수
            ratio: 각 카테고리별 비율 (vanilla_harmful: vanilla_benign: adversarial_harmful: adversarial_benign)
            random_seed: 랜덤 시드
            
        Returns:
            pd.DataFrame: 샘플링된 데이터
        """
        random.seed(random_seed)
        
        # 비율 합계 계산
        total_ratio = sum(ratio.values())
        
        # 각 카테고리별 샘플 수 계산
        samples_per_category = {
            category: int((count / total_ratio) * total_samples)
            for category, count in ratio.items()
        }
        
        print(f"\nSampling strategy:")
        for category, count in samples_per_category.items():
            print(f"  {category}: {count} samples")
        
        # 데이터 분류 및 수집
        vanilla_harmful = []
        vanilla_benign = []
        adversarial_harmful = []
        adversarial_benign = []
        
        print(f"\nProcessing training data...")
        
        # Training set에서 모든 카테고리 분류
        for example in self.train_data:
            data_type = example.get('data_type', '')
            
            if data_type == 'vanilla_harmful':
                prompt = example.get('vanilla', '')
                vanilla_harmful.append({'prompt': prompt, 'is_harmful': True, 'data_type': data_type})
            elif data_type == 'vanilla_benign':
                prompt = example.get('vanilla', '')
                vanilla_benign.append({'prompt': prompt, 'is_harmful': False, 'data_type': data_type})
            elif data_type == 'adversarial_harmful':
                prompt = example.get('adversarial', '')
                adversarial_harmful.append({'prompt': prompt, 'is_harmful': True, 'data_type': data_type})
            elif data_type == 'adversarial_benign':
                prompt = example.get('adversarial', '')
                adversarial_benign.append({'prompt': prompt, 'is_harmful': False, 'data_type': data_type})
        
        print(f"\nAvailable samples by category:")
        print(f"  vanilla_harmful: {len(vanilla_harmful):,}")
        print(f"  vanilla_benign: {len(vanilla_benign):,}")
        print(f"  adversarial_harmful: {len(adversarial_harmful):,}")
        print(f"  adversarial_benign: {len(adversarial_benign):,}")
        
        # 각 카테고리에서 샘플링
        categories = {
            'vanilla_harmful': vanilla_harmful,
            'vanilla_benign': vanilla_benign,
            'adversarial_harmful': adversarial_harmful,
            'adversarial_benign': adversarial_benign
        }
        
        sampled_data = []
        for category, count in samples_per_category.items():
            available = categories[category]
            if len(available) < count:
                print(f"  Warning: {category} has only {len(available)} samples, requested {count}")
                sampled = available
            else:
                sampled = random.sample(available, count)
            
            for example in sampled:
                sampled_data.append({
                    'prompt': example['prompt'],
                    'is_harmful': example['is_harmful'],
                    'category': category
                })
        
        # DataFrame으로 변환
        df = pd.DataFrame(sampled_data)
        
        # 섞기
        df = df.sample(frac=1, random_state=random_seed).reset_index(drop=True)
        
        print(f"\nFinal dataset: {len(df)} samples")
        print(df['category'].value_counts())
        
        return df
    
    def explore_dataset(self, num_examples: int = 5):
        """
        데이터셋 구조 탐색 (디버깅용)
        
        Args:
            num_examples: 출력할 예시 수
        """
        print(f"\n{'='*80}")
        print("Dataset Exploration")
        print(f"{'='*80}")
        
        print(f"\nTraining Dataset")
        print(f"  Size: {len(self.train_data):,}")
        print(f"  Features: {self.train_data.features}")
        
        # 각 data_type별로 예시 출력
        from collections import defaultdict
        examples_by_type = defaultdict(list)
        
        for example in self.train_data:
            data_type = example.get('data_type', '')
            if len(examples_by_type[data_type]) < 2:  # 각 타입별 2개씩
                examples_by_type[data_type].append(example)
        
        print(f"\n  Examples by data_type:")
        for data_type in sorted(examples_by_type.keys()):
            print(f"\n  [{data_type}]")
            for i, example in enumerate(examples_by_type[data_type], 1):
                print(f"    Example {i}:")
                for key, value in example.items():
                    if isinstance(value, str) and len(value) > 80:
                        print(f"      {key}: {value[:80]}...")
                    elif isinstance(value, list):
                        print(f"      {key}: {len(value)} items")
                    else:
                        print(f"      {key}: {value}")


if __name__ == "__main__":
    # 데이터 로더 테스트
    loader = WildJailbreakLoader()
    
    # 데이터셋 구조 탐색
    loader.explore_dataset(num_examples=3)
    
    # 샘플링 테스트
    print(f"\n{'='*80}")
    print("Sampling Test")
    print(f"{'='*80}")
    df = loader.load_and_sample(total_samples=20)  # 테스트용 20개
    print("\nSampled data preview:")
    print(df[['prompt', 'is_harmful', 'category']].head(10))

