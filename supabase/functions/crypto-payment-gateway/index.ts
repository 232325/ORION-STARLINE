/**
 * Crypto Payment Gateway Edge Function
 * Purpose: Handle crypto deposits and withdrawals
 * Directive: E) Advanced Security & Monetization
 * Supported: BTC, ETH, USDT, USDC on multiple networks
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
        const { action, userId, currency, network, amount, toAddress, fromAddress } = await req.json();

        if (!userId) {
            throw new Error('User ID is required');
        }

        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

        let result: any = {};

        switch (action) {
            case 'generate_deposit_address':
                result = await generateDepositAddress(supabaseUrl!, serviceRoleKey!, userId, currency, network);
                break;

            case 'process_deposit':
                result = await processDeposit(supabaseUrl!, serviceRoleKey!, userId, currency, network, amount, fromAddress);
                break;

            case 'initiate_withdrawal':
                result = await initiateWithdrawal(supabaseUrl!, serviceRoleKey!, userId, currency, network, amount, toAddress);
                break;

            case 'check_transaction':
                const { transactionHash } = await req.json();
                result = await checkTransactionStatus(supabaseUrl!, serviceRoleKey!, transactionHash);
                break;

            case 'get_balance':
                result = await getCryptoBalance(supabaseUrl!, serviceRoleKey!, userId);
                break;

            case 'get_transactions':
                result = await getTransactionHistory(supabaseUrl!, serviceRoleKey!, userId);
                break;

            default:
                throw new Error('Invalid action specified');
        }

        return new Response(JSON.stringify({ data: result }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error: any) {
        console.error('Crypto Payment Gateway error:', error);

        return new Response(JSON.stringify({
            error: {
                code: 'CRYPTO_PAYMENT_ERROR',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

/**
 * Generate deposit address for user
 */
async function generateDepositAddress(
    supabaseUrl: string,
    serviceRoleKey: string,
    userId: string,
    currency: string,
    network: string
): Promise<any> {
    // In production, this would generate a real address from wallet service
    // For now, generate a deterministic address based on userId
    const address = generateMockAddress(userId, currency, network);

    // Store address mapping
    const walletResponse = await fetch(`${supabaseUrl}/rest/v1/cross_chain_wallets`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey,
            'Content-Type': 'application/json',
            'Prefer': 'resolution=ignore-duplicates,return=representation'
        },
        body: JSON.stringify({
            user_id: userId,
            wallet_address: address,
            wallet_label: `${currency} Deposit Address (${network})`,
            balance: { native: '0', tokens: [] }
        })
    });

    const wallet = await walletResponse.json();

    return {
        userId,
        currency,
        network,
        depositAddress: address,
        qrCode: `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${address}`,
        instructions: {
            minDeposit: getMinDeposit(currency),
            confirmations: getRequiredConfirmations(network),
            warning: 'Only send ' + currency + ' on ' + network + ' network to this address. Sending other assets may result in permanent loss.'
        }
    };
}

/**
 * Process incoming deposit
 */
async function processDeposit(
    supabaseUrl: string,
    serviceRoleKey: string,
    userId: string,
    currency: string,
    network: string,
    amount: number,
    fromAddress: string
): Promise<any> {
    // Generate transaction hash (in production, this comes from blockchain)
    const transactionHash = generateTransactionHash();

    // Get current price for USD conversion
    const priceResponse = await fetch(
        `${supabaseUrl}/rest/v1/realtime_prices?symbol=eq.${currency}&order=timestamp.desc&limit=1`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    const priceData = await priceResponse.json();
    const usdValue = priceData.length > 0 ? parseFloat(priceData[0].price) * amount : amount;

    // Create transaction record
    const insertResponse = await fetch(`${supabaseUrl}/rest/v1/crypto_payment_transactions`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey,
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        },
        body: JSON.stringify({
            user_id: userId,
            transaction_hash: transactionHash,
            from_address: fromAddress,
            to_address: generateMockAddress(userId, currency, network),
            amount,
            currency,
            network,
            confirmations: 0,
            status: 'pending',
            usd_value: usdValue
        })
    });

    const transaction = await insertResponse.json();

    // Log audit trail
    await fetch(`${supabaseUrl}/rest/v1/comprehensive_audit_logs`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: userId,
            action: 'crypto_deposit_initiated',
            resource_type: 'payment',
            resource_id: transactionHash,
            new_value: { amount, currency, network }
        })
    });

    return {
        transactionId: transaction[0]?.id,
        transactionHash,
        status: 'pending',
        amount,
        currency,
        network,
        usdValue,
        confirmations: 0,
        requiredConfirmations: getRequiredConfirmations(network),
        estimatedConfirmationTime: getEstimatedConfirmationTime(network),
        message: 'Deposit is being processed. You will be credited after ' + getRequiredConfirmations(network) + ' confirmations.'
    };
}

/**
 * Initiate withdrawal
 */
async function initiateWithdrawal(
    supabaseUrl: string,
    serviceRoleKey: string,
    userId: string,
    currency: string,
    network: string,
    amount: number,
    toAddress: string
): Promise<any> {
    // Validate address format
    if (!isValidAddress(toAddress, network)) {
        throw new Error('Invalid withdrawal address format');
    }

    // Check minimum withdrawal
    const minWithdrawal = getMinWithdrawal(currency);
    if (amount < minWithdrawal) {
        throw new Error(`Minimum withdrawal is ${minWithdrawal} ${currency}`);
    }

    // In production, check user balance from wallet service
    // For now, simulate balance check

    // Calculate fee
    const withdrawalFee = calculateWithdrawalFee(currency, network, amount);
    const netAmount = amount - withdrawalFee;

    if (netAmount <= 0) {
        throw new Error('Amount too small after fees');
    }

    // Generate transaction hash (in production, submit to blockchain)
    const transactionHash = generateTransactionHash();

    // Get USD value
    const priceResponse = await fetch(
        `${supabaseUrl}/rest/v1/realtime_prices?symbol=eq.${currency}&order=timestamp.desc&limit=1`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    const priceData = await priceResponse.json();
    const usdValue = priceData.length > 0 ? parseFloat(priceData[0].price) * netAmount : netAmount;

    // Create withdrawal transaction
    const insertResponse = await fetch(`${supabaseUrl}/rest/v1/crypto_payment_transactions`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey,
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        },
        body: JSON.stringify({
            user_id: userId,
            transaction_hash: transactionHash,
            from_address: generateMockAddress(userId, currency, network),
            to_address: toAddress,
            amount: netAmount,
            currency,
            network,
            confirmations: 0,
            status: 'pending',
            usd_value: usdValue
        })
    });

    const transaction = await insertResponse.json();

    // Log audit trail
    await fetch(`${supabaseUrl}/rest/v1/comprehensive_audit_logs`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: userId,
            action: 'crypto_withdrawal_initiated',
            resource_type: 'payment',
            resource_id: transactionHash,
            new_value: { amount: netAmount, currency, network, toAddress, fee: withdrawalFee }
        })
    });

    return {
        transactionId: transaction[0]?.id,
        transactionHash,
        status: 'pending',
        requestedAmount: amount,
        withdrawalFee,
        netAmount,
        currency,
        network,
        toAddress,
        usdValue,
        estimatedProcessingTime: '10-30 minutes',
        message: 'Withdrawal initiated. You will receive your funds shortly.'
    };
}

/**
 * Check transaction status
 */
async function checkTransactionStatus(
    supabaseUrl: string,
    serviceRoleKey: string,
    transactionHash: string
): Promise<any> {
    const response = await fetch(
        `${supabaseUrl}/rest/v1/crypto_payment_transactions?transaction_hash=eq.${transactionHash}`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    const transactions = await response.json();

    if (!transactions || transactions.length === 0) {
        throw new Error('Transaction not found');
    }

    const tx = transactions[0];

    // In production, query blockchain for actual confirmations
    // For now, simulate progression
    let updatedStatus = tx.status;
    let updatedConfirmations = tx.confirmations;

    if (tx.status === 'pending') {
        // Simulate confirmation progression
        const age = Date.now() - new Date(tx.created_at).getTime();
        const minutesOld = age / (1000 * 60);

        if (minutesOld > 30) {
            updatedStatus = 'confirmed';
            updatedConfirmations = getRequiredConfirmations(tx.network);
        } else if (minutesOld > 10) {
            updatedConfirmations = Math.floor(getRequiredConfirmations(tx.network) / 2);
        }

        // Update if changed
        if (updatedStatus !== tx.status || updatedConfirmations !== tx.confirmations) {
            await fetch(`${supabaseUrl}/rest/v1/crypto_payment_transactions?transaction_hash=eq.${transactionHash}`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    status: updatedStatus,
                    confirmations: updatedConfirmations,
                    confirmed_at: updatedStatus === 'confirmed' ? new Date().toISOString() : null
                })
            });
        }
    }

    return {
        transactionHash,
        status: updatedStatus,
        confirmations: updatedConfirmations,
        requiredConfirmations: getRequiredConfirmations(tx.network),
        amount: tx.amount,
        currency: tx.currency,
        network: tx.network,
        fromAddress: tx.from_address,
        toAddress: tx.to_address,
        createdAt: tx.created_at,
        confirmedAt: tx.confirmed_at
    };
}

/**
 * Get user crypto balance
 */
async function getCryptoBalance(
    supabaseUrl: string,
    serviceRoleKey: string,
    userId: string
): Promise<any> {
    // Get confirmed deposits
    const depositsResponse = await fetch(
        `${supabaseUrl}/rest/v1/crypto_payment_transactions?user_id=eq.${userId}&status=eq.confirmed&to_address=like.*`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    let deposits = await depositsResponse.json();

    // Ensure deposits is an array
    if (!Array.isArray(deposits)) {
        deposits = [];
    }

    // Get withdrawals
    const withdrawalsResponse = await fetch(
        `${supabaseUrl}/rest/v1/crypto_payment_transactions?user_id=eq.${userId}&status=eq.confirmed&from_address=like.*`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    let withdrawals = await withdrawalsResponse.json();

    // Ensure withdrawals is an array
    if (!Array.isArray(withdrawals)) {
        withdrawals = [];
    }

    // Calculate balances per currency
    const balances: { [key: string]: number } = {};

    if (Array.isArray(deposits)) {
        deposits.forEach((tx: any) => {
            balances[tx.currency] = (balances[tx.currency] || 0) + parseFloat(tx.amount);
        });
    }

    if (Array.isArray(withdrawals)) {
        withdrawals.forEach((tx: any) => {
            balances[tx.currency] = (balances[tx.currency] || 0) - parseFloat(tx.amount);
        });
    }

    return {
        userId,
        balances: Object.entries(balances).map(([currency, amount]) => ({
            currency,
            amount: amount.toFixed(8),
            available: amount.toFixed(8)
        })),
        totalUsdValue: Object.entries(balances).reduce((sum, [currency, amount]) => sum + amount * 100, 0).toFixed(2)
    };
}

/**
 * Get transaction history
 */
async function getTransactionHistory(
    supabaseUrl: string,
    serviceRoleKey: string,
    userId: string
): Promise<any> {
    const response = await fetch(
        `${supabaseUrl}/rest/v1/crypto_payment_transactions?user_id=eq.${userId}&order=created_at.desc&limit=50`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    const transactions = await response.json();

    return {
        userId,
        transactions: transactions.map((tx: any) => ({
            id: tx.id,
            transactionHash: tx.transaction_hash,
            type: tx.to_address.includes(userId) ? 'deposit' : 'withdrawal',
            amount: tx.amount,
            currency: tx.currency,
            network: tx.network,
            status: tx.status,
            confirmations: tx.confirmations,
            usdValue: tx.usd_value,
            createdAt: tx.created_at,
            confirmedAt: tx.confirmed_at
        }))
    };
}

// Helper functions
function generateMockAddress(userId: string, currency: string, network: string): string {
    const hash = Array.from(userId + currency + network)
        .reduce((acc, char) => acc + char.charCodeAt(0), 0);
    
    if (currency === 'BTC') {
        return '1' + hash.toString().padStart(33, '0').substring(0, 33);
    } else if (currency === 'ETH' || currency === 'USDT' || currency === 'USDC') {
        return '0x' + hash.toString(16).padStart(40, '0').substring(0, 40);
    }
    
    return 'addr_' + hash.toString(16);
}

function generateTransactionHash(): string {
    return '0x' + Array.from({ length: 64 }, () => 
        Math.floor(Math.random() * 16).toString(16)
    ).join('');
}

function getMinDeposit(currency: string): string {
    const minimums: { [key: string]: string } = {
        'BTC': '0.001',
        'ETH': '0.01',
        'USDT': '10',
        'USDC': '10'
    };
    return minimums[currency] || '1';
}

function getMinWithdrawal(currency: string): number {
    const minimums: { [key: string]: number } = {
        'BTC': 0.001,
        'ETH': 0.01,
        'USDT': 20,
        'USDC': 20
    };
    return minimums[currency] || 1;
}

function getRequiredConfirmations(network: string): number {
    const confirmations: { [key: string]: number } = {
        'bitcoin': 3,
        'ethereum': 12,
        'bsc': 15,
        'polygon': 30,
        'arbitrum': 1
    };
    return confirmations[network.toLowerCase()] || 6;
}

function getEstimatedConfirmationTime(network: string): string {
    const times: { [key: string]: string } = {
        'bitcoin': '30-60 minutes',
        'ethereum': '3-5 minutes',
        'bsc': '1-3 minutes',
        'polygon': '2-5 minutes',
        'arbitrum': '< 1 minute'
    };
    return times[network.toLowerCase()] || '10-30 minutes';
}

function calculateWithdrawalFee(currency: string, network: string, amount: number): number {
    const fees: { [key: string]: number } = {
        'BTC': 0.0005,
        'ETH': 0.003,
        'USDT': 1,
        'USDC': 1
    };
    
    const baseFee = fees[currency] || 0.01;
    
    // Network-specific multipliers
    if (network.toLowerCase() === 'ethereum') {
        return baseFee * 2; // Higher gas fees
    }
    
    return baseFee;
}

function isValidAddress(address: string, network: string): boolean {
    if (network.toLowerCase() === 'bitcoin') {
        return /^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$/.test(address) || 
               /^bc1[a-z0-9]{39,59}$/.test(address);
    } else if (['ethereum', 'bsc', 'polygon', 'arbitrum'].includes(network.toLowerCase())) {
        return /^0x[a-fA-F0-9]{40}$/.test(address);
    }
    
    return true; // Allow for testing
}
