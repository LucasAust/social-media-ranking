#!/usr/bin/env python3
"""
Performance testing module for the social media ranking system.
Tests various algorithms with large datasets to measure performance.
"""

import time
import random
import psutil
import os
from typing import List, Dict, Any
from ranking_engine import RankingEngine, OptimizedRankingEngine
import numpy as np


class PerformanceTester:
    """Comprehensive performance testing for ranking algorithms."""
    
    def __init__(self):
        self.results = {}
        self.memory_usage = {}
        
    def generate_test_data(self, num_posts: int) -> List[Dict[str, Any]]:
        """Generate realistic test data for social media posts."""
        posts = []
        base_time = time.time() - (86400 * 30)  # 30 days ago
        
        for i in range(num_posts):
            # Generate realistic engagement metrics
            likes = random.randint(0, 10000)
            comments = random.randint(0, likes // 10)
            shares = random.randint(0, likes // 20)
            upvotes = random.randint(0, likes)
            downvotes = random.randint(0, likes // 5)
            
            # Random timestamp within last 30 days
            timestamp = base_time + random.random() * 86400 * 30
            
            posts.append({
                'post_id': f'post_{i:06d}',
                'likes': likes,
                'comments': comments,
                'shares': shares,
                'upvotes': upvotes,
                'downvotes': downvotes,
                'timestamp': timestamp
            })
            
        return posts
        
    def measure_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
        
    def benchmark_algorithm(self, engine: RankingEngine, algorithm: str, 
                          num_posts: int, num_runs: int = 5) -> Dict[str, Any]:
        """Benchmark a specific algorithm."""
        print(f"Benchmarking {algorithm} with {num_posts:,} posts...")
        
        # Generate test data
        test_data = self.generate_test_data(num_posts)
        
        # Measure memory before
        memory_before = self.measure_memory_usage()
        
        # Add posts and measure time
        start_time = time.time()
        engine.batch_add_posts(test_data)
        add_time = time.time() - start_time
        
        # Measure memory after adding posts
        memory_after_add = self.measure_memory_usage()
        
        # Benchmark ranking generation
        ranking_times = []
        for _ in range(num_runs):
            start_time = time.time()
            ranked_posts = engine.get_ranked_posts(algorithm=algorithm, limit=100)
            ranking_time = time.time() - start_time
            ranking_times.append(ranking_time)
            
        # Measure memory after ranking
        memory_after_ranking = self.measure_memory_usage()
        
        # Calculate statistics
        avg_ranking_time = np.mean(ranking_times)
        std_ranking_time = np.std(ranking_times)
        min_ranking_time = min(ranking_times)
        max_ranking_time = max(ranking_times)
        
        # Test update performance
        update_times = []
        for _ in range(min(100, num_posts)):
            post_id = f'post_{random.randint(0, num_posts-1):06d}'
            start_time = time.time()
            engine.update_post(post_id, likes=random.randint(0, 1000))
            update_time = time.time() - start_time
            update_times.append(update_time)
            
        avg_update_time = np.mean(update_times)
        
        return {
            'algorithm': algorithm,
            'num_posts': num_posts,
            'add_time_seconds': add_time,
            'add_rate_posts_per_second': num_posts / max(float(add_time), 0.001),  # Avoid division by zero
            'avg_ranking_time_ms': avg_ranking_time * 1000,
            'std_ranking_time_ms': std_ranking_time * 1000,
            'min_ranking_time_ms': min_ranking_time * 1000,
            'max_ranking_time_ms': max_ranking_time * 1000,
            'avg_update_time_ms': avg_update_time * 1000,
            'memory_usage_mb': memory_after_add,
            'memory_increase_mb': memory_after_add - memory_before,
            'posts_per_second_ranking': 100 / max(float(avg_ranking_time), 0.001),  # Avoid division by zero
            'num_runs': num_runs
        }
        
    def run_comprehensive_benchmark(self, max_posts: int = 1000000) -> Dict[str, Any]:
        """Run comprehensive benchmarks across different scales."""
        print("Starting comprehensive performance benchmark...")
        print("=" * 60)
        
        # Test different scales
        test_scales = [1000, 10000, 50000, 100000]
        test_scales = [scale for scale in test_scales if scale <= max_posts]
        
        algorithms = ["hot_score", "engagement_score", "time_decay", "hybrid"]
        
        all_results = {}
        
        for scale in test_scales:
            print(f"\nTesting scale: {scale:,} posts")
            print("-" * 40)
            
            scale_results = {}
            
            # Test regular engine
            print("Testing standard RankingEngine...")
            engine = RankingEngine()
            for algorithm in algorithms:
                result = self.benchmark_algorithm(engine, algorithm, scale)
                scale_results[f"standard_{algorithm}"] = result
                
            # Test optimized engine
            print("Testing OptimizedRankingEngine...")
            opt_engine = OptimizedRankingEngine()
            for algorithm in algorithms:
                result = self.benchmark_algorithm(opt_engine, algorithm, scale)
                scale_results[f"optimized_{algorithm}"] = result
                
            all_results[scale] = scale_results
            
        return all_results
        
    def print_results(self, results: Dict[str, Any]) -> None:
        """Print formatted benchmark results."""
        print("\n" + "=" * 80)
        print("PERFORMANCE BENCHMARK RESULTS")
        print("=" * 80)
        
        for scale, scale_results in results.items():
            print(f"\n📊 SCALE: {scale:,} POSTS")
            print("-" * 60)
            
            # Group by algorithm type
            for algorithm in ["hot_score", "engagement_score", "time_decay", "hybrid"]:
                print(f"\n🔸 Algorithm: {algorithm.upper()}")
                print(f"{'Engine':<15} {'Ranking (ms)':<12} {'Updates (ms)':<12} {'Memory (MB)':<12} {'Posts/sec':<12}")
                print("-" * 70)
                
                standard_key = f"standard_{algorithm}"
                optimized_key = f"optimized_{algorithm}"
                
                if standard_key in scale_results:
                    std = scale_results[standard_key]
                    print(f"{'Standard':<15} {std['avg_ranking_time_ms']:<12.2f} {std['avg_update_time_ms']:<12.2f} {std['memory_usage_mb']:<12.1f} {std['posts_per_second_ranking']:<12.0f}")
                
                if optimized_key in scale_results:
                    opt = scale_results[optimized_key]
                    print(f"{'Optimized':<15} {opt['avg_ranking_time_ms']:<12.2f} {opt['avg_update_time_ms']:<12.2f} {opt['memory_usage_mb']:<12.1f} {opt['posts_per_second_ranking']:<12.0f}")
                    
    def generate_performance_report(self, results: Dict[str, Any]) -> str:
        """Generate a detailed performance report."""
        report = []
        report.append("# Social Media Ranking System - Performance Report")
        report.append("")
        report.append("## Executive Summary")
        report.append("")
        
        # Find best performing configuration
        best_ranking_time = float('inf')
        best_config = None
        
        for scale, scale_results in results.items():
            for config, result in scale_results.items():
                if result['avg_ranking_time_ms'] < best_ranking_time:
                    best_ranking_time = result['avg_ranking_time_ms']
                    best_config = (scale, config, result)
        
        if best_config:
            scale, config, result = best_config
            report.append(f"- **Best Performance**: {config} at {scale:,} posts")
            report.append(f"- **Ranking Time**: {result['avg_ranking_time_ms']:.2f}ms")
            report.append(f"- **Throughput**: {result['posts_per_second_ranking']:.0f} posts/second")
            report.append(f"- **Memory Usage**: {result['memory_usage_mb']:.1f}MB")
            report.append("")
        
        report.append("## Detailed Results")
        report.append("")
        
        for scale, scale_results in results.items():
            report.append(f"### {scale:,} Posts")
            report.append("")
            report.append("| Algorithm | Engine | Ranking (ms) | Updates (ms) | Memory (MB) | Posts/sec |")
            report.append("|-----------|--------|--------------|--------------|-------------|-----------|")
            
            for algorithm in ["hot_score", "engagement_score", "time_decay", "hybrid"]:
                standard_key = f"standard_{algorithm}"
                optimized_key = f"optimized_{algorithm}"
                
                if standard_key in scale_results:
                    std = scale_results[standard_key]
                    report.append(f"| {algorithm} | Standard | {std['avg_ranking_time_ms']:.2f} | {std['avg_update_time_ms']:.2f} | {std['memory_usage_mb']:.1f} | {std['posts_per_second_ranking']:.0f} |")
                
                if optimized_key in scale_results:
                    opt = scale_results[optimized_key]
                    report.append(f"| {algorithm} | Optimized | {opt['avg_ranking_time_ms']:.2f} | {opt['avg_update_time_ms']:.2f} | {opt['memory_usage_mb']:.1f} | {opt['posts_per_second_ranking']:.0f} |")
            
            report.append("")
        
        return "\n".join(report)


def main():
    """Main function to run performance tests."""
    print("🚀 Social Media Ranking System - Performance Test")
    print("=" * 60)
    
    # Initialize tester
    tester = PerformanceTester()
    
    # Run comprehensive benchmark
    results = tester.run_comprehensive_benchmark(max_posts=100000)
    
    # Print results
    tester.print_results(results)
    
    # Generate and save report
    report = tester.generate_performance_report(results)
    with open('performance_report.md', 'w') as f:
        f.write(report)
    
    print(f"\n📄 Performance report saved to: performance_report.md")
    print("\n✅ Performance testing completed!")


if __name__ == "__main__":
    main() 