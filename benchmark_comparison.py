#!/usr/bin/env python3
"""
Benchmark comparison script for different ranking algorithms and implementations.
Compares performance across various scenarios and provides detailed analysis.
"""

import time
import random
import statistics
from typing import Dict, List, Any
from ranking_engine import RankingEngine, OptimizedRankingEngine
import numpy as np


class BenchmarkComparison:
    """Comprehensive benchmark comparison for ranking algorithms."""
    
    def __init__(self):
        self.results = {}
        
    def generate_realistic_data(self, num_posts: int, engagement_pattern: str = "normal") -> List[Dict[str, Any]]:
        """Generate realistic social media data with different engagement patterns."""
        posts = []
        base_time = time.time() - (86400 * 30)  # 30 days ago
        
        if engagement_pattern == "normal":
            # Normal distribution of engagement
            for i in range(num_posts):
                likes = max(0, int(random.gauss(500, 200)))
                comments = max(0, int(random.gauss(likes * 0.1, likes * 0.05)))
                shares = max(0, int(random.gauss(likes * 0.05, likes * 0.02)))
                upvotes = max(0, int(random.gauss(likes * 1.2, likes * 0.3)))
                downvotes = max(0, int(random.gauss(likes * 0.1, likes * 0.05)))
                
                # Random timestamp with some viral posts being recent
                if random.random() < 0.1:  # 10% chance of recent post
                    timestamp = time.time() - random.random() * 86400 * 3
                else:
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
                
        elif engagement_pattern == "viral":
            # Some posts go viral, most have low engagement
            for i in range(num_posts):
                if random.random() < 0.01:  # 1% viral posts
                    likes = random.randint(5000, 50000)
                    comments = random.randint(500, 5000)
                    shares = random.randint(200, 2000)
                    upvotes = random.randint(6000, 60000)
                    downvotes = random.randint(100, 1000)
                    timestamp = time.time() - random.random() * 86400 * 7  # Recent
                else:
                    likes = random.randint(0, 100)
                    comments = random.randint(0, 10)
                    shares = random.randint(0, 5)
                    upvotes = random.randint(0, 120)
                    downvotes = random.randint(0, 20)
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
                
        elif engagement_pattern == "uniform":
            # Uniform distribution
            for i in range(num_posts):
                likes = random.randint(0, 1000)
                comments = random.randint(0, 100)
                shares = random.randint(0, 50)
                upvotes = random.randint(0, 1200)
                downvotes = random.randint(0, 100)
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
        
    def benchmark_algorithm_comparison(self, num_posts: int = 10000) -> Dict[str, Any]:
        """Compare all algorithms with the same dataset."""
        print(f"🔍 Benchmarking algorithm comparison with {num_posts:,} posts...")
        
        # Generate test data
        test_data = self.generate_realistic_data(num_posts, "normal")
        
        # Test both engines
        engines = {
            'Standard': RankingEngine(),
            'Optimized': OptimizedRankingEngine()
        }
        
        algorithms = ['hot_score', 'engagement_score', 'time_decay', 'hybrid']
        
        results = {}
        
        for engine_name, engine in engines.items():
            print(f"\n🏃 Testing {engine_name} engine...")
            
            # Add posts
            start_time = time.time()
            engine.batch_add_posts(test_data)
            add_time = time.time() - start_time
            
            engine_results = {
                'add_time': add_time,
                'add_rate': len(test_data) / add_time,
                'algorithms': {}
            }
            
            # Test each algorithm
            for algorithm in algorithms:
                print(f"  Testing {algorithm}...")
                
                # Warm up cache
                engine.get_ranked_posts(algorithm=algorithm, limit=100)
                
                # Benchmark
                ranking_times = []
                for _ in range(10):  # Multiple runs for accuracy
                    start_time = time.time()
                    rankings = engine.get_ranked_posts(algorithm=algorithm, limit=100)
                    ranking_time = time.time() - start_time
                    ranking_times.append(ranking_time)
                
                # Calculate statistics
                avg_time = statistics.mean(ranking_times)
                std_time = statistics.stdev(ranking_times)
                min_time = min(ranking_times)
                max_time = max(ranking_times)
                
                engine_results['algorithms'][algorithm] = {
                    'avg_time_ms': avg_time * 1000,
                    'std_time_ms': std_time * 1000,
                    'min_time_ms': min_time * 1000,
                    'max_time_ms': max_time * 1000,
                    'throughput_posts_per_sec': 100 / max(float(avg_time), 0.001),  # Avoid division by zero
                    'rankings': rankings[:5]  # Top 5 for analysis
                }
            
            # Test update performance
            update_times = []
            for _ in range(100):
                post_id = f'post_{random.randint(0, num_posts-1):06d}'
                start_time = time.time()
                engine.update_post(post_id, likes=random.randint(0, 1000))
                update_time = time.time() - start_time
                update_times.append(update_time)
            
            engine_results['avg_update_time_ms'] = statistics.mean(update_times) * 1000
            engine_results['memory_usage_mb'] = engine.get_stats()['memory_usage_mb']
            
            results[engine_name] = engine_results
        
        return results
        
    def benchmark_scalability(self, max_posts: int = 100000) -> Dict[str, Any]:
        """Test scalability across different dataset sizes."""
        print(f"📈 Benchmarking scalability up to {max_posts:,} posts...")
        
        scales = [1000, 5000, 10000, 25000, 50000, 100000]
        scales = [scale for scale in scales if scale <= max_posts]
        
        results = {}
        
        for scale in scales:
            print(f"\nTesting scale: {scale:,} posts")
            
            # Generate data for this scale
            test_data = self.generate_realistic_data(scale, "normal")
            
            # Test optimized engine (better for large datasets)
            engine = OptimizedRankingEngine()
            
            # Measure add performance
            start_time = time.time()
            engine.batch_add_posts(test_data)
            add_time = time.time() - start_time
            
            # Measure ranking performance for each algorithm
            algorithm_times = {}
            for algorithm in ['hot_score', 'engagement_score', 'time_decay']:
                start_time = time.time()
                rankings = engine.get_ranked_posts(algorithm=algorithm, limit=100)
                ranking_time = time.time() - start_time
                algorithm_times[algorithm] = ranking_time * 1000  # Convert to ms
            
            # Measure memory usage
            memory_usage = engine.get_stats()['memory_usage_mb']
            
            results[scale] = {
                'add_time_seconds': add_time,
                'add_rate_posts_per_second': scale / add_time,
                'ranking_times_ms': algorithm_times,
                'memory_usage_mb': memory_usage,
                'posts_per_mb': scale / memory_usage if memory_usage > 0 else 0
            }
        
        return results
        
    def benchmark_engagement_patterns(self, num_posts: int = 10000) -> Dict[str, Any]:
        """Compare performance with different engagement patterns."""
        print(f"🎯 Benchmarking engagement patterns with {num_posts:,} posts...")
        
        patterns = ['normal', 'viral', 'uniform']
        results = {}
        
        for pattern in patterns:
            print(f"\nTesting {pattern} engagement pattern...")
            
            # Generate data with this pattern
            test_data = self.generate_realistic_data(num_posts, pattern)
            
            # Test with optimized engine
            engine = OptimizedRankingEngine()
            
            # Add posts
            start_time = time.time()
            engine.batch_add_posts(test_data)
            add_time = time.time() - start_time
            
            # Test each algorithm
            algorithm_results = {}
            for algorithm in ['hot_score', 'engagement_score', 'time_decay']:
                start_time = time.time()
                rankings = engine.get_ranked_posts(algorithm=algorithm, limit=100)
                ranking_time = time.time() - start_time
                
                algorithm_results[algorithm] = {
                    'ranking_time_ms': ranking_time * 1000,
                    'top_post_score': rankings[0]['score'] if rankings else 0,
                    'score_variance': np.var([post['score'] for post in rankings]) if rankings else 0
                }
            
            results[pattern] = {
                'add_time_seconds': add_time,
                'algorithms': algorithm_results,
                'memory_usage_mb': engine.get_stats()['memory_usage_mb']
            }
        
        return results
        
    def print_comprehensive_report(self, results: Dict[str, Any]) -> None:
        """Print a comprehensive benchmark report."""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE BENCHMARK REPORT")
        print("=" * 80)
        
        # Algorithm comparison results
        if 'algorithm_comparison' in results:
            print("\n🔍 ALGORITHM COMPARISON")
            print("-" * 60)
            
            for engine_name, engine_results in results['algorithm_comparison'].items():
                print(f"\n{engine_name} Engine:")
                print(f"  Add Rate: {engine_results['add_rate']:.0f} posts/second")
                print(f"  Update Time: {engine_results['avg_update_time_ms']:.2f}ms")
                print(f"  Memory Usage: {engine_results['memory_usage_mb']:.1f}MB")
                
                print("  Algorithm Performance:")
                for algorithm, perf in engine_results['algorithms'].items():
                    print(f"    {algorithm}: {perf['avg_time_ms']:.2f}ms "
                          f"(±{perf['std_time_ms']:.2f}ms) - "
                          f"{perf['throughput_posts_per_sec']:.0f} posts/sec")
        
        # Scalability results
        if 'scalability' in results:
            print("\n📈 SCALABILITY ANALYSIS")
            print("-" * 60)
            
            print(f"{'Posts':<10} {'Add (s)':<10} {'Hot (ms)':<10} {'Engage (ms)':<12} {'Memory (MB)':<12}")
            print("-" * 60)
            
            for scale in sorted(results['scalability'].keys()):
                data = results['scalability'][scale]
                print(f"{scale:<10,} {data['add_time_seconds']:<10.2f} "
                      f"{data['ranking_times_ms']['hot_score']:<10.2f} "
                      f"{data['ranking_times_ms']['engagement_score']:<12.2f} "
                      f"{data['memory_usage_mb']:<12.1f}")
        
        # Engagement pattern results
        if 'engagement_patterns' in results:
            print("\n🎯 ENGAGEMENT PATTERN ANALYSIS")
            print("-" * 60)
            
            for pattern, data in results['engagement_patterns'].items():
                print(f"\n{pattern.upper()} Pattern:")
                print(f"  Add Time: {data['add_time_seconds']:.2f}s")
                print(f"  Memory Usage: {data['memory_usage_mb']:.1f}MB")
                
                for algorithm, perf in data['algorithms'].items():
                    print(f"    {algorithm}: {perf['ranking_time_ms']:.2f}ms "
                          f"(Score Variance: {perf['score_variance']:.2f})")
        
        # Performance recommendations
        print("\n💡 PERFORMANCE RECOMMENDATIONS")
        print("-" * 60)
        
        if 'algorithm_comparison' in results:
            std_engine = results['algorithm_comparison']['Standard']
            opt_engine = results['algorithm_comparison']['Optimized']
            
            # Find fastest algorithm
            fastest_std = min(std_engine['algorithms'].items(), 
                            key=lambda x: x[1]['avg_time_ms'])
            fastest_opt = min(opt_engine['algorithms'].items(), 
                            key=lambda x: x[1]['avg_time_ms'])
            
            print(f"• Fastest Algorithm: {fastest_opt[0]} ({fastest_opt[1]['avg_time_ms']:.2f}ms)")
            print(f"• Optimization Benefit: {fastest_std[1]['avg_time_ms'] / fastest_opt[1]['avg_time_ms']:.1f}x faster")
            print(f"• Memory Efficiency: {opt_engine['memory_usage_mb'] / std_engine['memory_usage_mb']:.1f}x more efficient")
        
        if 'scalability' in results:
            scales = list(results['scalability'].keys())
            if len(scales) >= 2:
                first_scale = scales[0]
                last_scale = scales[-1]
                
                first_data = results['scalability'][first_scale]
                last_data = results['scalability'][last_scale]
                
                scaling_factor = last_scale / first_scale
                time_scaling = last_data['ranking_times_ms']['hot_score'] / first_data['ranking_times_ms']['hot_score']
                
                print(f"• Scalability: {scaling_factor:.0f}x more posts = {time_scaling:.1f}x more time")
                print(f"• Linear Scaling: {'Yes' if time_scaling < scaling_factor else 'No'}")


def main():
    """Run comprehensive benchmarks."""
    print("🚀 Social Media Ranking System - Comprehensive Benchmark")
    print("=" * 70)
    
    benchmark = BenchmarkComparison()
    results = {}
    
    # Run all benchmarks
    print("\n1. Algorithm Comparison Benchmark")
    results['algorithm_comparison'] = benchmark.benchmark_algorithm_comparison(10000)
    
    print("\n2. Scalability Benchmark")
    results['scalability'] = benchmark.benchmark_scalability(50000)
    
    print("\n3. Engagement Pattern Benchmark")
    results['engagement_patterns'] = benchmark.benchmark_engagement_patterns(10000)
    
    # Print comprehensive report
    benchmark.print_comprehensive_report(results)
    
    # Save results
    import json
    with open('benchmark_results.json', 'w') as f:
        # Convert numpy types to native Python types for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj
        
        json.dump(results, f, default=convert_numpy, indent=2)
    
    print(f"\n📄 Detailed results saved to: benchmark_results.json")
    print("\n✅ Benchmarking completed!")


if __name__ == "__main__":
    main() 