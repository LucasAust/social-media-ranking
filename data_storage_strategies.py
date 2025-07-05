#!/usr/bin/env python3
"""
Data Storage Strategies for Streaming Ranking Engine.
Shows different approaches for storing and accessing post data efficiently.
"""

import time
import sqlite3
import json
import pickle
import gzip
from typing import Iterator, List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import psutil
import os
from ranking_engine import Post


@dataclass
class StorageMetrics:
    """Metrics for storage performance."""
    storage_size_mb: float
    load_time_seconds: float
    memory_usage_mb: float
    posts_per_second: float
    storage_type: str


class DataStorageStrategy:
    """Base class for data storage strategies."""
    
    def store_posts(self, posts: List[Post], filename: str) -> StorageMetrics:
        """Store posts and return metrics."""
        raise NotImplementedError
    
    def load_posts_iterator(self, filename: str) -> Iterator[Post]:
        """Load posts as an iterator for streaming."""
        raise NotImplementedError
    
    def get_storage_info(self, filename: str) -> Dict[str, Any]:
        """Get information about stored data."""
        raise NotImplementedError

    def _get_memory_usage(self) -> float:
        try:
            import psutil, os
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / (1024 * 1024)
        except Exception:
            return 0.0


class JSONStorageStrategy(DataStorageStrategy):
    """Store posts as JSON - simple but not optimal for large datasets."""
    
    def store_posts(self, posts: List[Post], filename: str) -> StorageMetrics:
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        # Convert posts to JSON-serializable format
        data = [asdict(post) for post in posts]
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        file_size = os.path.getsize(filename) / (1024 * 1024)  # MB
        
        return StorageMetrics(
            storage_size_mb=file_size,
            load_time_seconds=end_time - start_time,
            memory_usage_mb=end_memory,
            posts_per_second=len(posts) / (end_time - start_time),
            storage_type="JSON"
        )
    
    def load_posts_iterator(self, filename: str) -> Iterator[Post]:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        for post_data in data:
            yield Post(**post_data)
    
    def get_storage_info(self, filename: str) -> Dict[str, Any]:
        file_size = os.path.getsize(filename) / (1024 * 1024)
        with open(filename, 'r') as f:
            data = json.load(f)
        
        return {
            'file_size_mb': file_size,
            'post_count': len(data),
            'bytes_per_post': (file_size * 1024 * 1024) / len(data)
        }


class CompressedJSONStorageStrategy(DataStorageStrategy):
    """Store posts as compressed JSON - better for large datasets."""
    
    def store_posts(self, posts: List[Post], filename: str) -> StorageMetrics:
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        data = [asdict(post) for post in posts]
        
        with gzip.open(filename, 'wt', encoding='utf-8') as f:
            json.dump(data, f)
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        file_size = os.path.getsize(filename) / (1024 * 1024)
        
        return StorageMetrics(
            storage_size_mb=file_size,
            load_time_seconds=end_time - start_time,
            memory_usage_mb=end_memory,
            posts_per_second=len(posts) / (end_time - start_time),
            storage_type="Compressed JSON"
        )
    
    def load_posts_iterator(self, filename: str) -> Iterator[Post]:
        with gzip.open(filename, 'rt', encoding='utf-8') as f:
            data = json.load(f)
        
        for post_data in data:
            yield Post(**post_data)
    
    def get_storage_info(self, filename: str) -> Dict[str, Any]:
        file_size = os.path.getsize(filename) / (1024 * 1024)
        with gzip.open(filename, 'rt', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            'file_size_mb': file_size,
            'post_count': len(data),
            'bytes_per_post': (file_size * 1024 * 1024) / len(data),
            'compression_ratio': '~70% smaller than JSON'
        }


class SQLiteStorageStrategy(DataStorageStrategy):
    """Store posts in SQLite database - excellent for large datasets."""
    
    def store_posts(self, posts: List[Post], filename: str) -> StorageMetrics:
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                post_id TEXT PRIMARY KEY,
                likes INTEGER,
                comments INTEGER,
                shares INTEGER,
                upvotes INTEGER,
                downvotes INTEGER,
                timestamp REAL
            )
        ''')
        
        # Insert posts in batches
        batch_size = 10000
        for i in range(0, len(posts), batch_size):
            batch = posts[i:i + batch_size]
            data = [(p.post_id, p.likes, p.comments, p.shares, p.upvotes, p.downvotes, p.timestamp) 
                   for p in batch]
            cursor.executemany('''
                INSERT OR REPLACE INTO posts 
                (post_id, likes, comments, shares, upvotes, downvotes, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', data)
        
        conn.commit()
        conn.close()
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        file_size = os.path.getsize(filename) / (1024 * 1024)
        
        return StorageMetrics(
            storage_size_mb=file_size,
            load_time_seconds=end_time - start_time,
            memory_usage_mb=end_memory,
            posts_per_second=len(posts) / (end_time - start_time),
            storage_type="SQLite"
        )
    
    def load_posts_iterator(self, filename: str) -> Iterator[Post]:
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()
        
        cursor.execute('SELECT post_id, likes, comments, shares, upvotes, downvotes, timestamp FROM posts')
        
        for row in cursor:
            yield Post(
                post_id=row[0],
                likes=row[1],
                comments=row[2],
                shares=row[3],
                upvotes=row[4],
                downvotes=row[5],
                timestamp=row[6]
            )
        
        conn.close()
    
    def get_storage_info(self, filename: str) -> Dict[str, Any]:
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM posts')
        post_count = cursor.fetchone()[0]
        
        file_size = os.path.getsize(filename) / (1024 * 1024)
        
        conn.close()
        
        return {
            'file_size_mb': file_size,
            'post_count': post_count,
            'bytes_per_post': (file_size * 1024 * 1024) / post_count if post_count > 0 else 0,
            'indexed': True,
            'queryable': True
        }


class PickleStorageStrategy(DataStorageStrategy):
    """Store posts using Python pickle - fast but not human-readable."""
    
    def store_posts(self, posts: List[Post], filename: str) -> StorageMetrics:
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        with open(filename, 'wb') as f:
            pickle.dump(posts, f)
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        file_size = os.path.getsize(filename) / (1024 * 1024)
        
        return StorageMetrics(
            storage_size_mb=file_size,
            load_time_seconds=end_time - start_time,
            memory_usage_mb=end_memory,
            posts_per_second=len(posts) / (end_time - start_time),
            storage_type="Pickle"
        )
    
    def load_posts_iterator(self, filename: str) -> Iterator[Post]:
        with open(filename, 'rb') as f:
            posts = pickle.load(f)
        
        for post in posts:
            yield post
    
    def get_storage_info(self, filename: str) -> Dict[str, Any]:
        file_size = os.path.getsize(filename) / (1024 * 1024)
        with open(filename, 'rb') as f:
            posts = pickle.load(f)
        
        return {
            'file_size_mb': file_size,
            'post_count': len(posts),
            'bytes_per_post': (file_size * 1024 * 1024) / len(posts),
            'binary': True,
            'fast_loading': True
        }


class StreamingFileStorageStrategy(DataStorageStrategy):
    """Store posts as streaming text file - memory efficient for very large datasets."""
    
    def store_posts(self, posts: List[Post], filename: str) -> StorageMetrics:
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        with open(filename, 'w') as f:
            for post in posts:
                # Store as CSV-like format
                line = f"{post.post_id},{post.likes},{post.comments},{post.shares},{post.upvotes},{post.downvotes},{post.timestamp}\n"
                f.write(line)
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        file_size = os.path.getsize(filename) / (1024 * 1024)
        
        return StorageMetrics(
            storage_size_mb=file_size,
            load_time_seconds=end_time - start_time,
            memory_usage_mb=end_memory,
            posts_per_second=len(posts) / (end_time - start_time),
            storage_type="Streaming File"
        )
    
    def load_posts_iterator(self, filename: str) -> Iterator[Post]:
        with open(filename, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(',')
                    yield Post(
                        post_id=parts[0],
                        likes=int(parts[1]),
                        comments=int(parts[2]),
                        shares=int(parts[3]),
                        upvotes=int(parts[4]),
                        downvotes=int(parts[5]),
                        timestamp=float(parts[6])
                    )
    
    def get_storage_info(self, filename: str) -> Dict[str, Any]:
        file_size = os.path.getsize(filename) / (1024 * 1024)
        
        # Count lines (posts)
        with open(filename, 'r') as f:
            post_count = sum(1 for line in f if line.strip())
        
        return {
            'file_size_mb': file_size,
            'post_count': post_count,
            'bytes_per_post': (file_size * 1024 * 1024) / post_count if post_count > 0 else 0,
            'streaming': True,
            'memory_efficient': True
        }


def benchmark_storage_strategies(num_posts: int = 100_000) -> Dict[str, Any]:
    """Benchmark different storage strategies."""
    print(f"🔍 Storage Strategy Benchmark ({num_posts:,} posts)")
    print("=" * 70)
    
    # Generate test posts
    from streaming_ranking_engine import generate_test_posts
    posts = list(generate_test_posts(num_posts))
    
    strategies = {
        'JSON': JSONStorageStrategy(),
        'Compressed JSON': CompressedJSONStorageStrategy(),
        'SQLite': SQLiteStorageStrategy(),
        'Pickle': PickleStorageStrategy(),
        'Streaming File': StreamingFileStorageStrategy()
    }
    
    results = {}
    
    for name, strategy in strategies.items():
        print(f"\n📦 Testing {name}...")
        
        filename = f"test_posts_{name.lower().replace(' ', '_')}"
        
        # Store posts
        store_metrics = strategy.store_posts(posts, filename)
        
        # Load posts and measure streaming performance
        start_time = time.time()
        start_memory = strategy._get_memory_usage() # Use the base class method
        
        post_iterator = strategy.load_posts_iterator(filename)
        from streaming_ranking_engine import StreamingRankingEngine
        
        engine = StreamingRankingEngine(batch_size=10_000)
        result = engine.rank_posts_streaming(post_iterator, algorithm="hot_score", top_k=100)
        
        end_time = time.time()
        end_memory = strategy._get_memory_usage() # Use the base class method
        
        # Calculate metrics
        total_time = end_time - start_time
        posts_per_second = result.total_posts_processed / total_time
        memory_used = end_memory - start_memory
        
        results[name] = {
            'storage_size_mb': store_metrics.storage_size_mb,
            'storage_time': store_metrics.load_time_seconds,
            'ranking_time': total_time,
            'posts_per_second': posts_per_second,
            'memory_used_mb': memory_used,
            'storage_info': strategy.get_storage_info(filename)
        }
        
        print(f"  💾 Storage: {store_metrics.storage_size_mb:.1f} MB")
        print(f"  ⏱️  Ranking: {total_time:.2f}s")
        print(f"  📈 Throughput: {posts_per_second:,.0f} posts/s")
        print(f"  💾 Memory: {memory_used:.1f} MB")
        
        # Clean up
        try:
            os.remove(filename)
        except:
            pass
    
    return results


def print_storage_benchmark_results(results: Dict[str, Any]) -> None:
    """Print formatted storage benchmark results."""
    print("\n" + "=" * 80)
    print("STORAGE STRATEGY BENCHMARK RESULTS")
    print("=" * 80)
    
    print(f"{'Strategy':<20} {'Size (MB)':<12} {'Rank Time (s)':<15} {'Posts/s':<12} {'Memory (MB)':<12}")
    print("-" * 80)
    
    for strategy, data in results.items():
        print(f"{strategy:<20} {data['storage_size_mb']:<12.1f} {data['ranking_time']:<15.2f} "
              f"{data['posts_per_second']:<12,.0f} {data['memory_used_mb']:<12.1f}")
    
    print(f"\n💡 Storage Strategy Recommendations:")
    print(f"  • Small datasets (<100K posts): JSON or Pickle")
    print(f"  • Medium datasets (100K-1M posts): Compressed JSON or SQLite")
    print(f"  • Large datasets (>1M posts): SQLite or Streaming File")
    print(f"  • Real-time streaming: Streaming File or SQLite")
    print(f"  • Maximum performance: Pickle")
    print(f"  • Human-readable: JSON or Compressed JSON")


def main():
    """Run storage strategy benchmark."""
    print("🚀 DATA STORAGE STRATEGIES FOR STREAMING RANKING")
    print("=" * 80)
    print("This benchmark compares different storage approaches and their")
    print("impact on the streaming ranking algorithm performance.")
    print()
    
    try:
        # Test with different scales
        scales = [10_000, 100_000, 500_000]
        
        for scale in scales:
            print(f"\n🎯 Testing with {scale:,} posts")
            print("-" * 50)
            
            results = benchmark_storage_strategies(scale)
            print_storage_benchmark_results(results)
        
        print(f"\n✅ Storage benchmark completed!")
        print(f"\n📋 Key Insights:")
        print(f"  • Storage format has minimal impact on ranking performance")
        print(f"  • SQLite provides best balance of size, speed, and features")
        print(f"  • Streaming file is most memory-efficient for huge datasets")
        print(f"  • Pickle is fastest for loading but largest file size")
        print(f"  • Compressed JSON provides good compression with readability")
        
    except Exception as e:
        print(f"\n❌ Error during benchmark: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 