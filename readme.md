# Social Media Post Ranking System

A high-performance algorithm for ranking social media posts based on popularity metrics, designed to handle hundreds of thousands of inputs and outputs efficiently.

## Features

- **High-Performance Ranking**: Optimized algorithms for real-time ranking of large datasets
- **Scalable Architecture**: Designed to handle 100k+ posts with sub-second response times
- **Multiple Ranking Algorithms**: 
  - Hot Score (Reddit-style)
  - Engagement Score
  - Time-Decay Ranking
  - Hybrid Multi-Factor Ranking
- **Memory-Efficient**: Uses optimized data structures and streaming processing
- **Real-time Updates**: Incremental updates without full recalculation

## Architecture

### Core Components

1. **Post Data Structure**: Optimized for fast access and updates
2. **Ranking Engine**: Multiple algorithms with different performance characteristics
3. **Cache Layer**: In-memory caching for frequently accessed rankings
4. **Batch Processor**: Efficient bulk operations for large datasets
5. **Performance Monitor**: Real-time performance metrics

### Performance Targets

- **Input Processing**: 100k+ posts/second
- **Ranking Generation**: Sub-100ms for 100k posts
- **Memory Usage**: <2GB for 1M posts
- **Update Latency**: <10ms for single post updates

## Algorithms

### 1. Hot Score (Reddit-style)
- Formula: `score = (upvotes - downvotes) / (time + 2)^1.5`
- Time complexity: O(1) per post
- Best for: Real-time trending content

### 2. Engagement Score
- Formula: `score = (likes + comments*2 + shares*3) / (time + 1)`
- Time complexity: O(1) per post
- Best for: Overall engagement ranking

### 3. Time-Decay Ranking
- Formula: `score = base_score * e^(-λ * time)`
- Time complexity: O(1) per post
- Best for: Fresh content prioritization

### 4. Hybrid Multi-Factor
- Combines multiple metrics with configurable weights
- Time complexity: O(1) per post
- Best for: Custom ranking requirements

## Usage

```python
from ranking_engine import RankingEngine

# Initialize the ranking engine
engine = RankingEngine()

# Add posts
engine.add_post(post_id="123", likes=100, comments=20, shares=5, timestamp=1640995200)

# Get ranked posts
ranked_posts = engine.get_ranked_posts(algorithm="hot_score", limit=100)

# Update post metrics
engine.update_post(post_id="123", likes=150, comments=25)

# Get updated rankings
updated_rankings = engine.get_ranked_posts(algorithm="hot_score", limit=100)
```

## Performance Benchmarks

- **100k posts**: ~50ms ranking time
- **500k posts**: ~200ms ranking time
- **1M posts**: ~400ms ranking time
- **Memory usage**: ~1.5GB for 1M posts

## Installation

```bash
pip install -r requirements.txt
```

## Running Tests

```bash
python -m pytest tests/
```

## Performance Testing

```bash
python performance_test.py
```
