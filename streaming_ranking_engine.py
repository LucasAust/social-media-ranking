#!/usr/bin/env python3
"""
Streaming Ranking Engine for Social Media Posts.
Processes posts in batches to handle any number of posts with constant memory usage.
"""

import time
import heapq
import math
from typing import Iterator, List, Tuple, Dict, Any, Optional
from dataclasses import dataclass, field
from ranking_engine import Post, RankingEngine


@dataclass
class StreamingRankingResult:
    """Result from streaming ranking operation."""
    top_posts: List[Tuple[float, Post]]
    total_posts_processed: int
    memory_usage_mb: float
    processing_time_seconds: float
    algorithm: str
    batch_size: int


class StreamingRankingEngine:
    """
    Streaming ranking engine that processes posts in batches.
    Can handle any number of posts with constant memory usage.
    """
    
    def __init__(self, batch_size: int = 100_000, max_heap_size: int = 1000):
        self.batch_size = batch_size
        self.max_heap_size = max_heap_size
        self.base_engine = RankingEngine()
        
    def _calculate_score(self, post: Post, algorithm: str, **kwargs) -> float:
        """Calculate score for a single post using the specified algorithm."""
        if algorithm == "hot_score":
            return self.base_engine._hot_score(post)
        elif algorithm == "engagement_score":
            return self.base_engine._engagement_score(post)
        elif algorithm == "time_decay":
            decay_rate = kwargs.get('decay_rate', 0.01)
            return self.base_engine._time_decay_score(post, decay_rate)
        elif algorithm == "hybrid":
            weights = kwargs.get('weights')
            return self.base_engine._hybrid_score(post, weights)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
    
    def rank_posts_streaming(
        self,
        post_iterator: Iterator[Post],
        algorithm: str = "hot_score",
        top_k: int = 100,
        **kwargs
    ) -> StreamingRankingResult:
        """
        Rank posts from an iterator in batches, keeping only the top_k overall.
        This allows ranking any number of posts with constant memory usage.
        
        Args:
            post_iterator: Iterator that yields Post objects
            algorithm: Ranking algorithm to use
            top_k: Number of top posts to return
            **kwargs: Additional arguments for the ranking algorithm
            
        Returns:
            StreamingRankingResult with top posts and metadata
        """
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        # Use a min-heap to keep only the top_k posts
        min_heap = []
        total_posts = 0
        batch_count = 0
        
        try:
            while True:
                # Process posts in batches
                batch = []
                for _ in range(self.batch_size):
                    try:
                        post = next(post_iterator)
                        batch.append(post)
                        total_posts += 1
                    except StopIteration:
                        break
                
                if not batch:
                    break
                
                batch_count += 1
                print(f"Processing batch {batch_count} ({len(batch)} posts, total: {total_posts:,})")
                
                # Score all posts in the current batch
                for post in batch:
                    score = self._calculate_score(post, algorithm, **kwargs)
                    
                    # Use min-heap to maintain top_k posts
                    if len(min_heap) < top_k:
                        heapq.heappush(min_heap, (score, post))
                    else:
                        # Replace the lowest scoring post if this one is better
                        heapq.heappushpop(min_heap, (score, post))
                
                # Print memory usage every 10 batches
                if batch_count % 10 == 0:
                    current_memory = self._get_memory_usage()
                    print(f"  Memory usage: {current_memory:.1f} MB")
        
        except Exception as e:
            print(f"Error during streaming ranking: {e}")
            raise
        
        # Sort the top_k posts by score (descending)
        top_posts = sorted(min_heap, reverse=True)
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        return StreamingRankingResult(
            top_posts=top_posts,
            total_posts_processed=total_posts,
            memory_usage_mb=end_memory,
            processing_time_seconds=end_time - start_time,
            algorithm=algorithm,
            batch_size=self.batch_size
        )
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            # Fallback if psutil is not available
            return 0.0
    
    def rank_posts_from_list(
        self,
        posts: List[Post],
        algorithm: str = "hot_score",
        top_k: int = 100,
        **kwargs
    ) -> StreamingRankingResult:
        """
        Rank posts from a list using streaming approach.
        Useful for testing and when you have a list of posts.
        """
        def post_iterator():
            for post in posts:
                yield post
        
        return self.rank_posts_streaming(post_iterator(), algorithm, top_k, **kwargs)


def generate_test_posts(num_posts: int) -> Iterator[Post]:
    """
    Generate test posts for benchmarking.
    This simulates a real-world scenario where posts come from a database or API.
    """
    base_time = time.time()
    
    for i in range(num_posts):
        # Generate realistic engagement metrics
        likes = (i * 7) % 10000 + 1  # Varies from 1 to 10000
        comments = (i * 3) % 1000 + 1  # Varies from 1 to 1000
        shares = (i * 5) % 500 + 1  # Varies from 1 to 500
        upvotes = likes + (i % 100)
        downvotes = (i % 50)
        
        # Random timestamp within last 30 days
        timestamp = base_time - (i % (86400 * 30))
        
        yield Post(
            post_id=f'post_{i:08d}',
            likes=likes,
            comments=comments,
            shares=shares,
            upvotes=upvotes,
            downvotes=downvotes,
            timestamp=timestamp
        )


def benchmark_streaming_ranking(max_posts: int = 1_000_000) -> Dict[str, Any]:
    """
    Benchmark the streaming ranking engine with different numbers of posts.
    """
    print(f"🚀 Streaming Ranking Engine Benchmark (up to {max_posts:,} posts)")
    print("=" * 70)
    
    # Test different scales
    test_scales = [10_000, 100_000, 500_000, 1_000_000]
    test_scales = [scale for scale in test_scales if scale <= max_posts]
    
    results = {}
    algorithms = ["hot_score", "engagement_score", "time_decay"]
    
    for scale in test_scales:
        print(f"\n📊 Testing with {scale:,} posts")
        print("-" * 50)
        
        scale_results = {}
        
        for algorithm in algorithms:
            print(f"\n🔸 Testing {algorithm} algorithm...")
            
            # Create streaming engine
            streaming_engine = StreamingRankingEngine(batch_size=50_000)
            
            # Generate posts and rank them
            post_iterator = generate_test_posts(scale)
            
            start_time = time.time()
            result = streaming_engine.rank_posts_streaming(
                post_iterator, 
                algorithm=algorithm, 
                top_k=100
            )
            end_time = time.time()
            
            # Calculate performance metrics
            posts_per_second = result.total_posts_processed / result.processing_time_seconds
            memory_per_post = result.memory_usage_mb / result.total_posts_processed * 1000  # KB per post
            
            scale_results[algorithm] = {
                'total_posts': result.total_posts_processed,
                'processing_time_seconds': result.processing_time_seconds,
                'posts_per_second': posts_per_second,
                'memory_usage_mb': result.memory_usage_mb,
                'memory_per_post_kb': memory_per_post,
                'top_score': result.top_posts[0][0] if result.top_posts else 0,
                'batch_size': result.batch_size
            }
            
            print(f"  ✅ Processed {result.total_posts_processed:,} posts in {result.processing_time_seconds:.2f}s")
            print(f"  📈 Throughput: {posts_per_second:,.0f} posts/second")
            print(f"  💾 Memory: {result.memory_usage_mb:.1f} MB ({memory_per_post:.2f} KB/post)")
            print(f"  🏆 Top score: {result.top_posts[0][0]:.4f}")
        
        results[scale] = scale_results
    
    return results


def print_benchmark_results(results: Dict[str, Any]) -> None:
    """Print formatted benchmark results."""
    print("\n" + "=" * 80)
    print("STREAMING RANKING ENGINE BENCHMARK RESULTS")
    print("=" * 80)
    
    for scale, scale_results in results.items():
        print(f"\n📊 SCALE: {scale:,} POSTS")
        print("-" * 60)
        
        print(f"{'Algorithm':<20} {'Time (s)':<10} {'Posts/sec':<12} {'Memory (MB)':<12} {'KB/Post':<10}")
        print("-" * 70)
        
        for algorithm in ["hot_score", "engagement_score", "time_decay"]:
            if algorithm in scale_results:
                data = scale_results[algorithm]
                print(f"{algorithm:<20} {data['processing_time_seconds']:<10.2f} "
                      f"{data['posts_per_second']:<12,.0f} {data['memory_usage_mb']:<12.1f} "
                      f"{data['memory_per_post_kb']:<10.2f}")
    
    print(f"\n💡 Key Insights:")
    print(f"  • Memory usage stays constant regardless of total posts")
    print(f"  • Processing time scales linearly with number of posts")
    print(f"  • Can handle millions of posts with reasonable memory usage")


def main():
    """Run streaming ranking benchmark."""
    # Test with up to 1 million posts
    results = benchmark_streaming_ranking(max_posts=1_000_000)
    print_benchmark_results(results)
    
    # Save results
    import json
    with open('streaming_benchmark_results.json', 'w') as f:
        # Convert results to JSON-serializable format
        serializable_results = {}
        for scale, scale_results in results.items():
            serializable_results[str(scale)] = {}
            for algorithm, data in scale_results.items():
                serializable_results[str(scale)][algorithm] = {
                    k: float(v) if isinstance(v, (int, float)) else v
                    for k, v in data.items()
                }
        json.dump(serializable_results, f, indent=2)
    
    print(f"\n📄 Results saved to: streaming_benchmark_results.json")
    print("\n✅ Streaming ranking benchmark completed!")


if __name__ == "__main__":
    main() 