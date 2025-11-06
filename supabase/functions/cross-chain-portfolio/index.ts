/**
 * Cross-Chain Portfolio Manager Edge Function
 * Purpose: Manage multi-chain cryptocurrency portfolios
 * Directive: C) Cross-Chain Blockchain Integration
 * Networks: Ethereum, BSC, Polygon, Arbitrum
 */

Deno.serve(async (req) => {
    const corsHeaders = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS, PUT, DELETE, PATCH',
        'Access-Control-Allow-Methods': '86400',
        'Access-Control-Allow-Credentials': 'false'
    };

    if (req.method === 'OPTIONS') {
        return new Response(null, { status: 200, headers: corsHeaders });
    }

    try {
        const { action, userId, walletAddress, networkId } = await req.json();

        if (!userId) {
            throw new Error('User ID is required');
        }

        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

        let result: any = {};

        switch (action) {
            case 'sync_portfolio':
                result = await syncCrossChainPortfolio(supabaseUrl!, serviceRoleKey!, userId, walletAddress);
                break;

            case 'get_portfolio':
                result = await getCrossChainPortfolio(supabaseUrl!, serviceRoleKey!, userId);
                break;

            case 'track_defi':
                result = await trackDeFiPositions(supabaseUrl!, serviceRoleKey!, userId);
                break;

            case 'check_gas':
                result = await checkGasPrices(supabaseUrl!, serviceRoleKey!);
                break;

            default:
                throw new Error('Invalid action specified');
        }

        return new Response(JSON.stringify({ data: result }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error: any) {
        console.error('Cross-Chain Portfolio Manager error:', error);

        return new Response(JSON.stringify({
            error: {
                code: 'CROSS_CHAIN_ERROR',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

/**
 * Sync portfolio across all chains
 */
async function syncCrossChainPortfolio(
    supabaseUrl: string,
    serviceRoleKey: string,
    userId: string,
    walletAddress?: string
): Promise<any> {
    // Get all blockchain networks
    const networksResponse = await fetch(`${supabaseUrl}/rest/v1/blockchain_networks?is_active=eq.true`, {
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey
        }
    });

    const networks = await networksResponse.json();

    // Get user's wallets
    const walletsResponse = await fetch(`${supabaseUrl}/rest/v1/cross_chain_wallets?user_id=eq.${userId}`, {
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey
        }
    });

    let wallets = await walletsResponse.json();

    // Ensure wallets is an array
    if (!Array.isArray(wallets)) {
        wallets = [];
    }

    // If wallet address provided and not in database, add it
    if (walletAddress && !wallets.some((w: any) => w.wallet_address === walletAddress)) {
        // Add new wallet (assuming first network if not specified)
        const newWallet = {
            user_id: userId,
            network_id: networks[0]?.id,
            wallet_address: walletAddress,
            wallet_label: 'Main Wallet',
            is_primary: wallets.length === 0
        };

        const insertResponse = await fetch(`${supabaseUrl}/rest/v1/cross_chain_wallets`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey,
                'Content-Type': 'application/json',
                'Prefer': 'return=representation'
            },
            body: JSON.stringify(newWallet)
        });

        const inserted = await insertResponse.json();
        wallets.push(inserted[0]);
    }

    // Sync balances for each wallet
    const balances: any[] = [];
    for (const wallet of wallets) {
        const network = networks.find((n: any) => n.id === wallet.network_id);
        
        // Simulate balance fetch (in production, call actual RPC)
        const balance = {
            native: (Math.random() * 10).toFixed(4),
            tokens: [
                { symbol: 'USDT', amount: (Math.random() * 10000).toFixed(2) },
                { symbol: 'USDC', amount: (Math.random() * 5000).toFixed(2) }
            ]
        };

        // Update wallet balance
        await fetch(`${supabaseUrl}/rest/v1/cross_chain_wallets?id=eq.${wallet.id}`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                balance,
                last_synced_at: new Date().toISOString()
            })
        });

        balances.push({
            network: network?.network_name,
            address: wallet.wallet_address,
            balance
        });
    }

    return {
        userId,
        walletsCount: wallets.length,
        networks: networks.length,
        balances,
        lastSynced: new Date().toISOString()
    };
}

/**
 * Get aggregated cross-chain portfolio
 */
async function getCrossChainPortfolio(
    supabaseUrl: string,
    serviceRoleKey: string,
    userId: string
): Promise<any> {
    // Get all user wallets with balances
    const walletsResponse = await fetch(`${supabaseUrl}/rest/v1/cross_chain_wallets?user_id=eq.${userId}`, {
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey
        }
    });

    let wallets = await walletsResponse.json();

    // Ensure wallets is an array
    if (!Array.isArray(wallets)) {
        wallets = [];
    }

    // Get DeFi positions
    const defiResponse = await fetch(`${supabaseUrl}/rest/v1/defi_positions?user_id=eq.${userId}&is_active=eq.true`, {
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey
        }
    });

    const defiPositions = await defiResponse.json();

    // Calculate total portfolio value
    let totalValue = 0;
    if (Array.isArray(wallets)) {
        wallets.forEach((w: any) => {
        if (w.balance?.tokens) {
            w.balance.tokens.forEach((t: any) => {
                totalValue += parseFloat(t.amount || 0);
            });
        }
        });
    }

    if (Array.isArray(defiPositions)) {
        defiPositions.forEach((p: any) => {
            totalValue += parseFloat(p.usd_value || 0);
        });
    }

    return {
        userId,
        totalValue: totalValue.toFixed(2),
        wallets: wallets.length,
        defiPositions: defiPositions.length,
        chains: [...new Set(wallets.map((w: any) => w.network_id))].length,
        breakdown: {
            wallets,
            defi: defiPositions
        }
    };
}

/**
 * Track DeFi positions
 */
async function trackDeFiPositions(
    supabaseUrl: string,
    serviceRoleKey: string,
    userId: string
): Promise<any> {
    // Get user's DeFi positions
    const defiResponse = await fetch(`${supabaseUrl}/rest/v1/defi_positions?user_id=eq.${userId}&is_active=eq.true`, {
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey
        }
    });

    let positions = await defiResponse.json();

    // If no positions, create sample positions
    if (positions.length === 0) {
        const samplePositions = [
            {
                user_id: userId,
                protocol: 'Uniswap V3',
                position_type: 'liquidity_pool',
                token_symbol: 'ETH-USDC',
                amount: 5000,
                usd_value: 5000,
                apy: 12.5,
                rewards: { pending: 25.50 },
                entry_timestamp: new Date().toISOString(),
                is_active: true
            },
            {
                user_id: userId,
                protocol: 'Aave',
                position_type: 'lending',
                token_symbol: 'USDT',
                amount: 10000,
                usd_value: 10000,
                apy: 4.8,
                rewards: { accrued: 120 },
                entry_timestamp: new Date().toISOString(),
                is_active: true
            }
        ];

        const insertResponse = await fetch(`${supabaseUrl}/rest/v1/defi_positions`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey,
                'Content-Type': 'application/json',
                'Prefer': 'return=representation'
            },
            body: JSON.stringify(samplePositions)
        });

        positions = await insertResponse.json();
    }

    // Calculate total DeFi value and rewards
    const totalValue = positions.reduce((sum: number, p: any) => sum + parseFloat(p.usd_value || 0), 0);
    const avgAPY = positions.reduce((sum: number, p: any) => sum + parseFloat(p.apy || 0), 0) / positions.length;

    return {
        positions,
        summary: {
            totalValue: totalValue.toFixed(2),
            averageAPY: avgAPY.toFixed(2),
            positionsCount: positions.length,
            protocols: [...new Set(positions.map((p: any) => p.protocol))]
        }
    };
}

/**
 * Check current gas prices across networks
 */
async function checkGasPrices(
    supabaseUrl: string,
    serviceRoleKey: string
): Promise<any> {
    const networksResponse = await fetch(`${supabaseUrl}/rest/v1/blockchain_networks?is_active=eq.true&is_testnet=eq.false`, {
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey
        }
    });

    const networks = await networksResponse.json();

    // Simulate gas price check (in production, call actual RPC)
    const gasPrices = networks.map((network: any) => {
        const baseGas = network.network_name === 'ethereum' ? 30 : 
                       network.network_name === 'bsc' ? 5 :
                       network.network_name === 'polygon' ? 40 : 10;
        
        const currentGas = baseGas + (Math.random() - 0.5) * 10;

        return {
            network: network.network_name,
            gasPrice: Math.max(1, currentGas).toFixed(2),
            unit: 'gwei',
            estimatedCost: {
                simple: (currentGas * 21000 / 1e9).toFixed(6),
                swap: (currentGas * 150000 / 1e9).toFixed(6),
                complex: (currentGas * 300000 / 1e9).toFixed(6)
            }
        };
    });

    return {
        timestamp: new Date().toISOString(),
        prices: gasPrices
    };
}
