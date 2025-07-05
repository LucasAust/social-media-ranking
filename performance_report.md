# Social Media Ranking System - Performance Report

## Executive Summary

- **Best Performance**: standard_engagement_score at 1,000 posts
- **Ranking Time**: 0.00ms
- **Throughput**: 100000 posts/second
- **Memory Usage**: 30.5MB

## Detailed Results

### 1,000 Posts

| Algorithm | Engine | Ranking (ms) | Updates (ms) | Memory (MB) | Posts/sec |
|-----------|--------|--------------|--------------|-------------|-----------|
| hot_score | Standard | 1.62 | 0.00 | 30.1 | 61587 |
| hot_score | Optimized | 0.00 | 0.00 | 30.7 | 100000 |
| engagement_score | Standard | 0.00 | 0.00 | 30.5 | 100000 |
| engagement_score | Optimized | 0.00 | 0.00 | 30.9 | 100000 |
| time_decay | Standard | 0.00 | 0.00 | 30.5 | 100000 |
| time_decay | Optimized | 0.00 | 0.00 | 31.0 | 100000 |
| hybrid | Standard | 1.67 | 0.00 | 30.6 | 59724 |
| hybrid | Optimized | 1.14 | 0.00 | 31.1 | 87341 |

### 10,000 Posts

| Algorithm | Engine | Ranking (ms) | Updates (ms) | Memory (MB) | Posts/sec |
|-----------|--------|--------------|--------------|-------------|-----------|
| hot_score | Standard | 3.41 | 0.00 | 36.8 | 29367 |
| hot_score | Optimized | 3.26 | 0.00 | 41.0 | 30661 |
| engagement_score | Standard | 0.40 | 0.06 | 38.7 | 100000 |
| engagement_score | Optimized | 1.69 | 0.00 | 42.7 | 59232 |
| time_decay | Standard | 1.72 | 0.00 | 39.3 | 57995 |
| time_decay | Optimized | 2.47 | 0.00 | 43.6 | 40506 |
| hybrid | Standard | 1.67 | 0.00 | 39.4 | 59809 |
| hybrid | Optimized | 1.76 | 0.00 | 43.7 | 56678 |

### 50,000 Posts

| Algorithm | Engine | Ranking (ms) | Updates (ms) | Memory (MB) | Posts/sec |
|-----------|--------|--------------|--------------|-------------|-----------|
| hot_score | Standard | 11.66 | 0.13 | 67.3 | 8576 |
| hot_score | Optimized | 14.06 | 0.00 | 86.5 | 7112 |
| engagement_score | Standard | 9.92 | 0.08 | 76.4 | 10078 |
| engagement_score | Optimized | 13.70 | 0.04 | 94.4 | 7298 |
| time_decay | Standard | 6.92 | 0.05 | 79.4 | 14450 |
| time_decay | Optimized | 11.26 | 0.00 | 98.0 | 8884 |
| hybrid | Standard | 12.40 | 0.02 | 79.4 | 8067 |
| hybrid | Optimized | 14.72 | 0.03 | 98.1 | 6793 |

### 100,000 Posts

| Algorithm | Engine | Ranking (ms) | Updates (ms) | Memory (MB) | Posts/sec |
|-----------|--------|--------------|--------------|-------------|-----------|
| hot_score | Standard | 34.33 | 0.16 | 118.6 | 2913 |
| hot_score | Optimized | 37.87 | 0.08 | 150.0 | 2641 |
| engagement_score | Standard | 26.45 | 0.17 | 137.7 | 3781 |
| engagement_score | Optimized | 30.56 | 0.08 | 159.6 | 3272 |
| time_decay | Standard | 24.51 | 0.05 | 144.3 | 4080 |
| time_decay | Optimized | 23.28 | 0.09 | 165.8 | 4296 |
| hybrid | Standard | 27.67 | 0.10 | 144.2 | 3614 |
| hybrid | Optimized | 28.07 | 0.00 | 165.9 | 3562 |
