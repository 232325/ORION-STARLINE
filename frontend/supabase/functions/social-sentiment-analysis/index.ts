// Social Sentiment Analysis - Real-time Social Media Monitoring
Deno.serve(async (req) => {
    const corsHeaders = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
    };

    if (req.method === 'OPTIONS') {
        return new Response(null, { headers: corsHeaders, status: 200 });
    }

    try {
        const url = new URL(req.url);
        const symbol = url.searchParams.get('symbol') || 'BTC/USDT';
        const platform = url.searchParams.get('platform') || 'all';

        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

        // Fetch social sentiment data
        let query = `${supabaseUrl}/rest/v1/social_media_sentiment?symbol=eq.${symbol}&order=timestamp.desc&limit=24`;
        if (platform !== 'all') {
            query += `&platform=eq.${platform}`;
        }

        const sentimentResponse = await fetch(query, {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        });

        let sentimentData = [];
        if (sentimentResponse.ok) {
            sentimentData = await sentimentResponse.json();
        }

        // Calculate metrics
        const avgSentiment = sentimentData.length > 0
            ? sentimentData.reduce((sum, s) => sum + (parseFloat(s.sentiment_score) || 0), 0) / sentimentData.length
            : 0;

        const totalMentions = sentimentData.reduce((sum, s) => sum + (s.mention_count || 0), 0);
        const avgFearGreed = sentimentData.length > 0
            ? sentimentData.reduce((sum, s) => sum + (parseFloat(s.fear_greed_index) || 50), 0) / sentimentData.length
            : 50;

        // Calculate trend
        const recentSentiment = sentimentData.slice(0, 6).reduce((sum, s) => sum + parseFloat(s.sentiment_score), 0) / 6;
        const olderSentiment = sentimentData.slice(6, 12).reduce((sum, s) => sum + parseFloat(s.sentiment_score), 0) / 6;
        const trend = recentSentiment > olderSentiment ? 'bullish' : recentSentiment < olderSentiment ? 'bearish' : 'neutral';

        // Platform breakdown
        const platformStats = {};
        sentimentData.forEach(s => {
            if (!platformStats[s.platform]) {
                platformStats[s.platform] = {
                    mentions: 0,
                    sentiment: 0,
                    count: 0
                };
            }
            platformStats[s.platform].mentions += s.mention_count;
            platformStats[s.platform].sentiment += parseFloat(s.sentiment_score);
            platformStats[s.platform].count += 1;
        });

        Object.keys(platformStats).forEach(p => {
            platformStats[p].avg_sentiment = platformStats[p].sentiment / platformStats[p].count;
        });

        return new Response(JSON.stringify({
            sentiment_data: sentimentData.slice(0, 12),
            metrics: {
                average_sentiment: avgSentiment.toFixed(4),
                total_mentions: totalMentions,
                fear_greed_index: avgFearGreed.toFixed(2),
                trend,
                platform_breakdown: platformStats
            },
            signals: {
                bullish_score: avgSentiment > 0.6 ? ((avgSentiment - 0.6) / 0.4 * 100).toFixed(0) : 0,
                bearish_score: avgSentiment < 0.4 ? ((0.4 - avgSentiment) / 0.4 * 100).toFixed(0) : 0,
                recommendation: avgSentiment > 0.65 ? 'strong_buy' : avgSentiment > 0.55 ? 'buy' : avgSentiment < 0.35 ? 'strong_sell' : avgSentiment < 0.45 ? 'sell' : 'hold'
            },
            success: true
        }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    } catch (error) {
        return new Response(JSON.stringify({ error: error.message, success: false }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 500
        });
    }
});
