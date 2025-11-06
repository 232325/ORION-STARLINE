/**
 * Backtesting Engine Edge Function
 * Purpose: Backtest trading strategies with historical data
 * Directive: D) Trading Platform Extensions
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
        const { action, strategyName, userId, startDate, endDate, initialCapital, parameters } = await req.json();

        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

        let result: any = {};

        switch (action) {
            case 'run_backtest':
                result = await runBacktest(
                    supabaseUrl!,
                    serviceRoleKey!,
                    strategyName,
                    userId,
                    startDate,
                    endDate,
                    initialCapital || 10000,
                    parameters || {}
                );
                break;

            case 'get_results':
                result = await getBacktestResults(supabaseUrl!, serviceRoleKey!, userId);
                break;

            case 'compare_strategies':
                const { strategyIds } = await req.json();
                result = await compareStrategies(supabaseUrl!, serviceRoleKey!, strategyIds);
                break;

            default:
                throw new Error('Invalid action');
        }

        return new Response(JSON.stringify({ data: result }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error: any) {
        console.error('Backtesting Engine error:', error);

        return new Response(JSON.stringify({
            error: {
                code: 'BACKTEST_ERROR',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

/**
 * Run backtest simulation
 */
async function runBacktest(
    supabaseUrl: string,
    serviceRoleKey: string,
    strategyName: string,
    userId: string,
    startDate: string,
    endDate: string,
    initialCapital: number,
    parameters: any
): Promise<any> {
    // Get historical price data
    const priceResponse = await fetch(
        `${supabaseUrl}/rest/v1/realtime_prices?timestamp=gte.${startDate}&timestamp=lte.${endDate}&order=timestamp.asc&limit=1000`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    const historicalData = await priceResponse.json();

    if (historicalData.length < 10) {
        throw new Error('Insufficient historical data for backtesting');
    }

    // Run strategy simulation
    const simulation = simulateStrategy(strategyName, historicalData, initialCapital, parameters);

    // Calculate performance metrics
    const metrics = calculatePerformanceMetrics(simulation, initialCapital);

    // Save backtest result
    const insertResponse = await fetch(`${supabaseUrl}/rest/v1/backtesting_results`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey,
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        },
        body: JSON.stringify({
            strategy_name: strategyName,
            user_id: userId,
            start_date: startDate,
            end_date: endDate,
            initial_capital: initialCapital,
            final_capital: metrics.finalCapital,
            total_return: metrics.totalReturn,
            annual_return: metrics.annualReturn,
            sharpe_ratio: metrics.sharpeRatio,
            max_drawdown: metrics.maxDrawdown,
            win_rate: metrics.winRate,
            total_trades: metrics.totalTrades,
            profitable_trades: metrics.profitableTrades,
            strategy_parameters: parameters,
            trade_history: simulation.trades,
            equity_curve: simulation.equityCurve
        })
    });

    const savedResult = await insertResponse.json();

    return {
        backtestId: savedResult[0]?.id,
        strategyName,
        period: {
            start: startDate,
            end: endDate,
            daysTraded: simulation.daysTraded
        },
        performance: metrics,
        trades: simulation.trades,
        equityCurve: simulation.equityCurve
    };
}

/**
 * Get backtest results for user
 */
async function getBacktestResults(
    supabaseUrl: string,
    serviceRoleKey: string,
    userId: string
): Promise<any> {
    const response = await fetch(
        `${supabaseUrl}/rest/v1/backtesting_results?user_id=eq.${userId}&order=created_at.desc&limit=50`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    const results = await response.json();

    return {
        userId,
        totalBacktests: results.length,
        results: results.map((r: any) => ({
            id: r.id,
            strategyName: r.strategy_name,
            period: {
                start: r.start_date,
                end: r.end_date
            },
            performance: {
                totalReturn: r.total_return,
                sharpeRatio: r.sharpe_ratio,
                maxDrawdown: r.max_drawdown,
                winRate: r.win_rate
            },
            createdAt: r.created_at
        }))
    };
}

/**
 * Compare multiple strategies
 */
async function compareStrategies(
    supabaseUrl: string,
    serviceRoleKey: string,
    strategyIds: string[]
): Promise<any> {
    const comparisons = [];

    for (const id of strategyIds) {
        const response = await fetch(
            `${supabaseUrl}/rest/v1/backtesting_results?id=eq.${id}`,
            {
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            }
        );

        const result = await response.json();
        if (result && result.length > 0) {
            comparisons.push(result[0]);
        }
    }

    // Rank strategies
    const ranked = comparisons.sort((a, b) => {
        const scoreA = calculateStrategyScore(a);
        const scoreB = calculateStrategyScore(b);
        return scoreB - scoreA;
    });

    return {
        totalStrategies: comparisons.length,
        comparison: ranked.map((s: any, index: number) => ({
            rank: index + 1,
            strategyName: s.strategy_name,
            totalReturn: s.total_return,
            sharpeRatio: s.sharpe_ratio,
            maxDrawdown: s.max_drawdown,
            winRate: s.win_rate,
            score: calculateStrategyScore(s).toFixed(2)
        })),
        bestStrategy: ranked[0]?.strategy_name
    };
}

/**
 * Simulate trading strategy
 */
function simulateStrategy(
    strategyName: string,
    historicalData: any[],
    initialCapital: number,
    parameters: any
): any {
    let capital = initialCapital;
    let position: any = null;
    const trades: any[] = [];
    const equityCurve: any[] = [];

    // Strategy parameters
    const fastMA = parameters.fastMA || 10;
    const slowMA = parameters.slowMA || 20;
    const rsiPeriod = parameters.rsiPeriod || 14;
    const rsiOverbought = parameters.rsiOverbought || 70;
    const rsiOversold = parameters.rsiOversold || 30;

    // Calculate indicators
    for (let i = slowMA; i < historicalData.length; i++) {
        const currentPrice = parseFloat(historicalData[i].price);
        const currentTime = historicalData[i].timestamp;

        // Calculate moving averages
        const fastMAValue = calculateMA(historicalData, i, fastMA);
        const slowMAValue = calculateMA(historicalData, i, slowMA);

        // Calculate RSI
        const rsi = calculateRSI(historicalData, i, rsiPeriod);

        // Apply strategy logic
        let signal = null;

        if (strategyName.toLowerCase().includes('momentum')) {
            // Momentum strategy: Buy when fast MA crosses above slow MA
            if (fastMAValue > slowMAValue && !position) {
                signal = 'buy';
            } else if (fastMAValue < slowMAValue && position) {
                signal = 'sell';
            }
        } else if (strategyName.toLowerCase().includes('mean_reversion')) {
            // Mean reversion: Buy when RSI oversold, sell when overbought
            if (rsi < rsiOversold && !position) {
                signal = 'buy';
            } else if (rsi > rsiOverbought && position) {
                signal = 'sell';
            }
        } else {
            // Default: Combined strategy
            if (fastMAValue > slowMAValue && rsi < 50 && !position) {
                signal = 'buy';
            } else if (fastMAValue < slowMAValue && rsi > 50 && position) {
                signal = 'sell';
            }
        }

        // Execute trade
        if (signal === 'buy' && !position) {
            const shares = Math.floor((capital * 0.95) / currentPrice); // Use 95% of capital
            const cost = shares * currentPrice;
            
            position = {
                entryPrice: currentPrice,
                entryTime: currentTime,
                shares,
                cost
            };

            capital -= cost;

            trades.push({
                type: 'buy',
                price: currentPrice,
                shares,
                timestamp: currentTime,
                indicators: { fastMA: fastMAValue, slowMA: slowMAValue, rsi }
            });
        } else if (signal === 'sell' && position) {
            const revenue = position.shares * currentPrice;
            const pnl = revenue - position.cost;
            const pnlPercent = (pnl / position.cost) * 100;

            capital += revenue;

            trades.push({
                type: 'sell',
                price: currentPrice,
                shares: position.shares,
                timestamp: currentTime,
                pnl,
                pnlPercent: pnlPercent.toFixed(2),
                holdingPeriod: Math.floor((new Date(currentTime).getTime() - new Date(position.entryTime).getTime()) / 86400000),
                indicators: { fastMA: fastMAValue, slowMA: slowMAValue, rsi }
            });

            position = null;
        }

        // Record equity curve
        const equity = capital + (position ? position.shares * currentPrice : 0);
        equityCurve.push({
            timestamp: currentTime,
            equity: equity.toFixed(2)
        });
    }

    // Close any open position
    if (position) {
        const lastPrice = parseFloat(historicalData[historicalData.length - 1].price);
        const revenue = position.shares * lastPrice;
        capital += revenue;
    }

    return {
        trades,
        equityCurve,
        finalCapital: capital,
        daysTraded: Math.floor((new Date(historicalData[historicalData.length - 1].timestamp).getTime() - 
                               new Date(historicalData[0].timestamp).getTime()) / 86400000)
    };
}

/**
 * Calculate performance metrics
 */
function calculatePerformanceMetrics(simulation: any, initialCapital: number): any {
    const finalCapital = simulation.finalCapital;
    const totalReturn = ((finalCapital - initialCapital) / initialCapital) * 100;
    
    // Calculate annual return
    const years = simulation.daysTraded / 365;
    const annualReturn = years > 0 ? (Math.pow(finalCapital / initialCapital, 1 / years) - 1) * 100 : 0;

    // Calculate trades statistics
    const sellTrades = simulation.trades.filter((t: any) => t.type === 'sell');
    const profitableTrades = sellTrades.filter((t: any) => parseFloat(t.pnl) > 0).length;
    const winRate = sellTrades.length > 0 ? (profitableTrades / sellTrades.length) * 100 : 0;

    // Calculate Sharpe ratio (simplified)
    const returns = sellTrades.map((t: any) => parseFloat(t.pnlPercent));
    const avgReturn = returns.length > 0 ? returns.reduce((a: number, b: number) => a + b, 0) / returns.length : 0;
    const stdDev = returns.length > 0 ? Math.sqrt(returns.reduce((sum: number, r: number) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length) : 1;
    const sharpeRatio = stdDev > 0 ? avgReturn / stdDev : 0;

    // Calculate max drawdown
    const equityCurve = simulation.equityCurve.map((e: any) => parseFloat(e.equity));
    const maxDrawdown = calculateMaxDrawdown(equityCurve);

    return {
        finalCapital: finalCapital.toFixed(2),
        totalReturn: totalReturn.toFixed(2),
        annualReturn: annualReturn.toFixed(2),
        sharpeRatio: sharpeRatio.toFixed(2),
        maxDrawdown: maxDrawdown.toFixed(2),
        totalTrades: simulation.trades.length,
        profitableTrades,
        winRate: winRate.toFixed(2)
    };
}

/**
 * Calculate moving average
 */
function calculateMA(data: any[], index: number, period: number): number {
    let sum = 0;
    for (let i = 0; i < period; i++) {
        sum += parseFloat(data[index - i].price);
    }
    return sum / period;
}

/**
 * Calculate RSI
 */
function calculateRSI(data: any[], index: number, period: number): number {
    let gains = 0;
    let losses = 0;

    for (let i = 1; i <= period; i++) {
        const change = parseFloat(data[index - i + 1].price) - parseFloat(data[index - i].price);
        if (change > 0) {
            gains += change;
        } else {
            losses += Math.abs(change);
        }
    }

    const avgGain = gains / period;
    const avgLoss = losses / period;

    if (avgLoss === 0) return 100;

    const rs = avgGain / avgLoss;
    return 100 - (100 / (1 + rs));
}

/**
 * Calculate maximum drawdown
 */
function calculateMaxDrawdown(equityCurve: number[]): number {
    let maxDrawdown = 0;
    let peak = equityCurve[0];

    for (const value of equityCurve) {
        if (value > peak) {
            peak = value;
        }
        const drawdown = ((peak - value) / peak) * 100;
        if (drawdown > maxDrawdown) {
            maxDrawdown = drawdown;
        }
    }

    return maxDrawdown;
}

/**
 * Calculate strategy score for comparison
 */
function calculateStrategyScore(strategy: any): number {
    const returnWeight = 0.3;
    const sharpeWeight = 0.3;
    const drawdownWeight = 0.2;
    const winRateWeight = 0.2;

    const returnScore = Math.min(parseFloat(strategy.total_return) / 100, 1);
    const sharpeScore = Math.min(parseFloat(strategy.sharpe_ratio) / 3, 1);
    const drawdownScore = Math.max(0, 1 - parseFloat(strategy.max_drawdown) / 50);
    const winRateScore = parseFloat(strategy.win_rate) / 100;

    return (returnScore * returnWeight + 
            sharpeScore * sharpeWeight + 
            drawdownScore * drawdownWeight + 
            winRateScore * winRateWeight) * 100;
}
