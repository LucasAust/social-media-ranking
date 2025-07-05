#!/usr/bin/env python3
"""
Example usage of the Social Media Ranking System.
Demonstrates various scenarios and use cases.
"""

import time
import random
from ranking_engine import RankingEngine, OptimizedRankingEngine


def basic_usage_example():
    """Basic usage example with a few posts."""
    print("🔸 Basic Usage Example")
    print("-" * 40)
    
    # Initialize the ranking engine
    engine = RankingEngine()
    
    # Add some posts
    posts_data = [
        {'post_id': 'post_001', 'likes': 150, 'comments': 25, 'shares': 10, 'upvotes': 200, 'downvotes': 5, 'timestamp': time.time() - 3600},
        {'post_id': 'post_002', 'likes': 300, 'comments': 50, 'shares': 20, 'upvotes': 350, 'downvotes': 10, 'timestamp': time.time() - 7200},
        {'post_id': 'post_003', 'likes': 75, 'comments': 15, 'shares': 5, 'upvotes': 100, 'downvotes': 2, 'timestamp': time.time() - 1800},
        {'post_id': 'post_004', 'likes': 500, 'comments': 100, 'shares': 50, 'upvotes': 600, 'downvotes': 15, 'timestamp': time.time() - 10800},
        {'post_id': 'post_005', 'likes': 200, 'comments': 30, 'shares': 15, 'upvotes': 250, 'downvotes': 8, 'timestamp': time.time() - 5400},
    ]
    
    for post_data in posts_data:
        engine.add_post(**post_data)
    
    # Get rankings using different algorithms
    algorithms = ['hot_score', 'engagement_score', 'time_decay', 'hybrid']
    
    for algorithm in algorithms:
        print(f"\n📊 Rankings using {algorithm}:")
        ranked_posts = engine.get_ranked_posts(algorithm=algorithm, limit=5)
        
        for post in ranked_posts:
            print(f"  #{post['rank']}: {post['post_id']} - Score: {post['score']:.4f} "
                  f"(Likes: {post['likes']}, Comments: {post['comments']}, Age: {post['age_hours']:.1f}h)")
    
    # Update a post and see how rankings change
    print(f"\n🔄 Updating post_001 with more engagement...")
    engine.update_post('post_001', likes=300, comments=50, shares=25)
    
    print(f"\n📊 Updated rankings (hot_score):")
    updated_rankings = engine.get_ranked_posts(algorithm='hot_score', limit=5)
    for post in updated_rankings:
        print(f"  #{post['rank']}: {post['post_id']} - Score: {post['score']:.4f} "
              f"(Likes: {post['likes']}, Comments: {post['comments']})")
    
    # Get system statistics
    stats = engine.get_stats()
    print(f"\n📈 System Statistics:")
    print(f"  Total Posts: {stats['total_posts']}")
    print(f"  Total Likes: {stats['total_likes']}")
    print(f"  Total Comments: {stats['total_comments']}")
    print(f"  Memory Usage: {stats['memory_usage_mb']:.1f} MB")


def large_scale_example():
    """Example with a larger dataset to demonstrate performance."""
    print("\n🔸 Large Scale Example (10,000 posts)")
    print("-" * 50)
    
    # Use optimized engine for better performance
    engine = OptimizedRankingEngine()
    
    # Generate realistic test data
    print("Generating test data...")
    base_time = time.time() - (86400 * 7)  # 7 days ago
    
    posts_data = []
    for i in range(10000):
        likes = random.randint(0, 5000)
        comments = random.randint(0, likes // 10)
        shares = random.randint(0, likes // 20)
        upvotes = random.randint(0, likes)
        downvotes = random.randint(0, likes // 5)
        timestamp = base_time + random.random() * 86400 * 7
        
        posts_data.append({
            'post_id': f'post_{i:06d}',
            'likes': likes,
            'comments': comments,
            'shares': shares,
            'upvotes': upvotes,
            'downvotes': downvotes,
            'timestamp': timestamp
        })
    
    # Batch add posts
    print("Adding posts to ranking engine...")
    start_time = time.time()
    engine.batch_add_posts(posts_data)
    add_time = time.time() - start_time
    print(f"Added {len(posts_data):,} posts in {add_time:.2f} seconds")
    
    # Test different algorithms
    algorithms = ['hot_score', 'engagement_score', 'time_decay']
    
    for algorithm in algorithms:
        print(f"\n🏃 Testing {algorithm} algorithm...")
        start_time = time.time()
        ranked_posts = engine.get_ranked_posts(algorithm=algorithm, limit=20)
        ranking_time = time.time() - start_time
        
        print(f"Ranking time: {ranking_time * 1000:.2f}ms")
        print(f"Top 5 posts:")
        
        for i, post in enumerate(ranked_posts[:5], 1):
            print(f"  {i}. {post['post_id']} - Score: {post['score']:.4f} "
                  f"(Likes: {post['likes']}, Age: {post['age_hours']:.1f}h)")
    
    # Test update performance
    print(f"\n⚡ Testing update performance...")
    update_times = []
    for _ in range(100):
        post_id = f'post_{random.randint(0, 9999):06d}'
        start_time = time.time()
        engine.update_post(post_id, likes=random.randint(0, 1000))
        update_time = time.time() - start_time
        update_times.append(update_time)
    
    avg_update_time = sum(update_times) / len(update_times)
    print(f"Average update time: {avg_update_time * 1000:.2f}ms")
    
    # Get final statistics
    stats = engine.get_stats()
    print(f"\n📊 Final Statistics:")
    print(f"  Total Posts: {stats['total_posts']:,}")
    print(f"  Memory Usage: {stats['memory_usage_mb']:.1f} MB")
    print(f"  Average Likes per Post: {stats['avg_likes_per_post']:.1f}")


def real_time_updates_example():
    """Example demonstrating real-time updates and ranking changes."""
    print("\n🔸 Real-time Updates Example")
    print("-" * 40)
    
    engine = RankingEngine()
    
    # Add some posts
    current_time = time.time()
    posts_data = [
        {'post_id': 'viral_post', 'likes': 100, 'comments': 20, 'shares': 5, 'timestamp': current_time - 3600},
        {'post_id': 'trending_post', 'likes': 200, 'comments': 40, 'shares': 15, 'timestamp': current_time - 7200},
        {'post_id': 'new_post', 'likes': 50, 'comments': 10, 'shares': 2, 'timestamp': current_time - 1800},
    ]
    
    for post_data in posts_data:
        engine.add_post(**post_data)
    
    print("Initial rankings:")
    initial_rankings = engine.get_ranked_posts(algorithm='hot_score', limit=3)
    for post in initial_rankings:
        print(f"  #{post['rank']}: {post['post_id']} - Score: {post['score']:.4f}")
    
    # Simulate viral growth
    print(f"\n🚀 Simulating viral growth for 'viral_post'...")
    
    for i in range(5):
        # Simulate rapid engagement increase
        current_likes = engine.posts['viral_post'].likes
        new_likes = current_likes + random.randint(50, 200)
        new_comments = engine.posts['viral_post'].comments + random.randint(10, 30)
        new_shares = engine.posts['viral_post'].shares + random.randint(5, 15)
        
        engine.update_post('viral_post', likes=new_likes, comments=new_comments, shares=new_shares)
        
        # Get updated rankings
        updated_rankings = engine.get_ranked_posts(algorithm='hot_score', limit=3)
        
        print(f"\nUpdate {i+1}:")
        for post in updated_rankings:
            print(f"  #{post['rank']}: {post['post_id']} - Score: {post['score']:.4f} "
                  f"(Likes: {post['likes']}, Comments: {post['comments']})")
        
        time.sleep(0.1)  # Small delay to simulate real-time updates


def algorithm_comparison_example():
    """Compare different ranking algorithms with the same dataset."""
    print("\n🔸 Algorithm Comparison Example")
    print("-" * 45)
    
    engine = RankingEngine()
    
    # Create posts with different characteristics
    current_time = time.time()
    posts_data = [
        # High engagement, recent
        {'post_id': 'recent_viral', 'likes': 1000, 'comments': 200, 'shares': 100, 'timestamp': current_time - 1800},
        # High engagement, older
        {'post_id': 'old_viral', 'likes': 2000, 'comments': 400, 'shares': 200, 'timestamp': current_time - 86400},
        # Low engagement, recent
        {'post_id': 'recent_quiet', 'likes': 10, 'comments': 2, 'shares': 1, 'timestamp': current_time - 900},
        # Medium engagement, medium age
        {'post_id': 'medium_post', 'likes': 500, 'comments': 100, 'shares': 50, 'timestamp': current_time - 43200},
    ]
    
    for post_data in posts_data:
        engine.add_post(**post_data)
    
    # Compare algorithms
    algorithms = {
        'hot_score': 'Reddit-style hot score',
        'engagement_score': 'Engagement-based ranking',
        'time_decay': 'Time-decay ranking',
        'hybrid': 'Hybrid multi-factor'
    }
    
    for algorithm, description in algorithms.items():
        print(f"\n📊 {description} ({algorithm}):")
        ranked_posts = engine.get_ranked_posts(algorithm=algorithm, limit=4)
        
        for post in ranked_posts:
            print(f"  #{post['rank']}: {post['post_id']} - Score: {post['score']:.4f} "
                  f"(Age: {post['age_hours']:.1f}h, Likes: {post['likes']})")


def main():
    """Run all examples."""
    print("🎯 Social Media Ranking System - Example Usage")
    print("=" * 60)
    
    # Run examples
    basic_usage_example()
    large_scale_example()
    real_time_updates_example()
    algorithm_comparison_example()
    
    print("\n✅ All examples completed!")
    print("\n💡 Tips:")
    print("  - Use OptimizedRankingEngine for datasets >10k posts")
    print("  - Cache rankings for frequently accessed results")
    print("  - Batch updates when possible for better performance")
    print("  - Monitor memory usage for very large datasets")


if __name__ == "__main__":
    main() 