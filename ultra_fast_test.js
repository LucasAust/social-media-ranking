const { createUltraFastRankingEngine, UltraFastUtils } = require('./ultra_fast_ranking');

/**
 * Ultra-fast performance test for the optimized ranking engine
 * Tests with millions of posts to demonstrate extreme performance
 * Usage: node ultra_fast_test.js [maxPosts] [algorithm]
 * Examples:
 *   node ultra_fast_test.js 5000000 hot_score
 *   node ultra_fast_test.js 10000000 engagement_score
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

async function ultraFastTest(maxPosts = 5000000, algorithm = 'hot_score') {
    console.log(`🚀 ULTRA-FAST PERFORMANCE TEST`);
    console.log(`🎯 Target: Up to ${formatNumber(maxPosts)} posts with ${algorithm.toUpperCase()}`);
    console.log('='.repeat(60));
    
    const testSizes = [
        100000,
        500000,
        1000000,
        2500000,
        5000000,
        10000000
    ].filter(size => size <= maxPosts);
    
    const results = [];
    
    for (const numPosts of testSizes) {
        console.log(`\n📊 TESTING ${formatNumber(numPosts)} POSTS`);
        console.log('-'.repeat(40));
        
        const startTime = performance.now();
        const startMemory = getMemoryUsage();
        
        console.log(`🔧 Creating ranking engine...`);
        const engine = createUltraFastRankingEngine({ batchSize: 50000 });
        
        console.log(`📈 Generating and ranking posts...`);
        const rankingStart = performance.now();
        
        // Generate posts in chunks to avoid memory issues
        const chunkSize = 100000;
        let totalProcessed = 0;
        
        for (let i = 0; i < numPosts; i += chunkSize) {
            const currentChunkSize = Math.min(chunkSize, numPosts - i);
            const posts = UltraFastUtils.generateTestPosts(currentChunkSize);
            
            const result = engine.rankPosts(posts, algorithm, 100);
            totalProcessed += currentChunkSize;
            
            if (i === 0) {
                // Show first chunk results
                console.log(`  ✅ First ${formatNumber(currentChunkSize)} posts processed`);
                console.log(`  🏆 Top Score: ${result.topPosts[0]?.[0].toFixed(6)}`);
                console.log(`  💾 Engine Memory: ${result.memoryUsageMb.toFixed(1)} MB`);
            }
        }
        
        const endTime = performance.now();
        const rankingTime = (endTime - rankingStart) / 1000;
        const totalTime = (endTime - startTime) / 1000;
        const endMemory = getMemoryUsage();
        
        const postsPerSecond = numPosts / rankingTime;
        
        console.log(`\n📊 RESULTS for ${formatNumber(numPosts)} posts:`);
        console.log(`  ⏱️  Total Time: ${totalTime.toFixed(3)}s`);
        console.log(`  🚀 Ranking Time: ${rankingTime.toFixed(3)}s`);
        console.log(`  📈 Posts/Second: ${postsPerSecond.toFixed(0)}`);
        console.log(`  💾 Process Memory: ${endMemory?.heapUsed}`);
        
        results.push({
            numPosts,
            totalTime,
            rankingTime,
            postsPerSecond,
            memoryUsage: endMemory?.heapUsed
        });
        
        // Check if we should continue
        if (rankingTime > 30) {
            console.log(`\n⚠️  Test took longer than 30 seconds, stopping here.`);
            break;
        }
    }
    
    // Summary
    console.log(`\n🏆 ULTRA-FAST TEST SUMMARY`);
    console.log('='.repeat(60));
    console.log(`Algorithm: ${algorithm.toUpperCase()}`);
    console.log(`Tests completed: ${results.length}`);
    
    if (results.length > 0) {
        const bestResult = results.reduce((best, current) => 
            current.postsPerSecond > best.postsPerSecond ? current : best
        );
        
        console.log(`\n🥇 BEST PERFORMANCE:`);
        console.log(`  📊 Posts: ${formatNumber(bestResult.numPosts)}`);
        console.log(`  🚀 Speed: ${bestResult.postsPerSecond.toFixed(0)} posts/sec`);
        console.log(`  ⏱️  Time: ${bestResult.rankingTime.toFixed(3)}s`);
        console.log(`  💾 Memory: ${bestResult.memoryUsage}`);
        
        console.log(`\n📈 ALL RESULTS:`);
        results.forEach((result, index) => {
            console.log(`  ${index + 1}. ${formatNumber(result.numPosts)} posts: ${result.postsPerSecond.toFixed(0)} posts/sec (${result.rankingTime.toFixed(3)}s)`);
        });
    }
    
    return results;
}

// Get command line arguments
const args = process.argv.slice(2);
const maxPosts = parseInt(args[0]) || 5000000;
const algorithm = args[1] || 'hot_score';

// Validate inputs
if (maxPosts <= 0) {
    console.error('❌ Invalid max post count. Please provide a positive number.');
    process.exit(1);
}

const validAlgorithms = ['hot_score', 'engagement_score', 'time_decay'];
if (!validAlgorithms.includes(algorithm)) {
    console.error(`❌ Invalid algorithm. Please use one of: ${validAlgorithms.join(', ')}`);
    process.exit(1);
}

// Run the test
ultraFastTest(maxPosts, algorithm)
    .then(results => {
        console.log(`\n✅ Ultra-fast test completed successfully!`);
        if (results.length > 0) {
            const bestSpeed = Math.max(...results.map(r => r.postsPerSecond));
            console.log(`🏅 Peak Performance: ${bestSpeed.toFixed(0)} posts/sec`);
        }
    })
    .catch(error => {
        console.error('❌ Ultra-fast test failed:', error.message);
        process.exit(1);
    }); 