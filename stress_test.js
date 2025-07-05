const { StreamingRankingEngine, generateTestPosts } = require('./ranking_engine');

/**
 * Comprehensive stress test for the ranking engine
 * Tests with 100,000s and 1,000,000s of posts
 */

function formatNumber(num) {
    return num.toLocaleString();
}

function formatBytes(bytes) {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}

function getMemoryUsage() {
    if (typeof process !== 'undefined' && process.memoryUsage) {
        const mem = process.memoryUsage();
        return {
            heapUsed: formatBytes(mem.heapUsed),
            heapTotal: formatBytes(mem.heapTotal),
            external: formatBytes(mem.external),
            rss: formatBytes(mem.rss)
        };
    }
    return null;
}

function printMemoryUsage(label) {
    const mem = getMemoryUsage();
    if (mem) {
        console.log(`  💾 ${label}:`);
        console.log(`    Heap Used: ${mem.heapUsed}`);
        console.log(`    Heap Total: ${mem.heapTotal}`);
        console.log(`    RSS: ${mem.rss}`);
    }
}

async function stressTest(numPosts, algorithm = 'hot_score', topK = 100) {
    console.log(`\n🚀 STRESS TEST: ${formatNumber(numPosts)} posts with ${algorithm.toUpperCase()}`);
    console.log('=' * 60);
    
    const startTime = performance.now();
    const startMemory = getMemoryUsage();
    
    console.log(`📊 Generating ${formatNumber(numPosts)} test posts...`);
    const posts = generateTestPosts(numPosts);
    
    const generationTime = performance.now();
    console.log(`✅ Generated ${formatNumber(posts.length)} posts in ${((generationTime - startTime) / 1000).toFixed(3)}s`);
    printMemoryUsage('After Generation');
    
    console.log(`\n🔧 Creating ranking engine...`);
    const engine = new StreamingRankingEngine(50000);
    
    console.log(`📈 Ranking posts with ${algorithm} algorithm...`);
    const rankingStart = performance.now();
    
    const result = engine.rankPostsFromList(posts, algorithm, topK);
    
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
    
    printMemoryUsage('Final');
    
    return {
        numPosts,
        algorithm,
        totalTime,
        rankingTime,
        postsPerSecond: numPosts / rankingTime,
        topScore: result.topPosts[0]?.[0],
        memoryUsage: result.memoryUsageMb,
        startMemory,
        endMemory
    };
}

async function runComprehensiveTests() {
    console.log('🔥 COMPREHENSIVE RANKING ENGINE STRESS TESTS');
    console.log('=' * 80);
    
    const testConfigs = [
        { posts: 100000, algorithm: 'hot_score' },
        { posts: 100000, algorithm: 'engagement_score' },
        { posts: 100000, algorithm: 'time_decay' },
        { posts: 500000, algorithm: 'hot_score' },
        { posts: 500000, algorithm: 'engagement_score' },
        { posts: 1000000, algorithm: 'hot_score' },
        { posts: 1000000, algorithm: 'engagement_score' },
        { posts: 2000000, algorithm: 'hot_score' }
    ];
    
    const results = [];
    
    for (const config of testConfigs) {
        try {
            const result = await stressTest(config.posts, config.algorithm);
            results.push(result);
            
            // Add a small delay between tests to let memory settle
            await new Promise(resolve => setTimeout(resolve, 1000));
            
        } catch (error) {
            console.error(`❌ Test failed for ${formatNumber(config.posts)} posts with ${config.algorithm}:`, error.message);
        }
    }
    
    // Print summary
    console.log('\n' + '=' * 80);
    console.log('📊 COMPREHENSIVE TEST SUMMARY');
    console.log('=' * 80);
    
    console.log('\n🏆 Performance Summary:');
    console.log('Posts | Algorithm | Time (s) | Posts/sec | Memory (MB)');
    console.log('-'.repeat(60));
    
    results.forEach(result => {
        console.log(`${formatNumber(result.numPosts).padStart(7)} | ${result.algorithm.padEnd(15)} | ${result.rankingTime.toFixed(3).padStart(7)} | ${result.postsPerSecond.toFixed(0).padStart(8)} | ${result.memoryUsage.toFixed(1).padStart(8)}`);
    });
    
    // Find best performance
    const bestPerformance = results.reduce((best, current) => 
        current.postsPerSecond > best.postsPerSecond ? current : best
    );
    
    console.log(`\n🏅 Best Performance: ${formatNumber(bestPerformance.numPosts)} posts with ${bestPerformance.algorithm} at ${bestPerformance.postsPerSecond.toFixed(0)} posts/sec`);
    
    // Save results
    const fs = require('fs');
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `stress_test_results_${timestamp}.json`;
    
    fs.writeFileSync(filename, JSON.stringify({
        timestamp: new Date().toISOString(),
        results,
        summary: {
            totalTests: results.length,
            bestPerformance: {
                posts: bestPerformance.numPosts,
                algorithm: bestPerformance.algorithm,
                postsPerSecond: bestPerformance.postsPerSecond
            }
        }
    }, null, 2));
    
    console.log(`\n✅ Results saved to: ${filename}`);
    
    return results;
}

// Memory leak detection
async function memoryLeakTest() {
    console.log('\n🔍 MEMORY LEAK DETECTION TEST');
    console.log('=' * 50);
    
    const iterations = 10;
    const postsPerIteration = 100000;
    const memorySnapshots = [];
    
    for (let i = 0; i < iterations; i++) {
        console.log(`\n🔄 Iteration ${i + 1}/${iterations}`);
        
        const startMem = process.memoryUsage().heapUsed;
        const posts = generateTestPosts(postsPerIteration);
        const engine = new StreamingRankingEngine(50000);
        const result = engine.rankPostsFromList(posts, 'hot_score', 100);
        const endMem = process.memoryUsage().heapUsed;
        
        memorySnapshots.push({
            iteration: i + 1,
            startMemory: startMem,
            endMemory: endMem,
            difference: endMem - startMem
        });
        
        console.log(`  Memory: ${formatBytes(startMem)} → ${formatBytes(endMem)} (${formatBytes(endMem - startMem)})`);
        
        // Force garbage collection if available
        if (global.gc) {
            global.gc();
        }
        
        // Small delay
        await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    const totalMemoryIncrease = memorySnapshots[memorySnapshots.length - 1].endMemory - memorySnapshots[0].startMemory;
    console.log(`\n📊 Memory Leak Analysis:`);
    console.log(`  Total Memory Increase: ${formatBytes(totalMemoryIncrease)}`);
    console.log(`  Average per Iteration: ${formatBytes(totalMemoryIncrease / iterations)}`);
    
    if (totalMemoryIncrease > 50 * 1024 * 1024) { // 50MB threshold
        console.log(`  ⚠️  Potential memory leak detected!`);
    } else {
        console.log(`  ✅ No significant memory leak detected`);
    }
}

// Run tests
async function main() {
    try {
        // Run comprehensive stress tests
        await runComprehensiveTests();
        
        // Run memory leak detection
        await memoryLeakTest();
        
        console.log('\n🎉 All tests completed successfully!');
        
    } catch (error) {
        console.error('❌ Test suite failed:', error);
        process.exit(1);
    }
}

// Export for use
module.exports = {
    stressTest,
    runComprehensiveTests,
    memoryLeakTest
};

// Run if called directly
if (require.main === module) {
    main();
} 