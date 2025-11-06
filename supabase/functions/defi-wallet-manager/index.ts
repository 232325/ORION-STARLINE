// DEFI WALLET MANAGER EDGE FUNCTION
// Multi-chain wallet management, balance tracking, transaction history

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
            case 'connect_wallet':
                const { walletAddress, walletType, chain, label } = requestBody;
                result = await connectWallet(supabaseUrl, serviceRoleKey, userId, walletAddress, walletType, chain, label);
                break;

            case 'get_wallets':
                result = await getWallets(supabaseUrl, serviceRoleKey, userId);
                break;

            case 'get_balances':
                const { walletId } = requestBody;
                result = await getWalletBalances(supabaseUrl, serviceRoleKey, userId, walletId);
                break;

            case 'get_all_balances':
                result = await getAllBalances(supabaseUrl, serviceRoleKey, userId);
                break;

            case 'get_transactions':
                const { walletId: txWalletId, limit } = requestBody;
                result = await getTransactions(supabaseUrl, serviceRoleKey, userId, txWalletId, limit);
                break;

            case 'track_gas_usage':
                result = await trackGasUsage(supabaseUrl, serviceRoleKey, userId);
                break;

            default:
                throw new Error(`Unknown action: ${action}`);
        }

        return new Response(JSON.stringify({ data: result }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('DeFi Wallet Manager error:', error);

        return new Response(JSON.stringify({
            error: {
                code: 'WALLET_MANAGER_FAILED',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

// Connect wallet
async function connectWallet(
    supabaseUrl: string,
    serviceRoleKey: string,
    userId: string,
    walletAddress: string,
    walletType: string,
    chain: string,
    label?: string
) {
    // Check if wallet already exists
    const checkResponse = await fetch(
        `${supabaseUrl}/rest/v1/user_wallets?user_id=eq.${userId}&wallet_address=eq.${walletAddress}&chain=eq.${chain}`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    if (!checkResponse.ok) {
        throw new Error('Failed to check wallet existence');
    }

    const existing = await checkResponse.json();

    if (existing.length > 0) {
        return {
            wallet: existing[0],
            message: 'Wallet already connected',
            is_new: false
        };
    }

    // Create new wallet connection
    const walletData = {
        user_id: userId,
        wallet_address: walletAddress,
        wallet_type: walletType,
        chain: chain,
        label: label || `${walletType} - ${chain}`,
        is_active: true,
        last_used_at: new Date().toISOString()
    };

    const response = await fetch(`${supabaseUrl}/rest/v1/user_wallets`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey,
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        },
        body: JSON.stringify(walletData)
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to connect wallet: ${errorText}`);
    }

    const createdWallet = await response.json();

    // Fetch initial balances
    await syncWalletBalances(supabaseUrl, serviceRoleKey, createdWallet[0].id, walletAddress, chain);

    return {
        wallet: createdWallet[0],
        message: 'Wallet connected successfully',
        is_new: true,
        next_steps: ['Sync balances', 'Enable notifications', 'Set up auto-tracking']
    };
}

// Sync wallet balances
async function syncWalletBalances(
    supabaseUrl: string,
    serviceRoleKey: string,
    walletId: string,
    walletAddress: string,
    chain: string
) {
    // Simulated balance data (in production, would call blockchain RPC)
    const mockBalances = [
        { token_symbol: 'ETH', token_address: '0x0', balance: Math.random() * 5, usd_value: Math.random() * 10000 },
        { token_symbol: 'USDC', token_address: '0xa0b...', balance: Math.random() * 10000, usd_value: Math.random() * 10000 },
        { token_symbol: 'DAI', token_address: '0xdai...', balance: Math.random() * 5000, usd_value: Math.random() * 5000 }
    ];

    for (const balance of mockBalances) {
        const balanceData = {
            wallet_id: walletId,
            token_symbol: balance.token_symbol,
            token_address: balance.token_address,
            chain: chain,
            balance: balance.balance,
            usd_value: balance.usd_value
        };

        await fetch(`${supabaseUrl}/rest/v1/wallet_balances`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(balanceData)
        });
    }
}

// Get wallets
async function getWallets(supabaseUrl: string, serviceRoleKey: string, userId: string) {
    const response = await fetch(
        `${supabaseUrl}/rest/v1/user_wallets?user_id=eq.${userId}&is_active=eq.true&order=last_used_at.desc`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    if (!response.ok) {
        throw new Error('Failed to fetch wallets');
    }

    const wallets = await response.json();

    // Get balance summary for each wallet
    const walletsWithBalances = await Promise.all(
        wallets.map(async (wallet: any) => {
            const balancesResponse = await fetch(
                `${supabaseUrl}/rest/v1/wallet_balances?wallet_id=eq.${wallet.id}`,
                {
                    headers: {
                        'Authorization': `Bearer ${serviceRoleKey}`,
                        'apikey': serviceRoleKey
                    }
                }
            );

            const balances = await balancesResponse.json();
            const totalUsdValue = balances.reduce((sum: number, b: any) =>
                sum + parseFloat(b.usd_value || 0), 0
            );

            return {
                ...wallet,
                total_usd_value: totalUsdValue,
                token_count: balances.length
            };
        })
    );

    return {
        wallets: walletsWithBalances,
        total_wallets: walletsWithBalances.length,
        chains_connected: [...new Set(walletsWithBalances.map((w: any) => w.chain))]
    };
}

// Get wallet balances
async function getWalletBalances(supabaseUrl: string, serviceRoleKey: string, userId: string, walletId: string) {
    // Verify wallet belongs to user
    const walletResponse = await fetch(
        `${supabaseUrl}/rest/v1/user_wallets?id=eq.${walletId}&user_id=eq.${userId}`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    if (!walletResponse.ok) {
        throw new Error('Wallet not found');
    }

    const wallets = await walletResponse.json();

    if (wallets.length === 0) {
        throw new Error('Wallet not found or access denied');
    }

    // Get balances
    const response = await fetch(
        `${supabaseUrl}/rest/v1/wallet_balances?wallet_id=eq.${walletId}&order=usd_value.desc`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    if (!response.ok) {
        throw new Error('Failed to fetch balances');
    }

    const balances = await response.json();
    const totalUsd = balances.reduce((sum: number, b: any) => sum + parseFloat(b.usd_value || 0), 0);

    return {
        wallet: wallets[0],
        balances,
        summary: {
            total_usd_value: totalUsd,
            token_count: balances.length,
            last_synced: balances[0]?.last_synced_at || new Date().toISOString()
        }
    };
}

// Get all balances across wallets
async function getAllBalances(supabaseUrl: string, serviceRoleKey: string, userId: string) {
    const walletsResponse = await fetch(
        `${supabaseUrl}/rest/v1/user_wallets?user_id=eq.${userId}&is_active=eq.true`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    if (!walletsResponse.ok) {
        throw new Error('Failed to fetch wallets');
    }

    const wallets = await walletsResponse.json();
    const walletIds = wallets.map((w: any) => w.id);

    // Get all balances
    const balancesPromises = walletIds.map((id: string) =>
        fetch(`${supabaseUrl}/rest/v1/wallet_balances?wallet_id=eq.${id}`, {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }).then(r => r.json())
    );

    const balancesArrays = await Promise.all(balancesPromises);
    const allBalances = balancesArrays.flat();

    // Aggregate by token
    const aggregated: Record<string, any> = {};

    for (const balance of allBalances) {
        const key = balance.token_symbol;
        if (!aggregated[key]) {
            aggregated[key] = {
                token_symbol: key,
                total_balance: 0,
                total_usd_value: 0,
                chains: []
            };
        }
        aggregated[key].total_balance += parseFloat(balance.balance);
        aggregated[key].total_usd_value += parseFloat(balance.usd_value || 0);
        if (!aggregated[key].chains.includes(balance.chain)) {
            aggregated[key].chains.push(balance.chain);
        }
    }

    const aggregatedArray = Object.values(aggregated).sort((a: any, b: any) =>
        b.total_usd_value - a.total_usd_value
    );

    const totalPortfolioValue = aggregatedArray.reduce((sum: number, item: any) =>
        sum + item.total_usd_value, 0
    );

    return {
        portfolio_value: totalPortfolioValue,
        tokens: aggregatedArray,
        chains_active: [...new Set(allBalances.map((b: any) => b.chain))],
        total_tokens: aggregatedArray.length
    };
}

// Get transactions
async function getTransactions(
    supabaseUrl: string,
    serviceRoleKey: string,
    userId: string,
    walletId?: string,
    limit: number = 50
) {
    let query = `${supabaseUrl}/rest/v1/wallet_transactions?order=timestamp.desc&limit=${limit}`;

    if (walletId) {
        query += `&wallet_id=eq.${walletId}`;
    }

    const response = await fetch(query, {
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey
        }
    });

    if (!response.ok) {
        throw new Error('Failed to fetch transactions');
    }

    const transactions = await response.json();

    const totalGas = transactions.reduce((sum: number, tx: any) =>
        sum + parseFloat(tx.total_fee_usd || 0), 0
    );

    return {
        transactions,
        statistics: {
            total_transactions: transactions.length,
            total_gas_spent: totalGas,
            transaction_types: groupByType(transactions),
            chains_used: [...new Set(transactions.map((tx: any) => tx.chain))]
        }
    };
}

// Track gas usage
async function trackGasUsage(supabaseUrl: string, serviceRoleKey: string, userId: string) {
    const response = await fetch(
        `${supabaseUrl}/rest/v1/gas_optimization_logs?user_id=eq.${userId}&order=created_at.desc&limit=100`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    if (!response.ok) {
        throw new Error('Failed to fetch gas logs');
    }

    const logs = await response.json();

    const totalGasSpent = logs.reduce((sum: number, log: any) =>
        sum + parseFloat(log.actual_gas || 0), 0
    );

    const totalSaved = logs.reduce((sum: number, log: any) =>
        sum + parseFloat(log.gas_saved || 0), 0
    );

    return {
        total_gas_spent: totalGasSpent,
        total_gas_saved: totalSaved,
        optimization_rate: logs.filter((l: any) => l.optimization_applied).length / logs.length * 100,
        by_chain: groupByChain(logs),
        by_operation: groupByOperation(logs),
        recommendations: [
            totalGasSpent > 100 ? 'Consider using Layer 2 solutions' : null,
            'Batch transactions when possible',
            'Execute during low gas periods (UTC 0-4)'
        ].filter(Boolean)
    };
}

// Helper functions
function groupByType(transactions: any[]): Record<string, number> {
    return transactions.reduce((acc: any, tx: any) => {
        acc[tx.tx_type] = (acc[tx.tx_type] || 0) + 1;
        return acc;
    }, {});
}

function groupByChain(logs: any[]): Record<string, number> {
    return logs.reduce((acc: any, log: any) => {
        acc[log.chain] = (acc[log.chain] || 0) + parseFloat(log.actual_gas || 0);
        return acc;
    }, {});
}

function groupByOperation(logs: any[]): Record<string, number> {
    return logs.reduce((acc: any, log: any) => {
        acc[log.operation_type] = (acc[log.operation_type] || 0) + 1;
        return acc;
    }, {});
}
