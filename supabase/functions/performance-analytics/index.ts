// Performance Analytics - Real Data Aggregation
// Bot trades va bot performance ma'lumotlarini agregatsiya qiladi

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
        const { user_id, bot_id, time_range } = await req.json();

        if (!user_id) {
            throw new Error('user_id is required');
        }

        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

        if (!supabaseUrl || !serviceRoleKey) {
            throw new Error('Supabase configuration missing');
        }

        // Calculate date range
        const now = new Date();
        let startDate = new Date();
        
        switch (time_range) {
            case '24h':
                startDate.setDate(now.getDate() - 1);
                break;
            case '7d':
                startDate.setDate(now.getDate() - 7);
                break;
            case '30d':
                startDate.setDate(now.getDate() - 30);
                break;
            case '90d':
                startDate.setDate(now.getDate() - 90);
                break;
            default:
                startDate.setFullYear(2020); // All time
        }

        // Fetch bot trades
        let tradesUrl = `${supabaseUrl}/rest/v1/bot_trades?user_id=eq.${user_id}&opened_at=gte.${startDate.toISOString()}&order=opened_at.desc`;
        if (bot_id) {
            tradesUrl += `&bot_id=eq.${bot_id}`;
        }

        const tradesResponse = await fetch(tradesUrl, {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey,
                'Content-Type': 'application/json'
            }
        });

        if (!tradesResponse.ok) {
            throw new Error('Failed to fetch trades');
        }

        const trades = await tradesResponse.json();

        // Calculate metrics
        const closedTrades = trades.filter((t: any) => t.status === 'closed');
        const profitableTrades = closedTrades.filter((t: any) => (t.profit_loss || 0) > 0);
        const losingTrades = closedTrades.filter((t: any) => (t.profit_loss || 0) <= 0);

        const totalProfit = profitableTrades.reduce((sum: number, t: any) => sum + (t.profit_loss || 0), 0);
        const totalLoss = Math.abs(losingTrades.reduce((sum: number, t: any) => sum + (t.profit_loss || 0), 0));
        const netProfit = totalProfit - totalLoss;

        const avgProfit = profitableTrades.length > 0 
            ? totalProfit / profitableTrades.length 
            : 0;
        const avgLoss = losingTrades.length > 0 
            ? totalLoss / losingTrades.length 
            : 0;

        const winRate = closedTrades.length > 0 
            ? (profitableTrades.length / closedTrades.length) * 100 
            : 0;

        const profitFactor = totalLoss > 0 ? totalProfit / totalLoss : totalProfit > 0 ? 999 : 0;

        // Best and worst trades
        const bestTrade = closedTrades.reduce((max: number, t: any) => 
            Math.max(max, t.profit_loss || 0), 0);
        const worstTrade = closedTrades.reduce((min: number, t: any) => 
            Math.min(min, t.profit_loss || 0), 0);

        // Calculate Sharpe Ratio
        const returns = closedTrades.map((t: any) => {
            const entryValue = t.entry_price * t.quantity;
            return entryValue > 0 ? (t.profit_loss || 0) / entryValue : 0;
        });

        let sharpeRatio = 0;
        if (returns.length > 1) {
            const avgReturn = returns.reduce((a: number, b: number) => a + b, 0) / returns.length;
            const variance = returns.reduce((sum: number, r: number) => 
                sum + Math.pow(r - avgReturn, 2), 0) / returns.length;
            const stdDev = Math.sqrt(variance);
            sharpeRatio = stdDev > 0 ? (avgReturn / stdDev) * Math.sqrt(252) : 0;
        }

        // Calculate max drawdown
        let peak = 0;
        let maxDrawdown = 0;
        let runningTotal = 0;

        closedTrades.forEach((t: any) => {
            runningTotal += (t.profit_loss || 0);
            if (runningTotal > peak) {
                peak = runningTotal;
            }
            const drawdown = peak > 0 ? ((peak - runningTotal) / peak) * 100 : 0;
            if (drawdown > maxDrawdown) {
                maxDrawdown = drawdown;
            }
        });

        // Daily returns
        const dailyReturnsMap = new Map();
        closedTrades.forEach((t: any) => {
            if (t.closed_at) {
                const date = t.closed_at.split('T')[0];
                const current = dailyReturnsMap.get(date) || 0;
                dailyReturnsMap.set(date, current + (t.profit_loss || 0));
            }
        });

        const dailyReturns = Array.from(dailyReturnsMap.entries())
            .map(([date, profit]) => ({ date, profit }))
            .sort((a, b) => a.date.localeCompare(b.date));

        // Trading pairs performance
        const pairsMap = new Map();
        trades.forEach((t: any) => {
            if (t.symbol) {
                const current = pairsMap.get(t.symbol) || { pair: t.symbol, trades: 0, profit: 0 };
                current.trades += 1;
                if (t.status === 'closed') {
                    current.profit += (t.profit_loss || 0);
                }
                pairsMap.set(t.symbol, current);
            }
        });

        const tradingPairs = Array.from(pairsMap.values())
            .sort((a, b) => b.profit - a.profit);

        const performanceData = {
            totalProfit: netProfit,
            totalTrades: closedTrades.length,
            winRate: winRate,
            avgProfit: avgProfit,
            avgLoss: avgLoss,
            bestTrade: bestTrade,
            worstTrade: worstTrade,
            profitFactor: profitFactor,
            sharpeRatio: sharpeRatio,
            maxDrawdown: maxDrawdown,
            dailyReturns: dailyReturns,
            tradingPairs: tradingPairs,
            timeRange: time_range || 'all',
            calculatedAt: new Date().toISOString()
        };

        return new Response(JSON.stringify({
            data: performanceData
        }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('Performance Analytics error:', error);

        return new Response(JSON.stringify({
            error: {
                code: 'ANALYTICS_ERROR',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});
