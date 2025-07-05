/**
 * JavaScript Ranking Engine - Performance comparison with Python version
 */

class Post {
    constructor(postId, options = {}) {
        this.postId = postId;
        this.likes = options.likes || 0;
        this.comments = options.comments || 0;
        this.shares = options.shares || 0;
        this.upvotes = options.upvotes || 0;
        this.downvotes = options.downvotes || 0;
        this.timestamp = options.timestamp || Date.now() / 1000;
        this.baseScore = this.likes + this.comments * 2 + this.shares * 3;
    }

    updateBaseScore() {
        this.baseScore = this.likes + this.comments * 2 + this.shares * 3;
    }
}

class StreamingRankingEngine {
    constructor(batchSize = 100000, maxHeapSize = 1000) {
        this.batchSize = batchSize;
        this.maxHeapSize = maxHeapSize;
    }

    hotScore(post) {
        const order = Math.log10(Math.max(Math.abs(post.upvotes - post.downvotes), 1));
        const sign = post.upvotes - post.downvotes > 0 ? 1 : 
                    post.upvotes - post.downvotes < 0 ? -1 : 0;
        const seconds = Date.now() / 1000 - post.timestamp - 1134028003;
        return Math.round((sign * order + seconds / 45000) * 10000000) / 10000000;
    }

    engagementScore(post) {
        const totalEngagement = post.likes + post.comments * 2 + post.shares * 3;
        const timeFactor = Date.now() / 1000 - post.timestamp + 1;
        return totalEngagement / timeFactor;
    }

    timeDecayScore(post, decayRate = 0.01) {
        const timeElapsed = Date.now() / 1000 - post.timestamp;
        return post.baseScore * Math.exp(-decayRate * timeElapsed);
    }

    calculateScore(post, algorithm, options = {}) {
        switch (algorithm) {
            case "hot_score":
                return this.hotScore(post);
            case "engagement_score":
                return this.engagementScore(post);
            case "time_decay":
                const decayRate = options.decayRate || 0.01;
                return this.timeDecayScore(post, decayRate);
            default:
                throw new Error(`Unknown algorithm: ${algorithm}`);
        }
    }

    rankPostsStreaming(postIterator, algorithm = "hot_score", topK = 100, options = {}) {
        const startTime = performance.now();
        const startMemory = this.getMemoryUsage();

        const minHeap = [];
        let totalPosts = 0;
        let batchCount = 0;

        try {
            while (true) {
                const batch = [];
                for (let i = 0; i < this.batchSize; i++) {
                    const next = postIterator.next();
                    if (next.done) break;
                    batch.push(next.value);
                    totalPosts++;
                }

                if (batch.length === 0) break;

                batchCount++;
                console.log(`Processing batch ${batchCount} (${batch.length} posts, total: ${totalPosts.toLocaleString()})`);

                for (const post of batch) {
                    const score = this.calculateScore(post, algorithm, options);

                    if (minHeap.length < topK) {
                        minHeap.push([score, post.postId, post]);
                        this.heapifyUp(minHeap, minHeap.length - 1);
                    } else {
                        if (score > minHeap[0][0]) {
                            minHeap[0] = [score, post.postId, post];
                            this.heapifyDown(minHeap, 0);
                        }
                    }
                }

                if (batchCount % 10 === 0) {
                    const currentMemory = this.getMemoryUsage();
                    console.log(`  Memory usage: ${currentMemory.toFixed(1)} MB`);
                }
            }
        } catch (error) {
            console.error(`Error during streaming ranking: ${error}`);
            throw error;
        }

        const topPosts = minHeap
            .sort((a, b) => b[0] - a[0])
            .map(([score, postId, post]) => [score, post]);

        const endTime = performance.now();
        const endMemory = this.getMemoryUsage();

        return {
            topPosts: topPosts,
            totalPostsProcessed: totalPosts,
            memoryUsageMb: endMemory,
            processingTimeSeconds: (endTime - startTime) / 1000,
            algorithm: algorithm,
            batchSize: this.batchSize
        };
    }

    heapifyUp(heap, index) {
        while (index > 0) {
            const parentIndex = Math.floor((index - 1) / 2);
            if (heap[parentIndex][0] <= heap[index][0]) break;
            [heap[parentIndex], heap[index]] = [heap[index], heap[parentIndex]];
            index = parentIndex;
        }
    }

    heapifyDown(heap, index) {
        while (true) {
            let smallest = index;
            const leftChild = 2 * index + 1;
            const rightChild = 2 * index + 2;

            if (leftChild < heap.length && heap[leftChild][0] < heap[smallest][0]) {
                smallest = leftChild;
            }
            if (rightChild < heap.length && heap[rightChild][0] < heap[smallest][0]) {
                smallest = rightChild;
            }

            if (smallest === index) break;
            [heap[index], heap[smallest]] = [heap[smallest], heap[index]];
            index = smallest;
        }
    }

    getMemoryUsage() {
        if (typeof process !== 'undefined' && process.memoryUsage) {
            return process.memoryUsage().heapUsed / 1024 / 1024;
        }
        return 0;
    }

    rankPostsFromList(posts, algorithm = "hot_score", topK = 100, options = {}) {
        const postIterator = {
            next: function() {
                if (this.index >= posts.length) {
                    return { done: true };
                }
                return { done: false, value: posts[this.index++] };
            },
            index: 0
        };

        return this.rankPostsStreaming(postIterator, algorithm, topK, options);
    }
}

function generateTestPosts(numPosts) {
    const baseTime = Date.now() / 1000;
    const posts = [];

    for (let i = 0; i < numPosts; i++) {
        const likes = (i * 7) % 10000 + 1;
        const comments = (i * 3) % 1000 + 1;
        const shares = (i * 5) % 500 + 1;
        const upvotes = likes + (i % 100);
        const downvotes = (i % 50);
        const timestamp = baseTime - (i % (86400 * 30));

        posts.push(new Post(`post_${i.toString().padStart(8, '0')}`, {
            likes,
            comments,
            shares,
            upvotes,
            downvotes,
            timestamp
        }));
    }

    return posts;
}

function benchmarkStreamingRanking(maxPosts = 1000000) {
    console.log(`🚀 JavaScript Streaming Ranking Engine Benchmark (up to ${maxPosts.toLocaleString()} posts)`);
    console.log("=" * 70);

    const results = {};
    const testScales = [10000, 100000, 500000, 1000000].filter(scale => scale <= maxPosts);

    for (const scale of testScales) {
        console.log(`\n📊 Testing ${scale.toLocaleString()} posts...`);
        results[scale] = {};

        const posts = generateTestPosts(scale);
        const engine = new StreamingRankingEngine(50000);

        const algorithms = ["hot_score", "engagement_score", "time_decay"];

        for (const algorithm of algorithms) {
            console.log(`  Running ${algorithm}...`);
            
            const result = engine.rankPostsFromList(posts, algorithm, 100);
            
            results[scale][algorithm] = {
                total_posts: result.totalPostsProcessed,
                processing_time_seconds: result.processingTimeSeconds,
                posts_per_second: result.totalPostsProcessed / result.processingTimeSeconds,
                memory_usage_mb: result.memoryUsageMb,
                memory_per_post_kb: (result.memoryUsageMb * 1024) / result.totalPostsProcessed,
                top_score: result.topPosts[0]?.[0] || 0,
                batch_size: result.batchSize
            };

            console.log(`    ✅ ${result.totalPostsProcessed.toLocaleString()} posts in ${result.processingTimeSeconds.toFixed(3)}s`);
            console.log(`    📈 ${(result.totalPostsProcessed / result.processingTimeSeconds).toFixed(0)} posts/sec`);
            console.log(`    💾 ${result.memoryUsageMb.toFixed(1)} MB memory`);
        }
    }

    return results;
}

function printBenchmarkResults(results) {
    console.log("\n" + "=" * 80);
    console.log("📊 JAVASCRIPT RANKING ENGINE BENCHMARK RESULTS");
    console.log("=" * 80);

    for (const [scale, algorithms] of Object.entries(results)) {
        console.log(`\n🎯 ${parseInt(scale).toLocaleString()} Posts:`);
        console.log("-" * 50);

        for (const [algorithm, metrics] of Object.entries(algorithms)) {
            console.log(`\n  ${algorithm.toUpperCase()}:`);
            console.log(`    ⏱️  Processing Time: ${metrics.processing_time_seconds.toFixed(3)}s`);
            console.log(`    🚀 Throughput: ${metrics.posts_per_second.toFixed(0)} posts/sec`);
            console.log(`    💾 Memory Usage: ${metrics.memory_usage_mb.toFixed(1)} MB`);
            console.log(`    📊 Memory per Post: ${metrics.memory_per_post_kb.toFixed(3)} KB`);
            console.log(`    🏆 Top Score: ${metrics.top_score.toFixed(6)}`);
        }
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        Post,
        StreamingRankingEngine,
        generateTestPosts,
        benchmarkStreamingRanking,
        printBenchmarkResults
    };
}

// Run benchmark if called directly
if (typeof require !== 'undefined' && require.main === module) {
    const results = benchmarkStreamingRanking(100000);
    printBenchmarkResults(results);
    
    // Save results to file
    const fs = require('fs');
    fs.writeFileSync('javascript_benchmark_results.json', JSON.stringify(results, null, 2));
    console.log("\n✅ Results saved to javascript_benchmark_results.json");
} 