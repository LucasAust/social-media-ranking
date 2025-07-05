#!/usr/bin/env python3
"""
Quick Start Guide for the Social Media Ranking System.
Run this script to see the system in action immediately.
"""

from ranking_engine import RankingEngine
import time


def quick_demo():
    """Quick demonstration of the ranking system."""
    print("🚀 Social Media Ranking System - Quick Start")
    print("=" * 50)
    
    # Create ranking engine
    engine = RankingEngine()
    
    # Add some sample posts
    print("\n📝 Adding sample posts...")
    
    current_time = time.time()
    sample_posts = [
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
        }
    ]
    
    for post_data in sample_posts:
        engine.add_post(**post_data)
        print(f"  ✅ Added: {post_data['post_id']} ({post_data['likes']} likes)")
    
    # Show rankings with different algorithms
    print("\n📊 Ranking Results:")
    print("-" * 30)
    
    algorithms = ['hot_score', 'engagement_score', 'time_decay']
    
    for algorithm in algorithms:
        print(f"\n🔸 {algorithm.replace('_', ' ').title()}:")
        ranked_posts = engine.get_ranked_posts(algorithm=algorithm, limit=3)
        
        for post in ranked_posts:
            print(f"  #{post['rank']}: {post['post_id']} - Score: {post['score']:.4f}")
    
    # Demonstrate real-time update
    print(f"\n🔄 Real-time Update Demo:")
    print("Updating 'recipe_shared' with more engagement...")
    
    engine.update_post('recipe_shared', 
                      likes=50000, 
                      comments=2500, 
                      shares=8000)
    
    print("Updated rankings (hot_score):")
    updated_rankings = engine.get_ranked_posts(algorithm='hot_score', limit=3)
    for post in updated_rankings:
        print(f"  #{post['rank']}: {post['post_id']} - Score: {post['score']:.4f}")
    
    # Show system stats
    stats = engine.get_stats()
    print(f"\n📈 System Statistics:")
    print(f"  Total Posts: {stats['total_posts']}")
    print(f"  Total Likes: {stats['total_likes']:,}")
    print(f"  Memory Usage: {stats['memory_usage_mb']:.1f} MB")
    
    print(f"\n✅ Quick start completed!")
    print(f"\n💡 Next steps:")
    print(f"  • Run 'python demo.py' for a comprehensive demo")
    print(f"  • Run 'python performance_test.py' for performance testing")
    print(f"  • Check 'example_usage.py' for more examples")
    print(f"  • Read the README.md for detailed documentation")


if __name__ == "__main__":
    quick_demo() 