Deno.serve(async (req) => {
    const corsHeaders = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Max-Age': '86400',
    };

    if (req.method === 'OPTIONS') {
        return new Response(null, { status: 200, headers: corsHeaders });
    }

    try {
        const { positionId, currentPrice } = await req.json();

        if (!positionId || !currentPrice) {
            throw new Error('Position ID and current price are required');
        }

        const authHeader = req.headers.get('authorization');
        if (!authHeader) {
            throw new Error('No authorization header');
        }

        const token = authHeader.replace('Bearer ', '');
        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

        if (!supabaseUrl || !serviceRoleKey) {
            throw new Error('Supabase configuration missing');
        }

        // Get position details
        const positionResponse = await fetch(
            `${supabaseUrl}/rest/v1/positions?id=eq.${positionId}`,
            {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json'
                }
            }
        );

        if (!positionResponse.ok) {
            throw new Error('Failed to fetch position');
        }

        const positions = await positionResponse.json();
        if (positions.length === 0) {
            throw new Error('Position not found');
        }

        const position = positions[0];
        const entryPrice = parseFloat(position.entry_price);
        const size = parseFloat(position.size);
        const leverage = parseFloat(position.leverage || 1);
        
        // Calculate unrealized PnL
        let unrealizedPnl = 0;
        if (position.side === 'long' || position.position_type === 'long') {
            unrealizedPnl = (currentPrice - entryPrice) * size * leverage;
        } else {
            unrealizedPnl = (entryPrice - currentPrice) * size * leverage;
        }

        // Update position
        const updateResponse = await fetch(
            `${supabaseUrl}/rest/v1/positions?id=eq.${positionId}`,
            {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=representation'
                },
                body: JSON.stringify({
                    current_price: currentPrice,
                    unrealized_pnl: unrealizedPnl,
                    updated_at: new Date().toISOString()
                })
            }
        );

        if (!updateResponse.ok) {
            const errorText = await updateResponse.text();
            throw new Error(`Failed to update position: ${errorText}`);
        }

        const updatedPosition = await updateResponse.json();

        return new Response(JSON.stringify({ data: updatedPosition[0] }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('Update position error:', error);
        return new Response(JSON.stringify({
            error: {
                code: 'UPDATE_POSITION_FAILED',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});
