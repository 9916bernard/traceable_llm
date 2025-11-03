#!/usr/bin/env python3
"""
Blockchain Performance 결과 분석 및 시각화

테스트 결과를 분석하고 그래프와 리포트를 생성합니다.
"""

import json
import argparse
import os
import sys
from datetime import datetime
from typing import List, Dict, Any
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # GUI 없이 그래프 생성

# 한글 폰트 설정 (MacOS)
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False


class BlockchainPerformanceAnalyzer:
    """블록체인 성능 분석기"""
    
    def __init__(self, results: List[Dict[str, Any]]):
        self.results = results
        self.successful_results = [r for r in results if r.get('success')]
        
        if not self.successful_results:
            raise ValueError("No successful test results to analyze")
    
    def extract_metrics(self) -> Dict[str, List[float]]:
        """테스트 결과에서 주요 메트릭 추출"""
        metrics = {
            'commit_times': [],
            'verification_times': [],
            'tx_submission_times': [],
            'tx_confirmation_times': [],
            'gas_used': [],
            'gas_price_gwei': [],
            'gas_cost_eth': [],
            'test_numbers': []
        }
        
        for result in self.successful_results:
            commit = result.get('commit', {})
            timing = commit.get('timing', {})
            verification = result.get('verification', {})
            verify_timing = verification.get('timing', {})
            
            metrics['test_numbers'].append(result['test_number'])
            metrics['commit_times'].append(timing.get('total_commit_time', 0))
            metrics['tx_submission_times'].append(timing.get('tx_submission_time', 0))
            metrics['tx_confirmation_times'].append(timing.get('tx_confirmation_time', 0))
            metrics['verification_times'].append(verify_timing.get('total_verification_time', 0))
            metrics['gas_used'].append(commit.get('gas_used', 0))
            metrics['gas_price_gwei'].append(commit.get('gas_price_gwei', 0))
            metrics['gas_cost_eth'].append(commit.get('gas_cost_eth', 0))
        
        return metrics
    
    def calculate_statistics(self, data: List[float]) -> Dict[str, float]:
        """통계 계산"""
        if not data:
            return {}
        
        return {
            'mean': np.mean(data),
            'median': np.median(data),
            'std': np.std(data),
            'min': np.min(data),
            'max': np.max(data),
            'q1': np.percentile(data, 25),
            'q3': np.percentile(data, 75)
        }
    
    def generate_summary_report(self, output_dir: str):
        """요약 리포트 생성"""
        metrics = self.extract_metrics()
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("BLOCKCHAIN PERFORMANCE TEST REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Total Tests: {len(self.results)}")
        report_lines.append(f"Successful Tests: {len(self.successful_results)}")
        report_lines.append(f"Failed Tests: {len(self.results) - len(self.successful_results)}")
        report_lines.append("")
        
        # Commit Latency 통계
        commit_stats = self.calculate_statistics(metrics['commit_times'])
        report_lines.append("=" * 80)
        report_lines.append("COMMIT LATENCY (Sepolia Testnet)")
        report_lines.append("=" * 80)
        report_lines.append(f"Average:        {commit_stats['mean']:.3f}s")
        report_lines.append(f"Median:         {commit_stats['median']:.3f}s")
        report_lines.append(f"Std Dev:        {commit_stats['std']:.3f}s")
        report_lines.append(f"Min:            {commit_stats['min']:.3f}s")
        report_lines.append(f"Max:            {commit_stats['max']:.3f}s")
        report_lines.append(f"Q1 (25%):       {commit_stats['q1']:.3f}s")
        report_lines.append(f"Q3 (75%):       {commit_stats['q3']:.3f}s")
        report_lines.append("")
        
        # TX Submission vs Confirmation 분해
        tx_sub_stats = self.calculate_statistics(metrics['tx_submission_times'])
        tx_conf_stats = self.calculate_statistics(metrics['tx_confirmation_times'])
        report_lines.append("  Breakdown:")
        report_lines.append(f"    - TX Submission (Avg):   {tx_sub_stats['mean']:.3f}s")
        report_lines.append(f"    - TX Confirmation (Avg): {tx_conf_stats['mean']:.3f}s")
        report_lines.append("")
        
        # Verification Latency 통계
        verify_stats = self.calculate_statistics(metrics['verification_times'])
        report_lines.append("=" * 80)
        report_lines.append("VERIFICATION LATENCY (Etherscan API)")
        report_lines.append("=" * 80)
        report_lines.append(f"Average:        {verify_stats['mean']:.3f}s")
        report_lines.append(f"Median:         {verify_stats['median']:.3f}s")
        report_lines.append(f"Std Dev:        {verify_stats['std']:.3f}s")
        report_lines.append(f"Min:            {verify_stats['min']:.3f}s")
        report_lines.append(f"Max:            {verify_stats['max']:.3f}s")
        report_lines.append("")
        
        # Gas Cost 통계
        gas_used_stats = self.calculate_statistics(metrics['gas_used'])
        gas_price_stats = self.calculate_statistics(metrics['gas_price_gwei'])
        gas_cost_stats = self.calculate_statistics(metrics['gas_cost_eth'])
        
        report_lines.append("=" * 80)
        report_lines.append("GAS USAGE AND COSTS (Sepolia Testnet)")
        report_lines.append("=" * 80)
        report_lines.append(f"Gas Used (Avg):      {gas_used_stats['mean']:.0f} gas")
        report_lines.append(f"Gas Used (Min/Max):  {gas_used_stats['min']:.0f} / {gas_used_stats['max']:.0f} gas")
        report_lines.append(f"Gas Price (Avg):     {gas_price_stats['mean']:.2f} Gwei")
        report_lines.append(f"Cost per TX (Avg):   {gas_cost_stats['mean']:.6f} ETH")
        report_lines.append(f"Total Cost:          {sum(metrics['gas_cost_eth']):.6f} ETH")
        report_lines.append("")
        
        # Layer 2 Cost Estimation
        if self.successful_results:
            first_result = self.successful_results[0]
            cost_analysis = first_result.get('cost_analysis', {})
            if cost_analysis:
                report_lines.append("=" * 80)
                report_lines.append("LAYER 2 MAINNET COST ESTIMATION")
                report_lines.append("=" * 80)
                
                eth_price = cost_analysis.get('eth_price_usd', 2500)
                report_lines.append(f"ETH Price (at test time): ${eth_price:.2f} USD")
                report_lines.append("")
                
                l1_cost = cost_analysis.get('l1_mainnet', {})
                if l1_cost:
                    avg_l1_cost_usd = l1_cost.get('total_cost_usd', 0) / len(self.successful_results) * len(self.successful_results)
                    report_lines.append(f"Ethereum L1 Mainnet (estimated):")
                    report_lines.append(f"  - Cost per TX: ${l1_cost.get('total_cost_usd', 0):.4f} USD")
                    report_lines.append("")
                
                l2_networks = cost_analysis.get('l2_networks', {})
                if l2_networks:
                    report_lines.append("Layer 2 Networks (estimated):")
                    for network, data in l2_networks.items():
                        report_lines.append(f"  {network.upper()}:")
                        report_lines.append(f"    - Cost per TX: ${data['estimated_cost_usd']:.4f} USD")
                        report_lines.append(f"    - Cost Reduction: {data['cost_reduction_percent']:.1f}%")
                    report_lines.append("")
                
                cheapest = cost_analysis.get('cheapest_l2', {})
                if cheapest:
                    report_lines.append(f"Cheapest Option: {cheapest.get('network', 'N/A').upper()}")
                    report_lines.append(f"  - Cost: ${cheapest.get('estimated_cost_usd', 0):.4f} USD per TX")
                    report_lines.append("")
        
        report_lines.append("=" * 80)
        report_lines.append("KEY FINDINGS")
        report_lines.append("=" * 80)
        report_lines.append(f"1. Average commit latency: {commit_stats['mean']:.2f}s")
        report_lines.append(f"2. Average verification latency: {verify_stats['mean']:.2f}s")
        report_lines.append(f"3. Verification is ~{commit_stats['mean']/verify_stats['mean']:.1f}x faster than commit")
        report_lines.append(f"4. Most commit time spent on: TX confirmation ({tx_conf_stats['mean']/commit_stats['mean']*100:.1f}%)")
        report_lines.append(f"5. Average gas cost per TX: {gas_cost_stats['mean']:.6f} ETH")
        report_lines.append("=" * 80)
        
        # 파일에 저장
        os.makedirs(os.path.join(output_dir, 'reports'), exist_ok=True)
        report_path = os.path.join(output_dir, 'reports', 'performance_summary.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print('\n'.join(report_lines))
        print(f"\n📄 Report saved: {report_path}")
        
        return report_path
    
    def generate_visualizations(self, output_dir: str):
        """시각화 그래프 생성"""
        metrics = self.extract_metrics()
        os.makedirs(os.path.join(output_dir, 'visualizations'), exist_ok=True)
        
        # 1. Commit Latency Distribution
        self._plot_distribution(
            data=metrics['commit_times'],
            title='Commit Latency Distribution',
            xlabel='Commit Time (seconds)',
            ylabel='Frequency',
            filename=os.path.join(output_dir, 'visualizations', 'commit_latency_distribution.png')
        )
        
        # 2. Verification Latency Distribution
        self._plot_distribution(
            data=metrics['verification_times'],
            title='Verification Latency Distribution',
            xlabel='Verification Time (seconds)',
            ylabel='Frequency',
            filename=os.path.join(output_dir, 'visualizations', 'verification_latency_distribution.png')
        )
        
        # 3. Latency Over Time (Line Chart)
        self._plot_latency_over_time(
            test_numbers=metrics['test_numbers'],
            commit_times=metrics['commit_times'],
            verification_times=metrics['verification_times'],
            filename=os.path.join(output_dir, 'visualizations', 'latency_over_time.png')
        )
        
        # 4. Latency Box Plot (Comparison)
        self._plot_latency_boxplot(
            commit_times=metrics['commit_times'],
            verification_times=metrics['verification_times'],
            tx_submission_times=metrics['tx_submission_times'],
            tx_confirmation_times=metrics['tx_confirmation_times'],
            filename=os.path.join(output_dir, 'visualizations', 'latency_comparison_boxplot.png')
        )
        
        # 5. Gas Cost Distribution
        self._plot_distribution(
            data=metrics['gas_cost_eth'],
            title='Gas Cost Distribution',
            xlabel='Cost (ETH)',
            ylabel='Frequency',
            filename=os.path.join(output_dir, 'visualizations', 'gas_cost_distribution.png')
        )
        
        # 6. Layer 2 Cost Comparison
        if self.successful_results and self.successful_results[0].get('cost_analysis'):
            self._plot_l2_cost_comparison(
                cost_analysis=self.successful_results[0]['cost_analysis'],
                filename=os.path.join(output_dir, 'visualizations', 'l2_cost_comparison.png')
            )
        
        print("\n✅ All visualizations generated!")
    
    def _plot_distribution(self, data: List[float], title: str, xlabel: str, ylabel: str, filename: str):
        """히스토그램 그리기"""
        plt.figure(figsize=(10, 6))
        plt.hist(data, bins=20, edgecolor='black', alpha=0.7)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel(xlabel, fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        
        # 통계 정보 추가
        stats = self.calculate_statistics(data)
        textstr = f"Mean: {stats['mean']:.3f}\nMedian: {stats['median']:.3f}\nStd: {stats['std']:.3f}"
        plt.text(0.7, 0.95, textstr, transform=plt.gca().transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig(filename, dpi=150)
        plt.close()
        print(f"📊 Saved: {filename}")
    
    def _plot_latency_over_time(self, test_numbers: List[int], commit_times: List[float],
                                verification_times: List[float], filename: str):
        """시간에 따른 latency 변화 그래프"""
        plt.figure(figsize=(12, 6))
        plt.plot(test_numbers, commit_times, marker='o', label='Commit Latency', linewidth=2)
        plt.plot(test_numbers, verification_times, marker='s', label='Verification Latency', linewidth=2)
        plt.title('Latency Over Time', fontsize=14, fontweight='bold')
        plt.xlabel('Test Number', fontsize=12)
        plt.ylabel('Time (seconds)', fontsize=12)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(filename, dpi=150)
        plt.close()
        print(f"📊 Saved: {filename}")
    
    def _plot_latency_boxplot(self, commit_times: List[float], verification_times: List[float],
                              tx_submission_times: List[float], tx_confirmation_times: List[float],
                              filename: str):
        """Latency 비교 Box Plot"""
        plt.figure(figsize=(12, 7))
        
        data_to_plot = [
            commit_times,
            verification_times,
            tx_submission_times,
            tx_confirmation_times
        ]
        labels = ['Total Commit', 'Verification', 'TX Submission', 'TX Confirmation']
        
        bp = plt.boxplot(data_to_plot, labels=labels, patch_artist=True)
        
        # 색상 설정
        colors = ['lightblue', 'lightgreen', 'lightyellow', 'lightcoral']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
        
        plt.title('Latency Comparison (Box Plot)', fontsize=14, fontweight='bold')
        plt.ylabel('Time (seconds)', fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(filename, dpi=150)
        plt.close()
        print(f"📊 Saved: {filename}")
    
    def _plot_l2_cost_comparison(self, cost_analysis: Dict[str, Any], filename: str):
        """Layer 2 cost 비교 bar chart"""
        l1_cost = cost_analysis['l1_mainnet']['total_cost_usd']
        l2_networks = cost_analysis['l2_networks']
        
        networks = ['L1 (Ethereum)'] + [net.upper() for net in l2_networks.keys()]
        costs = [l1_cost] + [data['estimated_cost_usd'] for data in l2_networks.values()]
        colors = ['red'] + ['green'] * len(l2_networks)
        
        plt.figure(figsize=(12, 7))
        bars = plt.bar(networks, costs, color=colors, alpha=0.7, edgecolor='black')
        
        # 값 표시
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:.4f}',
                    ha='center', va='bottom', fontsize=10)
        
        plt.title('Layer 2 Cost Comparison (Per Transaction)', fontsize=14, fontweight='bold')
        plt.ylabel('Cost (USD)', fontsize=12)
        plt.xlabel('Network', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(filename, dpi=150)
        plt.close()
        print(f"📊 Saved: {filename}")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='Analyze Blockchain Performance Test Results')
    parser.add_argument('--input', type=str, required=True,
                        help='Path to JSON result file')
    parser.add_argument('--output', type=str, default=None,
                        help='Output directory (default: same as input directory)')
    
    args = parser.parse_args()
    
    # 입력 파일 읽기
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file not found: {args.input}")
        sys.exit(1)
    
    with open(args.input, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    print(f"📂 Loaded {len(results)} test results from: {args.input}")
    
    # 출력 디렉토리 설정
    if args.output:
        output_dir = args.output
    else:
        # 입력 파일의 상위 디렉토리 사용
        output_dir = os.path.dirname(os.path.dirname(args.input))
    
    print(f"📁 Output directory: {output_dir}")
    
    try:
        # 분석기 생성
        analyzer = BlockchainPerformanceAnalyzer(results)
        
        # 요약 리포트 생성
        print("\n" + "="*80)
        print("📊 Generating Summary Report...")
        print("="*80)
        analyzer.generate_summary_report(output_dir)
        
        # 시각화 생성
        print("\n" + "="*80)
        print("📈 Generating Visualizations...")
        print("="*80)
        analyzer.generate_visualizations(output_dir)
        
        print("\n✅ Analysis completed successfully!")
        print(f"📁 Results saved to: {output_dir}")
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()



