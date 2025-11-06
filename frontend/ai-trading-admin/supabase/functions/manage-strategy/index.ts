// AI Trading Platform - Manage Strategy Edge Function
// Strategiyani boshqarish (start/stop)

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
        const { strategyId, action } = await req.json();

        if (!strategyId || !action) {
            return new Response(JSON.stringify({ error: 'Missing required fields' }), {
                status: 400,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        if (action !== 'start' && action !== 'stop') {
            return new Response(JSON.stringify({ error: 'Invalid action. Use "start" or "stop"' }), {
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

        // Fetch strategy from database
        const strategyResponse = await fetch(
            `${supabaseUrl}/rest/v1/strategies?id=eq.${strategyId}&user_id=eq.${userId}`,
            {
                headers: {
                    'apikey': supabaseKey,
                    'Authorization': `Bearer ${supabaseKey}`,
                    'Content-Type': 'application/json'
                }
            }
        );

        const strategies = await strategyResponse.json();

        if (!strategies || strategies.length === 0) {
            return new Response(JSON.stringify({ error: 'Strategy not found' }), {
                status: 404,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        const strategy = strategies[0];

        // Validate action
        if (action === 'start' && strategy.is_active) {
            return new Response(JSON.stringify({ 
                error: 'Strategy is already active' 
            }), {
                status: 400,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        if (action === 'stop' && !strategy.is_active) {
            return new Response(JSON.stringify({ 
                error: 'Strategy is already stopped' 
            }), {
                status: 400,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        // Update strategy status
        const updateResponse = await fetch(
            `${supabaseUrl}/rest/v1/strategies?id=eq.${strategyId}`,
            {
                method: 'PATCH',
                headers: {
                    'apikey': supabaseKey,
                    'Authorization': `Bearer ${supabaseKey}`,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=representation'
                },
                body: JSON.stringify({
                    is_active: action === 'start',
                    updated_at: new Date().toISOString()
                })
            }
        );

        if (!updateResponse.ok) {
            throw new Error('Failed to update strategy');
        }

        const updatedStrategy = await updateResponse.json();

        // Log the action
        console.log(`Strategy ${strategyId} ${action === 'start' ? 'started' : 'stopped'} by user ${userId}`);

        return new Response(JSON.stringify({ 
            success: true,
            data: updatedStrategy[0],
            message: `Strategy ${action === 'start' ? 'started' : 'stopped'} successfully`
        }), {
            status: 200,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('Error managing strategy:', error);
        return new Response(JSON.stringify({ 
            error: error.message || 'Internal server error' 
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});
