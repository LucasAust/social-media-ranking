"""
Configuration file for the Social Media Ranking System.
Contains all configurable parameters for algorithms and performance tuning.
"""

from typing import Dict, Any


class RankingConfig:
    """Configuration class for ranking algorithms and system parameters."""
    
    # Cache settings
    CACHE_TTL = 60  # Cache time-to-live in seconds
    CACHE_SIZE = 10000  # Maximum number of cached rankings
    
    # Algorithm parameters
    ALGORITHM_PARAMS = {
        'hot_score': {
            'description': 'Reddit-style hot score algorithm',
            'time_weight': 45000,  # Time decay factor
            'order_base': 10,  # Base for logarithmic calculation
            'epoch_offset': 1134028003  # Reddit epoch offset
        },
        
        'engagement_score': {
            'description': 'Engagement-based ranking algorithm',
            'like_weight': 1.0,
            'comment_weight': 2.0,
            'share_weight': 3.0,
            'time_factor': 1.0  # Minimum time factor to avoid division by zero
        },
        
        'time_decay': {
            'description': 'Time-decay ranking algorithm',
            'decay_rate': 0.1,  # Exponential decay rate
            'base_score_weights': {
                'likes': 1.0,
                'comments': 2.0,
                'shares': 3.0
            }
        },
        
        'hybrid': {
            'description': 'Hybrid multi-factor ranking algorithm',
            'weights': {
                'likes': 1.0,
                'comments': 2.0,
                'shares': 3.0,
                'time_decay': 0.1
            },
            'normalize_scores': True
        }
    }
    
    # Performance settings
    PERFORMANCE = {
        'batch_size': 1000,  # Default batch size for bulk operations
        'max_posts': 1000000,  # Maximum number of posts to handle
        'memory_limit_mb': 2048,  # Memory limit in MB
        'ranking_timeout_ms': 1000,  # Maximum time for ranking operation
        'update_timeout_ms': 100  # Maximum time for update operation
    }
    
    # Default algorithm weights for hybrid ranking
    DEFAULT_HYBRID_WEIGHTS = {
        'likes': 1.0,
        'comments': 2.0,
        'shares': 3.0,
        'time_decay': 0.1,
        'recency_boost': 1.2,
        'viral_penalty': 0.8
    }
    
    # Time-based parameters
    TIME_PARAMS = {
        'hours_in_day': 24,
        'seconds_in_hour': 3600,
        'viral_threshold_hours': 48,  # Posts older than this get viral penalty
        'fresh_content_hours': 6,  # Posts newer than this get recency boost
        'max_age_days': 30  # Maximum age for posts to be considered
    }
    
    # Engagement thresholds
    ENGAGEMENT_THRESHOLDS = {
        'viral_likes': 10000,
        'viral_comments': 500,
        'viral_shares': 1000,
        'high_engagement_likes': 1000,
        'high_engagement_comments': 100,
        'high_engagement_shares': 200,
        'low_engagement_likes': 10,
        'low_engagement_comments': 1,
        'low_engagement_shares': 1
    }
    
    # Ranking limits
    RANKING_LIMITS = {
        'default_limit': 100,
        'max_limit': 1000,
        'min_limit': 1,
        'cache_limit': 500
    }
    
    @classmethod
    def get_algorithm_params(cls, algorithm: str) -> Dict[str, Any]:
        """Get parameters for a specific algorithm."""
        return cls.ALGORITHM_PARAMS.get(algorithm, {})
    
    @classmethod
    def get_hybrid_weights(cls, custom_weights: Dict[str, float] | None = None) -> Dict[str, float]:
        """Get hybrid algorithm weights, with optional custom overrides."""
        weights = cls.DEFAULT_HYBRID_WEIGHTS.copy()
        if custom_weights:
            weights.update(custom_weights)
        return weights
    
    @classmethod
    def is_viral_post(cls, likes: int, comments: int, shares: int) -> bool:
        """Check if a post meets viral engagement thresholds."""
        return (likes >= cls.ENGAGEMENT_THRESHOLDS['viral_likes'] or
                comments >= cls.ENGAGEMENT_THRESHOLDS['viral_comments'] or
                shares >= cls.ENGAGEMENT_THRESHOLDS['viral_shares'])
    
    @classmethod
    def is_high_engagement(cls, likes: int, comments: int, shares: int) -> bool:
        """Check if a post meets high engagement thresholds."""
        return (likes >= cls.ENGAGEMENT_THRESHOLDS['high_engagement_likes'] or
                comments >= cls.ENGAGEMENT_THRESHOLDS['high_engagement_comments'] or
                shares >= cls.ENGAGEMENT_THRESHOLDS['high_engagement_shares'])
    
    @classmethod
    def is_low_engagement(cls, likes: int, comments: int, shares: int) -> bool:
        """Check if a post meets low engagement thresholds."""
        return (likes <= cls.ENGAGEMENT_THRESHOLDS['low_engagement_likes'] and
                comments <= cls.ENGAGEMENT_THRESHOLDS['low_engagement_comments'] and
                shares <= cls.ENGAGEMENT_THRESHOLDS['low_engagement_shares'])


# Environment-specific configurations
class DevelopmentConfig(RankingConfig):
    """Development environment configuration."""
    CACHE_TTL = 30  # Shorter cache for development
    PERFORMANCE = {
        **RankingConfig.PERFORMANCE,
        'max_posts': 10000,  # Lower limit for development
        'memory_limit_mb': 512
    }


class ProductionConfig(RankingConfig):
    """Production environment configuration."""
    CACHE_TTL = 300  # Longer cache for production
    PERFORMANCE = {
        **RankingConfig.PERFORMANCE,
        'max_posts': 1000000,  # Higher limit for production
        'memory_limit_mb': 4096
    }


class TestingConfig(RankingConfig):
    """Testing environment configuration."""
    CACHE_TTL = 5  # Very short cache for testing
    PERFORMANCE = {
        **RankingConfig.PERFORMANCE,
        'max_posts': 1000,  # Small limit for testing
        'memory_limit_mb': 256
    }


# Configuration factory
def get_config(environment: str = 'development') -> RankingConfig:
    """Get configuration for the specified environment."""
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    return configs.get(environment, DevelopmentConfig) 