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
        const { userId, type, severity, message, details } = await req.json();

        if (!userId || !type || !severity || !message) {
            throw new Error('User ID, type, severity, and message are required');
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

        // Create alert
        const alertResponse = await fetch(`${supabaseUrl}/rest/v1/alerts`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey,
                'Content-Type': 'application/json',
                'Prefer': 'return=representation'
            },
            body: JSON.stringify({
                user_id: userId,
                type: type,
                severity: severity,
                message: message,
                details: details || {},
                read: false
            })
        });

        if (!alertResponse.ok) {
            const errorText = await alertResponse.text();
            throw new Error(`Failed to create alert: ${errorText}`);
        }

        const alert = await alertResponse.json();

        return new Response(JSON.stringify({ data: alert[0] }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('Create alert error:', error);
        return new Response(JSON.stringify({
            error: {
                code: 'CREATE_ALERT_FAILED',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});
