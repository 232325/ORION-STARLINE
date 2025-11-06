// Algorithmic Trading Engine - Phase 4.1
// Executes automated trading based on bot configurations and signals

Deno.serve(async (req) => {
    const corsHeaders = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Max-Age': '86400'
    };

    if (req.method === 'OPTIONS') {
        return new Response(null, { status: 200, headers: corsHeaders });
    }

    try {
        const { bot_id, execution_type, force_execution } = await req.json();

        if (!bot_id) {
            throw new Error('Bot ID is required');
        }

        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
        const alphaVantageKey = Deno.env.get('ALPHA_VANTAGE_API_KEY');

        const startTime = Date.now();

        // Get bot details
        const botResponse = await fetch(
            `${supabaseUrl}/rest/v1/ai_trading_bots?id=eq.${bot_id}`,
            {
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            }
        );

        if (!botResponse.ok) {
            throw new Error('Failed to fetch bot details');
        }

        const bots = await botResponse.json();
        if (bots.length === 0) {
            throw new Error('Bot not found');
        }

        const bot = bots[0];

        // Check if bot is active
        if (bot.status !== 'active' && !force_execution) {
            return new Response(JSON.stringify({
                data: {
                    message: 'Bot is not active',
                    status: bot.status
                }
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        // Get bot configuration
        const configResponse = await fetch(
            `${supabaseUrl}/rest/v1/bot_configurations?bot_id=eq.${bot_id}`,
            {
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            }
        );

        const configs = await configResponse.json();
        const config = configs[0] || {};

        // Log execution start
        const executionRecord = {
            bot_id: bot_id,
            execution_type: execution_type || 'signal_check',
            status: 'running',
            input_data: {
                bot_type: bot.bot_type,
                trading_pairs: bot.trading_pairs,
                current_capital: bot.current_capital
            },
            started_at: new Date().toISOString()
        };

        const execResponse = await fetch(`${supabaseUrl}/rest/v1/algorithm_executions`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey,
                'Content-Type': 'application/json',
                'Prefer': 'return=representation'
            },
            body: JSON.stringify(executionRecord)
        });

        const execData = await execResponse.json();
        const executionId = execData[0]?.id;

        // Process each trading pair
        const tradingResults = [];

        for (const symbol of bot.trading_pairs.slice(0, 3)) { // Limit to 3 for performance
            try {
                // Get current market price
                const priceResponse = await fetch(
                    `https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=${symbol}&apikey=${alphaVantageKey}`
                );

                if (!priceResponse.ok) {
                    continue;
                }

                const priceData = await priceResponse.json();
                const quote = priceData['Global Quote'];
                
                if (!quote) {
                    continue;
                }

                const currentPrice = parseFloat(quote['05. price']);
                const changePercent = parseFloat(quote['10. change percent'].replace('%', ''));

                // Get ML predictions if enabled
                let mlSignal = null;
                if (config.use_ml_predictions) {
                    const predictionResponse = await fetch(`${supabaseUrl}/rest/v1/ml_predictions?symbol=eq.${symbol}&order=prediction_time.desc&limit=1`, {
                        headers: {
                            'Authorization': `Bearer ${serviceRoleKey}`,
                            'apikey': serviceRoleKey
                        }
                    });

                    const predictions = await predictionResponse.json();
                    if (predictions.length > 0) {
                        const pred = predictions[0];
                        mlSignal = {
                            direction: pred.predicted_direction,
                            confidence: pred.confidence_score,
                            predicted_price: pred.predicted_price
                        };
                    }
                }

                // Generate trading signal based on bot type
                let signal = null;

                switch (bot.bot_type) {
                    case 'conservative':
                        // Conservative: Only trade on high confidence signals
                        if (mlSignal && mlSignal.confidence > 0.75) {
                            signal = {
                                action: mlSignal.direction === 'up' ? 'BUY' : 'SELL',
                                confidence: mlSignal.confidence,
                                reason: 'High confidence ML prediction'
                            };
                        }
                        break;

                    case 'aggressive':
                        // Aggressive: Trade on medium confidence or strong price movement
                        if ((mlSignal && mlSignal.confidence > 0.55) || Math.abs(changePercent) > 2) {
                            signal = {
                                action: changePercent > 0 || (mlSignal && mlSignal.direction === 'up') ? 'BUY' : 'SELL',
                                confidence: mlSignal ? mlSignal.confidence : 0.6,
                                reason: Math.abs(changePercent) > 2 ? 'Strong price movement' : 'ML prediction'
                            };
                        }
                        break;

                    case 'balanced':
                        // Balanced: Combine multiple factors
                        if (mlSignal && mlSignal.confidence > 0.65 && Math.abs(changePercent) > 0.5) {
                            const mlDirection = mlSignal.direction === 'up';
                            const priceDirection = changePercent > 0;
                            
                            if (mlDirection === priceDirection) {
                                signal = {
                                    action: mlDirection ? 'BUY' : 'SELL',
                                    confidence: (mlSignal.confidence + 0.7) / 2,
                                    reason: 'ML and price trend alignment'
                                };
                            }
                        }
                        break;

                    case 'grid':
                        // Grid: Buy on dips, sell on peaks
                        if (changePercent < -1) {
                            signal = {
                                action: 'BUY',
                                confidence: Math.min(-changePercent / 5, 1),
                                reason: 'Grid: Buy on dip'
                            };
                        } else if (changePercent > 1) {
                            signal = {
                                action: 'SELL',
                                confidence: Math.min(changePercent / 5, 1),
                                reason: 'Grid: Sell on peak'
                            };
                        }
                        break;

                    case 'arbitrage':
                        // Arbitrage: Look for price discrepancies (simplified)
                        if (mlSignal && Math.abs(currentPrice - mlSignal.predicted_price) / currentPrice > 0.01) {
                            signal = {
                                action: mlSignal.predicted_price > currentPrice ? 'BUY' : 'SELL',
                                confidence: mlSignal.confidence,
                                reason: 'Arbitrage opportunity detected'
                            };
                        }
                        break;
                }

                // Execute trade if signal is strong enough
                if (signal && signal.confidence > 0.6) {
                    // Calculate position size based on risk management
                    const riskAmount = bot.current_capital * (config.risk_percentage / 100);
                    const positionSize = Math.min(
                        riskAmount / currentPrice,
                        bot.max_position_size
                    );

                    // Calculate stop loss and take profit
                    const stopLossPrice = signal.action === 'BUY' 
                        ? currentPrice * (1 - config.stop_loss_percentage / 100)
                        : currentPrice * (1 + config.stop_loss_percentage / 100);

                    const takeProfitPrice = signal.action === 'BUY'
                        ? currentPrice * (1 + config.take_profit_percentage / 100)
                        : currentPrice * (1 - config.take_profit_percentage / 100);

                    // Create trade record
                    const trade = {
                        bot_id: bot_id,
                        user_id: bot.user_id,
                        trade_type: signal.action,
                        symbol: symbol,
                        quantity: positionSize,
                        entry_price: currentPrice,
                        status: 'open',
                        stop_loss_price: stopLossPrice,
                        take_profit_price: takeProfitPrice,
                        entry_signal: {
                            type: signal.reason,
                            confidence: signal.confidence,
                            ml_prediction: mlSignal,
                            price_change: changePercent
                        },
                        market_conditions: {
                            price: currentPrice,
                            change_percent: changePercent,
                            timestamp: new Date().toISOString()
                        },
                        opened_at: new Date().toISOString()
                    };

                    await fetch(`${supabaseUrl}/rest/v1/bot_trading_history`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${serviceRoleKey}`,
                            'apikey': serviceRoleKey,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(trade)
                    });

                    tradingResults.push({
                        symbol: symbol,
                        action: signal.action,
                        price: currentPrice,
                        quantity: positionSize,
                        signal: signal
                    });
                } else {
                    tradingResults.push({
                        symbol: symbol,
                        action: 'HOLD',
                        reason: signal ? 'Low confidence' : 'No signal generated',
                        price: currentPrice
                    });
                }

            } catch (error) {
                console.error(`Error processing ${symbol}:`, error);
                tradingResults.push({
                    symbol: symbol,
                    error: error.message
                });
            }

            // Rate limiting
            await new Promise(resolve => setTimeout(resolve, 12000)); // 12 seconds between requests
        }

        // Update execution record
        const executionTime = Date.now() - startTime;

        if (executionId) {
            await fetch(`${supabaseUrl}/rest/v1/algorithm_executions?id=eq.${executionId}`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    status: 'completed',
                    output_data: {
                        trades_executed: tradingResults.filter(r => r.action !== 'HOLD' && !r.error).length,
                        results: tradingResults
                    },
                    execution_time_ms: executionTime,
                    completed_at: new Date().toISOString()
                })
            });
        }

        // Update bot's last active time
        await fetch(`${supabaseUrl}/rest/v1/ai_trading_bots?id=eq.${bot_id}`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                last_active_at: new Date().toISOString()
            })
        });

        return new Response(JSON.stringify({
            data: {
                bot_id: bot_id,
                execution_id: executionId,
                execution_time_ms: executionTime,
                trading_results: tradingResults,
                summary: {
                    total_symbols: bot.trading_pairs.length,
                    trades_executed: tradingResults.filter(r => r.action !== 'HOLD' && !r.error).length,
                    holds: tradingResults.filter(r => r.action === 'HOLD').length,
                    errors: tradingResults.filter(r => r.error).length
                }
            }
        }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('Algorithmic Trading Engine error:', error);

        return new Response(JSON.stringify({
            error: {
                code: 'TRADING_ENGINE_ERROR',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});
