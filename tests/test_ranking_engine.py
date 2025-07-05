#!/usr/bin/env python3
"""
Unit tests for the Social Media Ranking System.
Tests correctness, performance, and edge cases.
"""

import pytest
import time
import random
from ranking_engine import RankingEngine, OptimizedRankingEngine, Post


class TestPost:
    """Test the Post data structure."""
    
    def test_post_creation(self):
        """Test basic post creation."""
        post = Post(post_id="test_123", likes=100, comments=20, shares=5)
        
        assert post.post_id == "test_123"
        assert post.likes == 100
        assert post.comments == 20
        assert post.shares == 5
        assert post.base_score == 100 + 20 * 2 + 5 * 3  # 100 + 40 + 15 = 155
        
    def test_post_defaults(self):
        """Test post creation with defaults."""
        post = Post(post_id="test_123")
        
        assert post.likes == 0
        assert post.comments == 0
        assert post.shares == 0
        assert post.upvotes == 0
        assert post.downvotes == 0
        assert post.base_score == 0
        assert post.timestamp > 0
        
    def test_post_base_score_calculation(self):
        """Test base score calculation."""
        post = Post(post_id="test", likes=50, comments=10, shares=5)
        expected_score = 50 + 10 * 2 + 5 * 3  # 50 + 20 + 15 = 85
        assert post.base_score == expected_score


class TestRankingEngine:
    """Test the basic RankingEngine."""
    
    def setup_method(self):
        """Set up test environment."""
        self.engine = RankingEngine()
        
    def test_add_post(self):
        """Test adding a single post."""
        self.engine.add_post("test_123", likes=100, comments=20)
        
        assert "test_123" in self.engine.posts
        assert self.engine.posts["test_123"].likes == 100
        assert self.engine.posts["test_123"].comments == 20
        
    def test_add_duplicate_post(self):
        """Test adding duplicate post raises error."""
        self.engine.add_post("test_123", likes=100)
        
        with pytest.raises(ValueError, match="already exists"):
            self.engine.add_post("test_123", likes=200)
            
    def test_update_post(self):
        """Test updating post metrics."""
        self.engine.add_post("test_123", likes=100, comments=20)
        self.engine.update_post("test_123", likes=150, comments=30)
        
        post = self.engine.posts["test_123"]
        assert post.likes == 150
        assert post.comments == 30
        assert post.base_score == 150 + 30 * 2  # 150 + 60 = 210
        
    def test_update_nonexistent_post(self):
        """Test updating non-existent post raises error."""
        with pytest.raises(ValueError, match="not found"):
            self.engine.update_post("nonexistent", likes=100)
            
    def test_hot_score_algorithm(self):
        """Test hot score algorithm."""
        # Add posts with different characteristics
        current_time = time.time()
        
        # High engagement, recent
        self.engine.add_post("post1", upvotes=100, downvotes=5, timestamp=current_time - 3600)
        # Low engagement, recent
        self.engine.add_post("post2", upvotes=10, downvotes=2, timestamp=current_time - 1800)
        # High engagement, older
        self.engine.add_post("post3", upvotes=200, downvotes=10, timestamp=current_time - 7200)
        
        ranked_posts = self.engine.get_ranked_posts(algorithm="hot_score", limit=3)
        
        # Should have 3 posts
        assert len(ranked_posts) == 3
        
        # Scores should be in descending order
        scores = [post['score'] for post in ranked_posts]
        assert scores == sorted(scores, reverse=True)
        
    def test_engagement_score_algorithm(self):
        """Test engagement score algorithm."""
        current_time = time.time()
        
        # High engagement
        self.engine.add_post("post1", likes=100, comments=20, shares=10, timestamp=current_time - 3600)
        # Medium engagement
        self.engine.add_post("post2", likes=50, comments=10, shares=5, timestamp=current_time - 1800)
        # Low engagement
        self.engine.add_post("post3", likes=10, comments=2, shares=1, timestamp=current_time - 900)
        
        ranked_posts = self.engine.get_ranked_posts(algorithm="engagement_score", limit=3)
        
        assert len(ranked_posts) == 3
        
        # Scores should be in descending order
        scores = [post['score'] for post in ranked_posts]
        assert scores == sorted(scores, reverse=True)
        
    def test_time_decay_algorithm(self):
        """Test time decay algorithm."""
        current_time = time.time()
        
        # Recent post with high engagement
        self.engine.add_post("post1", likes=100, comments=20, shares=10, timestamp=current_time - 1800)
        # Older post with high engagement
        self.engine.add_post("post2", likes=200, comments=40, shares=20, timestamp=current_time - 7200)
        
        ranked_posts = self.engine.get_ranked_posts(algorithm="time_decay", limit=2)
        
        assert len(ranked_posts) == 2
        
        # Recent post should rank higher due to time decay
        assert ranked_posts[0]['post_id'] == "post1"
        
    def test_hybrid_algorithm(self):
        """Test hybrid algorithm."""
        current_time = time.time()
        
        self.engine.add_post("post1", likes=100, comments=20, shares=10, timestamp=current_time - 3600)
        self.engine.add_post("post2", likes=200, comments=40, shares=20, timestamp=current_time - 7200)
        
        ranked_posts = self.engine.get_ranked_posts(algorithm="hybrid", limit=2)
        
        assert len(ranked_posts) == 2
        
        # Should have valid scores
        for post in ranked_posts:
            assert isinstance(post['score'], (int, float))
            assert post['score'] >= 0
            
    def test_unknown_algorithm(self):
        """Test that unknown algorithm raises error."""
        self.engine.add_post("test", likes=100)
        
        with pytest.raises(ValueError, match="Unknown algorithm"):
            self.engine.get_ranked_posts(algorithm="unknown_algorithm")
            
    def test_get_post_rank(self):
        """Test getting rank of specific post."""
        current_time = time.time()
        
        self.engine.add_post("post1", likes=100, timestamp=current_time - 3600)
        self.engine.add_post("post2", likes=200, timestamp=current_time - 7200)
        self.engine.add_post("post3", likes=50, timestamp=current_time - 1800)
        
        # Get rank of post2 (should be #1 due to highest likes)
        rank = self.engine.get_post_rank("post2", algorithm="engagement_score")
        assert rank == 1
        
        # Get rank of non-existent post
        rank = self.engine.get_post_rank("nonexistent", algorithm="engagement_score")
        assert rank is None
        
    def test_batch_add_posts(self):
        """Test batch adding posts."""
        posts_data = [
            {'post_id': 'post1', 'likes': 100, 'comments': 20},
            {'post_id': 'post2', 'likes': 200, 'comments': 40},
            {'post_id': 'post3', 'likes': 50, 'comments': 10},
        ]
        
        self.engine.batch_add_posts(posts_data)
        
        assert len(self.engine.posts) == 3
        assert "post1" in self.engine.posts
        assert "post2" in self.engine.posts
        assert "post3" in self.engine.posts
        
    def test_cache_invalidation(self):
        """Test that cache is invalidated on updates."""
        self.engine.add_post("test", likes=100)
        
        # Get rankings (should cache)
        rankings1 = self.engine.get_ranked_posts(algorithm="engagement_score")
        
        # Update post
        self.engine.update_post("test", likes=200)
        
        # Get rankings again (should recalculate)
        rankings2 = self.engine.get_ranked_posts(algorithm="engagement_score")
        
        # Scores should be different
        assert rankings1[0]['score'] != rankings2[0]['score']
        
    def test_get_stats(self):
        """Test getting system statistics."""
        self.engine.add_post("post1", likes=100, comments=20, shares=10)
        self.engine.add_post("post2", likes=200, comments=40, shares=20)
        
        stats = self.engine.get_stats()
        
        assert stats['total_posts'] == 2
        assert stats['total_likes'] == 300
        assert stats['total_comments'] == 60
        assert stats['total_shares'] == 30
        assert stats['avg_likes_per_post'] == 150
        assert stats['avg_comments_per_post'] == 30
        assert stats['avg_shares_per_post'] == 15
        assert stats['memory_usage_mb'] > 0


class TestOptimizedRankingEngine:
    """Test the OptimizedRankingEngine."""
    
    def setup_method(self):
        """Set up test environment."""
        self.engine = OptimizedRankingEngine()
        
    def test_optimized_engine_inheritance(self):
        """Test that optimized engine inherits from base engine."""
        assert isinstance(self.engine, RankingEngine)
        
    def test_optimized_engine_performance(self):
        """Test that optimized engine performs better with large datasets."""
        # Create large dataset
        posts_data = []
        for i in range(1000):
            posts_data.append({
                'post_id': f'post_{i}',
                'likes': random.randint(0, 1000),
                'comments': random.randint(0, 100),
                'shares': random.randint(0, 50),
                'timestamp': time.time() - random.randint(0, 86400)
            })
        
        # Test performance
        start_time = time.time()
        self.engine.batch_add_posts(posts_data)
        add_time = time.time() - start_time
        
        start_time = time.time()
        rankings = self.engine.get_ranked_posts(algorithm="hot_score", limit=100)
        ranking_time = time.time() - start_time
        
        # Should complete within reasonable time
        assert add_time < 1.0  # Should add 1000 posts in under 1 second
        assert ranking_time < 0.1  # Should rank in under 100ms
        
        # Should return correct number of rankings
        assert len(rankings) == 100
        
    def test_optimized_engine_correctness(self):
        """Test that optimized engine produces same results as base engine."""
        # Create test data
        posts_data = [
            {'post_id': 'post1', 'likes': 100, 'comments': 20, 'shares': 10, 'timestamp': time.time() - 3600},
            {'post_id': 'post2', 'likes': 200, 'comments': 40, 'shares': 20, 'timestamp': time.time() - 7200},
            {'post_id': 'post3', 'likes': 50, 'comments': 10, 'shares': 5, 'timestamp': time.time() - 1800},
        ]
        
        # Test with base engine
        base_engine = RankingEngine()
        base_engine.batch_add_posts(posts_data)
        base_rankings = base_engine.get_ranked_posts(algorithm="engagement_score", limit=3)
        
        # Test with optimized engine
        opt_engine = OptimizedRankingEngine()
        opt_engine.batch_add_posts(posts_data)
        opt_rankings = opt_engine.get_ranked_posts(algorithm="engagement_score", limit=3)
        
        # Results should be the same
        assert len(base_rankings) == len(opt_rankings)
        
        for i in range(len(base_rankings)):
            assert base_rankings[i]['post_id'] == opt_rankings[i]['post_id']
            assert abs(base_rankings[i]['score'] - opt_rankings[i]['score']) < 1e-6


class TestPerformance:
    """Performance tests."""
    
    def test_large_dataset_performance(self):
        """Test performance with large dataset."""
        engine = OptimizedRankingEngine()
        
        # Generate large dataset
        posts_data = []
        for i in range(10000):
            posts_data.append({
                'post_id': f'post_{i:06d}',
                'likes': random.randint(0, 5000),
                'comments': random.randint(0, 500),
                'shares': random.randint(0, 200),
                'timestamp': time.time() - random.randint(0, 86400 * 7)
            })
        
        # Measure add performance
        start_time = time.time()
        engine.batch_add_posts(posts_data)
        add_time = time.time() - start_time
        
        # Measure ranking performance
        start_time = time.time()
        rankings = engine.get_ranked_posts(algorithm="hot_score", limit=100)
        ranking_time = time.time() - start_time
        
        # Performance assertions
        assert add_time < 2.0  # Should add 10k posts in under 2 seconds
        assert ranking_time < 0.05  # Should rank in under 50ms
        
        # Memory usage should be reasonable
        stats = engine.get_stats()
        assert stats['memory_usage_mb'] < 100  # Should use less than 100MB for 10k posts
        
    def test_update_performance(self):
        """Test update performance."""
        engine = OptimizedRankingEngine()
        
        # Add posts
        for i in range(1000):
            engine.add_post(f'post_{i}', likes=random.randint(0, 1000))
        
        # Measure update performance
        update_times = []
        for _ in range(100):
            post_id = f'post_{random.randint(0, 999)}'
            start_time = time.time()
            engine.update_post(post_id, likes=random.randint(0, 1000))
            update_time = time.time() - start_time
            update_times.append(update_time)
        
        avg_update_time = sum(update_times) / len(update_times)
        
        # Updates should be very fast
        assert avg_update_time < 0.001  # Should update in under 1ms on average


if __name__ == "__main__":
    pytest.main([__file__]) 