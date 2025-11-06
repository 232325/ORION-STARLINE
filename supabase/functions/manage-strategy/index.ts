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
        const { strategyId, action, config } = await req.json();

        if (!strategyId || !action) {
            throw new Error('Strategy ID and action are required');
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

        // Verify user
        const userResponse = await fetch(`${supabaseUrl}/auth/v1/user`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'apikey': serviceRoleKey
            }
        });

        if (!userResponse.ok) {
            throw new Error('Invalid token');
        }

        const userData = await userResponse.json();

        let updateData: any = {
            updated_at: new Date().toISOString()
        };

        switch (action) {
            case 'start':
                updateData.is_active = true;
                break;
            case 'stop':
                updateData.is_active = false;
                break;
            case 'pause':
                updateData.is_active = false;
                break;
            case 'configure':
                if (config) {
                    updateData.parameters = config;
                }
                break;
            default:
                throw new Error('Invalid action');
        }

        // Update strategy
        const updateResponse = await fetch(
            `${supabaseUrl}/rest/v1/strategies?id=eq.${strategyId}`,
            {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=representation'
                },
                body: JSON.stringify(updateData)
            }
        );

        if (!updateResponse.ok) {
            const errorText = await updateResponse.text();
            throw new Error(`Failed to update strategy: ${errorText}`);
        }

        const updatedStrategy = await updateResponse.json();

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
                message: `Strategy ${action}: ${updatedStrategy[0]?.name || 'Unknown'}`,
                details: {
                    strategy_id: strategyId,
                    action: action,
                    user_id: userData.id
                }
            })
        });

        return new Response(JSON.stringify({ data: updatedStrategy[0] }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('Manage strategy error:', error);
        return new Response(JSON.stringify({
            error: {
                code: 'MANAGE_STRATEGY_FAILED',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});
