/**
 * DeFi & Decentralized Trading Edge Function
 * Purpose: DEX integrations, yield farming, staking, liquidity provision
 * Phase: 3 - DeFi Trading
 */

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
        const { action, userId, network, ...params } = await req.json();

        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

        let result: any = {};

        switch (action) {
            case 'get_dex_price':
                result = await getDexPrice(network, params.tokenA, params.tokenB, params.dex);
                break;
            case 'find_best_route':
                result = await findBestSwapRoute(network, params.tokenA, params.tokenB, params.amount);
                break;
            case 'get_liquidity_pools':
                result = await getLiquidityPools(supabaseUrl!, serviceRoleKey!, network);
                break;
            case 'calculate_yield':
                result = await calculateYieldFarming(params.poolAddress, params.amount);
                break;
            case 'get_staking_opportunities':
                result = await getStakingOpportunities(supabaseUrl!, serviceRoleKey!, network);
                break;
            case 'track_defi_position':
                result = await trackDeFiPosition(supabaseUrl!, serviceRoleKey!, userId, params);
                break;
            default:
                throw new Error('Invalid action');
        }

        return new Response(JSON.stringify({ data: result }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error: any) {
        return new Response(JSON.stringify({
            error: { code: 'DEFI_TRADING_ERROR', message: error.message }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

/**
 * Get DEX price for token pair
 */
async function getDexPrice(network: string, tokenA: string, tokenB: string, dex: string) {
    // Simulate DEX price fetching (in production, use actual DEX APIs/contracts)
    const dexAPIs: any = {
        'uniswap': `https://api.uniswap.org/v2/quote?tokenIn=${tokenA}&tokenOut=${tokenB}`,
        'pancakeswap': `https://api.pancakeswap.info/api/v2/tokens/${tokenA}`,
        '1inch': `https://api.1inch.io/v5.0/${getChainId(network)}/quote`
    };

    // Mock response for demonstration
    const basePrice = 1500 + Math.random() * 100;
    const slippage = 0.001 + Math.random() * 0.002;

    return {
        dex,
        network,
        tokenPair: `${tokenA}/${tokenB}`,
        price: basePrice.toFixed(2),
        priceImpact: (slippage * 100).toFixed(3) + '%',
        liquidity: ((Math.random() * 10000000) + 1000000).toFixed(2),
        timestamp: new Date().toISOString()
    };
}

/**
 * Find best swap route across multiple DEXes
 */
async function findBestSwapRoute(network: string, tokenA: string, tokenB: string, amount: number) {
    const dexes = ['uniswap', 'pancakeswap', '1inch', 'sushiswap'];
    const routes: any[] = [];

    for (const dex of dexes) {
        const price = await getDexPrice(network, tokenA, tokenB, dex);
        const outputAmount = amount * parseFloat(price.price);
        const fee = outputAmount * 0.003; // 0.3% fee

        routes.push({
            dex,
            inputAmount: amount,
            outputAmount: (outputAmount - fee).toFixed(6),
            fee: fee.toFixed(6),
            priceImpact: price.priceImpact,
            route: [tokenA, tokenB]
        });
    }

    // Sort by best output
    routes.sort((a, b) => parseFloat(b.outputAmount) - parseFloat(a.outputAmount));

    return {
        bestRoute: routes[0],
        allRoutes: routes,
        savings: (parseFloat(routes[0].outputAmount) - parseFloat(routes[routes.length - 1].outputAmount)).toFixed(6),
        recommendation: `Use ${routes[0].dex} for best rate`
    };
}

/**
 * Get available liquidity pools
 */
async function getLiquidityPools(url: string, key: string, network: string) {
    // Get liquidity pools from database
    const poolsResp = await fetch(
        `${url}/rest/v1/defi_liquidity_pools?network=eq.${network}&is_active=eq.true&order=tvl.desc&limit=20`,
        { headers: { 'Authorization': `Bearer ${key}`, 'apikey': key } }
    );
    let pools = await poolsResp.json();
    if (!Array.isArray(pools)) pools = [];

    // If no pools, return sample data
    if (pools.length === 0) {
        return [
            {
                protocol: 'Uniswap V3',
                pair: 'ETH/USDC',
                apr: '45.2%',
                tvl: '$125,000,000',
                volume24h: '$45,000,000',
                fees24h: '$135,000'
            },
            {
                protocol: 'PancakeSwap',
                pair: 'BNB/BUSD',
                apr: '38.5%',
                tvl: '$85,000,000',
                volume24h: '$32,000,000',
                fees24h: '$96,000'
            },
            {
                protocol: 'SushiSwap',
                pair: 'MATIC/USDT',
                apr: '52.8%',
                tvl: '$45,000,000',
                volume24h: '$18,000,000',
                fees24h: '$54,000'
            }
        ];
    }

    return pools;
}

/**
 * Calculate yield farming returns
 */
async function calculateYieldFarming(poolAddress: string, amount: number) {
    // Simulate yield calculation
    const baseAPR = 35 + Math.random() * 40; // 35-75% APR
    const farmingRewards = 5 + Math.random() * 15; // 5-20% farming rewards
    const totalAPY = baseAPR + farmingRewards;

    const dailyYield = (amount * totalAPY / 100) / 365;
    const weeklyYield = dailyYield * 7;
    const monthlyYield = dailyYield * 30;
    const yearlyYield = amount * totalAPY / 100;

    return {
        poolAddress,
        depositAmount: amount,
        apr: baseAPR.toFixed(2) + '%',
        farmingRewards: farmingRewards.toFixed(2) + '%',
        totalAPY: totalAPY.toFixed(2) + '%',
        projectedReturns: {
            daily: dailyYield.toFixed(2),
            weekly: weeklyYield.toFixed(2),
            monthly: monthlyYield.toFixed(2),
            yearly: yearlyYield.toFixed(2)
        },
        risks: [
            'Impermanent Loss',
            'Smart Contract Risk',
            'Market Volatility'
        ]
    };
}

/**
 * Get staking opportunities
 */
async function getStakingOpportunities(url: string, key: string, network: string) {
    const opportunities = [
        {
            protocol: 'Ethereum 2.0',
            asset: 'ETH',
            apr: '4.5%',
            minStake: 32,
            lockPeriod: 'Until ETH 2.0 merge complete',
            risk: 'LOW'
        },
        {
            protocol: 'Polygon',
            asset: 'MATIC',
            apr: '8.2%',
            minStake: 1,
            lockPeriod: '21 days',
            risk: 'LOW'
        },
        {
            protocol: 'Cosmos',
            asset: 'ATOM',
            apr: '12.5%',
            minStake: 0.1,
            lockPeriod: '21 days',
            risk: 'MEDIUM'
        },
        {
            protocol: 'Solana',
            asset: 'SOL',
            apr: '6.8%',
            minStake: 0.01,
            lockPeriod: '3 days',
            risk: 'MEDIUM'
        }
    ];

    return {
        network,
        opportunities,
        totalOpportunities: opportunities.length,
        averageAPR: '8.0%'
    };
}

/**
 * Track DeFi position
 */
async function trackDeFiPosition(url: string, key: string, userId: string, params: any) {
    const position = {
        user_id: userId,
        protocol: params.protocol,
        position_type: params.type, // 'liquidity', 'staking', 'farming'
        token_symbol: params.symbol,
        amount: params.amount,
        entry_price: params.entryPrice,
        current_value: params.amount * params.entryPrice,
        apy: params.apy,
        rewards_earned: 0,
        is_active: true,
        entry_timestamp: new Date().toISOString()
    };

    const resp = await fetch(`${url}/rest/v1/defi_positions`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${key}`,
            'apikey': key,
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        },
        body: JSON.stringify(position)
    });

    const data = await resp.json();
    return Array.isArray(data) ? data[0] : data;
}

/**
 * Helper: Get chain ID
 */
function getChainId(network: string): number {
    const chains: any = {
        'ethereum': 1,
        'bsc': 56,
        'polygon': 137,
        'arbitrum': 42161,
        'optimism': 10
    };
    return chains[network.toLowerCase()] || 1;
}
