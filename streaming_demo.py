#!/usr/bin/env python3
"""
Demo script for the Streaming Ranking Engine.
Shows how to process any number of posts with constant memory usage.
"""

import time
import sys
from streaming_ranking_engine import (
    StreamingRankingEngine,
    generate_test_posts,
    benchmark_streaming_ranking
)


def demo_small_scale():
    """Demo with a small number of posts."""
    print("🎯 DEMO 1: Small Scale (1,000 posts)")
    print("=" * 50)
    
    engine = StreamingRankingEngine(batch_size=100)
    post_iterator = generate_test_posts(1000)
    
    start_time = time.time()
    result = engine.rank_posts_streaming(post_iterator, algorithm="hot_score", top_k=10)
    end_time = time.time()
    
    print(f"✅ Processed {result.total_posts_processed:,} posts in {result.processing_time_seconds:.3f}s")
    print(f"📈 Throughput: {result.total_posts_processed / result.processing_time_seconds:,.0f} posts/second")
    print(f"💾 Memory usage: {result.memory_usage_mb:.1f} MB")
    print(f"🔝 Top 3 posts:")
    
    for i, (score, post) in enumerate(result.top_posts[:3], 1):
        print(f"  {i}. Post {post.post_id}: Score {score:.4f} "
              f"(Likes: {post.likes}, Comments: {post.comments}, Shares: {post.shares})")


def demo_medium_scale():
    """Demo with a medium number of posts."""
    print("\n🎯 DEMO 2: Medium Scale (100,000 posts)")
    print("=" * 50)
    
    engine = StreamingRankingEngine(batch_size=10_000)
    post_iterator = generate_test_posts(100_000)
    
    start_time = time.time()
    result = engine.rank_posts_streaming(post_iterator, algorithm="engagement_score", top_k=20)
    end_time = time.time()
    
    print(f"✅ Processed {result.total_posts_processed:,} posts in {result.processing_time_seconds:.2f}s")
    print(f"📈 Throughput: {result.total_posts_processed / result.processing_time_seconds:,.0f} posts/second")
    print(f"💾 Memory usage: {result.memory_usage_mb:.1f} MB")
    print(f"🔝 Top 5 posts:")
    
    for i, (score, post) in enumerate(result.top_posts[:5], 1):
        print(f"  {i}. Post {post.post_id}: Score {score:.4f} "
              f"(Likes: {post.likes}, Comments: {post.comments}, Shares: {post.shares})")


def demo_large_scale():
    """Demo with a large number of posts."""
    print("\n🎯 DEMO 3: Large Scale (1,000,000 posts)")
    print("=" * 50)
    
    engine = StreamingRankingEngine(batch_size=50_000)
    post_iterator = generate_test_posts(1_000_000)
    
    start_time = time.time()
    result = engine.rank_posts_streaming(post_iterator, algorithm="time_decay", top_k=50)
    end_time = time.time()
    
    print(f"✅ Processed {result.total_posts_processed:,} posts in {result.processing_time_seconds:.2f}s")
    print(f"📈 Throughput: {result.total_posts_processed / result.processing_time_seconds:,.0f} posts/second")
    print(f"💾 Memory usage: {result.memory_usage_mb:.1f} MB")
    print(f"🔝 Top 10 posts:")
    
    for i, (score, post) in enumerate(result.top_posts[:10], 1):
        print(f"  {i}. Post {post.post_id}: Score {score:.4f} "
              f"(Likes: {post.likes}, Comments: {post.comments}, Shares: {post.shares})")


def demo_memory_comparison():
    """Demo comparing memory usage between streaming and non-streaming approaches."""
    print("\n🎯 DEMO 4: Memory Usage Comparison")
    print("=" * 50)
    
    # Test different scales
    scales = [10_000, 100_000, 500_000]
    
    for scale in scales:
        print(f"\n📊 Testing with {scale:,} posts:")
        
        # Streaming approach
        engine = StreamingRankingEngine(batch_size=10_000)
        post_iterator = generate_test_posts(scale)
        
        result = engine.rank_posts_streaming(post_iterator, algorithm="hot_score", top_k=100)
        
        memory_per_post_kb = result.memory_usage_mb / result.total_posts_processed * 1000
        
        print(f"  💾 Streaming Memory: {result.memory_usage_mb:.1f} MB ({memory_per_post_kb:.3f} KB/post)")
        print(f"  ⚡ Processing Time: {result.processing_time_seconds:.2f}s")
        print(f"  📈 Throughput: {result.total_posts_processed / result.processing_time_seconds:,.0f} posts/second")


def demo_different_algorithms():
    """Demo different ranking algorithms with streaming."""
    print("\n🎯 DEMO 5: Different Ranking Algorithms")
    print("=" * 50)
    
    engine = StreamingRankingEngine(batch_size=5_000)
    post_iterator = generate_test_posts(50_000)
    
    algorithms = [
        ("hot_score", "Hot Score"),
        ("engagement_score", "Engagement Score"),
        ("time_decay", "Time Decay")
    ]
    
    for algorithm, name in algorithms:
        print(f"\n🔸 {name} Algorithm:")
        
        # Reset iterator for each algorithm
        post_iterator = generate_test_posts(50_000)
        
        result = engine.rank_posts_streaming(post_iterator, algorithm=algorithm, top_k=10)
        
        print(f"  ✅ Processed {result.total_posts_processed:,} posts in {result.processing_time_seconds:.2f}s")
        print(f"  📈 Throughput: {result.total_posts_processed / result.processing_time_seconds:,.0f} posts/second")
        print(f"  💾 Memory: {result.memory_usage_mb:.1f} MB")
        print(f"  🏆 Top score: {result.top_posts[0][0]:.4f}")


def demo_custom_batch_sizes():
    """Demo different batch sizes and their impact."""
    print("\n🎯 DEMO 6: Batch Size Impact")
    print("=" * 50)
    
    batch_sizes = [1_000, 10_000, 50_000, 100_000]
    test_posts = 100_000
    
    for batch_size in batch_sizes:
        print(f"\n📦 Batch Size: {batch_size:,}")
        
        engine = StreamingRankingEngine(batch_size=batch_size)
        post_iterator = generate_test_posts(test_posts)
        
        result = engine.rank_posts_streaming(post_iterator, algorithm="hot_score", top_k=100)
        
        print(f"  ✅ Processed {result.total_posts_processed:,} posts in {result.processing_time_seconds:.2f}s")
        print(f"  📈 Throughput: {result.total_posts_processed / result.processing_time_seconds:,.0f} posts/second")
        print(f"  💾 Memory: {result.memory_usage_mb:.1f} MB")


def main():
    """Run all demos."""
    print("🚀 STREAMING RANKING ENGINE DEMO")
    print("=" * 60)
    print("This demo shows how the streaming ranking engine can handle")
    print("any number of posts with constant memory usage.")
    print()
    
    try:
        # Run demos
        demo_small_scale()
        demo_medium_scale()
        demo_large_scale()
        demo_memory_comparison()
        demo_different_algorithms()
        demo_custom_batch_sizes()
        
        print("\n" + "=" * 60)
        print("✅ All demos completed successfully!")
        print("\n💡 Key Benefits of Streaming Ranking:")
        print("  • Constant memory usage regardless of total posts")
        print("  • Can handle millions of posts efficiently")
        print("  • Real-time processing with minimal latency")
        print("  • Scalable to distributed systems")
        print("  • Suitable for production social media applications")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 