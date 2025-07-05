import time
import math
import heapq
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import numpy as np


@dataclass
class Post:
    """Optimized post data structure for fast access and updates."""
    post_id: str
    likes: int = 0
    comments: int = 0
    shares: int = 0
    upvotes: int = 0
    downvotes: int = 0
    timestamp: float = field(default_factory=time.time)
    base_score: float = 0.0
    
    def __post_init__(self):
        """Calculate initial base score."""
        self.base_score = self.likes + self.comments * 2 + self.shares * 3


class RankingEngine:
    """
    High-performance ranking engine for social media posts.
    Designed to handle hundreds of thousands of posts efficiently.
    """
    
    def __init__(self, cache_size: int = 10000):
        self.posts: Dict[str, Post] = {}
        self.cache_size = cache_size
        self.ranking_cache: Dict[str, List[Tuple[float, str]]] = {}
        self.cache_timestamps: Dict[str, float] = {}
        self.cache_ttl = 60  # Cache for 60 seconds
        
    def add_post(self, post_id: str, **kwargs) -> None:
        """Add a new post to the ranking system."""
        if post_id in self.posts:
            raise ValueError(f"Post {post_id} already exists")
        
        self.posts[post_id] = Post(post_id=post_id, **kwargs)
        self._invalidate_cache()
        
    def update_post(self, post_id: str, **kwargs) -> None:
        """Update an existing post's metrics."""
        if post_id not in self.posts:
            raise ValueError(f"Post {post_id} not found")
        
        post = self.posts[post_id]
        for key, value in kwargs.items():
            if hasattr(post, key):
                setattr(post, key, value)
        
        # Recalculate base score
        post.base_score = post.likes + post.comments * 2 + post.shares * 3
        self._invalidate_cache()
        
    def _invalidate_cache(self) -> None:
        """Invalidate all cached rankings."""
        self.ranking_cache.clear()
        self.cache_timestamps.clear()
        
    def _is_cache_valid(self, algorithm: str) -> bool:
        """Check if cached ranking is still valid."""
        if algorithm not in self.cache_timestamps:
            return False
        return time.time() - self.cache_timestamps[algorithm] < self.cache_ttl
        
    def _hot_score(self, post: Post) -> float:
        """Calculate Reddit-style hot score."""
        order = math.log10(max(abs(post.upvotes - post.downvotes), 1))
        sign = 1 if post.upvotes - post.downvotes > 0 else -1 if post.upvotes - post.downvotes < 0 else 0
        seconds = time.time() - post.timestamp - 1134028003
        return round(sign * order + seconds / 45000, 7)
        
    def _engagement_score(self, post: Post) -> float:
        """Calculate engagement-based score."""
        total_engagement = post.likes + post.comments * 2 + post.shares * 3
        time_factor = time.time() - post.timestamp + 1
        return total_engagement / time_factor
        
    def _time_decay_score(self, post: Post, decay_rate: float = 0.01) -> float:
        """Calculate time-decay score."""
        time_elapsed = time.time() - post.timestamp
        return post.base_score * math.exp(-decay_rate * time_elapsed)
        
    def _hybrid_score(self, post: Post, weights: Dict[str, float] | None = None) -> float:
        """Calculate hybrid multi-factor score."""
        if weights is None:
            weights = {
                'likes': 1.0,
                'comments': 2.0,
                'shares': 3.0,
                'time_decay': 0.1
            }
        
        engagement = (post.likes * weights['likes'] + 
                     post.comments * weights['comments'] + 
                     post.shares * weights['shares'])
        
        time_elapsed = time.time() - post.timestamp
        time_factor = math.exp(-weights['time_decay'] * time_elapsed)
        
        return engagement * time_factor
        
    def _calculate_scores(self, algorithm: str, **kwargs) -> List[Tuple[float, str]]:
        """Calculate scores for all posts using the specified algorithm."""
        scores = []
        
        for post_id, post in self.posts.items():
            if algorithm == "hot_score":
                score = self._hot_score(post)
            elif algorithm == "engagement_score":
                score = self._engagement_score(post)
            elif algorithm == "time_decay":
                decay_rate = kwargs.get('decay_rate', 0.01)
                score = self._time_decay_score(post, decay_rate)
            elif algorithm == "hybrid":
                weights = kwargs.get('weights')
                score = self._hybrid_score(post, weights)
            else:
                raise ValueError(f"Unknown algorithm: {algorithm}")
                
            scores.append((score, post_id))
            
        return scores
        
    def get_ranked_posts(self, algorithm: str = "hot_score", limit: int = 100, 
                        **kwargs) -> List[Dict[str, Any]]:
        """
        Get ranked posts using the specified algorithm.
        Returns list of post dictionaries with ranking information.
        """
        # Check cache first
        if self._is_cache_valid(algorithm):
            cached_scores = self.ranking_cache[algorithm]
        else:
            # Calculate new scores
            scores = self._calculate_scores(algorithm, **kwargs)
            
            # Sort by score (descending) and limit
            scores.sort(reverse=True)
            
            # Cache the results
            self.ranking_cache[algorithm] = scores
            self.cache_timestamps[algorithm] = time.time()
            
            cached_scores = scores
            
        # Return top posts with ranking info
        result = []
        for rank, (score, post_id) in enumerate(cached_scores[:limit], 1):
            post = self.posts[post_id]
            result.append({
                'rank': rank,
                'post_id': post_id,
                'score': score,
                'likes': post.likes,
                'comments': post.comments,
                'shares': post.shares,
                'upvotes': post.upvotes,
                'downvotes': post.downvotes,
                'timestamp': post.timestamp,
                'age_hours': (time.time() - post.timestamp) / 3600
            })
            
        return result
        
    def get_post_rank(self, post_id: str, algorithm: str = "hot_score", **kwargs) -> Optional[int]:
        """Get the rank of a specific post."""
        ranked_posts = self.get_ranked_posts(algorithm, limit=len(self.posts), **kwargs)
        
        for post_data in ranked_posts:
            if post_data['post_id'] == post_id:
                return post_data['rank']
                
        return None
        
    def batch_add_posts(self, posts_data: List[Dict[str, Any]]) -> None:
        """Efficiently add multiple posts at once."""
        for post_data in posts_data:
            post_data_copy = post_data.copy()
            post_id = post_data_copy.pop('post_id')
            self.posts[post_id] = Post(post_id=post_id, **post_data_copy)
            
        self._invalidate_cache()
        
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        total_posts = len(self.posts)
        total_likes = sum(post.likes for post in self.posts.values())
        total_comments = sum(post.comments for post in self.posts.values())
        total_shares = sum(post.shares for post in self.posts.values())
        
        return {
            'total_posts': total_posts,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'total_shares': total_shares,
            'avg_likes_per_post': total_likes / total_posts if total_posts > 0 else 0,
            'avg_comments_per_post': total_comments / total_posts if total_posts > 0 else 0,
            'avg_shares_per_post': total_shares / total_posts if total_posts > 0 else 0,
            'cache_size': len(self.ranking_cache),
            'memory_usage_mb': self._estimate_memory_usage()
        }
        
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB."""
        # Rough estimation: each post object ~200 bytes
        post_memory = len(self.posts) * 200
        cache_memory = len(self.ranking_cache) * 1000  # Rough estimate for cache
        return (post_memory + cache_memory) / (1024 * 1024)  # Convert to MB


class OptimizedRankingEngine(RankingEngine):
    """
    Further optimized version using numpy for vectorized operations.
    Best for very large datasets (100k+ posts).
    """
    
    def __init__(self, cache_size: int = 10000):
        super().__init__(cache_size)
        self.post_arrays = {}  # Store post data as numpy arrays for vectorization
        
    def _vectorized_calculate_scores(self, algorithm: str, **kwargs) -> List[Tuple[float, str]]:
        """Vectorized score calculation using numpy for better performance."""
        if not self.posts:
            return []
            
        # Convert to numpy arrays for vectorized operations
        post_ids = list(self.posts.keys())
        likes = np.array([self.posts[pid].likes for pid in post_ids])
        comments = np.array([self.posts[pid].comments for pid in post_ids])
        shares = np.array([self.posts[pid].shares for pid in post_ids])
        upvotes = np.array([self.posts[pid].upvotes for pid in post_ids])
        downvotes = np.array([self.posts[pid].downvotes for pid in post_ids])
        timestamps = np.array([self.posts[pid].timestamp for pid in post_ids])
        
        current_time = time.time()
        time_elapsed = current_time - timestamps
        
        if algorithm == "hot_score":
            votes_diff = upvotes - downvotes
            order = np.log10(np.maximum(np.abs(votes_diff), 1))
            sign = np.sign(votes_diff)
            seconds = time_elapsed - 1134028003
            scores = sign * order + seconds / 45000
            
        elif algorithm == "engagement_score":
            engagement = likes + comments * 2 + shares * 3
            scores = engagement / (time_elapsed + 1)
            
        elif algorithm == "time_decay":
            decay_rate = kwargs.get('decay_rate', 0.1)
            base_scores = likes + comments * 2 + shares * 3
            scores = base_scores * np.exp(-decay_rate * time_elapsed)
            
        elif algorithm == "hybrid":
            weights = kwargs.get('weights', {
                'likes': 1.0, 'comments': 2.0, 'shares': 3.0, 'time_decay': 0.1
            })
            engagement = (likes * weights['likes'] + 
                         comments * weights['comments'] + 
                         shares * weights['shares'])
            time_factor = np.exp(-weights['time_decay'] * time_elapsed)
            scores = engagement * time_factor
            
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
            
        # Create list of (score, post_id) tuples
        score_tuples = [(float(score), post_id) for score, post_id in zip(scores, post_ids)]
        return score_tuples 