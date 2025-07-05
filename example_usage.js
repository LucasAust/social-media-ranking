const { StreamingRankingEngine, generateTestPosts } = require('./ranking_engine');

// Generate 10,000 test posts
testPosts = generateTestPosts(10000);

// Create the ranking engine
const engine = new StreamingRankingEngine(50000);

// Rank posts using the 'hot_score' algorithm
const result = engine.rankPostsFromList(testPosts, 'hot_score', 100);

console.log('Top post score:', result.topPosts[0][0]);
console.log('Processed', result.totalPostsProcessed, 'posts in', result.processingTimeSeconds.toFixed(3), 'seconds'); 