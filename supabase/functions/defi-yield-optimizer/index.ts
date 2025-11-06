// DEFI YIELD OPTIMIZER EDGE FUNCTION
// Automated yield tracking, optimization, and rebalancing
// Protocols: Uniswap V3, Aave, Compound, Yearn, Convex, Beefy

Deno.serve(async (req) => {
    const corsHeaders = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
        'Access-Control-Max-Age': '86400',
        'Access-Control-Allow-Credentials': 'false'
    };

    if (req.method === 'OPTIONS') {
        return new Response(null, { status: 200, headers: corsHeaders });
    }

    try {
        const requestBody = await req.json();
        const { action } = requestBody;

        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

        if (!supabaseUrl || !serviceRoleKey) {
            throw new Error('Supabase configuration missing');
        }

        // Get user from auth header
        const authHeader = req.headers.get('authorization');
        if (!authHeader) {
            throw new Error('No authorization header');
        }

        const token = authHeader.replace('Bearer ', '');
        const userResponse = await fetch(`${supabaseUrl}/auth/v1/user`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'apikey': serviceRoleKey
            }
        });

        if (!userResponse.ok) {
            throw new Error('Invalid token');
        }

        const userData = await userResponse.json();
        const userId = userData.id;

        let result;

        switch (action) {
            case 'get_top_yields':
                const { chain, minApy, maxRisk } = requestBody;
                result = await getTopYields(supabaseUrl, serviceRoleKey, chain, minApy, maxRisk);
                break;

            case 'create_position':
                const { protocolYieldId, amount } = requestBody;
                result = await createYieldPosition(supabaseUrl, serviceRoleKey, userId, protocolYieldId, amount);
                break;

            case 'get_user_positions':
                result = await getUserPositions(supabaseUrl, serviceRoleKey, userId);
                break;

            case 'calculate_impermanent_loss':
                const { tokenPair, entryPrice, currentPrice } = requestBody;
                result = calculateImpermanentLoss(tokenPair, entryPrice, currentPrice);
                break;

            case 'optimize_strategy':
                const { strategyType, investmentAmount } = requestBody;
                result = await optimizeStrategy(supabaseUrl, serviceRoleKey, strategyType, investmentAmount);
                break;

            case 'auto_rebalance':
                result = await autoRebalance(supabaseUrl, serviceRoleKey, userId);
                break;

            default:
                throw new Error(`Unknown action: ${action}`);
        }

        return new Response(JSON.stringify({ data: result }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('DeFi Yield Optimizer error:', error);

        return new Response(JSON.stringify({
            error: {
                code: 'YIELD_OPTIMIZER_FAILED',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

// Get top yielding opportunities
async function getTopYields(supabaseUrl: string, serviceRoleKey: string, chain?: string, minApy?: number, maxRisk?: number) {
    let query = `${supabaseUrl}/rest/v1/defi_protocol_yields?order=apy.desc&limit=20`;

    if (chain) {
        query += `&chain=eq.${chain}`;
    }
    if (minApy) {
        query += `&apy=gte.${minApy}`;
    }
    if (maxRisk) {
        query += `&risk_score=lte.${maxRisk}`;
    }

    const response = await fetch(query, {
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey
        }
    });

    if (!response.ok) {
        throw new Error('Failed to fetch yield opportunities');
    }

    const yields = await response.json();

    // Enhance with calculated metrics
    const enhancedYields = yields.map((y: any) => ({
        ...y,
        risk_adjusted_return: parseFloat(y.apy) / (parseFloat(y.risk_score) || 1),
        estimated_daily_return: (parseFloat(y.apy) / 365).toFixed(4),
        recommendation_score: calculateRecommendationScore(y)
    }));

    return {
        opportunities: enhancedYields,
        filters_applied: { chain, minApy, maxRisk },
        market_summary: {
            avg_apy: calculateAverage(enhancedYields, 'apy'),
            highest_apy: Math.max(...enhancedYields.map((y: any) => parseFloat(y.apy))),
            safest_option: enhancedYields.reduce((min: any, y: any) =>
                parseFloat(y.risk_score) < parseFloat(min.risk_score) ? y : min,
                enhancedYields[0]
            )
        }
    };
}

// Calculate recommendation score
function calculateRecommendationScore(yieldData: any): number {
    const apyWeight = 0.4;
    const riskWeight = 0.3;
    const tvlWeight = 0.2;
    const volumeWeight = 0.1;

    const apyScore = Math.min(parseFloat(yieldData.apy) / 100, 1) * 100;
    const riskScore = (5 - parseFloat(yieldData.risk_score || 3)) * 20;
    const tvlScore = Math.min(parseFloat(yieldData.tvl || 0) / 1000000000, 1) * 100;
    const volumeScore = Math.min(parseFloat(yieldData.daily_volume || 0) / 100000000, 1) * 100;

    return (
        apyScore * apyWeight +
        riskScore * riskWeight +
        tvlScore * tvlWeight +
        volumeScore * volumeWeight
    );
}

// Create yield position
async function createYieldPosition(
    supabaseUrl: string,
    serviceRoleKey: string,
    userId: string,
    protocolYieldId: string,
    amount: number
) {
    // Get protocol yield details
    const yieldResponse = await fetch(
        `${supabaseUrl}/rest/v1/defi_protocol_yields?id=eq.${protocolYieldId}`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    if (!yieldResponse.ok) {
        throw new Error('Protocol yield not found');
    }

    const yieldData = await yieldResponse.json();

    if (yieldData.length === 0) {
        throw new Error('Invalid protocol yield ID');
    }

    const protocolYield = yieldData[0];

    // Check minimum deposit
    if (protocolYield.min_deposit && amount < parseFloat(protocolYield.min_deposit)) {
        throw new Error(`Minimum deposit is ${protocolYield.min_deposit} ${protocolYield.token_symbol}`);
    }

    // Create position
    const positionData = {
        user_id: userId,
        protocol_yield_id: protocolYieldId,
        amount_deposited: amount,
        current_value: amount,
        apy_at_entry: protocolYield.apy,
        current_apy: protocolYield.apy,
        status: 'active',
        auto_rebalance: true
    };

    const response = await fetch(`${supabaseUrl}/rest/v1/user_yield_positions`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey,
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        },
        body: JSON.stringify(positionData)
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to create position: ${errorText}`);
    }

    const createdPosition = await response.json();

    // Calculate projected earnings
    const dailyRate = parseFloat(protocolYield.apy) / 365 / 100;
    const projectedEarnings = {
        daily: amount * dailyRate,
        weekly: amount * dailyRate * 7,
        monthly: amount * dailyRate * 30,
        yearly: amount * (parseFloat(protocolYield.apy) / 100)
    };

    return {
        position: createdPosition[0],
        protocol_details: protocolYield,
        projected_earnings: projectedEarnings,
        auto_compound_enabled: protocolYield.auto_compound
    };
}

// Get user positions
async function getUserPositions(supabaseUrl: string, serviceRoleKey: string, userId: string) {
    const response = await fetch(
        `${supabaseUrl}/rest/v1/user_yield_positions?user_id=eq.${userId}&status=eq.active&order=created_at.desc`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    if (!response.ok) {
        throw new Error('Failed to fetch positions');
    }

    const positions = await response.json();

    // Calculate portfolio statistics
    const totalDeposited = positions.reduce((sum: number, pos: any) =>
        sum + parseFloat(pos.amount_deposited), 0
    );

    const totalCurrentValue = positions.reduce((sum: number, pos: any) =>
        sum + parseFloat(pos.current_value), 0
    );

    const totalEarned = positions.reduce((sum: number, pos: any) =>
        sum + parseFloat(pos.total_earned || 0), 0
    );

    const avgApy = calculateAverage(positions, 'current_apy');

    return {
        positions,
        portfolio_summary: {
            total_deposited: totalDeposited,
            current_value: totalCurrentValue,
            total_earned: totalEarned,
            total_return_percentage: ((totalCurrentValue - totalDeposited) / totalDeposited) * 100,
            average_apy: avgApy,
            active_positions: positions.length
        }
    };
}

// Calculate impermanent loss
function calculateImpermanentLoss(tokenPair: string, entryPrice: any, currentPrice: any) {
    const priceRatio = currentPrice.token1 / entryPrice.token1;
    const impermanentLossPercent = (2 * Math.sqrt(priceRatio) / (1 + priceRatio) - 1) * 100;

    return {
        token_pair: tokenPair,
        entry_prices: entryPrice,
        current_prices: currentPrice,
        price_change_percentage: ((currentPrice.token1 / entryPrice.token1 - 1) * 100).toFixed(2),
        impermanent_loss_percentage: Math.abs(impermanentLossPercent).toFixed(2),
        hodl_value_comparison: impermanentLossPercent < 0 ? 'LP position underperforming' : 'LP position outperforming',
        recommendation: Math.abs(impermanentLossPercent) > 5 ? 'Consider rebalancing' : 'Position is stable'
    };
}

// Optimize strategy
async function optimizeStrategy(
    supabaseUrl: string,
    serviceRoleKey: string,
    strategyType: string,
    investmentAmount: number
) {
    // Strategy parameters
    const strategies: Record<string, any> = {
        conservative: { minApy: 5, maxRisk: 2, protocols: ['Aave', 'Compound'] },
        balanced: { minApy: 10, maxRisk: 3, protocols: ['Yearn', 'Convex', 'Aave'] },
        aggressive: { minApy: 20, maxRisk: 5, protocols: ['Beefy', 'Yearn', 'Convex'] }
    };

    const strategy = strategies[strategyType] || strategies.balanced;

    // Get suitable yield opportunities
    const yields = await getTopYields(supabaseUrl, serviceRoleKey, undefined, strategy.minApy, strategy.maxRisk);

    // Filter by preferred protocols
    const suitable = yields.opportunities.filter((y: any) =>
        strategy.protocols.some((p: string) => y.protocol_name.includes(p))
    ).slice(0, 5);

    // Allocate investment
    const allocation = suitable.map((y: any, index: number) => ({
        protocol: y.protocol_name,
        token: y.token_symbol,
        apy: y.apy,
        risk_score: y.risk_score,
        allocation_percentage: index === 0 ? 40 : 15,
        amount: investmentAmount * (index === 0 ? 0.4 : 0.15)
    }));

    const avgApy = allocation.reduce((sum: number, a: any) =>
        sum + parseFloat(a.apy) * (a.allocation_percentage / 100), 0
    );

    return {
        strategy_type: strategyType,
        investment_amount: investmentAmount,
        allocation,
        expected_annual_return: investmentAmount * (avgApy / 100),
        weighted_avg_apy: avgApy.toFixed(2),
        risk_level: strategyType
    };
}

// Auto rebalance positions
async function autoRebalance(supabaseUrl: string, serviceRoleKey: string, userId: string) {
    const positions = await getUserPositions(supabaseUrl, serviceRoleKey, userId);

    const rebalanceActions = [];

    for (const position of positions.positions) {
        const currentApy = parseFloat(position.current_apy);
        const entryApy = parseFloat(position.apy_at_entry);

        // Check if APY dropped significantly
        if (currentApy < entryApy * 0.7) {
            rebalanceActions.push({
                position_id: position.id,
                action: 'withdraw_and_reinvest',
                reason: 'APY dropped below threshold',
                current_apy: currentApy,
                target_apy: entryApy
            });
        }
    }

    return {
        positions_checked: positions.positions.length,
        rebalance_actions: rebalanceActions,
        estimated_improvement: rebalanceActions.length * 5, // percentage
        next_check_in: '24 hours'
    };
}

// Utility: Calculate average
function calculateAverage(arr: any[], field: string): number {
    if (arr.length === 0) return 0;
    const sum = arr.reduce((acc: number, item: any) => acc + parseFloat(item[field] || 0), 0);
    return sum / arr.length;
}
