/**
 * Blockchain RPC Integration Edge Function
 * Purpose: Real blockchain interactions via RPC nodes
 * Directive: C) Cross-Chain Blockchain Integration - Production Ready
 * Networks: Ethereum, BSC, Polygon, Arbitrum
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
        // Parse request body once
        const requestBody = await req.json();
        const { action, network, address, contractAddress, method, params, txHash, blockNumber, transaction, tokenAddress } = requestBody;

        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

        // RPC endpoints (use public RPC for production, or configure private RPC)
        const rpcEndpoints: { [key: string]: string } = {
            'ethereum': 'https://eth.llamarpc.com',
            'bsc': 'https://bsc-dataseed.binance.org',
            'polygon': 'https://polygon-rpc.com',
            'arbitrum': 'https://arb1.arbitrum.io/rpc'
        };

        const rpcUrl = rpcEndpoints[network.toLowerCase()];
        if (!rpcUrl) {
            throw new Error('Unsupported network: ' + network);
        }

        let result: any = {};

        switch (action) {
            case 'get_balance':
                result = await getBalance(rpcUrl, address);
                break;

            case 'get_transaction':
                result = await getTransaction(rpcUrl, txHash);
                break;

            case 'get_block':
                result = await getBlock(rpcUrl, blockNumber || 'latest');
                break;

            case 'call_contract':
                result = await callContract(rpcUrl, contractAddress, method, params);
                break;

            case 'get_gas_price':
                result = await getGasPrice(rpcUrl);
                break;

            case 'estimate_gas':
                result = await estimateGas(rpcUrl, transaction);
                break;

            case 'get_token_balance':
                result = await getTokenBalance(rpcUrl, address, tokenAddress);
                break;

            default:
                throw new Error('Invalid action: ' + action);
        }

        // Log interaction
        await fetch(`${supabaseUrl}/rest/v1/smart_contract_interactions`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: 'system',
                contract_address: contractAddress || address,
                function_name: action,
                parameters: { network, address, method, params },
                status: 'confirmed'
            })
        });

        return new Response(JSON.stringify({ data: result }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error: any) {
        console.error('Blockchain RPC error:', error);

        return new Response(JSON.stringify({
            error: {
                code: 'BLOCKCHAIN_RPC_ERROR',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

/**
 * Get ETH/native token balance
 */
async function getBalance(rpcUrl: string, address: string): Promise<any> {
    const response = await fetch(rpcUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'eth_getBalance',
            params: [address, 'latest'],
            id: 1
        })
    });

    const data = await response.json();

    if (data.error) {
        throw new Error(data.error.message);
    }

    const balanceWei = parseInt(data.result, 16);
    const balanceEth = balanceWei / 1e18;

    return {
        address,
        balance: balanceEth.toString(),
        balanceWei: balanceWei.toString(),
        unit: 'ETH'
    };
}

/**
 * Get transaction details
 */
async function getTransaction(rpcUrl: string, txHash: string): Promise<any> {
    const response = await fetch(rpcUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'eth_getTransactionByHash',
            params: [txHash],
            id: 1
        })
    });

    const data = await response.json();

    if (data.error) {
        throw new Error(data.error.message);
    }

    if (!data.result) {
        throw new Error('Transaction not found');
    }

    const tx = data.result;

    // Get transaction receipt for status
    const receiptResponse = await fetch(rpcUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'eth_getTransactionReceipt',
            params: [txHash],
            id: 2
        })
    });

    const receiptData = await receiptResponse.json();
    const receipt = receiptData.result;

    return {
        hash: tx.hash,
        from: tx.from,
        to: tx.to,
        value: (parseInt(tx.value, 16) / 1e18).toString(),
        gasUsed: receipt ? parseInt(receipt.gasUsed, 16) : null,
        status: receipt ? (receipt.status === '0x1' ? 'success' : 'failed') : 'pending',
        blockNumber: tx.blockNumber ? parseInt(tx.blockNumber, 16) : null,
        confirmations: receipt ? 'confirmed' : 'pending'
    };
}

/**
 * Get block information
 */
async function getBlock(rpcUrl: string, blockNumber: string): Promise<any> {
    const response = await fetch(rpcUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'eth_getBlockByNumber',
            params: [blockNumber === 'latest' ? blockNumber : '0x' + parseInt(blockNumber).toString(16), false],
            id: 1
        })
    });

    const data = await response.json();

    if (data.error) {
        throw new Error(data.error.message);
    }

    const block = data.result;

    return {
        number: parseInt(block.number, 16),
        hash: block.hash,
        timestamp: parseInt(block.timestamp, 16),
        transactionCount: block.transactions.length,
        gasUsed: parseInt(block.gasUsed, 16),
        gasLimit: parseInt(block.gasLimit, 16)
    };
}

/**
 * Call smart contract method (read-only)
 */
async function callContract(
    rpcUrl: string,
    contractAddress: string,
    method: string,
    params: any[]
): Promise<any> {
    // For this example, we'll implement common ERC20 methods
    let data = '';

    if (method === 'balanceOf') {
        // balanceOf(address)
        data = '0x70a08231' + params[0].replace('0x', '').padStart(64, '0');
    } else if (method === 'totalSupply') {
        // totalSupply()
        data = '0x18160ddd';
    } else if (method === 'decimals') {
        // decimals()
        data = '0x313ce567';
    } else {
        throw new Error('Unsupported contract method: ' + method);
    }

    const response = await fetch(rpcUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'eth_call',
            params: [{
                to: contractAddress,
                data
            }, 'latest'],
            id: 1
        })
    });

    const responseData = await response.json();

    if (responseData.error) {
        throw new Error(responseData.error.message);
    }

    return {
        contractAddress,
        method,
        result: responseData.result,
        decoded: parseInt(responseData.result, 16)
    };
}

/**
 * Get current gas price
 */
async function getGasPrice(rpcUrl: string): Promise<any> {
    const response = await fetch(rpcUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'eth_gasPrice',
            id: 1
        })
    });

    const data = await response.json();

    if (data.error) {
        throw new Error(data.error.message);
    }

    const gasPriceWei = parseInt(data.result, 16);
    const gasPriceGwei = gasPriceWei / 1e9;

    return {
        gasPrice: gasPriceGwei.toFixed(2),
        unit: 'gwei',
        estimatedCost: {
            simple: (gasPriceWei * 21000 / 1e18).toFixed(6) + ' ETH',
            erc20: (gasPriceWei * 65000 / 1e18).toFixed(6) + ' ETH',
            complex: (gasPriceWei * 150000 / 1e18).toFixed(6) + ' ETH'
        }
    };
}

/**
 * Estimate gas for transaction
 */
async function estimateGas(rpcUrl: string, transaction: any): Promise<any> {
    const response = await fetch(rpcUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'eth_estimateGas',
            params: [transaction],
            id: 1
        })
    });

    const data = await response.json();

    if (data.error) {
        throw new Error(data.error.message);
    }

    const gasEstimate = parseInt(data.result, 16);

    return {
        gasEstimate,
        gasEstimateFormatted: gasEstimate.toString()
    };
}

/**
 * Get ERC20 token balance
 */
async function getTokenBalance(
    rpcUrl: string,
    address: string,
    tokenAddress: string
): Promise<any> {
    // Call balanceOf(address)
    const data = '0x70a08231' + address.replace('0x', '').padStart(64, '0');

    const response = await fetch(rpcUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'eth_call',
            params: [{
                to: tokenAddress,
                data
            }, 'latest'],
            id: 1
        })
    });

    const responseData = await response.json();

    if (responseData.error) {
        throw new Error(responseData.error.message);
    }

    const balance = parseInt(responseData.result, 16);

    // Get decimals
    const decimalsData = '0x313ce567';
    const decimalsResponse = await fetch(rpcUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'eth_call',
            params: [{
                to: tokenAddress,
                data: decimalsData
            }, 'latest'],
            id: 2
        })
    });

    const decimalsData2 = await decimalsResponse.json();
    const decimals = parseInt(decimalsData2.result, 16);

    const formattedBalance = balance / Math.pow(10, decimals);

    return {
        address,
        tokenAddress,
        balance: formattedBalance.toString(),
        balanceRaw: balance.toString(),
        decimals
    };
}
