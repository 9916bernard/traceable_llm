import os
from typing import Dict, List, Any, Optional
from datasets import load_dataset
from dotenv import load_dotenv

load_dotenv()

class DatasetService:
    """Hugging Face 데이터셋 로드 및 관리 서비스"""
    
    def __init__(self):
        self.hf_token = os.getenv('HUGGINGFACE_TOKEN')
        if not self.hf_token:
            raise ValueError("HUGGINGFACE_TOKEN이 환경 변수에 설정되지 않았습니다.")
    
    def load_wildjailbreak_dataset(self, split: str = 'train') -> Dict[str, Any]:
        """
        allenai/wildjailbreak 데이터셋 로드
        
        Args:
            split: 데이터셋 split ('train', 'test', 'validation' 등)
        
        Returns:
            데이터셋 정보와 샘플 데이터를 포함한 딕셔너리
        """
        try:
            # 데이터셋 로드
            dataset = load_dataset(
                "allenai/wildjailbreak",
                split=split,
                token=self.hf_token
            )
            
            # 데이터셋 정보 추출
            dataset_info = {
                'success': True,
                'dataset_name': 'allenai/wildjailbreak',
                'split': split,
                'num_rows': len(dataset),
                'features': list(dataset.features.keys()) if hasattr(dataset, 'features') else [],
                'dataset': dataset
            }
            
            return dataset_info
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'dataset_name': 'allenai/wildjailbreak',
                'split': split
            }
    
    def get_dataset_samples(self, dataset: Any, num_samples: int = 5) -> List[Dict[str, Any]]:
        """
        데이터셋에서 샘플 데이터 가져오기
        
        Args:
            dataset: 로드된 데이터셋 객체
            num_samples: 가져올 샘플 수
        
        Returns:
            샘플 데이터 리스트
        """
        try:
            samples = []
            for i in range(min(num_samples, len(dataset))):
                samples.append(dict(dataset[i]))
            return samples
        except Exception as e:
            return []
    
    def load_and_get_samples(self, split: str = 'train', num_samples: int = 5) -> Dict[str, Any]:
        """
        데이터셋 로드 및 샘플 데이터 반환
        
        Args:
            split: 데이터셋 split
            num_samples: 샘플 수
        
        Returns:
            데이터셋 정보와 샘플 데이터
        """
        result = self.load_wildjailbreak_dataset(split)
        
        if result['success']:
            samples = self.get_dataset_samples(result['dataset'], num_samples)
            result['samples'] = samples
            # dataset 객체는 직렬화할 수 없으므로 제거
            del result['dataset']
        
        return result
    
    def search_dataset_by_keyword(self, dataset: Any, keyword: str, field: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        데이터셋에서 키워드로 검색
        
        Args:
            dataset: 로드된 데이터셋 객체
            keyword: 검색할 키워드
            field: 검색할 필드 (None이면 모든 텍스트 필드 검색)
            limit: 반환할 최대 결과 수
        
        Returns:
            검색 결과 리스트
        """
        try:
            results = []
            keyword_lower = keyword.lower()
            
            for i, item in enumerate(dataset):
                if len(results) >= limit:
                    break
                
                item_dict = dict(item)
                
                # 특정 필드 검색
                if field and field in item_dict:
                    if keyword_lower in str(item_dict[field]).lower():
                        results.append(item_dict)
                # 모든 필드 검색
                elif not field:
                    for value in item_dict.values():
                        if isinstance(value, str) and keyword_lower in value.lower():
                            results.append(item_dict)
                            break
            
            return results
            
        except Exception as e:
            return []


