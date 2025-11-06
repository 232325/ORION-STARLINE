/**
 * Sentiment Analyzer Edge Function
 * Purpose: Advanced sentiment analysis for trading signals
 * Directive: B) New AI/ML Modules Integration
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
        const { action, symbol, text, source } = await req.json();

        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

        let result: any = {};

        switch (action) {
            case 'analyze':
                result = await analyzeSentiment(supabaseUrl!, serviceRoleKey!, text, symbol, source);
                break;

            case 'aggregate':
                result = await aggregateSentiment(supabaseUrl!, serviceRoleKey!, symbol);
                break;

            case 'trending':
                result = await getTrendingSentiments(supabaseUrl!, serviceRoleKey!);
                break;

            default:
                throw new Error('Invalid action');
        }

        return new Response(JSON.stringify({ data: result }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error: any) {
        console.error('Sentiment Analyzer error:', error);

        return new Response(JSON.stringify({
            error: {
                code: 'SENTIMENT_ANALYSIS_ERROR',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

/**
 * Analyze sentiment of text
 */
async function analyzeSentiment(
    supabaseUrl: string,
    serviceRoleKey: string,
    text: string,
    symbol: string,
    source: string
): Promise<any> {
    // Perform sentiment analysis
    const sentimentResult = performTextSentimentAnalysis(text);

    // Extract keywords and entities
    const keywords = extractKeywords(text);
    const entities = extractEntities(text, symbol);

    // Save to database
    const insertResponse = await fetch(`${supabaseUrl}/rest/v1/sentiment_analysis`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey,
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        },
        body: JSON.stringify({
            source,
            symbol,
            content: text,
            sentiment_score: sentimentResult.score,
            sentiment_label: sentimentResult.label,
            confidence: sentimentResult.confidence,
            keywords,
            entities,
            model_used: 'rule_based_v1'
        })
    });

    const savedData = await insertResponse.json();

    return {
        ...sentimentResult,
        keywords,
        entities,
        saved: savedData[0]
    };
}

/**
 * Aggregate sentiment for a symbol
 */
async function aggregateSentiment(
    supabaseUrl: string,
    serviceRoleKey: string,
    symbol: string
): Promise<any> {
    // Get recent sentiment data (last 24 hours)
    const oneDayAgo = new Date(Date.now() - 86400000).toISOString();

    const response = await fetch(
        `${supabaseUrl}/rest/v1/sentiment_analysis?symbol=eq.${symbol}&created_at=gte.${oneDayAgo}&order=created_at.desc`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    const sentiments = await response.json();

    if (sentiments.length === 0) {
        return {
            symbol,
            overallSentiment: 'neutral',
            score: 0,
            dataPoints: 0,
            message: 'No sentiment data available'
        };
    }

    // Calculate weighted average
    const weightedScores = sentiments.map((s: any, index: number) => {
        const recencyWeight = 1 - (index / sentiments.length) * 0.5; // More recent = higher weight
        const confidenceWeight = parseFloat(s.confidence || 0.5);
        return parseFloat(s.sentiment_score) * recencyWeight * confidenceWeight;
    });

    const totalWeight = sentiments.reduce((sum: number, s: any, index: number) => {
        const recencyWeight = 1 - (index / sentiments.length) * 0.5;
        const confidenceWeight = parseFloat(s.confidence || 0.5);
        return sum + recencyWeight * confidenceWeight;
    }, 0);

    const avgScore = weightedScores.reduce((a: number, b: number) => a + b, 0) / totalWeight;

    // Group by source
    const bySource: { [key: string]: number } = {};
    sentiments.forEach((s: any) => {
        if (!bySource[s.source]) {
            bySource[s.source] = 0;
        }
        bySource[s.source]++;
    });

    // Determine overall sentiment
    let overallSentiment = 'neutral';
    if (avgScore > 0.3) overallSentiment = avgScore > 0.6 ? 'very_positive' : 'positive';
    if (avgScore < -0.3) overallSentiment = avgScore < -0.6 ? 'very_negative' : 'negative';

    return {
        symbol,
        overallSentiment,
        score: avgScore.toFixed(4),
        dataPoints: sentiments.length,
        breakdown: {
            bySource,
            positiveCount: sentiments.filter((s: any) => parseFloat(s.sentiment_score) > 0.3).length,
            neutralCount: sentiments.filter((s: any) => Math.abs(parseFloat(s.sentiment_score)) <= 0.3).length,
            negativeCount: sentiments.filter((s: any) => parseFloat(s.sentiment_score) < -0.3).length
        },
        recentTrend: calculateTrend(sentiments),
        topKeywords: aggregateKeywords(sentiments)
    };
}

/**
 * Get trending sentiments
 */
async function getTrendingSentiments(
    supabaseUrl: string,
    serviceRoleKey: string
): Promise<any> {
    // Get recent sentiment data
    const oneHourAgo = new Date(Date.now() - 3600000).toISOString();

    const response = await fetch(
        `${supabaseUrl}/rest/v1/sentiment_analysis?created_at=gte.${oneHourAgo}`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    const sentiments = await response.json();

    // Group by symbol
    const symbolGroups: { [key: string]: any[] } = {};
    sentiments.forEach((s: any) => {
        if (!symbolGroups[s.symbol]) {
            symbolGroups[s.symbol] = [];
        }
        symbolGroups[s.symbol].push(s);
    });

    // Calculate average sentiment for each symbol
    const trending = Object.keys(symbolGroups).map(symbol => {
        const group = symbolGroups[symbol];
        const avgScore = group.reduce((sum: number, s: any) => sum + parseFloat(s.sentiment_score), 0) / group.length;
        
        return {
            symbol,
            sentimentScore: avgScore.toFixed(4),
            mentions: group.length,
            sources: [...new Set(group.map((s: any) => s.source))],
            label: avgScore > 0.3 ? 'positive' : avgScore < -0.3 ? 'negative' : 'neutral'
        };
    }).sort((a, b) => b.mentions - a.mentions);

    return {
        period: 'last_hour',
        trending: trending.slice(0, 10), // Top 10
        totalSymbols: Object.keys(symbolGroups).length,
        totalMentions: sentiments.length
    };
}

/**
 * Perform text sentiment analysis
 */
function performTextSentimentAnalysis(text: string): any {
    const lowerText = text.toLowerCase();

    // Positive words
    const positiveWords = ['bullish', 'buy', 'moon', 'profit', 'gain', 'surge', 'rally', 'breakout', 'strong', 'growth', 'opportunity', 'pump'];
    const negativeWords = ['bearish', 'sell', 'dump', 'loss', 'crash', 'fall', 'decline', 'weak', 'risk', 'warning', 'drop'];

    let positiveCount = 0;
    let negativeCount = 0;

    positiveWords.forEach(word => {
        const regex = new RegExp(`\\b${word}\\b`, 'gi');
        const matches = lowerText.match(regex);
        if (matches) positiveCount += matches.length;
    });

    negativeWords.forEach(word => {
        const regex = new RegExp(`\\b${word}\\b`, 'gi');
        const matches = lowerText.match(regex);
        if (matches) negativeCount += matches.length;
    });

    // Calculate score (-1 to 1)
    const total = positiveCount + negativeCount;
    const score = total > 0 ? (positiveCount - negativeCount) / (total + 5) : 0; // +5 for smoothing

    // Calculate confidence
    const confidence = Math.min(total / 10, 1); // More words = higher confidence

    // Determine label
    let label = 'neutral';
    if (score > 0.3) label = score > 0.6 ? 'very_positive' : 'positive';
    if (score < -0.3) label = score < -0.6 ? 'very_negative' : 'negative';

    return {
        score: score.toFixed(4),
        label,
        confidence: confidence.toFixed(4),
        analysis: {
            positiveWords: positiveCount,
            negativeWords: negativeCount,
            totalWords: text.split(/\s+/).length
        }
    };
}

/**
 * Extract keywords from text
 */
function extractKeywords(text: string): string[] {
    const stopWords = ['the', 'is', 'at', 'which', 'on', 'a', 'an', 'as', 'are', 'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'];
    
    const words = text.toLowerCase()
        .replace(/[^a-z0-9\s]/g, '')
        .split(/\s+/)
        .filter(word => word.length > 3 && !stopWords.includes(word));

    // Count frequency
    const frequency: { [key: string]: number } = {};
    words.forEach(word => {
        frequency[word] = (frequency[word] || 0) + 1;
    });

    // Sort by frequency and return top 10
    return Object.keys(frequency)
        .sort((a, b) => frequency[b] - frequency[a])
        .slice(0, 10);
}

/**
 * Extract entities (companies, symbols, etc.)
 */
function extractEntities(text: string, symbol: string): any {
    const entities: any = {
        symbols: [symbol],
        companies: [],
        numbers: []
    };

    // Extract dollar amounts
    const dollarRegex = /\$\d+(?:,\d{3})*(?:\.\d{2})?/g;
    const amounts = text.match(dollarRegex);
    if (amounts) {
        entities.numbers = amounts;
    }

    // Extract percentages
    const percentRegex = /\d+(?:\.\d+)?%/g;
    const percents = text.match(percentRegex);
    if (percents) {
        entities.numbers = [...entities.numbers, ...percents];
    }

    // Extract ticker symbols (3-5 uppercase letters)
    const tickerRegex = /\b[A-Z]{3,5}\b/g;
    const tickers = text.match(tickerRegex);
    if (tickers) {
        entities.symbols = [...new Set([...entities.symbols, ...tickers])];
    }

    return entities;
}

/**
 * Calculate sentiment trend
 */
function calculateTrend(sentiments: any[]): string {
    if (sentiments.length < 5) return 'insufficient_data';

    const recent = sentiments.slice(0, Math.floor(sentiments.length / 2));
    const older = sentiments.slice(Math.floor(sentiments.length / 2));

    const recentAvg = recent.reduce((sum: number, s: any) => sum + parseFloat(s.sentiment_score), 0) / recent.length;
    const olderAvg = older.reduce((sum: number, s: any) => sum + parseFloat(s.sentiment_score), 0) / older.length;

    const diff = recentAvg - olderAvg;

    if (diff > 0.2) return 'improving';
    if (diff < -0.2) return 'deteriorating';
    return 'stable';
}

/**
 * Aggregate keywords from multiple sentiments
 */
function aggregateKeywords(sentiments: any[]): string[] {
    const allKeywords: { [key: string]: number } = {};

    sentiments.forEach((s: any) => {
        if (s.keywords && Array.isArray(s.keywords)) {
            s.keywords.forEach((keyword: string) => {
                allKeywords[keyword] = (allKeywords[keyword] || 0) + 1;
            });
        }
    });

    return Object.keys(allKeywords)
        .sort((a, b) => allKeywords[b] - allKeywords[a])
        .slice(0, 10);
}
