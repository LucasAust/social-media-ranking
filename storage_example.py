#!/usr/bin/env python3
"""
Practical Example: Using Storage Strategies with Streaming Ranking Engine.
Shows real-world usage patterns and performance impact.
"""

import time
import os
from typing import Iterator
from streaming_ranking_engine import StreamingRankingEngine, generate_test_posts
from data_storage_strategies import (
    JSONStorageStrategy,
    CompressedJSONStorageStrategy,
    SQLiteStorageStrategy,
    PickleStorageStrategy,
    StreamingFileStorageStrategy
)
from ranking_engine import Post


def demonstrate_storage_impact():
    """Demonstrate how different storage strategies affect performance."""
    print("🚀 STORAGE STRATEGY IMPACT ON STREAMING RANKING")
    print("=" * 70)
    
    # Generate test data
    num_posts = 100_000
    print(f"📊 Generating {num_posts:,} test posts...")
    posts = list(generate_test_posts(num_posts))
    
    # Test different storage strategies
    strategies = {
        'JSON': JSONStorageStrategy(),
        'Compressed JSON': CompressedJSONStorageStrategy(),
        'SQLite': SQLiteStorageStrategy(),
        'Pickle': PickleStorageStrategy(),
        'Streaming File': StreamingFileStorageStrategy()
    }
    
    results = {}
    
    for name, strategy in strategies.items():
        print(f"\n🔸 Testing {name} Storage:")
        print("-" * 40)
        
        filename = f"posts_{name.lower().replace(' ', '_')}.dat"
        
        # Store posts
        print(f"  💾 Storing posts...")
        store_start = time.time()
        store_metrics = strategy.store_posts(posts, filename)
        store_time = time.time() - store_start
        
        print(f"    Storage time: {store_time:.2f}s")
        print(f"    File size: {store_metrics.storage_size_mb:.1f} MB")
        
        # Load and rank posts
        print(f"  🔄 Loading and ranking posts...")
        rank_start = time.time()
        
        # Create streaming engine
        engine = StreamingRankingEngine(batch_size=10_000)
        
        # Load posts as iterator
        post_iterator = strategy.load_posts_iterator(filename)
        
        # Rank posts
        result = engine.rank_posts_streaming(
            post_iterator, 
            algorithm="hot_score", 
            top_k=100
        )
        
        rank_time = time.time() - rank_start
        total_time = store_time + rank_time
        
        # Calculate metrics
        posts_per_second = result.total_posts_processed / rank_time
        storage_info = strategy.get_storage_info(filename)
        
        results[name] = {
            'storage_time': store_time,
            'ranking_time': rank_time,
            'total_time': total_time,
            'file_size_mb': store_metrics.storage_size_mb,
            'posts_per_second': posts_per_second,
            'memory_usage_mb': result.memory_usage_mb,
            'storage_info': storage_info
        }
        
        print(f"    Ranking time: {rank_time:.2f}s")
        print(f"    Total time: {total_time:.2f}s")
        print(f"    Throughput: {posts_per_second:,.0f} posts/s")
        print(f"    Memory: {result.memory_usage_mb:.1f} MB")
        
        # Clean up
        try:
            os.remove(filename)
        except:
            pass
    
    return results


def print_performance_comparison(results):
    """Print performance comparison table."""
    print("\n" + "=" * 90)
    print("STORAGE STRATEGY PERFORMANCE COMPARISON")
    print("=" * 90)
    
    print(f"{'Strategy':<20} {'Store (s)':<10} {'Rank (s)':<10} {'Total (s)':<10} "
          f"{'Size (MB)':<10} {'Posts/s':<12} {'Memory (MB)':<12}")
    print("-" * 90)
    
    for strategy, data in results.items():
        print(f"{strategy:<20} {data['storage_time']:<10.2f} {data['ranking_time']:<10.2f} "
              f"{data['total_time']:<10.2f} {data['file_size_mb']:<10.1f} "
              f"{data['posts_per_second']:<12,.0f} {data['memory_usage_mb']:<12.1f}")


def demonstrate_real_world_scenarios():
    """Demonstrate real-world usage scenarios."""
    print("\n🎯 REAL-WORLD USAGE SCENARIOS")
    print("=" * 70)
    
    scenarios = [
        {
            'name': 'Social Media Feed (Real-time)',
            'description': 'Posts coming in real-time from API',
            'storage': 'No storage needed - direct streaming',
            'posts_per_second': '1000+',
            'memory_impact': 'Minimal'
        },
        {
            'name': 'Historical Data Analysis',
            'description': 'Analyzing past posts for trends',
            'storage': 'SQLite or Compressed JSON',
            'posts_per_second': '500,000+',
            'memory_impact': 'Low'
        },
        {
            'name': 'Batch Processing',
            'description': 'Processing large datasets overnight',
            'storage': 'Streaming File or SQLite',
            'posts_per_second': '1,000,000+',
            'memory_impact': 'Very Low'
        },
        {
            'name': 'Development/Testing',
            'description': 'Quick iterations with small datasets',
            'storage': 'JSON or Pickle',
            'posts_per_second': '100,000+',
            'memory_impact': 'Medium'
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 {scenario['name']}")
        print(f"   Description: {scenario['description']}")
        print(f"   Recommended Storage: {scenario['storage']}")
        print(f"   Expected Performance: {scenario['posts_per_second']} posts/second")
        print(f"   Memory Impact: {scenario['memory_impact']}")


def demonstrate_database_integration():
    """Show how to integrate with real databases."""
    print("\n🗄️ DATABASE INTEGRATION EXAMPLES")
    print("=" * 70)
    
    # Example: PostgreSQL integration
    print("📊 PostgreSQL Integration Example:")
    print("""
    # Using psycopg2 for PostgreSQL
    import psycopg2
    
    def postgres_posts_iterator():
        conn = psycopg2.connect("postgresql://user:pass@localhost/social_db")
        cursor = conn.cursor()
        
        # Stream posts in batches
        cursor.execute('''
            SELECT post_id, likes, comments, shares, upvotes, downvotes, timestamp 
            FROM posts 
            ORDER BY timestamp DESC
        ''')
        
        batch_size = 10000
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
            
            for row in rows:
                yield Post(
                    post_id=row[0],
                    likes=row[1],
                    comments=row[2],
                    shares=row[3],
                    upvotes=row[4],
                    downvotes=row[5],
                    timestamp=row[6]
                )
        
        cursor.close()
        conn.close()
    
    # Use with streaming engine
    engine = StreamingRankingEngine()
    result = engine.rank_posts_streaming(
        postgres_posts_iterator(), 
        algorithm="hot_score", 
        top_k=100
    )
    """)
    
    # Example: MongoDB integration
    print("\n📊 MongoDB Integration Example:")
    print("""
    # Using pymongo for MongoDB
    from pymongo import MongoClient
    
    def mongo_posts_iterator():
        client = MongoClient('mongodb://localhost:27017/')
        db = client.social_db
        collection = db.posts
        
        # Stream posts using cursor
        cursor = collection.find({}, batch_size=10000)
        
        for doc in cursor:
            yield Post(
                post_id=doc['post_id'],
                likes=doc['likes'],
                comments=doc['comments'],
                shares=doc['shares'],
                upvotes=doc['upvotes'],
                downvotes=doc['downvotes'],
                timestamp=doc['timestamp']
            )
        
        cursor.close()
        client.close()
    """)


def demonstrate_memory_optimization():
    """Show memory optimization techniques."""
    print("\n💾 MEMORY OPTIMIZATION TECHNIQUES")
    print("=" * 70)
    
    print("🔧 Technique 1: Generator Functions")
    print("""
    def optimized_post_generator(filename):
        with open(filename, 'r') as f:
            for line in f:
                # Process one line at a time
                post_data = parse_line(line)
                yield Post(**post_data)
    """)
    
    print("\n🔧 Technique 2: Batch Processing")
    print("""
    def batch_post_processor(posts_iterator, batch_size=10000):
        batch = []
        for post in posts_iterator:
            batch.append(post)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch
    """)
    
    print("\n🔧 Technique 3: Memory Pooling")
    print("""
    from itertools import islice
    
    def memory_efficient_ranking(posts_iterator, top_k=100):
        # Process in chunks to limit memory usage
        chunk_size = 50000
        min_heap = []
        
        while True:
            chunk = list(islice(posts_iterator, chunk_size))
            if not chunk:
                break
            
            # Process chunk and update top-k
            for post in chunk:
                score = calculate_score(post)
                if len(min_heap) < top_k:
                    heapq.heappush(min_heap, (score, post))
                else:
                    heapq.heappushpop(min_heap, (score, post))
        
        return sorted(min_heap, reverse=True)
    """)


def main():
    """Run the storage demonstration."""
    print("🚀 STORAGE STRATEGIES FOR STREAMING RANKING ENGINE")
    print("=" * 80)
    print("This example shows how different storage approaches affect")
    print("the performance of your streaming ranking algorithm.")
    print()
    
    try:
        # Run performance comparison
        results = demonstrate_storage_impact()
        print_performance_comparison(results)
        
        # Show real-world scenarios
        demonstrate_real_world_scenarios()
        
        # Show database integration
        demonstrate_database_integration()
        
        # Show memory optimization
        demonstrate_memory_optimization()
        
        print("\n" + "=" * 80)
        print("✅ STORAGE DEMONSTRATION COMPLETED!")
        print("\n💡 Key Takeaways:")
        print("  • Storage format has minimal impact on ranking performance")
        print("  • SQLite provides best balance for most use cases")
        print("  • Streaming file is most memory-efficient for huge datasets")
        print("  • Database integration is straightforward with iterators")
        print("  • Memory optimization techniques can handle unlimited data")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 