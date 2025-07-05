const { createUltraFastRankingEngine, UltraFastUtils } = require('./ultra_fast_ranking');

/**
 * Quick test for specific post counts
 * Usage: node quick_test.js [postCount] [algorithm]
 * Examples:
 *   node quick_test.js 100000 hot_score
 *   node quick_test.js 1000000 engagement_score
 */

function formatNumber(num) {
    return num.toLocaleString();
}

function getMemoryUsage() {
    if (typeof process !== 'undefined' && process.memoryUsage) {
        const mem = process.memoryUsage();
        return {
            heapUsed: (mem.heapUsed / 1024 / 1024).toFixed(1) + ' MB',
            heapTotal: (mem.heapTotal / 1024 / 1024).toFixed(1) + ' MB',
            rss: (mem.rss / 1024 / 1024).toFixed(1) + ' MB'
        };
    }
    return null;
}

async function quickTest(numPosts, algorithm = 'hot_score') {
    console.log(`🚀 QUICK TEST: ${formatNumber(numPosts)} posts with ${algorithm.toUpperCase()}`);
    console.log('='.repeat(50));
    
    const startTime = performance.now();
    const startMemory = getMemoryUsage();
    
    console.log(`📊 Generating ${formatNumber(numPosts)} posts...`);
    const posts = UltraFastUtils.generateTestPosts(numPosts);
    
    const generationTime = performance.now();
    console.log(`✅ Generated in ${((generationTime - startTime) / 1000).toFixed(3)}s`);
    console.log(`💾 Memory after generation: ${startMemory?.heapUsed}`);
    
    console.log(`\n🔧 Creating ranking engine...`);
    const engine = createUltraFastRankingEngine({ batchSize: 50000 });
    
    console.log(`📈 Ranking posts...`);
    const rankingStart = performance.now();
    
    const result = engine.rankPosts(posts, algorithm, 100);
    
    const endTime = performance.now();
    const rankingTime = (endTime - rankingStart) / 1000;
    const totalTime = (endTime - startTime) / 1000;
    const endMemory = getMemoryUsage();
    
    console.log(`\n📊 RESULTS:`);
    console.log(`  ⏱️  Total Time: ${totalTime.toFixed(3)}s`);
    console.log(`  🚀 Ranking Time: ${rankingTime.toFixed(3)}s`);
    console.log(`  📈 Posts/Second: ${(numPosts / rankingTime).toFixed(0)}`);
    console.log(`  🏆 Top Score: ${result.topPosts[0]?.[0].toFixed(6)}`);
    console.log(`  📊 Top Post ID: ${result.topPosts[0]?.[1].postId}`);
    console.log(`  💾 Engine Memory: ${result.memoryUsageMb.toFixed(1)} MB`);
    console.log(`  💾 Process Memory: ${endMemory?.heapUsed}`);
    
    return {
        numPosts,
        algorithm,
        totalTime,
        rankingTime,
        postsPerSecond: numPosts / rankingTime,
        topScore: result.topPosts[0]?.[0],
        memoryUsage: result.memoryUsageMb
    };
}

// Get command line arguments
const args = process.argv.slice(2);
const numPosts = parseInt(args[0]) || 100000;
const algorithm = args[1] || 'hot_score';

// Validate inputs
if (numPosts <= 0) {
    console.error('❌ Invalid post count. Please provide a positive number.');
    process.exit(1);
}

const validAlgorithms = ['hot_score', 'engagement_score', 'time_decay'];
if (!validAlgorithms.includes(algorithm)) {
    console.error(`❌ Invalid algorithm. Please use one of: ${validAlgorithms.join(', ')}`);
    process.exit(1);
}

// Run the test
quickTest(numPosts, algorithm)
    .then(result => {
        console.log(`\n✅ Test completed successfully!`);
        console.log(`🏅 Performance: ${result.postsPerSecond.toFixed(0)} posts/sec`);
    })
    .catch(error => {
        console.error('❌ Test failed:', error.message);
        process.exit(1);
    }); 