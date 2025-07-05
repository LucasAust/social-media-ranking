#!/usr/bin/env python3
"""
Simple demo of the Social Media Ranking System.
Shows the system in action with a small, realistic dataset.
"""

import time
import random
from ranking_engine import RankingEngine


def create_sample_posts():
    """Create a realistic sample of social media posts."""
    current_time = time.time()
    
    posts = [
        {
            'post_id': 'viral_cat_video',
            'likes': 15420,
            'comments': 892,
            'shares': 2341,
            'upvotes': 16500,
            'downvotes': 80,
            'timestamp': current_time - 3600  # 1 hour ago
        },
        {
            'post_id': 'tech_news_ai',
            'likes': 3240,
            'comments': 156,
            'shares': 89,
            'upvotes': 3400,
            'downvotes': 160,
            'timestamp': current_time - 7200  # 2 hours ago
        },
        {
            'post_id': 'recipe_shared',
            'likes': 567,
            'comments': 45,
            'shares': 23,
            'upvotes': 600,
            'downvotes': 33,
            'timestamp': current_time - 1800  # 30 minutes ago
        },
        {
            'post_id': 'old_viral_post',
            'likes': 25000,
            'comments': 1200,
            'shares': 5000,
            'upvotes': 27000,
            'downvotes': 2000,
            'timestamp': current_time - 86400 * 7  # 7 days ago
        },
        {
            'post_id': 'quiet_post',
            'likes': 12,
            'comments': 2,
            'shares': 1,
            'upvotes': 15,
            'downvotes': 3,
            'timestamp': current_time - 900  # 15 minutes ago
        },
        {
            'post_id': 'controversial_topic',
            'likes': 800,
            'comments': 450,
            'shares': 120,
            'upvotes': 1200,
            'downvotes': 400,
            'timestamp': current_time - 5400  # 1.5 hours ago
        }
    ]
    
    return posts


def demo_basic_ranking():
    """Demonstrate basic ranking functionality."""
    print("🎯 Social Media Ranking System - Demo")
    print("=" * 50)
    
    # Initialize the ranking engine
    engine = RankingEngine()
    
    # Add sample posts
    print("\n📝 Adding sample posts...")
    posts = create_sample_posts()
    
    for post_data in posts:
        engine.add_post(**post_data)
        print(f"  Added: {post_data['post_id']} ({post_data['likes']} likes)")
    
    # Show rankings with different algorithms
    algorithms = {
        'hot_score': 'Reddit-style Hot Score',
        'engagement_score': 'Engagement-based Ranking',
        'time_decay': 'Time-Decay Ranking',
        'hybrid': 'Hybrid Multi-Factor'
    }
    
    for algorithm, description in algorithms.items():
        print(f"\n📊 {description}")
        print("-" * 40)
        
        ranked_posts = engine.get_ranked_posts(algorithm=algorithm, limit=6)
        
        for post in ranked_posts:
            age_hours = post['age_hours']
            print(f"  #{post['rank']}: {post['post_id']}")
            print(f"      Score: {post['score']:.4f}")
            print(f"      Likes: {post['likes']}, Comments: {post['comments']}, Shares: {post['shares']}")
            print(f"      Age: {age_hours:.1f} hours")
            print()


def demo_real_time_updates():
    """Demonstrate real-time updates and ranking changes."""
    print("\n🔄 Real-Time Updates Demo")
    print("=" * 40)
    
    engine = RankingEngine()
    
    # Add a few posts
    posts = create_sample_posts()[:3]  # Just first 3 posts
    for post_data in posts:
        engine.add_post(**post_data)
    
    print("Initial rankings (hot_score):")
    initial_rankings = engine.get_ranked_posts(algorithm='hot_score', limit=3)
    for post in initial_rankings:
        print(f"  #{post['rank']}: {post['post_id']} - Score: {post['score']:.4f}")
    
    # Simulate viral growth
    print(f"\n🚀 Simulating viral growth for 'recipe_shared'...")
    
    # Update the recipe post with massive engagement
    engine.update_post('recipe_shared', 
                      likes=50000, 
                      comments=2500, 
                      shares=8000,
                      upvotes=55000,
                      downvotes=500)
    
    print("Updated rankings (hot_score):")
    updated_rankings = engine.get_ranked_posts(algorithm='hot_score', limit=3)
    for post in updated_rankings:
        print(f"  #{post['rank']}: {post['post_id']} - Score: {post['score']:.4f}")
    
    # Show how different algorithms react
    print(f"\n📈 How different algorithms react to the viral post:")
    
    for algorithm in ['hot_score', 'engagement_score', 'time_decay']:
        rankings = engine.get_ranked_posts(algorithm=algorithm, limit=3)
        top_post = rankings[0]
        print(f"  {algorithm}: #{top_post['rank']} {top_post['post_id']} (Score: {top_post['score']:.4f})")


def demo_algorithm_differences():
    """Show how different algorithms prioritize content differently."""
    print("\n🔍 Algorithm Comparison Demo")
    print("=" * 40)
    
    engine = RankingEngine()
    
    # Create posts with different characteristics
    current_time = time.time()
    
    test_posts = [
        {
            'post_id': 'recent_high_engagement',
            'likes': 1000,
            'comments': 100,
            'shares': 50,
            'timestamp': current_time - 1800  # 30 minutes ago
        },
        {
            'post_id': 'old_high_engagement',
            'likes': 2000,
            'comments': 200,
            'shares': 100,
            'timestamp': current_time - 86400 * 5  # 5 days ago
        },
        {
            'post_id': 'recent_low_engagement',
            'likes': 50,
            'comments': 5,
            'shares': 2,
            'timestamp': current_time - 900  # 15 minutes ago
        }
    ]
    
    for post_data in test_posts:
        engine.add_post(**post_data)
    
    algorithms = ['hot_score', 'engagement_score', 'time_decay']
    
    print("How different algorithms rank the same posts:")
    print(f"{'Algorithm':<20} {'#1':<25} {'#2':<25} {'#3':<25}")
    print("-" * 80)
    
    for algorithm in algorithms:
        rankings = engine.get_ranked_posts(algorithm=algorithm, limit=3)
        row = f"{algorithm:<20}"
        for post in rankings:
            row += f"{post['post_id']:<25}"
        print(row)
    
    print(f"\n💡 Key Differences:")
    print(f"  • Hot Score: Balances engagement and recency")
    print(f"  • Engagement Score: Prioritizes total engagement")
    print(f"  • Time Decay: Favors recent content heavily")


def demo_performance():
    """Demonstrate performance with a larger dataset."""
    print("\n⚡ Performance Demo")
    print("=" * 30)
    
    from ranking_engine import OptimizedRankingEngine
    
    # Use optimized engine for better performance
    engine = OptimizedRankingEngine()
    
    # Generate larger dataset
    print("Generating 1,000 posts...")
    posts_data = []
    current_time = time.time()
    
    for i in range(1000):
        likes = random.randint(0, 5000)
        comments = random.randint(0, likes // 10)
        shares = random.randint(0, likes // 20)
        timestamp = current_time - random.randint(0, 86400 * 7)  # Random time in last week
        
        posts_data.append({
            'post_id': f'post_{i:06d}',
            'likes': likes,
            'comments': comments,
            'shares': shares,
            'upvotes': likes + random.randint(-100, 100),
            'downvotes': random.randint(0, likes // 10),
            'timestamp': timestamp
        })
    
    # Measure performance
    print("Adding posts...")
    start_time = time.time()
    engine.batch_add_posts(posts_data)
    add_time = time.time() - start_time
    
    print("Generating rankings...")
    start_time = time.time()
    rankings = engine.get_ranked_posts(algorithm='hot_score', limit=100)
    ranking_time = time.time() - start_time
    
    # Show results
    print(f"\n📊 Performance Results:")
    print(f"  Posts added: {len(posts_data):,}")
    print(f"  Add time: {add_time:.3f} seconds")
    print(f"  Add rate: {len(posts_data) / add_time:.0f} posts/second")
    print(f"  Ranking time: {ranking_time * 1000:.2f} milliseconds")
    print(f"  Memory usage: {engine.get_stats()['memory_usage_mb']:.1f} MB")
    
    print(f"\n🏆 Top 5 Posts:")
    for i, post in enumerate(rankings[:5], 1):
        print(f"  {i}. {post['post_id']} - Score: {post['score']:.4f} "
              f"(Likes: {post['likes']}, Age: {post['age_hours']:.1f}h)")


def main():
    """Run all demos."""
    print("🎬 Social Media Ranking System - Interactive Demo")
    print("=" * 60)
    
    # Run demos
    demo_basic_ranking()
    demo_real_time_updates()
    demo_algorithm_differences()
    demo_performance()
    
    print("\n✅ Demo completed!")
    print("\n🚀 Ready to use in your social media app!")
    print("   - Handle 100k+ posts efficiently")
    print("   - Real-time ranking updates")
    print("   - Multiple ranking algorithms")
    print("   - Sub-100ms response times")


if __name__ == "__main__":
    main() 