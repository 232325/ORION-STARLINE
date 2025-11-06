// Copy Trading Leaderboard - REAL DATABASE
Deno.serve(async (req) => {
    const corsHeaders = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
    };

    if (req.method === 'OPTIONS') {
        return new Response(null, { headers: corsHeaders, status: 200 });
    }

    try {
        const url = new URL(req.url);
        const limit = parseInt(url.searchParams.get('limit') || '20');
        const sortBy = url.searchParams.get('sort_by') || 'total_profit';

        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

        const sortColumns = {
            'total_profit': 'total_profit',
            'win_rate': 'win_rate',
            'followers': 'total_followers'
        };
        const sortColumn = sortColumns[sortBy] || 'total_profit';

        const response = await fetch(
            `${supabaseUrl}/rest/v1/copy_traders?select=*&order=${sortColumn}.desc&limit=${limit}`,
            {
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            }
        );

        const traders = await response.json();

        return new Response(JSON.stringify({ traders, total: traders.length, success: true }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    } catch (error) {
        return new Response(JSON.stringify({ error: error.message, success: false }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 500
        });
    }
});
