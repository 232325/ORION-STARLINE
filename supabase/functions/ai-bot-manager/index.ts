// AI Bot Manager - Phase 4.1
// Handles CRUD operations for AI trading bots

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
        const { action, bot_id, user_id, bot_data } = await req.json();

        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

        if (!supabaseUrl || !serviceRoleKey) {
            throw new Error('Supabase configuration missing');
        }

        let response;

        switch (action) {
            case 'create': {
                // Create new bot
                const newBot = {
                    user_id: user_id || bot_data.user_id,
                    bot_name: bot_data.bot_name,
                    bot_type: bot_data.bot_type,
                    description: bot_data.description || '',
                    status: 'inactive',
                    trading_pairs: bot_data.trading_pairs || [],
                    initial_capital: bot_data.initial_capital || 0,
                    current_capital: bot_data.initial_capital || 0,
                    max_position_size: bot_data.max_position_size || 0,
                    max_daily_trades: bot_data.max_daily_trades || 10
                };

                const createResponse = await fetch(`${supabaseUrl}/rest/v1/ai_trading_bots`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${serviceRoleKey}`,
                        'apikey': serviceRoleKey,
                        'Content-Type': 'application/json',
                        'Prefer': 'return=representation'
                    },
                    body: JSON.stringify(newBot)
                });

                if (!createResponse.ok) {
                    throw new Error(`Failed to create bot: ${await createResponse.text()}`);
                }

                const botResult = await createResponse.json();
                const createdBot = botResult[0];

                // Create default configuration
                const defaultConfig = {
                    bot_id: createdBot.id,
                    risk_percentage: bot_data.risk_percentage || 2.0,
                    stop_loss_percentage: bot_data.stop_loss_percentage || 2.0,
                    take_profit_percentage: bot_data.take_profit_percentage || 5.0,
                    use_ai_signals: true,
                    use_ml_predictions: true,
                    use_sentiment_analysis: true
                };

                await fetch(`${supabaseUrl}/rest/v1/bot_configurations`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${serviceRoleKey}`,
                        'apikey': serviceRoleKey,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(defaultConfig)
                });

                response = { bot: createdBot, message: 'Bot created successfully' };
                break;
            }

            case 'get_all': {
                // Get all bots for user
                const getResponse = await fetch(
                    `${supabaseUrl}/rest/v1/ai_trading_bots?user_id=eq.${user_id}&order=created_at.desc`,
                    {
                        headers: {
                            'Authorization': `Bearer ${serviceRoleKey}`,
                            'apikey': serviceRoleKey
                        }
                    }
                );

                if (!getResponse.ok) {
                    throw new Error('Failed to fetch bots');
                }

                const bots = await getResponse.json();
                response = { bots, count: bots.length };
                break;
            }

            case 'get_by_id': {
                // Get specific bot
                const getResponse = await fetch(
                    `${supabaseUrl}/rest/v1/ai_trading_bots?id=eq.${bot_id}`,
                    {
                        headers: {
                            'Authorization': `Bearer ${serviceRoleKey}`,
                            'apikey': serviceRoleKey
                        }
                    }
                );

                if (!getResponse.ok) {
                    throw new Error('Failed to fetch bot');
                }

                const botData = await getResponse.json();
                
                // Also get configuration
                const configResponse = await fetch(
                    `${supabaseUrl}/rest/v1/bot_configurations?bot_id=eq.${bot_id}`,
                    {
                        headers: {
                            'Authorization': `Bearer ${serviceRoleKey}`,
                            'apikey': serviceRoleKey
                        }
                    }
                );

                const configData = await configResponse.json();

                response = { 
                    bot: botData[0], 
                    configuration: configData[0] || null 
                };
                break;
            }

            case 'update': {
                // Update bot
                const updateResponse = await fetch(
                    `${supabaseUrl}/rest/v1/ai_trading_bots?id=eq.${bot_id}`,
                    {
                        method: 'PATCH',
                        headers: {
                            'Authorization': `Bearer ${serviceRoleKey}`,
                            'apikey': serviceRoleKey,
                            'Content-Type': 'application/json',
                            'Prefer': 'return=representation'
                        },
                        body: JSON.stringify({
                            ...bot_data,
                            updated_at: new Date().toISOString()
                        })
                    }
                );

                if (!updateResponse.ok) {
                    throw new Error('Failed to update bot');
                }

                const updated = await updateResponse.json();
                response = { bot: updated[0], message: 'Bot updated successfully' };
                break;
            }

            case 'start': {
                // Start bot
                const startResponse = await fetch(
                    `${supabaseUrl}/rest/v1/ai_trading_bots?id=eq.${bot_id}`,
                    {
                        method: 'PATCH',
                        headers: {
                            'Authorization': `Bearer ${serviceRoleKey}`,
                            'apikey': serviceRoleKey,
                            'Content-Type': 'application/json',
                            'Prefer': 'return=representation'
                        },
                        body: JSON.stringify({
                            status: 'active',
                            started_at: new Date().toISOString(),
                            last_active_at: new Date().toISOString()
                        })
                    }
                );

                if (!startResponse.ok) {
                    throw new Error('Failed to start bot');
                }

                const started = await startResponse.json();
                response = { bot: started[0], message: 'Bot started successfully' };
                break;
            }

            case 'stop': {
                // Stop bot
                const stopResponse = await fetch(
                    `${supabaseUrl}/rest/v1/ai_trading_bots?id=eq.${bot_id}`,
                    {
                        method: 'PATCH',
                        headers: {
                            'Authorization': `Bearer ${serviceRoleKey}`,
                            'apikey': serviceRoleKey,
                            'Content-Type': 'application/json',
                            'Prefer': 'return=representation'
                        },
                        body: JSON.stringify({
                            status: 'inactive',
                            stopped_at: new Date().toISOString()
                        })
                    }
                );

                if (!stopResponse.ok) {
                    throw new Error('Failed to stop bot');
                }

                const stopped = await stopResponse.json();
                response = { bot: stopped[0], message: 'Bot stopped successfully' };
                break;
            }

            case 'pause': {
                // Pause bot
                const pauseResponse = await fetch(
                    `${supabaseUrl}/rest/v1/ai_trading_bots?id=eq.${bot_id}`,
                    {
                        method: 'PATCH',
                        headers: {
                            'Authorization': `Bearer ${serviceRoleKey}`,
                            'apikey': serviceRoleKey,
                            'Content-Type': 'application/json',
                            'Prefer': 'return=representation'
                        },
                        body: JSON.stringify({
                            status: 'paused'
                        })
                    }
                );

                if (!pauseResponse.ok) {
                    throw new Error('Failed to pause bot');
                }

                const paused = await pauseResponse.json();
                response = { bot: paused[0], message: 'Bot paused successfully' };
                break;
            }

            case 'delete': {
                // Delete bot
                const deleteResponse = await fetch(
                    `${supabaseUrl}/rest/v1/ai_trading_bots?id=eq.${bot_id}`,
                    {
                        method: 'DELETE',
                        headers: {
                            'Authorization': `Bearer ${serviceRoleKey}`,
                            'apikey': serviceRoleKey
                        }
                    }
                );

                if (!deleteResponse.ok) {
                    throw new Error('Failed to delete bot');
                }

                response = { message: 'Bot deleted successfully' };
                break;
            }

            case 'get_stats': {
                // Get bot statistics
                const statsResponse = await fetch(
                    `${supabaseUrl}/rest/v1/ai_trading_bots?id=eq.${bot_id}`,
                    {
                        headers: {
                            'Authorization': `Bearer ${serviceRoleKey}`,
                            'apikey': serviceRoleKey
                        }
                    }
                );

                if (!statsResponse.ok) {
                    throw new Error('Failed to fetch bot stats');
                }

                const bot = (await statsResponse.json())[0];

                // Get recent trades
                const tradesResponse = await fetch(
                    `${supabaseUrl}/rest/v1/bot_trading_history?bot_id=eq.${bot_id}&order=opened_at.desc&limit=10`,
                    {
                        headers: {
                            'Authorization': `Bearer ${serviceRoleKey}`,
                            'apikey': serviceRoleKey
                        }
                    }
                );

                const recentTrades = await tradesResponse.json();

                response = {
                    stats: {
                        total_trades: bot.total_trades,
                        winning_trades: bot.winning_trades,
                        losing_trades: bot.losing_trades,
                        win_rate: bot.win_rate,
                        total_profit: bot.total_profit,
                        total_loss: bot.total_loss,
                        current_capital: bot.current_capital,
                        sharpe_ratio: bot.sharpe_ratio,
                        max_drawdown: bot.max_drawdown,
                        status: bot.status
                    },
                    recent_trades: recentTrades
                };
                break;
            }

            default:
                throw new Error('Invalid action');
        }

        return new Response(JSON.stringify({ data: response }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('AI Bot Manager error:', error);

        return new Response(JSON.stringify({
            error: {
                code: 'BOT_MANAGER_ERROR',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});
