"""
Result Analyzer and Visualizer
실험 결과 분석 및 시각화 (논문 게재용)
"""
import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
from typing import Dict, List, Any
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import RAW_DATA_DIR, VISUALIZATIONS_DIR, REPORTS_DIR


class ResultAnalyzer:
    """실험 결과 분석 및 시각화"""
    
    def __init__(self, experiment_file: str):
        """
        Args:
            experiment_file: 실험 결과 JSON 파일 경로
        """
        # 결과 저장 디렉토리 생성
        os.makedirs(VISUALIZATIONS_DIR, exist_ok=True)
        os.makedirs(REPORTS_DIR, exist_ok=True)
        
        # 실험 결과 로드
        with open(experiment_file, 'r', encoding='utf-8') as f:
            self.experiment_data = json.load(f)
        
        self.experiment_name = self.experiment_data['experiment_name']
        self.results = self.experiment_data['results']
        self.models = list(self.experiment_data['models'].keys())
        
        # 결과 DataFrame 생성
        self.df = self._create_results_dataframe()
        
        print(f"Loaded experiment: {self.experiment_name}")
        print(f"Total samples: {len(self.results)}")
        print(f"Models: {self.models}")
    
    def _create_results_dataframe(self) -> pd.DataFrame:
        """결과를 DataFrame으로 변환"""
        data = []
        
        for result in self.results:
            row = {
                'prompt': result['prompt'],
                'ground_truth': result['ground_truth'],
                'category': result['category'],
                'consensus_prediction': result['consensus_prediction'],
                'consensus_correct': result['consensus_correct'],
                'harmful_votes': result['harmful_votes'],
                'safe_votes': result['safe_votes']
            }
            
            # 개별 모델 결과 추가
            for model in self.models:
                model_result = result['model_results'][model]
                row[f'{model}_prediction'] = model_result['is_harmful']
                row[f'{model}_correct'] = result['individual_accuracy'][model]
                row[f'{model}_response_time'] = model_result['response_time']
            
            data.append(row)
        
        return pd.DataFrame(data)
    
    def calculate_metrics(self) -> Dict[str, Dict[str, float]]:
        """모든 모델 및 consensus에 대한 평가 지표 계산"""
        metrics = {}
        
        # Consensus 메트릭
        y_true = self.df['ground_truth'].astype(int)
        y_pred = self.df['consensus_prediction'].astype(int)
        
        metrics['consensus'] = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1_score': f1_score(y_true, y_pred, zero_division=0),
            'confusion_matrix': confusion_matrix(y_true, y_pred).tolist()
        }
        
        # 개별 모델 메트릭
        for model in self.models:
            y_pred_model = self.df[f'{model}_prediction'].astype(int)
            
            metrics[model] = {
                'accuracy': accuracy_score(y_true, y_pred_model),
                'precision': precision_score(y_true, y_pred_model, zero_division=0),
                'recall': recall_score(y_true, y_pred_model, zero_division=0),
                'f1_score': f1_score(y_true, y_pred_model, zero_division=0),
                'confusion_matrix': confusion_matrix(y_true, y_pred_model).tolist(),
                'avg_response_time': self.df[f'{model}_response_time'].mean()
            }
        
        return metrics
    
    def generate_comparison_table(self, metrics: Dict[str, Dict[str, float]]) -> pd.DataFrame:
        """비교 표 생성"""
        comparison_data = []
        
        for model_name, model_metrics in metrics.items():
            comparison_data.append({
                'Model': 'Consensus (5 models)' if model_name == 'consensus' else model_name.upper(),
                'Accuracy': f"{model_metrics['accuracy']:.4f}",
                'Precision': f"{model_metrics['precision']:.4f}",
                'Recall': f"{model_metrics['recall']:.4f}",
                'F1 Score': f"{model_metrics['f1_score']:.4f}",
                'Avg Response Time (s)': f"{model_metrics.get('avg_response_time', 'N/A'):.2f}" if isinstance(model_metrics.get('avg_response_time'), float) else 'N/A'
            })
        
        df_comparison = pd.DataFrame(comparison_data)
        
        # CSV로 저장
        output_path = os.path.join(REPORTS_DIR, f"{self.experiment_name}_comparison_table.csv")
        df_comparison.to_csv(output_path, index=False)
        print(f"Comparison table saved to: {output_path}")
        
        return df_comparison
    
    def plot_accuracy_comparison(self, metrics: Dict[str, Dict[str, float]]):
        """정확도 비교 막대 그래프"""
        models_list = ['consensus'] + self.models
        accuracies = [metrics[model]['accuracy'] for model in models_list]
        
        # 모델 이름 포맷팅
        model_labels = ['Consensus\n(5 models)'] + [m.upper() for m in self.models]
        
        plt.figure(figsize=(12, 6))
        colors = ['#2ecc71' if model == 'consensus' else '#3498db' for model in models_list]
        bars = plt.bar(model_labels, accuracies, color=colors, alpha=0.8, edgecolor='black')
        
        # 값 표시
        for bar, acc in zip(bars, accuracies):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{acc:.4f}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.xlabel('Model', fontsize=12, fontweight='bold')
        plt.ylabel('Accuracy', fontsize=12, fontweight='bold')
        plt.title('Model Accuracy Comparison: Consensus vs Individual Models', 
                 fontsize=14, fontweight='bold', pad=20)
        plt.ylim(0, 1.1)
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        plt.tight_layout()
        
        output_path = os.path.join(VISUALIZATIONS_DIR, f"{self.experiment_name}_accuracy_comparison.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Accuracy comparison plot saved to: {output_path}")
        plt.close()
    
    def plot_metrics_radar(self, metrics: Dict[str, Dict[str, float]]):
        """레이더 차트로 여러 메트릭 비교"""
        metric_names = ['Accuracy', 'Precision', 'Recall', 'F1 Score']
        
        fig = go.Figure()
        
        for model_name in ['consensus'] + self.models:
            model_metrics = metrics[model_name]
            values = [
                model_metrics['accuracy'],
                model_metrics['precision'],
                model_metrics['recall'],
                model_metrics['f1_score']
            ]
            
            label = 'Consensus (5 models)' if model_name == 'consensus' else model_name.upper()
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=metric_names,
                fill='toself',
                name=label
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=True,
            title="Model Performance Metrics Comparison",
            font=dict(size=12)
        )
        
        output_path = os.path.join(VISUALIZATIONS_DIR, f"{self.experiment_name}_metrics_radar.html")
        fig.write_html(output_path)
        print(f"Radar chart saved to: {output_path}")
    
    def plot_confusion_matrices(self, metrics: Dict[str, Dict[str, float]]):
        """Confusion Matrix 시각화"""
        n_models = len(self.models) + 1  # consensus 포함
        n_cols = 3
        n_rows = (n_models + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
        axes = axes.flatten()
        
        for idx, model_name in enumerate(['consensus'] + self.models):
            cm = np.array(metrics[model_name]['confusion_matrix'])
            
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                       xticklabels=['Benign', 'Harmful'],
                       yticklabels=['Benign', 'Harmful'],
                       ax=axes[idx], cbar=True)
            
            title = 'Consensus (5 models)' if model_name == 'consensus' else model_name.upper()
            axes[idx].set_title(f'{title}\nAccuracy: {metrics[model_name]["accuracy"]:.4f}',
                              fontweight='bold')
            axes[idx].set_xlabel('Predicted')
            axes[idx].set_ylabel('Actual')
        
        # 빈 subplot 숨기기
        for idx in range(n_models, len(axes)):
            axes[idx].set_visible(False)
        
        plt.suptitle('Confusion Matrices: Consensus vs Individual Models', 
                    fontsize=16, fontweight='bold', y=1.00)
        plt.tight_layout()
        
        output_path = os.path.join(VISUALIZATIONS_DIR, f"{self.experiment_name}_confusion_matrices.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Confusion matrices saved to: {output_path}")
        plt.close()
    
    def plot_category_performance(self, metrics: Dict[str, Dict[str, float]]):
        """카테고리별 성능 비교"""
        categories = self.df['category'].unique()
        
        category_metrics = {}
        for category in categories:
            category_df = self.df[self.df['category'] == category]
            y_true = category_df['ground_truth'].astype(int)
            
            category_metrics[category] = {}
            
            # Consensus
            y_pred = category_df['consensus_prediction'].astype(int)
            category_metrics[category]['consensus'] = accuracy_score(y_true, y_pred)
            
            # 개별 모델
            for model in self.models:
                y_pred_model = category_df[f'{model}_prediction'].astype(int)
                category_metrics[category][model] = accuracy_score(y_true, y_pred_model)
        
        # 그래프 그리기
        x = np.arange(len(categories))
        width = 0.15
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        for idx, model_name in enumerate(['consensus'] + self.models):
            accuracies = [category_metrics[cat][model_name] for cat in categories]
            offset = width * (idx - len(self.models) / 2)
            label = 'Consensus' if model_name == 'consensus' else model_name.upper()
            ax.bar(x + offset, accuracies, width, label=label, alpha=0.8)
        
        ax.set_xlabel('Category', fontsize=12, fontweight='bold')
        ax.set_ylabel('Accuracy', fontsize=12, fontweight='bold')
        ax.set_title('Accuracy by Prompt Category', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([cat.replace('_', '\n') for cat in categories])
        ax.legend(loc='upper right')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_ylim(0, 1.1)
        
        plt.tight_layout()
        
        output_path = os.path.join(VISUALIZATIONS_DIR, f"{self.experiment_name}_category_performance.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Category performance plot saved to: {output_path}")
        plt.close()
    
    def generate_full_report(self):
        """전체 보고서 생성"""
        print(f"\n{'='*80}")
        print(f"Generating Analysis Report: {self.experiment_name}")
        print(f"{'='*80}\n")
        
        # 메트릭 계산
        metrics = self.calculate_metrics()
        
        # 1. 비교 표 생성
        print("\n1. Generating comparison table...")
        comparison_df = self.generate_comparison_table(metrics)
        print("\nComparison Table:")
        print(comparison_df.to_string(index=False))
        
        # 2. 정확도 비교 그래프
        print("\n2. Plotting accuracy comparison...")
        self.plot_accuracy_comparison(metrics)
        
        # 3. 레이더 차트
        print("\n3. Creating radar chart...")
        self.plot_metrics_radar(metrics)
        
        # 4. Confusion matrices
        print("\n4. Plotting confusion matrices...")
        self.plot_confusion_matrices(metrics)
        
        # 5. 카테고리별 성능
        print("\n5. Analyzing category performance...")
        self.plot_category_performance(metrics)
        
        # 6. 텍스트 보고서 생성
        print("\n6. Generating text report...")
        self._generate_text_report(metrics, comparison_df)
        
        print(f"\n{'='*80}")
        print(f"Analysis Complete!")
        print(f"Reports saved to: {REPORTS_DIR}")
        print(f"Visualizations saved to: {VISUALIZATIONS_DIR}")
        print(f"{'='*80}\n")
    
    def _generate_text_report(self, metrics: Dict, comparison_df: pd.DataFrame):
        """텍스트 보고서 생성"""
        report_path = os.path.join(REPORTS_DIR, f"{self.experiment_name}_report.txt")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write(f"EXPERIMENT ANALYSIS REPORT\n")
            f.write(f"Experiment: {self.experiment_name}\n")
            f.write(f"Date: {self.experiment_data['timestamp']}\n")
            f.write("="*80 + "\n\n")
            
            f.write("1. EXPERIMENT CONFIGURATION\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total Samples: {len(self.results)}\n")
            f.write(f"Consensus Threshold: {self.experiment_data['consensus_threshold']}/5\n")
            f.write(f"Models Tested:\n")
            for model, model_id in self.experiment_data['models'].items():
                f.write(f"  - {model}: {model_id}\n")
            f.write("\n")
            
            f.write("2. PERFORMANCE COMPARISON\n")
            f.write("-" * 40 + "\n")
            f.write(comparison_df.to_string(index=False))
            f.write("\n\n")
            
            f.write("3. KEY FINDINGS\n")
            f.write("-" * 40 + "\n")
            
            consensus_acc = metrics['consensus']['accuracy']
            individual_accs = [metrics[m]['accuracy'] for m in self.models]
            avg_individual = np.mean(individual_accs)
            max_individual = max(individual_accs)
            
            f.write(f"Consensus Accuracy: {consensus_acc:.4f}\n")
            f.write(f"Average Individual Model Accuracy: {avg_individual:.4f}\n")
            f.write(f"Best Individual Model Accuracy: {max_individual:.4f}\n")
            if avg_individual > 0:
                f.write(f"Improvement over Average: {(consensus_acc - avg_individual):.4f} ({((consensus_acc - avg_individual) / avg_individual * 100):.2f}%)\n")
            else:
                f.write(f"Improvement over Average: {(consensus_acc - avg_individual):.4f}\n")
            
            if max_individual > 0:
                f.write(f"Improvement over Best: {(consensus_acc - max_individual):.4f} ({((consensus_acc - max_individual) / max_individual * 100):.2f}%)\n")
            else:
                f.write(f"Improvement over Best: {(consensus_acc - max_individual):.4f}\n")
            f.write("\n")
            
            f.write("4. CATEGORY BREAKDOWN\n")
            f.write("-" * 40 + "\n")
            for category in self.df['category'].unique():
                category_df = self.df[self.df['category'] == category]
                y_true = category_df['ground_truth'].astype(int)
                y_pred = category_df['consensus_prediction'].astype(int)
                acc = accuracy_score(y_true, y_pred)
                f.write(f"{category}: {acc:.4f} ({len(category_df)} samples)\n")
            
            f.write("\n" + "="*80 + "\n")
        
        print(f"Text report saved to: {report_path}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python result_analyzer.py <experiment_json_file>")
        sys.exit(1)
    
    analyzer = ResultAnalyzer(sys.argv[1])
    analyzer.generate_full_report()

