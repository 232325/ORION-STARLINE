// News Trading Bot - Real-time News Analysis
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
        const symbol = url.searchParams.get('symbol') || 'BTC';
        const limit = parseInt(url.searchParams.get('limit') || '10');

        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

        // Fetch recent news
        const newsResponse = await fetch(
            `${supabaseUrl}/rest/v1/news_articles?symbols=cs.{${symbol}}&order=published_at.desc&limit=${limit}`,
            {
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            }
        );

        let news = [];
        if (newsResponse.ok) {
            news = await newsResponse.json();
        }

        // Fetch news signals
        const signalsResponse = await fetch(
            `${supabaseUrl}/rest/v1/news_trading_signals?symbol=eq.${symbol}/USDT&order=created_at.desc&limit=${limit}`,
            {
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            }
        );

        let signals = [];
        if (signalsResponse.ok) {
            signals = await signalsResponse.json();
        }

        // Calculate aggregated sentiment
        const avgSentiment = news.length > 0
            ? news.reduce((sum, n) => sum + (parseFloat(n.sentiment_score) || 0), 0) / news.length
            : 0;

        const positiveNews = news.filter(n => parseFloat(n.sentiment_score) > 0.6).length;
        const negativeNews = news.filter(n => parseFloat(n.sentiment_score) < 0.4).length;

        return new Response(JSON.stringify({
            news,
            signals,
            summary: {
                total_articles: news.length,
                average_sentiment: avgSentiment.toFixed(4),
                positive_count: positiveNews,
                negative_count: negativeNews,
                neutral_count: news.length - positiveNews - negativeNews,
                last_updated: new Date().toISOString()
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
