// DEFI ARBITRAGE SCANNER EDGE FUNCTION
// Cross-chain and cross-DEX arbitrage opportunities
// Flash loan integration, MEV protection, gas optimization

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

        let result;

        switch (action) {
            case 'scan_opportunities':
                const { minProfit, maxRisk } = requestBody;
                result = await scanArbitrageOpportunities(supabaseUrl, serviceRoleKey, minProfit, maxRisk);
                break;

            case 'get_flash_loan_opportunities':
                result = await getFlashLoanOpportunities(supabaseUrl, serviceRoleKey);
                break;

            case 'calculate_arbitrage_profit':
                const { tokenSymbol, buyChain, buyDex, buyPrice, sellChain, sellDex, sellPrice, amount } = requestBody;
                result = calculateArbitrageProfit(tokenSymbol, buyChain, buyDex, buyPrice, sellChain, sellDex, sellPrice, amount);
                break;

            case 'execute_arbitrage':
                const { opportunityId } = requestBody;
                result = await executeArbitrage(supabaseUrl, serviceRoleKey, opportunityId);
                break;

            case 'get_mev_protection_status':
                result = await getMevProtectionStatus(supabaseUrl, serviceRoleKey);
                break;

            default:
                throw new Error(`Unknown action: ${action}`);
        }

        return new Response(JSON.stringify({ data: result }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('DeFi Arbitrage Scanner error:', error);

        return new Response(JSON.stringify({
            error: {
                code: 'ARBITRAGE_SCANNER_FAILED',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

// Scan arbitrage opportunities
async function scanArbitrageOpportunities(
    supabaseUrl: string,
    serviceRoleKey: string,
    minProfit: number = 50,
    maxRisk: string = 'medium'
) {
    // Fetch active arbitrage opportunities
    let query = `${supabaseUrl}/rest/v1/cross_chain_arbitrage?is_active=eq.true&order=net_profit.desc&limit=50`;

    if (minProfit) {
        query += `&net_profit=gte.${minProfit}`;
    }

    const response = await fetch(query, {
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey
        }
    });

    if (!response.ok) {
        throw new Error('Failed to fetch arbitrage opportunities');
    }

    let opportunities = await response.json();

    // Filter by risk level
    if (maxRisk) {
        const riskLevels: Record<string, number> = { low: 1, medium: 2, high: 3 };
        const maxRiskValue = riskLevels[maxRisk] || 2;
        opportunities = opportunities.filter((opp: any) =>
            (riskLevels[opp.risk_level] || 2) <= maxRiskValue
        );
    }

    // Add execution recommendations
    const enhancedOpportunities = opportunities.map((opp: any) => ({
        ...opp,
        execution_priority: calculateExecutionPriority(opp),
        gas_optimization_suggestion: suggestGasOptimization(opp),
        mev_protection_needed: parseFloat(opp.net_profit) > 500,
        estimated_execution_time: estimateExecutionTime(opp)
    }));

    return {
        opportunities: enhancedOpportunities,
        total_found: enhancedOpportunities.length,
        highest_profit: enhancedOpportunities[0],
        market_conditions: {
            volatility: 'moderate',
            gas_prices: 'normal',
            optimal_execution_window: '5 minutes'
        }
    };
}

// Calculate execution priority
function calculateExecutionPriority(opportunity: any): string {
    const profit = parseFloat(opportunity.net_profit);
    const liquidity = parseFloat(opportunity.liquidity_score || 50);
    const risk = opportunity.risk_level;

    if (profit > 1000 && liquidity > 70 && risk === 'low') return 'critical';
    if (profit > 500 && liquidity > 50) return 'high';
    if (profit > 200) return 'medium';
    return 'low';
}

// Suggest gas optimization
function suggestGasOptimization(opportunity: any): string {
    const sourceChain = opportunity.source_chain;
    const destChain = opportunity.destination_chain;

    if (sourceChain === 'Ethereum' || destChain === 'Ethereum') {
        return 'Use Layer 2 or execute during low gas hours (UTC 0-4)';
    }

    if (sourceChain === 'BSC' || destChain === 'BSC') {
        return 'Gas is low, execute anytime';
    }

    return 'Consider batching transactions for gas savings';
}

// Estimate execution time
function estimateExecutionTime(opportunity: any): string {
    const sourceChain = opportunity.source_chain;
    const destChain = opportunity.destination_chain;

    const blockTimes: Record<string, number> = {
        'Ethereum': 12,
        'BSC': 3,
        'Polygon': 2,
        'Arbitrum': 0.3,
        'Optimism': 2
    };

    const sourceTime = blockTimes[sourceChain] || 10;
    const destTime = blockTimes[destChain] || 10;
    const totalSeconds = (sourceTime * 3) + (destTime * 3) + 30; // 3 confirmations each + overhead

    return `${Math.ceil(totalSeconds / 60)} minutes`;
}

// Get flash loan opportunities
async function getFlashLoanOpportunities(supabaseUrl: string, serviceRoleKey: string) {
    const response = await fetch(
        `${supabaseUrl}/rest/v1/flash_loan_opportunities?is_executable=eq.true&order=estimated_profit.desc&limit=20`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    if (!response.ok) {
        throw new Error('Failed to fetch flash loan opportunities');
    }

    const opportunities = await response.json();

    // Add execution analysis
    const analyzed = opportunities.map((opp: any) => {
        const loanAmount = parseFloat(opp.max_loan_amount);
        const profit = parseFloat(opp.estimated_profit);
        const fee = loanAmount * (parseFloat(opp.fee_percentage) / 100);

        return {
            ...opp,
            net_profit_after_fees: profit - fee,
            roi_percentage: ((profit - fee) / loanAmount) * 100,
            complexity_score: calculateComplexityScore(opp.dex_path),
            recommended_gas_limit: 500000 * (opp.dex_path?.length || 3)
        };
    });

    return {
        opportunities: analyzed,
        flash_loan_providers: [
            { name: 'Aave V3', fee: 0.09, max_loan: 'Unlimited', chains: ['Ethereum', 'Polygon', 'Arbitrum'] },
            { name: 'dYdX', fee: 0, max_loan: 'Based on liquidity', chains: ['Ethereum'] },
            { name: 'Uniswap V3', fee: 'Variable', max_loan: 'Pool dependent', chains: ['Ethereum', 'Polygon'] }
        ],
        execution_tips: [
            'Test with small amounts first',
            'Monitor gas prices closely',
            'Use MEV protection for large profits',
            'Have backup execution paths'
        ]
    };
}

// Calculate complexity score
function calculateComplexityScore(dexPath: any): number {
    if (!dexPath || !Array.isArray(dexPath)) return 5;
    return Math.min(dexPath.length * 2, 10);
}

// Calculate arbitrage profit
function calculateArbitrageProfit(
    tokenSymbol: string,
    buyChain: string,
    buyDex: string,
    buyPrice: number,
    sellChain: string,
    sellDex: string,
    sellPrice: number,
    amount: number
) {
    // Price difference
    const priceDifference = sellPrice - buyPrice;
    const priceDifferencePercent = (priceDifference / buyPrice) * 100;

    // Gross profit
    const grossProfit = amount * priceDifference;

    // Estimate fees
    const buyFee = amount * buyPrice * 0.003; // 0.3% DEX fee
    const sellFee = amount * sellPrice * 0.003;

    // Gas costs (simplified)
    const gasCosts: Record<string, number> = {
        'Ethereum': 50,
        'BSC': 5,
        'Polygon': 0.5,
        'Arbitrum': 2,
        'Optimism': 1
    };

    const buyGasCost = gasCosts[buyChain] || 20;
    const sellGasCost = gasCosts[sellChain] || 20;
    const totalGasCost = buyGasCost + sellGasCost;

    // Bridge fee if cross-chain
    let bridgeFee = 0;
    if (buyChain !== sellChain) {
        bridgeFee = amount * sellPrice * 0.001; // 0.1% bridge fee
    }

    const totalFees = buyFee + sellFee + totalGasCost + bridgeFee;
    const netProfit = grossProfit - totalFees;
    const netProfitPercent = (netProfit / (amount * buyPrice)) * 100;

    return {
        token: tokenSymbol,
        amount,
        buy_location: `${buyDex} (${buyChain})`,
        buy_price: buyPrice,
        sell_location: `${sellDex} (${sellChain})`,
        sell_price: sellPrice,
        price_difference_percent: priceDifferencePercent.toFixed(2),
        gross_profit: grossProfit.toFixed(2),
        fees_breakdown: {
            dex_fees: (buyFee + sellFee).toFixed(2),
            gas_costs: totalGasCost.toFixed(2),
            bridge_fee: bridgeFee.toFixed(2),
            total: totalFees.toFixed(2)
        },
        net_profit: netProfit.toFixed(2),
        net_profit_percent: netProfitPercent.toFixed(2),
        is_profitable: netProfit > 0,
        risk_assessment: netProfit > 100 ? 'low' : netProfit > 20 ? 'medium' : 'high'
    };
}

// Execute arbitrage
async function executeArbitrage(supabaseUrl: string, serviceRoleKey: string, opportunityId: string) {
    // Fetch opportunity details
    const response = await fetch(
        `${supabaseUrl}/rest/v1/cross_chain_arbitrage?id=eq.${opportunityId}`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    if (!response.ok) {
        throw new Error('Opportunity not found');
    }

    const opportunities = await response.json();

    if (opportunities.length === 0 || !opportunities[0].is_active) {
        throw new Error('Opportunity expired or not available');
    }

    const opportunity = opportunities[0];

    // Execution plan
    const executionPlan = {
        step_1: {
            action: 'buy',
            chain: opportunity.source_chain,
            dex: opportunity.source_dex,
            token: opportunity.token_symbol,
            price: opportunity.source_price,
            estimated_gas: '150,000 units'
        },
        step_2: opportunity.source_chain !== opportunity.destination_chain ? {
            action: 'bridge',
            from: opportunity.source_chain,
            to: opportunity.destination_chain,
            estimated_time: '10 minutes'
        } : null,
        step_3: {
            action: 'sell',
            chain: opportunity.destination_chain,
            dex: opportunity.destination_dex,
            price: opportunity.destination_price,
            estimated_gas: '150,000 units'
        }
    };

    return {
        opportunity,
        execution_plan,
        expected_profit: opportunity.net_profit,
        mev_protection_enabled: true,
        status: 'ready_to_execute',
        next_steps: [
            'Approve token spending',
            'Execute buy transaction',
            'Bridge if needed',
            'Execute sell transaction'
        ],
        warnings: [
            'Price may change during execution',
            'Gas prices may fluctuate',
            'Ensure sufficient balance for fees'
        ]
    };
}

// Get MEV protection status
async function getMevProtectionStatus(supabaseUrl: string, serviceRoleKey: string) {
    const response = await fetch(
        `${supabaseUrl}/rest/v1/mev_protection_logs?order=created_at.desc&limit=100`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    if (!response.ok) {
        throw new Error('Failed to fetch MEV logs');
    }

    const logs = await response.json();

    const protectedCount = logs.filter((log: any) => log.protected).length;
    const totalSaved = logs.reduce((sum: number, log: any) =>
        sum + parseFloat(log.potential_loss || 0) - parseFloat(log.actual_loss || 0), 0
    );

    return {
        total_transactions: logs.length,
        protected_transactions: protectedCount,
        protection_rate: ((protectedCount / logs.length) * 100).toFixed(2),
        total_saved_usd: totalSaved.toFixed(2),
        protection_methods: {
            flashbots: logs.filter((l: any) => l.protection_method === 'flashbots').length,
            private_mempool: logs.filter((l: any) => l.protection_method === 'private_mempool').length
        },
        mev_types_detected: {
            frontrun: logs.filter((l: any) => l.mev_type === 'frontrun').length,
            backrun: logs.filter((l: any) => l.mev_type === 'backrun').length,
            sandwich: logs.filter((l: any) => l.mev_type === 'sandwich').length
        }
    };
}
