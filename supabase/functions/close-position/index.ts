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
        const { positionId, closingPrice } = await req.json();

        if (!positionId || !closingPrice) {
            throw new Error('Position ID and closing price are required');
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
        
        // Calculate realized PnL
        let realizedPnl = 0;
        if (position.side === 'long' || position.position_type === 'long') {
            realizedPnl = (closingPrice - entryPrice) * size * leverage;
        } else {
            realizedPnl = (entryPrice - closingPrice) * size * leverage;
        }

        // Close position
        const closeResponse = await fetch(
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
                    status: 'closed',
                    current_price: closingPrice,
                    unrealized_pnl: realizedPnl,
                    closed_at: new Date().toISOString(),
                    updated_at: new Date().toISOString()
                })
            }
        );

        if (!closeResponse.ok) {
            const errorText = await closeResponse.text();
            throw new Error(`Failed to close position: ${errorText}`);
        }

        const closedPosition = await closeResponse.json();

        // Log the event
        await fetch(`${supabaseUrl}/rest/v1/system_logs`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                level: 'info',
                message: `Position closed: ${position.symbol}`,
                details: {
                    position_id: positionId,
                    realized_pnl: realizedPnl,
                    closing_price: closingPrice
                }
            })
        });

        return new Response(JSON.stringify({ 
            data: {
                position: closedPosition[0],
                realized_pnl: realizedPnl
            }
        }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('Close position error:', error);
        return new Response(JSON.stringify({
            error: {
                code: 'CLOSE_POSITION_FAILED',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});
