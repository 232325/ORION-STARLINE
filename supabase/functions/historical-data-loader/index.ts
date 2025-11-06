/**
 * Historical Data Loader Edge Function
 * Purpose: Load historical market data from Alpha Vantage for backtesting
 * Directive: Backtesting Engine Support
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
        const { symbols, timeframe, outputSize } = await req.json();

        if (!symbols || !Array.isArray(symbols)) {
            throw new Error('Symbols array is required');
        }

        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
        const alphaVantageKey = Deno.env.get('ALPHA_VANTAGE_API_KEY');

        if (!alphaVantageKey) {
            throw new Error('Alpha Vantage API key not configured');
        }

        const results: any[] = [];
        const errors: any[] = [];

        // Process each symbol
        for (const symbol of symbols.slice(0, 5)) { // Limit to 5 per request due to API limits
            try {
                console.log(`Fetching historical data for ${symbol}...`);

                // Determine Alpha Vantage function based on timeframe
                const avFunction = timeframe === 'daily' ? 'TIME_SERIES_DAILY' : 
                                 timeframe === 'weekly' ? 'TIME_SERIES_WEEKLY' :
                                 timeframe === 'monthly' ? 'TIME_SERIES_MONTHLY' :
                                 'TIME_SERIES_DAILY';

                const avOutputSize = outputSize || 'full'; // 'compact' (100 points) or 'full' (20+ years)

                // Fetch from Alpha Vantage
                const avUrl = `https://www.alphavantage.co/query?function=${avFunction}&symbol=${symbol}&outputsize=${avOutputSize}&apikey=${alphaVantageKey}`;
                
                const avResponse = await fetch(avUrl);
                const avData = await avResponse.json();

                // Check for API errors
                if (avData['Error Message']) {
                    throw new Error(avData['Error Message']);
                }

                if (avData['Note']) {
                    // API rate limit hit
                    errors.push({
                        symbol,
                        error: 'API rate limit reached. Please try again in 1 minute.'
                    });
                    continue;
                }

                // Extract time series data
                const timeSeriesKey = avFunction === 'TIME_SERIES_DAILY' ? 'Time Series (Daily)' :
                                     avFunction === 'TIME_SERIES_WEEKLY' ? 'Weekly Time Series' :
                                     avFunction === 'TIME_SERIES_MONTHLY' ? 'Monthly Time Series' :
                                     'Time Series (Daily)';

                const timeSeries = avData[timeSeriesKey];

                if (!timeSeries) {
                    throw new Error('No time series data returned from Alpha Vantage');
                }

                // Convert to our format and batch insert
                const priceRecords = [];
                let count = 0;

                for (const [date, values] of Object.entries(timeSeries)) {
                    const open = parseFloat(values['1. open']);
                    const high = parseFloat(values['2. high']);
                    const low = parseFloat(values['3. low']);
                    const close = parseFloat(values['4. close']);
                    const volume = parseFloat(values['5. volume']);

                    priceRecords.push({
                        symbol,
                        price: close,
                        bid: close * 0.999,
                        ask: close * 1.001,
                        volume,
                        change_24h: close - open,
                        change_percent_24h: ((close - open) / open) * 100,
                        high_24h: high,
                        low_24h: low,
                        source: 'alpha_vantage',
                        timestamp: new Date(date + 'T16:00:00Z').toISOString() // Market close time
                    });

                    count++;

                    // Batch insert every 100 records to avoid timeout
                    if (priceRecords.length >= 100) {
                        await insertBatch(supabaseUrl!, serviceRoleKey!, priceRecords);
                        priceRecords.length = 0; // Clear array
                    }
                }

                // Insert remaining records
                if (priceRecords.length > 0) {
                    await insertBatch(supabaseUrl!, serviceRoleKey!, priceRecords);
                }

                console.log(`Successfully loaded ${count} records for ${symbol}`);

                results.push({
                    symbol,
                    recordsLoaded: count,
                    timeframe,
                    status: 'success'
                });

                // Rate limiting: wait 12 seconds between requests (Alpha Vantage free tier: 5 calls/min)
                if (symbols.indexOf(symbol) < symbols.length - 1) {
                    await new Promise(resolve => setTimeout(resolve, 12000));
                }

            } catch (symbolError: any) {
                console.error(`Error loading data for ${symbol}:`, symbolError.message);
                errors.push({
                    symbol,
                    error: symbolError.message
                });
            }
        }

        return new Response(JSON.stringify({
            data: {
                results,
                errors,
                summary: {
                    totalSymbols: symbols.length,
                    successful: results.length,
                    failed: errors.length,
                    message: results.length > 0 
                        ? 'Historical data loaded successfully'
                        : 'No data loaded. Check errors.'
                }
            }
        }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error: any) {
        console.error('Historical Data Loader error:', error);

        return new Response(JSON.stringify({
            error: {
                code: 'HISTORICAL_DATA_LOAD_FAILED',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

/**
 * Insert batch of price records
 */
async function insertBatch(
    supabaseUrl: string,
    serviceRoleKey: string,
    records: any[]
): Promise<void> {
    const insertResponse = await fetch(`${supabaseUrl}/rest/v1/realtime_prices`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey,
            'Content-Type': 'application/json',
            'Prefer': 'resolution=ignore-duplicates'
        },
        body: JSON.stringify(records)
    });

    if (!insertResponse.ok) {
        const errorText = await insertResponse.text();
        console.error('Batch insert failed:', errorText);
        // Don't throw, continue with next batch
    }
}
