#!/usr/bin/env python3
"""
Tests for the Streaming Ranking Engine.
"""

import pytest
import time
from typing import Iterator
from streaming_ranking_engine import (
    StreamingRankingEngine, 
    StreamingRankingResult,
    generate_test_posts
)
from ranking_engine import Post


def test_streaming_ranking_basic():
    """Test basic streaming ranking functionality."""
    engine = StreamingRankingEngine(batch_size=100)
    
    # Create test posts
    posts = [
        Post(post_id="1", likes=100, comments=10, shares=5, upvotes=120, downvotes=5, timestamp=time.time()),
        Post(post_id="2", likes=200, comments=20, shares=10, upvotes=240, downvotes=10, timestamp=time.time()),
        Post(post_id="3", likes=50, comments=5, shares=2, upvotes=60, downvotes=2, timestamp=time.time()),
    ]
    
    def post_iterator():
        for post in posts:
            yield post
    
    result = engine.rank_posts_streaming(post_iterator(), algorithm="hot_score", top_k=2)
    
    assert result.total_posts_processed == 3
    assert len(result.top_posts) == 2
    assert result.algorithm == "hot_score"
    assert result.batch_size == 100
    
    # Check that posts are sorted by score (descending)
    scores = [score for score, _ in result.top_posts]
    assert scores == sorted(scores, reverse=True)


def test_streaming_ranking_large_scale():
    """Test streaming ranking with a large number of posts."""
    engine = StreamingRankingEngine(batch_size=1000)
    
    # Generate 10,000 test posts
    post_iterator = generate_test_posts(10_000)
    
    result = engine.rank_posts_streaming(post_iterator, algorithm="hot_score", top_k=100)
    
    assert result.total_posts_processed == 10_000
    assert len(result.top_posts) == 100
    assert result.processing_time_seconds > 0
    assert result.memory_usage_mb > 0
    
    # Verify top posts are correctly ranked
    scores = [score for score, _ in result.top_posts]
    assert scores == sorted(scores, reverse=True)


def test_streaming_ranking_different_algorithms():
    """Test streaming ranking with different algorithms."""
    engine = StreamingRankingEngine(batch_size=500)
    
    algorithms = ["hot_score", "engagement_score", "time_decay"]
    
    for algorithm in algorithms:
        # Generate fresh posts for each algorithm
        post_iterator = generate_test_posts(1000)
        
        result = engine.rank_posts_streaming(post_iterator, algorithm=algorithm, top_k=10)
        
        assert result.total_posts_processed == 1000
        assert len(result.top_posts) == 10
        assert result.algorithm == algorithm
        
        # Verify scores are reasonable (some algorithms can have negative scores)
        scores = [score for score, _ in result.top_posts]
        assert scores == sorted(scores, reverse=True)


def test_streaming_ranking_memory_usage():
    """Test that memory usage stays reasonable with large datasets."""
    engine = StreamingRankingEngine(batch_size=1000)
    
    # Test with different scales
    scales = [1000, 10000, 50000]
    
    for scale in scales:
        post_iterator = generate_test_posts(scale)
        
        result = engine.rank_posts_streaming(post_iterator, algorithm="hot_score", top_k=100)
        
        # Memory usage should be reasonable (less than 1GB for 50k posts)
        assert result.memory_usage_mb < 1000
        
        # Memory per post should be reasonable (streaming approach)
        memory_per_post_kb = result.memory_usage_mb / result.total_posts_processed * 1000
        assert memory_per_post_kb < 100.0  # Less than 100KB per post (more realistic)


def test_streaming_ranking_top_k_limits():
    """Test that top_k parameter works correctly."""
    engine = StreamingRankingEngine(batch_size=100)
    
    # Test different top_k values
    for top_k in [1, 10, 50, 100]:
        # Generate fresh posts for each test
        post_iterator = generate_test_posts(1000)
        
        result = engine.rank_posts_streaming(post_iterator, algorithm="hot_score", top_k=top_k)
        
        assert len(result.top_posts) == top_k
        assert result.total_posts_processed == 1000


def test_streaming_ranking_batch_size():
    """Test that different batch sizes work correctly."""
    batch_sizes = [100, 1000, 10000]
    
    for batch_size in batch_sizes:
        engine = StreamingRankingEngine(batch_size=batch_size)
        post_iterator = generate_test_posts(5000)
        
        result = engine.rank_posts_streaming(post_iterator, algorithm="hot_score", top_k=50)
        
        assert result.batch_size == batch_size
        assert result.total_posts_processed == 5000
        assert len(result.top_posts) == 50


def test_streaming_ranking_empty_iterator():
    """Test handling of empty post iterator."""
    engine = StreamingRankingEngine()
    
    def empty_iterator():
        return iter([])
    
    result = engine.rank_posts_streaming(empty_iterator(), algorithm="hot_score", top_k=100)
    
    assert result.total_posts_processed == 0
    assert len(result.top_posts) == 0
    assert result.processing_time_seconds >= 0


def test_streaming_ranking_unknown_algorithm():
    """Test error handling for unknown algorithm."""
    engine = StreamingRankingEngine()
    
    post_iterator = generate_test_posts(100)
    
    with pytest.raises(ValueError, match="Unknown algorithm"):
        engine.rank_posts_streaming(post_iterator, algorithm="unknown_algorithm", top_k=10)


def test_streaming_ranking_from_list():
    """Test the convenience method for ranking from a list."""
    engine = StreamingRankingEngine(batch_size=100)
    
    posts = [
        Post(post_id="1", likes=100, comments=10, shares=5, upvotes=120, downvotes=5, timestamp=time.time()),
        Post(post_id="2", likes=200, comments=20, shares=10, upvotes=240, downvotes=10, timestamp=time.time()),
        Post(post_id="3", likes=50, comments=5, shares=2, upvotes=60, downvotes=2, timestamp=time.time()),
    ]
    
    result = engine.rank_posts_from_list(posts, algorithm="hot_score", top_k=2)
    
    assert result.total_posts_processed == 3
    assert len(result.top_posts) == 2
    assert result.algorithm == "hot_score"


def test_streaming_ranking_performance_benchmark():
    """Test performance characteristics of streaming ranking."""
    engine = StreamingRankingEngine(batch_size=1000)
    
    # Test with 10k posts
    post_iterator = generate_test_posts(10_000)
    
    start_time = time.time()
    result = engine.rank_posts_streaming(post_iterator, algorithm="hot_score", top_k=100)
    end_time = time.time()
    
    # Verify performance metrics
    assert result.processing_time_seconds > 0
    assert result.processing_time_seconds < 10  # Should be fast
    
    # Calculate throughput
    posts_per_second = result.total_posts_processed / result.processing_time_seconds
    assert posts_per_second > 1000  # Should process at least 1000 posts/second
    
    # Memory efficiency (more realistic expectation)
    memory_per_post_kb = result.memory_usage_mb / result.total_posts_processed * 1000
    assert memory_per_post_kb < 10.0  # Less than 10KB per post


def test_streaming_ranking_consistency():
    """Test that streaming ranking produces consistent results."""
    engine = StreamingRankingEngine(batch_size=1000)
    
    # Generate the same posts twice
    post_iterator1 = generate_test_posts(1000)
    post_iterator2 = generate_test_posts(1000)
    
    result1 = engine.rank_posts_streaming(post_iterator1, algorithm="hot_score", top_k=10)
    result2 = engine.rank_posts_streaming(post_iterator2, algorithm="hot_score", top_k=10)
    
    # Results should be identical
    assert result1.total_posts_processed == result2.total_posts_processed
    assert len(result1.top_posts) == len(result2.top_posts)
    
    # Top scores should be very similar (allow for small floating point differences)
    scores1 = [score for score, _ in result1.top_posts]
    scores2 = [score for score, _ in result2.top_posts]
    
    # Check that scores are approximately equal (within 0.001)
    for s1, s2 in zip(scores1, scores2):
        assert abs(s1 - s2) < 0.001


if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v"]) 