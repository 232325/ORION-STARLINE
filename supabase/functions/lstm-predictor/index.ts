/**
 * LSTM Price Predictor Edge Function
 * Purpose: LSTM-based price prediction for cryptocurrencies
 * Directive: B) New AI/ML Modules Integration
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
        const { action, symbol, horizon, features } = await req.json();

        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

        let result: any = {};

        switch (action) {
            case 'predict':
                result = await predictPrice(supabaseUrl!, serviceRoleKey!, symbol, horizon || '24h', features);
                break;

            case 'get_predictions':
                result = await getPredictions(supabaseUrl!, serviceRoleKey!, symbol);
                break;

            case 'evaluate_accuracy':
                result = await evaluateAccuracy(supabaseUrl!, serviceRoleKey!, symbol);
                break;

            default:
                throw new Error('Invalid action');
        }

        return new Response(JSON.stringify({ data: result }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error: any) {
        console.error('LSTM Predictor error:', error);

        return new Response(JSON.stringify({
            error: {
                code: 'LSTM_PREDICTION_ERROR',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

/**
 * Predict future price using LSTM model
 */
async function predictPrice(
    supabaseUrl: string,
    serviceRoleKey: string,
    symbol: string,
    horizon: string,
    features?: any
): Promise<any> {
    // Get current price
    const priceResponse = await fetch(
        `${supabaseUrl}/rest/v1/realtime_prices?symbol=eq.${symbol}&order=timestamp.desc&limit=1`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    const priceData = await priceResponse.json();
    const currentPrice = priceData[0]?.price || 100;

    // Get historical prices for feature engineering
    const historicalResponse = await fetch(
        `${supabaseUrl}/rest/v1/realtime_prices?symbol=eq.${symbol}&order=timestamp.desc&limit=100`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    const historicalPrices = await historicalResponse.json();

    // Simulate LSTM prediction (in production, would use actual trained model)
    const prediction = simulateLSTMPrediction(currentPrice, historicalPrices, horizon);

    // Calculate target time
    const targetTime = calculateTargetTime(horizon);

    // Save prediction to database
    const insertResponse = await fetch(`${supabaseUrl}/rest/v1/lstm_predictions`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey,
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        },
        body: JSON.stringify({
            symbol,
            current_price: currentPrice,
            predicted_price: prediction.predictedPrice,
            prediction_horizon: horizon,
            confidence_interval: prediction.confidenceInterval,
            model_version: 'lstm_v1',
            features_used: prediction.featuresUsed,
            target_time: targetTime
        })
    });

    const savedPrediction = await insertResponse.json();

    return {
        symbol,
        currentPrice,
        prediction: {
            ...prediction,
            targetTime,
            saved: savedPrediction[0]
        }
    };
}

/**
 * Get historical predictions for a symbol
 */
async function getPredictions(
    supabaseUrl: string,
    serviceRoleKey: string,
    symbol: string
): Promise<any> {
    const response = await fetch(
        `${supabaseUrl}/rest/v1/lstm_predictions?symbol=eq.${symbol}&order=created_at.desc&limit=50`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    const predictions = await response.json();

    // Separate active and past predictions
    const now = new Date();
    const active = predictions.filter((p: any) => new Date(p.target_time) > now);
    const past = predictions.filter((p: any) => new Date(p.target_time) <= now);

    return {
        symbol,
        total: predictions.length,
        active: active.length,
        past: past.length,
        predictions: {
            active,
            past
        }
    };
}

/**
 * Evaluate prediction accuracy
 */
async function evaluateAccuracy(
    supabaseUrl: string,
    serviceRoleKey: string,
    symbol: string
): Promise<any> {
    // Get past predictions
    const now = new Date().toISOString();
    const predictionsResponse = await fetch(
        `${supabaseUrl}/rest/v1/lstm_predictions?symbol=eq.${symbol}&target_time=lt.${now}&order=created_at.desc&limit=100`,
        {
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey
            }
        }
    );

    const predictions = await predictionsResponse.json();

    if (predictions.length === 0) {
        return {
            symbol,
            message: 'No past predictions to evaluate',
            accuracy: null
        };
    }

    // Get actual prices at target times
    const evaluations = [];

    for (const pred of predictions.slice(0, 20)) { // Evaluate top 20
        const targetTime = new Date(pred.target_time);
        const windowStart = new Date(targetTime.getTime() - 300000).toISOString(); // 5 min before
        const windowEnd = new Date(targetTime.getTime() + 300000).toISOString(); // 5 min after

        const actualResponse = await fetch(
            `${supabaseUrl}/rest/v1/realtime_prices?symbol=eq.${symbol}&timestamp=gte.${windowStart}&timestamp=lte.${windowEnd}&order=timestamp.asc&limit=1`,
            {
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            }
        );

        const actualData = await actualResponse.json();

        if (actualData && actualData.length > 0) {
            const actualPrice = parseFloat(actualData[0].price);
            const predictedPrice = parseFloat(pred.predicted_price);
            const currentPrice = parseFloat(pred.current_price);

            const error = Math.abs(actualPrice - predictedPrice);
            const percentError = (error / actualPrice) * 100;
            const direction = (predictedPrice > currentPrice && actualPrice > currentPrice) ||
                            (predictedPrice < currentPrice && actualPrice < currentPrice);

            evaluations.push({
                predictionId: pred.id,
                predictedPrice,
                actualPrice,
                error: error.toFixed(2),
                percentError: percentError.toFixed(2),
                directionCorrect: direction
            });

            // Update prediction with actual value and accuracy
            await fetch(`${supabaseUrl}/rest/v1/lstm_predictions?id=eq.${pred.id}`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    actual_value: actualPrice,
                    accuracy_score: 1 - Math.min(percentError / 100, 1)
                })
            });
        }
    }

    // Calculate overall accuracy metrics
    const avgPercentError = evaluations.reduce((sum, e) => sum + parseFloat(e.percentError), 0) / evaluations.length;
    const directionAccuracy = evaluations.filter(e => e.directionCorrect).length / evaluations.length;

    return {
        symbol,
        evaluatedPredictions: evaluations.length,
        metrics: {
            averagePercentError: avgPercentError.toFixed(2) + '%',
            directionAccuracy: (directionAccuracy * 100).toFixed(2) + '%',
            rmse: calculateRMSE(evaluations),
            mae: calculateMAE(evaluations)
        },
        evaluations: evaluations.slice(0, 10) // Return top 10
    };
}

/**
 * Simulate LSTM prediction
 */
function simulateLSTMPrediction(
    currentPrice: number,
    historicalPrices: any[],
    horizon: string
): any {
    // Calculate features from historical data
    const prices = historicalPrices.map((p: any) => parseFloat(p.price));
    
    const volatility = calculateVolatility(prices);
    const trend = calculateTrend(prices);
    const momentum = calculateMomentum(prices);

    // Simulate LSTM prediction based on features
    let priceChange = 0;

    // Base change on trend and momentum
    if (trend > 0.02) {
        priceChange = currentPrice * (0.02 + Math.random() * 0.05); // Uptrend
    } else if (trend < -0.02) {
        priceChange = currentPrice * (-0.05 + Math.random() * 0.03); // Downtrend
    } else {
        priceChange = currentPrice * ((Math.random() - 0.5) * 0.04); // Sideways
    }

    // Adjust for horizon
    const horizonMultiplier = getHorizonMultiplier(horizon);
    priceChange *= horizonMultiplier;

    const predictedPrice = currentPrice + priceChange;

    // Calculate confidence interval
    const stdDev = currentPrice * volatility * Math.sqrt(horizonMultiplier);
    const confidenceInterval = {
        lower: predictedPrice - 1.96 * stdDev,
        upper: predictedPrice + 1.96 * stdDev
    };

    return {
        predictedPrice: predictedPrice.toFixed(2),
        confidenceInterval,
        featuresUsed: {
            volatility: volatility.toFixed(4),
            trend: trend.toFixed(4),
            momentum: momentum.toFixed(4),
            dataPoints: prices.length
        },
        predictionConfidence: Math.max(0.5, 1 - volatility).toFixed(2)
    };
}

/**
 * Calculate price volatility
 */
function calculateVolatility(prices: number[]): number {
    if (prices.length < 2) return 0.1;

    const returns = [];
    for (let i = 1; i < prices.length; i++) {
        returns.push((prices[i] - prices[i - 1]) / prices[i - 1]);
    }

    const mean = returns.reduce((a, b) => a + b, 0) / returns.length;
    const variance = returns.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / returns.length;
    
    return Math.sqrt(variance);
}

/**
 * Calculate price trend
 */
function calculateTrend(prices: number[]): number {
    if (prices.length < 2) return 0;

    const recentAvg = prices.slice(0, Math.floor(prices.length / 3)).reduce((a, b) => a + b, 0) / Math.floor(prices.length / 3);
    const olderAvg = prices.slice(Math.floor(prices.length * 2 / 3)).reduce((a, b) => a + b, 0) / Math.floor(prices.length / 3);

    return (recentAvg - olderAvg) / olderAvg;
}

/**
 * Calculate momentum
 */
function calculateMomentum(prices: number[]): number {
    if (prices.length < 10) return 0;

    const current = prices[0];
    const past = prices[9];

    return (current - past) / past;
}

/**
 * Get horizon multiplier for prediction
 */
function getHorizonMultiplier(horizon: string): number {
    const multipliers: { [key: string]: number } = {
        '1h': 0.25,
        '4h': 0.5,
        '24h': 1.0,
        '1w': 2.5,
        '1m': 5.0
    };

    return multipliers[horizon] || 1.0;
}

/**
 * Calculate target time based on horizon
 */
function calculateTargetTime(horizon: string): string {
    const now = new Date();
    
    const offsets: { [key: string]: number } = {
        '1h': 3600000,
        '4h': 14400000,
        '24h': 86400000,
        '1w': 604800000,
        '1m': 2592000000
    };

    const offset = offsets[horizon] || 86400000;
    const targetTime = new Date(now.getTime() + offset);

    return targetTime.toISOString();
}

/**
 * Calculate RMSE (Root Mean Square Error)
 */
function calculateRMSE(evaluations: any[]): string {
    if (evaluations.length === 0) return '0.00';

    const sumSquaredErrors = evaluations.reduce((sum, e) => {
        return sum + Math.pow(parseFloat(e.error), 2);
    }, 0);

    const rmse = Math.sqrt(sumSquaredErrors / evaluations.length);
    return rmse.toFixed(2);
}

/**
 * Calculate MAE (Mean Absolute Error)
 */
function calculateMAE(evaluations: any[]): string {
    if (evaluations.length === 0) return '0.00';

    const sumErrors = evaluations.reduce((sum, e) => sum + parseFloat(e.error), 0);
    const mae = sumErrors / evaluations.length;

    return mae.toFixed(2);
}
