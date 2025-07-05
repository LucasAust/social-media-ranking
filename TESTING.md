# 🧪 Testing Guide for Social Media Ranking Engine

This guide shows you how to test the ranking engine with 100,000s and 1,000,000s of posts.

## 🚀 Quick Tests

### Test Specific Post Counts

```bash
# Test with 100,000 posts
npm run test-100k
# or
node quick_test.js 100000

# Test with 500,000 posts
npm run test-500k
# or
node quick_test.js 500000

# Test with 1,000,000 posts
npm run test-1m
# or
node quick_test.js 1000000

# Test with 2,000,000 posts
npm run test-2m
# or
node quick_test.js 2000000
```

### Test Different Algorithms

```bash
# Test with hot_score algorithm (default)
node quick_test.js 1000000 hot_score

# Test with engagement_score algorithm
node quick_test.js 1000000 engagement_score

# Test with time_decay algorithm
node quick_test.js 1000000 time_decay
```

## 🔥 Comprehensive Stress Tests

### Run All Stress Tests
```bash
npm run stress-test
# or
node stress_test.js
```

This will test:
- 100,000 posts with all 3 algorithms
- 500,000 posts with hot_score and engagement_score
- 1,000,000 posts with hot_score and engagement_score
- 2,000,000 posts with hot_score
- Memory leak detection

### Expected Results

Based on our tests:

| Posts | Algorithm | Time (s) | Posts/sec | Memory (MB) |
|-------|-----------|----------|-----------|-------------|
| 100,000 | hot_score | ~0.05 | ~1,870,000 | ~24 |
| 500,000 | hot_score | ~0.15 | ~3,330,000 | ~95 |
| 1,000,000 | hot_score | ~0.31 | ~3,270,000 | ~190 |
| 2,000,000 | hot_score | ~0.62 | ~3,230,000 | ~380 |

## 📊 Performance Benchmarks

### Standard Benchmark
```bash
npm run benchmark
# or
node ranking_engine.js
```

This runs the standard benchmark suite and saves results to `javascript_benchmark_results.json`.

## 🧪 Custom Testing

### Test Your Own Data
```javascript
const { StreamingRankingEngine } = require('./ranking_engine');

// Create your own posts
const myPosts = [
    {
        postId: 'post_1',
        likes: 1000,
        comments: 50,
        shares: 25,
        upvotes: 1050,
        downvotes: 10,
        timestamp: Date.now() / 1000
    },
    // ... more posts
];

const engine = new StreamingRankingEngine(50000);
const result = engine.rankPostsFromList(myPosts, 'hot_score', 100);

console.log('Top posts:', result.topPosts.slice(0, 5));
```

### Test with Database Data
```javascript
const { StreamingRankingEngine } = require('./ranking_engine');

async function testWithDatabase() {
    // Fetch posts from your database
    const dbPosts = await fetchPostsFromDatabase();
    
    // Convert to the format expected by the engine
    const posts = dbPosts.map(post => ({
        postId: post.id,
        likes: post.likes || 0,
        comments: post.comments || 0,
        shares: post.shares || 0,
        upvotes: post.upvotes || 0,
        downvotes: post.downvotes || 0,
        timestamp: new Date(post.created_at).getTime() / 1000
    }));
    
    const engine = new StreamingRankingEngine(50000);
    const result = engine.rankPostsFromList(posts, 'hot_score', 100);
    
    return result;
}
```

## 🔍 Memory Monitoring

### Enable Garbage Collection (for memory leak detection)
```bash
# Run with garbage collection enabled
node --expose-gc stress_test.js
```

### Monitor Memory Usage
The stress tests automatically monitor:
- Heap used memory
- Heap total memory
- RSS (Resident Set Size)
- Engine-specific memory usage

## 📈 Performance Tips

### For Maximum Performance
1. **Use appropriate batch sizes**: 50,000 posts per batch works well
2. **Choose the right algorithm**: 
   - `hot_score`: Best for Reddit-style content
   - `engagement_score`: Best for social media engagement
   - `time_decay`: Best for time-sensitive content
3. **Monitor memory**: Keep an eye on memory usage for very large datasets

### For Production Testing
1. **Test with real data**: Use actual post data from your database
2. **Test under load**: Run multiple ranking operations simultaneously
3. **Monitor performance**: Track posts/second and memory usage
4. **Test edge cases**: Empty posts, malformed data, etc.

## 🐛 Troubleshooting

### Common Issues

**Out of Memory Error**
```bash
# Increase Node.js memory limit
node --max-old-space-size=4096 quick_test.js 1000000
```

**Slow Performance**
- Check if your system has enough RAM
- Try smaller batch sizes
- Use a faster algorithm for your use case

**Incorrect Results**
- Verify your post data format
- Check that timestamps are in seconds (not milliseconds)
- Ensure all required fields are present

## 📊 Expected Performance

### Hardware Requirements
- **RAM**: 2GB+ for 1M+ posts
- **CPU**: Any modern CPU (V8 JIT optimizes well)
- **Storage**: Minimal (all processing in memory)

### Performance Targets
- **100,000 posts**: < 0.1 seconds
- **1,000,000 posts**: < 0.5 seconds
- **10,000,000 posts**: < 5 seconds

### Memory Usage
- **100,000 posts**: ~25MB
- **1,000,000 posts**: ~190MB
- **10,000,000 posts**: ~1.9GB

## 🎯 Next Steps

1. **Start with quick tests**: `npm run test-100k`
2. **Run comprehensive tests**: `npm run stress-test`
3. **Test with your data**: Integrate with your database
4. **Monitor in production**: Track performance metrics
5. **Optimize as needed**: Adjust batch sizes and algorithms

---

**🚀 Your ranking engine is ready for production-scale testing!** 