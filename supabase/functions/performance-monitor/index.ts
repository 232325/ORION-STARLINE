/**
 * Performance Monitor Edge Function
 * Purpose: Monitor and optimize system performance
 * Directive: A) Database & Performance Optimization
 */

Deno.serve(async (req) => {
    const corsHeaders = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS, PUT, DELETE, PATCH',
        'Access-Control-Max-Age': '86400',
        'Access-Control-Allow-Credentials': 'false'
    };

    if (req.method === 'OPTIONS') {
        return new Response(null, { status: 200, headers: corsHeaders });
    }

    try {
        const { action, metricType, timeRange } = await req.json();

        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

        let result: any = {};

        switch (action) {
            case 'record_metric':
                const { metricName, value, unit, metadata } = await req.json();
                result = await recordMetric(supabaseUrl!, serviceRoleKey!, metricType, metricName, value, unit, metadata);
                break;

            case 'get_metrics':
                result = await getMetrics(supabaseUrl!, serviceRoleKey!, metricType, timeRange || '1h');
                break;

            case 'analyze_performance':
                result = await analyzePerformance(supabaseUrl!, serviceRoleKey!);
                break;

            case 'get_cache_stats':
                result = await getCacheStatistics(supabaseUrl!, serviceRoleKey!);
                break;

            case 'optimize_cache':
                result = await optimizeCache(supabaseUrl!, serviceRoleKey!);
                break;

            default:
                throw new Error('Invalid action');
        }

        return new Response(JSON.stringify({ data: result }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error: any) {
        console.error('Performance Monitor error:', error);

        return new Response(JSON.stringify({
            error: {
                code: 'PERFORMANCE_MONITOR_ERROR',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

/**
 * Record performance metric
 */
async function recordMetric(
    supabaseUrl: string,
    serviceRoleKey: string,
    metricType: string,
    metricName: string,
    value: number,
    unit: string,
    metadata: any
): Promise<any> {
    const response = await fetch(`${supabaseUrl}/rest/v1/performance_metrics`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey,
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        },
        body: JSON.stringify({
            metric_type: metricType,
            metric_name: metricName,
            value,
            unit,
            metadata,
            recorded_at: new Date().toISOString()
        })
    });

    const data = await response.json();

    return {
        success: true,
        metric: data[0],
        message: 'Metric recorded successfully'
    };
}

/**
 * Get performance metrics
 */
async function getMetrics(
    supabaseUrl: string,
    serviceRoleKey: string,
    metricType: string,
    timeRange: string
): Promise<any> {
    // Calculate time range
    const now = new Date();
    let startTime = new Date(now);

    switch (timeRange) {
        case '1h':
            startTime.setHours(now.getHours() - 1);
            break;
        case '24h':
            startTime.setHours(now.getHours() - 24);
            break;
        case '7d':
            startTime.setDate(now.getDate() - 7);
            break;
        case '30d':
            startTime.setDate(now.getDate() - 30);
            break;
        default:
            startTime.setHours(now.getHours() - 1);
    }

    let url = `${supabaseUrl}/rest/v1/performance_metrics?recorded_at=gte.${startTime.toISOString()}&order=recorded_at.asc`;
    
    if (metricType) {
        url += `&metric_type=eq.${metricType}`;
    }

    const response = await fetch(url, {
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey
        }
    });

    const metrics = await response.json();

    // Calculate statistics
    const stats = calculateMetricStats(metrics);

    return {
        timeRange,
        metricType,
        totalDataPoints: metrics.length,
        metrics,
        statistics: stats
    };
}

/**
 * Analyze overall system performance
 */
async function analyzePerformance(
    supabaseUrl: string,
    serviceRoleKey: string
): Promise<any> {
    // Get recent metrics (last hour)
    const oneHourAgo = new Date(Date.now() - 3600000).toISOString();

    const metricsResponse = await fetch(
        `${supabaseUrl}/rest/v1/performance_metrics?recorded_at=gte.${oneHourAgo}`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    const metrics = await metricsResponse.json();

    // Group metrics by type
    const groupedMetrics: { [key: string]: any[] } = {};
    metrics.forEach((m: any) => {
        if (!groupedMetrics[m.metric_type]) {
            groupedMetrics[m.metric_type] = [];
        }
        groupedMetrics[m.metric_type].push(m);
    });

    // Analyze each metric type
    const analysis: any = {};

    Object.keys(groupedMetrics).forEach(type => {
        const typeMetrics = groupedMetrics[type];
        const values = typeMetrics.map((m: any) => parseFloat(m.value));
        const avg = values.reduce((a: number, b: number) => a + b, 0) / values.length;
        const max = Math.max(...values);
        const min = Math.min(...values);

        analysis[type] = {
            dataPoints: values.length,
            average: avg.toFixed(2),
            max: max.toFixed(2),
            min: min.toFixed(2),
            trend: values.length >= 2 ? (values[values.length - 1] > values[0] ? 'increasing' : 'decreasing') : 'stable'
        };
    });

    // Check for performance issues
    const issues: any[] = [];

    if (analysis['api_response']?.average > 1000) {
        issues.push({
            type: 'slow_api_response',
            severity: 'high',
            message: `Average API response time ${analysis['api_response'].average}ms exceeds threshold`
        });
    }

    if (analysis['cache_hit']?.average < 0.5) {
        issues.push({
            type: 'low_cache_hit_rate',
            severity: 'medium',
            message: `Cache hit rate ${(analysis['cache_hit'].average * 100).toFixed(0)}% is below optimal`
        });
    }

    return {
        timestamp: new Date().toISOString(),
        period: 'last_hour',
        analysis,
        issues,
        healthScore: calculateHealthScore(analysis, issues)
    };
}

/**
 * Get cache statistics
 */
async function getCacheStatistics(
    supabaseUrl: string,
    serviceRoleKey: string
): Promise<any> {
    const response = await fetch(`${supabaseUrl}/rest/v1/cache_entries`, {
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey
        }
    });

    const cacheEntries = await response.json();

    const now = new Date();
    const expired = cacheEntries.filter((e: any) => new Date(e.expires_at) < now);
    const active = cacheEntries.filter((e: any) => new Date(e.expires_at) >= now);

    const totalHits = cacheEntries.reduce((sum: number, e: any) => sum + (e.hit_count || 0), 0);
    const avgHits = cacheEntries.length > 0 ? totalHits / cacheEntries.length : 0;

    return {
        totalEntries: cacheEntries.length,
        activeEntries: active.length,
        expiredEntries: expired.length,
        totalHits,
        averageHitsPerEntry: avgHits.toFixed(2),
        hitRate: cacheEntries.length > 0 ? (totalHits / (cacheEntries.length * 10)).toFixed(2) : '0.00',
        recommendations: generateCacheRecommendations(active, expired, avgHits)
    };
}

/**
 * Optimize cache
 */
async function optimizeCache(
    supabaseUrl: string,
    serviceRoleKey: string
): Promise<any> {
    // Remove expired cache entries
    const now = new Date().toISOString();

    const deleteResponse = await fetch(
        `${supabaseUrl}/rest/v1/cache_entries?expires_at=lt.${now}`,
        {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    // Get low-hit entries
    const lowHitResponse = await fetch(
        `${supabaseUrl}/rest/v1/cache_entries?hit_count=lt.5`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    const lowHitEntries = await lowHitResponse.json();

    // Remove low-hit entries older than 1 day
    const oneDayAgo = new Date(Date.now() - 86400000).toISOString();
    await fetch(
        `${supabaseUrl}/rest/v1/cache_entries?hit_count=lt.5&created_at=lt.${oneDayAgo}`,
        {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    return {
        success: true,
        expiredRemoved: 'Expired entries cleaned',
        lowHitRemoved: lowHitEntries.filter((e: any) => new Date(e.created_at) < new Date(oneDayAgo)).length,
        message: 'Cache optimized successfully'
    };
}

/**
 * Calculate metric statistics
 */
function calculateMetricStats(metrics: any[]): any {
    if (metrics.length === 0) {
        return {
            count: 0,
            average: 0,
            min: 0,
            max: 0,
            stdDev: 0
        };
    }

    const values = metrics.map((m: any) => parseFloat(m.value));
    const avg = values.reduce((a: number, b: number) => a + b, 0) / values.length;
    const max = Math.max(...values);
    const min = Math.min(...values);
    
    const variance = values.reduce((sum: number, val: number) => sum + Math.pow(val - avg, 2), 0) / values.length;
    const stdDev = Math.sqrt(variance);

    return {
        count: metrics.length,
        average: avg.toFixed(2),
        min: min.toFixed(2),
        max: max.toFixed(2),
        stdDev: stdDev.toFixed(2)
    };
}

/**
 * Calculate health score
 */
function calculateHealthScore(analysis: any, issues: any[]): string {
    let score = 100;

    // Deduct points for each issue
    issues.forEach((issue: any) => {
        if (issue.severity === 'critical') score -= 30;
        else if (issue.severity === 'high') score -= 20;
        else if (issue.severity === 'medium') score -= 10;
        else score -= 5;
    });

    score = Math.max(0, score);

    if (score >= 90) return 'Excellent';
    if (score >= 75) return 'Good';
    if (score >= 60) return 'Fair';
    if (score >= 40) return 'Poor';
    return 'Critical';
}

/**
 * Generate cache recommendations
 */
function generateCacheRecommendations(active: any[], expired: any[], avgHits: number): string[] {
    const recommendations: string[] = [];

    if (expired.length > active.length * 0.2) {
        recommendations.push('High number of expired entries - consider adjusting TTL values');
    }

    if (avgHits < 5) {
        recommendations.push('Low cache hit rate - review caching strategy');
    }

    if (active.length > 1000) {
        recommendations.push('Large cache size - consider implementing cache eviction policy');
    }

    if (recommendations.length === 0) {
        recommendations.push('Cache is optimally configured');
    }

    return recommendations;
}
