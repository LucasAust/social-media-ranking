/**
 * Ultra-Fast Social Media Ranking Engine
 * Maximum performance with easy backend integration
 */

class UltraFastPost {
    constructor(data) {
        // Direct property assignment for maximum speed
        this.postId = data.postId || data.post_id || data.id || data._id;
        this.likes = (data.likes || 0) | 0; // Bitwise OR for fast integer conversion
        this.comments = (data.comments || 0) | 0;
        this.shares = (data.shares || 0) | 0;
        this.upvotes = (data.upvotes || 0) | 0;
        this.downvotes = (data.downvotes || 0) | 0;
        
        // Fast timestamp conversion
        this.timestamp = typeof data.timestamp === 'number' 
            ? (data.timestamp > 1000000000000 ? data.timestamp / 1000 : data.timestamp)
            : (data.timestamp ? new Date(data.timestamp).getTime() / 1000 : Date.now() / 1000);
        
        // Pre-calculate base score
        this.baseScore = this.likes + (this.comments << 1) + (this.shares * 3); // Bit shift for *2
    }
}

class UltraFastRankingEngine {
    constructor(options = {}) {
        this.batchSize = options.batchSize || 100000;
        this.enableLogging = options.enableLogging !== false;
        this.cacheResults = options.cacheResults !== false;
        this.cache = new Map();
        this.cacheTimeout = options.cacheTimeout || 60000;
        
        // Pre-calculate constants for performance
        this.REDDIT_EPOCH = 1134028003;
        this.REDDIT_ORDER = 45000;
        this.currentTime = Date.now() / 1000;
    }

    // Ultra-optimized hot score calculation
    hotScore(post) {
        const voteDiff = post.upvotes - post.downvotes;
        const order = Math.log10(Math.max(Math.abs(voteDiff), 1));
        const sign = voteDiff > 0 ? 1 : voteDiff < 0 ? -1 : 0;
        const seconds = this.currentTime - post.timestamp - this.REDDIT_EPOCH;
        return sign * order + seconds / this.REDDIT_ORDER;
    }

    // Ultra-optimized engagement score
    engagementScore(post) {
        const timeFactor = this.currentTime - post.timestamp + 1;
        return post.baseScore / timeFactor;
    }

    // Ultra-optimized time decay score
    timeDecayScore(post, decayRate = 0.01) {
        const timeElapsed = this.currentTime - post.timestamp;
        return post.baseScore * Math.exp(-decayRate * timeElapsed);
    }

    // Fast score calculation with minimal branching
    calculateScore(post, algorithm, options = {}) {
        switch (algorithm) {
            case "hot_score": return this.hotScore(post);
            case "engagement_score": return this.engagementScore(post);
            case "time_decay": return this.timeDecayScore(post, options.decayRate || 0.01);
            default: throw new Error(`Unknown algorithm: ${algorithm}`);
        }
    }

    // Ultra-fast ranking with optimized memory management
    rankPosts(posts, algorithm = "hot_score", topK = 100, options = {}) {
        const startTime = performance.now();
        
        // Update current time once
        this.currentTime = Date.now() / 1000;
        
        // Check cache
        const cacheKey = this.getCacheKey(posts, algorithm, topK, options);
        if (this.cacheResults && this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < this.cacheTimeout) {
                return { ...cached.result, cached: true };
            }
        }

        // Convert posts efficiently
        const optimizedPosts = new Array(posts.length);
        for (let i = 0; i < posts.length; i++) {
            optimizedPosts[i] = posts[i] instanceof UltraFastPost ? posts[i] : new UltraFastPost(posts[i]);
        }

        // Use a more efficient heap implementation
        const minHeap = [];
        const heapLength = Math.min(topK, optimizedPosts.length);

        // Process posts in optimized batches
        for (let i = 0; i < optimizedPosts.length; i += this.batchSize) {
            const batchEnd = Math.min(i + this.batchSize, optimizedPosts.length);
            
            if (this.enableLogging && i % (this.batchSize * 10) === 0) {
                console.log(`Processing batch ${Math.floor(i / this.batchSize) + 1} (${batchEnd}/${optimizedPosts.length} posts)`);
            }

            for (let j = i; j < batchEnd; j++) {
                const post = optimizedPosts[j];
                const score = this.calculateScore(post, algorithm, options);

                if (minHeap.length < heapLength) {
                    minHeap.push([score, post.postId, post]);
                    this.heapifyUp(minHeap, minHeap.length - 1);
                } else if (score > minHeap[0][0]) {
                    minHeap[0] = [score, post.postId, post];
                    this.heapifyDown(minHeap, 0);
                }
            }
        }

        // Sort results efficiently
        const topPosts = minHeap
            .sort((a, b) => b[0] - a[0])
            .map(([score, postId, post]) => [score, post]);

        const endTime = performance.now();
        const result = {
            topPosts,
            totalPostsProcessed: optimizedPosts.length,
            memoryUsageMb: this.getMemoryUsage(),
            processingTimeSeconds: (endTime - startTime) / 1000,
            algorithm,
            postsPerSecond: optimizedPosts.length / ((endTime - startTime) / 1000),
            cached: false
        };

        // Cache the result
        if (this.cacheResults) {
            this.cache.set(cacheKey, {
                result,
                timestamp: Date.now()
            });
        }

        return result;
    }

    // Ultra-optimized heap operations
    heapifyUp(heap, index) {
        while (index > 0) {
            const parentIndex = (index - 1) >> 1;
            if (heap[parentIndex][0] <= heap[index][0]) break;
            [heap[parentIndex], heap[index]] = [heap[index], heap[parentIndex]];
            index = parentIndex;
        }
    }

    heapifyDown(heap, index) {
        const length = heap.length;
        while (true) {
            let smallest = index;
            const leftChild = (index << 1) + 1;
            const rightChild = leftChild + 1;

            if (leftChild < length && heap[leftChild][0] < heap[smallest][0]) {
                smallest = leftChild;
            }
            if (rightChild < length && heap[rightChild][0] < heap[smallest][0]) {
                smallest = rightChild;
            }

            if (smallest === index) break;
            [heap[index], heap[smallest]] = [heap[smallest], heap[index]];
            index = smallest;
        }
    }

    // Fast cache key generation
    getCacheKey(posts, algorithm, topK, options) {
        return `${algorithm}_${topK}_${posts.length}_${JSON.stringify(options)}`;
    }

    // Cache management
    clearCache() {
        this.cache.clear();
    }

    getCacheStats() {
        return {
            size: this.cache.size,
            maxSize: this.maxHeapSize
        };
    }

    // Memory usage
    getMemoryUsage() {
        if (typeof process !== 'undefined' && process.memoryUsage) {
            return process.memoryUsage().heapUsed / 1024 / 1024;
        }
        return 0;
    }

    // Batch ranking for multiple algorithms
    rankPostsMultipleAlgorithms(posts, algorithms = ['hot_score'], topK = 100, options = {}) {
        const results = {};
        
        for (const algorithm of algorithms) {
            results[algorithm] = this.rankPosts(posts, algorithm, topK, options);
        }
        
        return results;
    }
}

// Factory function for easy instantiation
function createUltraFastRankingEngine(options = {}) {
    return new UltraFastRankingEngine(options);
}

// Utility functions optimized for speed
const UltraFastUtils = {
    // Fast database conversion
    convertFromDatabase(dbPosts, idField = 'id') {
        const converted = new Array(dbPosts.length);
        for (let i = 0; i < dbPosts.length; i++) {
            const post = dbPosts[i];
            converted[i] = {
                postId: post[idField],
                likes: (post.likes || 0) | 0,
                comments: (post.comments || 0) | 0,
                shares: (post.shares || 0) | 0,
                upvotes: (post.upvotes || 0) | 0,
                downvotes: (post.downvotes || 0) | 0,
                timestamp: post.created_at || post.timestamp || Date.now() / 1000
            };
        }
        return converted;
    },

    // Fast result formatting
    formatResults(results, includeMetadata = true) {
        const posts = new Array(results.topPosts.length);
        for (let i = 0; i < results.topPosts.length; i++) {
            const [score, post] = results.topPosts[i];
            posts[i] = {
                rank: i + 1,
                postId: post.postId,
                score: score,
                likes: post.likes,
                comments: post.comments,
                shares: post.shares,
                upvotes: post.upvotes,
                downvotes: post.downvotes,
                timestamp: post.timestamp
            };
        }

        const formatted = { posts };

        if (includeMetadata) {
            formatted.metadata = {
                totalPosts: results.totalPostsProcessed,
                processingTime: results.processingTimeSeconds,
                postsPerSecond: results.postsPerSecond,
                algorithm: results.algorithm,
                memoryUsage: results.memoryUsageMb
            };
        }

        return formatted;
    },

    // Fast test data generation
    generateTestPosts(numPosts) {
        const posts = new Array(numPosts);
        const baseTime = Date.now() / 1000;

        for (let i = 0; i < numPosts; i++) {
            const likes = (i * 7) % 10000 + 1;
            const comments = (i * 3) % 1000 + 1;
            const shares = (i * 5) % 500 + 1;
            const upvotes = likes + (i % 100);
            const downvotes = (i % 50);
            const timestamp = baseTime - (i % (86400 * 30));

            posts[i] = {
                postId: `post_${i.toString().padStart(8, '0')}`,
                likes,
                comments,
                shares,
                upvotes,
                downvotes,
                timestamp
            };
        }

        return posts;
    }
};

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        UltraFastRankingEngine,
        UltraFastPost,
        createUltraFastRankingEngine,
        UltraFastUtils
    };
}

// Export for ES modules
if (typeof exports !== 'undefined') {
    exports.UltraFastRankingEngine = UltraFastRankingEngine;
    exports.UltraFastPost = UltraFastPost;
    exports.createUltraFastRankingEngine = createUltraFastRankingEngine;
    exports.UltraFastUtils = UltraFastUtils;
} 