"""
다양한 모델 성능 비교 스크립트

영어 중심 멀티랭귀지 프롬프트 필터링을 위한 최적 모델을 찾습니다.
"""

import torch
import torch.nn.functional as F
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    TrainingArguments, 
    Trainer
)
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import pandas as pd
import numpy as np
import json
from pathlib import Path
import time
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class ModelComparator:
    """모델 성능 비교 클래스"""
    
    def __init__(self, data_dir: str = "datasets"):
        self.data_dir = Path(data_dir)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 테스트할 모델들
        self.models_to_test = [
            "xlm-roberta-base",           # 멀티랭귀지 RoBERTa
            "bert-base-multilingual-cased",  # 멀티랭귀지 BERT
            "distilbert-base-multilingual-cased",  # 경량화 BERT
            "roberta-base",               # 영어 RoBERTa
            "bert-base-uncased"           # 영어 BERT
        ]
        
        # 레이블 매핑
        self.label2id = {
            'APPROPRIATE': 0,
            'JAILBREAK': 1,
            'HARMFUL': 2,
            'ADULT': 3,
            'MEANINGLESS': 4
        }
        self.id2label = {v: k for k, v in self.label2id.items()}
    
    def load_test_data(self) -> Tuple[List[str], List[str]]:
        """테스트 데이터 로드"""
        test_path = self.data_dir / "test.json"
        
        if not test_path.exists():
            raise FileNotFoundError(f"테스트 데이터를 찾을 수 없습니다: {test_path}")
        
        with open(test_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        texts = [item['text'] for item in data]
        labels = [item['label'] for item in data]
        
        return texts, labels
    
    def test_model_performance(self, model_name: str, test_texts: List[str], test_labels: List[str]) -> Dict:
        """단일 모델 성능 테스트"""
        print(f"\n{model_name} 모델 테스트 중...")
        
        try:
            # 모델과 토크나이저 로드
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                num_labels=5,
                problem_type="single_label_classification"
            )
            
            model.to(self.device)
            model.eval()
            
            # 모델 설정
            model.config.id2label = self.id2label
            model.config.label2id = self.label2id
            
            # 예측 수행
            predictions = []
            inference_times = []
            
            with torch.no_grad():
                for text in test_texts:
                    start_time = time.time()
                    
                    # 토크나이징
                    inputs = tokenizer(
                        text,
                        truncation=True,
                        padding=True,
                        max_length=512,
                        return_tensors='pt'
                    )
                    
                    # 디바이스로 이동
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                    
                    # 예측
                    outputs = model(**inputs)
                    predictions_tensor = F.softmax(outputs.logits, dim=-1)
                    predicted_class_id = torch.argmax(predictions_tensor, dim=-1).item()
                    
                    end_time = time.time()
                    inference_times.append(end_time - start_time)
                    
                    predictions.append(predicted_class_id)
            
            # 레이블 인코딩
            true_labels = [self.label2id[label] for label in test_labels]
            
            # 성능 메트릭 계산
            accuracy = accuracy_score(true_labels, predictions)
            precision, recall, f1, _ = precision_recall_fscore_support(
                true_labels, predictions, average='weighted'
            )
            
            # 평균 추론 시간
            avg_inference_time = np.mean(inference_times)
            
            # 모델 크기 (대략적)
            model_size = sum(p.numel() for p in model.parameters()) / 1e6  # MB
            
            return {
                'model_name': model_name,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'avg_inference_time': avg_inference_time,
                'model_size_mb': model_size,
                'success': True
            }
            
        except Exception as e:
            print(f"모델 {model_name} 테스트 실패: {str(e)}")
            return {
                'model_name': model_name,
                'accuracy': 0.0,
                'precision': 0.0,
                'recall': 0.0,
                'f1_score': 0.0,
                'avg_inference_time': 0.0,
                'model_size_mb': 0.0,
                'success': False,
                'error': str(e)
            }
    
    def compare_all_models(self) -> pd.DataFrame:
        """모든 모델 성능 비교"""
        print("모델 성능 비교 시작...")
        
        # 테스트 데이터 로드
        test_texts, test_labels = self.load_test_data()
        print(f"테스트 데이터: {len(test_texts)}개")
        
        # 각 모델 테스트
        results = []
        
        for model_name in self.models_to_test:
            result = self.test_model_performance(model_name, test_texts, test_labels)
            results.append(result)
        
        # 결과를 DataFrame으로 변환
        df = pd.DataFrame(results)
        
        # 성공한 모델만 필터링
        successful_models = df[df['success'] == True].copy()
        
        # 성능 순으로 정렬
        successful_models = successful_models.sort_values('f1_score', ascending=False)
        
        return successful_models
    
    def print_comparison_results(self, results_df: pd.DataFrame):
        """비교 결과 출력"""
        print("\n" + "="*80)
        print("모델 성능 비교 결과")
        print("="*80)
        
        for _, row in results_df.iterrows():
            print(f"\n모델: {row['model_name']}")
            print(f"  정확도: {row['accuracy']:.4f}")
            print(f"  F1 점수: {row['f1_score']:.4f}")
            print(f"  정밀도: {row['precision']:.4f}")
            print(f"  재현율: {row['recall']:.4f}")
            print(f"  평균 추론 시간: {row['avg_inference_time']:.4f}초")
            print(f"  모델 크기: {row['model_size_mb']:.1f}MB")
        
        # 최고 성능 모델 추천
        if not results_df.empty:
            best_model = results_df.iloc[0]
            print(f"\n🏆 최고 성능 모델: {best_model['model_name']}")
            print(f"   F1 점수: {best_model['f1_score']:.4f}")
            print(f"   정확도: {best_model['accuracy']:.4f}")
    
    def save_comparison_results(self, results_df: pd.DataFrame, filename: str = "model_comparison_results.json"):
        """비교 결과 저장"""
        output_path = self.data_dir / filename
        
        # DataFrame을 JSON으로 변환
        results_dict = results_df.to_dict('records')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results_dict, f, ensure_ascii=False, indent=2)
        
        print(f"비교 결과 저장 완료: {output_path}")
        return output_path

def main():
    """메인 실행 함수"""
    comparator = ModelComparator()
    
    # 모델 성능 비교
    results_df = comparator.compare_all_models()
    
    # 결과 출력
    comparator.print_comparison_results(results_df)
    
    # 결과 저장
    comparator.save_comparison_results(results_df)
    
    print("\n모델 비교 완료!")

if __name__ == "__main__":
    main()

