/**
 * Options Pricing Calculator Edge Function
 * Purpose: Calculate options prices using Black-Scholes and Greeks
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
        const { action, symbol, contractType, strikePrice, expirationDate, spotPrice, volatility, riskFreeRate } = await req.json();

        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

        let result: any = {};

        if (action === 'calculate_price') {
            // Calculate option price using Black-Scholes
            const S = spotPrice; // Current spot price
            const K = strikePrice; // Strike price
            const T = calculateTimeToExpiry(expirationDate); // Time to expiry in years
            const r = riskFreeRate || 0.05; // Risk-free rate (5% default)
            const sigma = volatility || 0.3; // Implied volatility (30% default)

            const optionPrice = blackScholes(S, K, T, r, sigma, contractType);
            const greeks = calculateGreeks(S, K, T, r, sigma, contractType);

            result = {
                symbol,
                contractType,
                strikePrice,
                spotPrice,
                expirationDate,
                timeToExpiry: T,
                optionPrice: optionPrice.toFixed(4),
                greeks,
                impliedVolatility: sigma,
                riskFreeRate: r
            };

            // Save to database
            const contractData = {
                symbol,
                contract_type: contractType,
                strike_price: strikePrice,
                expiration_date: expirationDate,
                premium: optionPrice,
                implied_volatility: sigma,
                delta: greeks.delta,
                gamma: greeks.gamma,
                theta: greeks.theta,
                vega: greeks.vega,
                last_price: optionPrice
            };

            await fetch(`${supabaseUrl}/rest/v1/options_contracts`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(contractData)
            });

        } else if (action === 'get_chain') {
            // Get options chain for a symbol
            const contractsResponse = await fetch(
                `${supabaseUrl}/rest/v1/options_contracts?symbol=eq.${symbol}&order=strike_price.asc`,
                {
                    headers: {
                        'Authorization': `Bearer ${serviceRoleKey}`,
                        'apikey': serviceRoleKey
                    }
                }
            );

            const contracts = await contractsResponse.json();

            result = {
                symbol,
                chain: contracts,
                callsCount: contracts.filter((c: any) => c.contract_type === 'call').length,
                putsCount: contracts.filter((c: any) => c.contract_type === 'put').length
            };

        } else if (action === 'analyze_strategy') {
            // Analyze multi-leg options strategy
            const { legs } = await req.json();
            result = analyzeOptionsStrategy(legs, spotPrice);

        } else {
            throw new Error('Invalid action');
        }

        return new Response(JSON.stringify({ data: result }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error: any) {
        console.error('Options Pricing error:', error);

        return new Response(JSON.stringify({
            error: {
                code: 'OPTIONS_PRICING_ERROR',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

/**
 * Black-Scholes option pricing formula
 */
function blackScholes(
    S: number,
    K: number,
    T: number,
    r: number,
    sigma: number,
    type: string
): number {
    if (T <= 0) return type === 'call' ? Math.max(S - K, 0) : Math.max(K - S, 0);

    const d1 = (Math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * Math.sqrt(T));
    const d2 = d1 - sigma * Math.sqrt(T);

    const Nd1 = normalCDF(d1);
    const Nd2 = normalCDF(d2);
    const NminusD1 = normalCDF(-d1);
    const NminusD2 = normalCDF(-d2);

    if (type === 'call') {
        return S * Nd1 - K * Math.exp(-r * T) * Nd2;
    } else {
        return K * Math.exp(-r * T) * NminusD2 - S * NminusD1;
    }
}

/**
 * Calculate option Greeks
 */
function calculateGreeks(
    S: number,
    K: number,
    T: number,
    r: number,
    sigma: number,
    type: string
): any {
    if (T <= 0) {
        return { delta: 0, gamma: 0, theta: 0, vega: 0, rho: 0 };
    }

    const d1 = (Math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * Math.sqrt(T));
    const d2 = d1 - sigma * Math.sqrt(T);

    const Nd1 = normalCDF(d1);
    const nd1 = normalPDF(d1);
    const Nd2 = normalCDF(d2);

    // Delta
    const delta = type === 'call' ? Nd1 : Nd1 - 1;

    // Gamma (same for calls and puts)
    const gamma = nd1 / (S * sigma * Math.sqrt(T));

    // Theta
    const theta1 = -(S * nd1 * sigma) / (2 * Math.sqrt(T));
    const theta2 = type === 'call' 
        ? r * K * Math.exp(-r * T) * Nd2
        : -r * K * Math.exp(-r * T) * normalCDF(-d2);
    const theta = (theta1 - theta2) / 365; // Per day

    // Vega (same for calls and puts)
    const vega = (S * nd1 * Math.sqrt(T)) / 100;

    // Rho
    const rho = type === 'call'
        ? K * T * Math.exp(-r * T) * Nd2 / 100
        : -K * T * Math.exp(-r * T) * normalCDF(-d2) / 100;

    return {
        delta: delta.toFixed(4),
        gamma: gamma.toFixed(4),
        theta: theta.toFixed(4),
        vega: vega.toFixed(4),
        rho: rho.toFixed(4)
    };
}

/**
 * Normal cumulative distribution function
 */
function normalCDF(x: number): number {
    const t = 1 / (1 + 0.2316419 * Math.abs(x));
    const d = 0.3989423 * Math.exp(-x * x / 2);
    const prob = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
    return x > 0 ? 1 - prob : prob;
}

/**
 * Normal probability density function
 */
function normalPDF(x: number): number {
    return Math.exp(-0.5 * x * x) / Math.sqrt(2 * Math.PI);
}

/**
 * Calculate time to expiry in years
 */
function calculateTimeToExpiry(expirationDate: string): number {
    const expiry = new Date(expirationDate);
    const now = new Date();
    const diffMs = expiry.getTime() - now.getTime();
    const diffDays = diffMs / (1000 * 60 * 60 * 24);
    return Math.max(0, diffDays / 365);
}

/**
 * Analyze multi-leg options strategy
 */
function analyzeOptionsStrategy(legs: any[], spotPrice: number): any {
    let maxProfit = 0;
    let maxLoss = 0;
    let breakeven: number[] = [];

    // Calculate payoff at different price points
    const priceRange = [];
    const payoffs = [];
    
    for (let price = spotPrice * 0.8; price <= spotPrice * 1.2; price += spotPrice * 0.01) {
        let totalPayoff = 0;
        
        legs.forEach((leg: any) => {
            const intrinsicValue = leg.type === 'call'
                ? Math.max(price - leg.strike, 0)
                : Math.max(leg.strike - price, 0);
            
            const legPayoff = leg.position === 'long'
                ? (intrinsicValue - leg.premium) * leg.quantity
                : (leg.premium - intrinsicValue) * leg.quantity;
            
            totalPayoff += legPayoff;
        });
        
        priceRange.push(price.toFixed(2));
        payoffs.push(totalPayoff.toFixed(2));
        
        if (totalPayoff > maxProfit) maxProfit = totalPayoff;
        if (totalPayoff < maxLoss) maxLoss = totalPayoff;
    }

    return {
        strategyName: identifyStrategy(legs),
        maxProfit: maxProfit.toFixed(2),
        maxLoss: maxLoss.toFixed(2),
        breakeven,
        payoffDiagram: {
            prices: priceRange,
            payoffs
        },
        riskRewardRatio: maxProfit > 0 && maxLoss < 0 ? (maxProfit / Math.abs(maxLoss)).toFixed(2) : 'N/A'
    };
}

/**
 * Identify options strategy type
 */
function identifyStrategy(legs: any[]): string {
    if (legs.length === 1) {
        return `${legs[0].position} ${legs[0].type}`;
    } else if (legs.length === 2) {
        const types = legs.map((l: any) => l.type).sort();
        if (types[0] === types[1]) {
            return types[0] === 'call' ? 'Call Spread' : 'Put Spread';
        } else {
            return 'Straddle';
        }
    } else if (legs.length === 4) {
        return 'Iron Condor';
    }
    return 'Custom Strategy';
}
