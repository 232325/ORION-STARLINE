// AI Trading Platform - Close Position Edge Function
// Pozitsiyani yopish uchun

Deno.serve(async (req) => {
    const corsHeaders = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
        'Access-Control-Max-Age': '86400',
    };

    // CORS preflight
    if (req.method === 'OPTIONS') {
        return new Response(null, { status: 200, headers: corsHeaders });
    }

    try {
        // Get authorization header
        const authHeader = req.headers.get('authorization');
        if (!authHeader) {
            return new Response(JSON.stringify({ error: 'Authorization header missing' }), {
                status: 401,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        // Parse request body
        const { positionId, closingPrice } = await req.json();

        if (!positionId || !closingPrice) {
            return new Response(JSON.stringify({ error: 'Missing required fields' }), {
                status: 400,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        // Get Supabase client
        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

        if (!supabaseUrl || !supabaseKey) {
            return new Response(JSON.stringify({ error: 'Server configuration error' }), {
                status: 500,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        // Extract user ID from JWT token
        const token = authHeader.replace('Bearer ', '');
        const jwtPayload = JSON.parse(atob(token.split('.')[1]));
        const userId = jwtPayload.sub;

        if (!userId) {
            return new Response(JSON.stringify({ error: 'Invalid token' }), {
                status: 401,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        // Fetch position from database
        const positionResponse = await fetch(
            `${supabaseUrl}/rest/v1/positions?id=eq.${positionId}&user_id=eq.${userId}`,
            {
                headers: {
                    'apikey': supabaseKey,
                    'Authorization': `Bearer ${supabaseKey}`,
                    'Content-Type': 'application/json'
                }
            }
        );

        const positions = await positionResponse.json();

        if (!positions || positions.length === 0) {
            return new Response(JSON.stringify({ error: 'Position not found' }), {
                status: 404,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        const position = positions[0];

        // Calculate final PnL
        const priceDifference = parseFloat(closingPrice) - parseFloat(position.entry_price);
        const finalPnl = position.side === 'long' 
            ? priceDifference * parseFloat(position.size)
            : -priceDifference * parseFloat(position.size);

        // Update position
        const updateResponse = await fetch(
            `${supabaseUrl}/rest/v1/positions?id=eq.${positionId}`,
            {
                method: 'PATCH',
                headers: {
                    'apikey': supabaseKey,
                    'Authorization': `Bearer ${supabaseKey}`,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=representation'
                },
                body: JSON.stringify({
                    status: 'closed',
                    current_price: closingPrice,
                    unrealized_pnl: finalPnl.toFixed(2),
                    closed_at: new Date().toISOString()
                })
            }
        );

        if (!updateResponse.ok) {
            throw new Error('Failed to update position');
        }

        // Update user profile
        const profileResponse = await fetch(
            `${supabaseUrl}/rest/v1/profiles?user_id=eq.${userId}`,
            {
                headers: {
                    'apikey': supabaseKey,
                    'Authorization': `Bearer ${supabaseKey}`,
                    'Content-Type': 'application/json'
                }
            }
        );

        const profiles = await profileResponse.json();
        if (profiles && profiles.length > 0) {
            const profile = profiles[0];
            const newBalance = parseFloat(profile.balance) + finalPnl;
            const newTotalPnl = parseFloat(profile.total_pnl) + finalPnl;
            const newTotalTrades = (profile.total_trades || 0) + 1;

            await fetch(
                `${supabaseUrl}/rest/v1/profiles?user_id=eq.${userId}`,
                {
                    method: 'PATCH',
                    headers: {
                        'apikey': supabaseKey,
                        'Authorization': `Bearer ${supabaseKey}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        balance: newBalance.toFixed(2),
                        total_pnl: newTotalPnl.toFixed(2),
                        total_trades: newTotalTrades,
                        updated_at: new Date().toISOString()
                    })
                }
            );
        }

        const updatedPosition = await updateResponse.json();

        return new Response(JSON.stringify({ 
            success: true,
            data: updatedPosition[0],
            message: 'Position closed successfully'
        }), {
            status: 200,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('Error closing position:', error);
        return new Response(JSON.stringify({ 
            error: error.message || 'Internal server error' 
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});
