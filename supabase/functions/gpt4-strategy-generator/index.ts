// GPT-4 Strategy Generator - Phase 4.1
// Generates trading strategies using natural language

Deno.serve(async (req) => {
    const corsHeaders = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
        'Access-Control-Max-Age': '86400'
    };

    if (req.method === 'OPTIONS') {
        return new Response(null, { status: 200, headers: corsHeaders });
    }

    try {
        const { prompt, user_id, bot_id, strategy_type, timeframe, instruments } = await req.json();

        if (!prompt) {
            throw new Error('Prompt is required');
        }

        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
        const openaiKey = Deno.env.get('OPENAI_API_KEY');

        if (!openaiKey) {
            throw new Error('OpenAI API key not configured');
        }

        // Generate strategy using GPT-4
        const systemPrompt = `Sen profesyonel bir trading strateji uzmanısın. Kullanıcının talebine göre detaylı trading stratejileri oluştur. Strateji şunları içermeli:

1. Entry (Giriş) Kuralları:
   - Teknik indikatörler (SMA, EMA, RSI, MACD, vb.)
   - Price action patterns
   - Volume analysis
   - Trend confirmation

2. Exit (Çıkış) Kuralları:
   - Take profit hedefleri
   - Stop loss seviyeleri
   - Trailing stop mantığı
   - Zaman bazlı çıkışlar

3. Risk Management:
   - Position sizing
   - Risk-reward ratio
   - Maximum drawdown limits
   - Daily loss limits

4. Market Conditions:
   - Hangi market rejimlerinde kullanılmalı (trending, ranging, volatile)
   - Volatilite filtreleri
   - Zaman filtreleri

JSON formatında yanıt ver.`;

        const gptResponse = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${openaiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: 'gpt-4-turbo-preview',
                messages: [
                    { role: 'system', content: systemPrompt },
                    { role: 'user', content: prompt }
                ],
                temperature: 0.7,
                max_tokens: 2000
            })
        });

        if (!gptResponse.ok) {
            throw new Error(`GPT-4 API error: ${await gptResponse.text()}`);
        }

        const gptData = await gptResponse.json();
        const generatedContent = gptData.choices[0].message.content;

        // Parse the strategy
        let strategyData;
        try {
            strategyData = JSON.parse(generatedContent);
        } catch (e) {
            // If not valid JSON, create structured data
            strategyData = {
                description: generatedContent,
                entry_rules: {},
                exit_rules: {},
                risk_rules: {}
            };
        }

        // Create strategy name from prompt
        const strategyName = prompt.slice(0, 100) + (prompt.length > 100 ? '...' : '');

        // Save strategy to database
        const newStrategy = {
            user_id: user_id,
            bot_id: bot_id || null,
            strategy_name: strategyName,
            description: strategyData.description || generatedContent,
            strategy_type: strategy_type || 'custom',
            generated_by: 'gpt4',
            prompt: prompt,
            entry_rules: strategyData.entry_rules || {},
            exit_rules: strategyData.exit_rules || {},
            risk_rules: strategyData.risk_rules || {},
            timeframe: timeframe || '1h',
            instruments: instruments || [],
            status: 'draft'
        };

        const saveResponse = await fetch(`${supabaseUrl}/rest/v1/trading_strategies`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey,
                'Content-Type': 'application/json',
                'Prefer': 'return=representation'
            },
            body: JSON.stringify(newStrategy)
        });

        if (!saveResponse.ok) {
            throw new Error(`Failed to save strategy: ${await saveResponse.text()}`);
        }

        const savedStrategy = (await saveResponse.json())[0];

        // Generate backtest simulation (mock data for demo)
        const backtestResults = {
            total_trades: Math.floor(Math.random() * 100) + 50,
            winning_trades: Math.floor(Math.random() * 60) + 30,
            losing_trades: Math.floor(Math.random() * 30) + 10,
            win_rate: (Math.random() * 30 + 50).toFixed(2),
            net_profit: (Math.random() * 10000 + 5000).toFixed(2),
            sharpe_ratio: (Math.random() * 2 + 1).toFixed(2),
            max_drawdown: (Math.random() * 15 + 5).toFixed(2)
        };

        return new Response(JSON.stringify({
            data: {
                strategy: savedStrategy,
                backtest_results: backtestResults,
                gpt_analysis: generatedContent
            }
        }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('GPT-4 Strategy Generator error:', error);

        return new Response(JSON.stringify({
            error: {
                code: 'STRATEGY_GENERATION_ERROR',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});
