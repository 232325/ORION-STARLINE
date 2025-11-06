// Subscription Management - REAL DATABASE
Deno.serve(async (req) => {
    const corsHeaders = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
    };

    if (req.method === 'OPTIONS') {
        return new Response(null, { headers: corsHeaders, status: 200 });
    }

    try {
        const { action, plan_id, billing_cycle } = await req.json();
        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

        const authHeader = req.headers.get('authorization');
        let userId = null;
        
        if (authHeader) {
            const token = authHeader.replace('Bearer ', '');
            const userResponse = await fetch(`${supabaseUrl}/auth/v1/user`, {
                headers: { 'Authorization': `Bearer ${token}`, 'apikey': serviceRoleKey }
            });
            if (userResponse.ok) {
                const userData = await userResponse.json();
                userId = userData.id;
            }
        }

        if (action === 'get_plans') {
            const response = await fetch(
                `${supabaseUrl}/rest/v1/subscription_plans?is_active=eq.true&order=sort_order`,
                {
                    headers: {
                        'Authorization': `Bearer ${serviceRoleKey}`,
                        'apikey': serviceRoleKey
                    }
                }
            );
            const plans = await response.json();
            return new Response(JSON.stringify({ plans, success: true }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        if (action === 'subscribe') {
            if (!userId) throw new Error('Authentication required');

            const now = new Date();
            const periodEnd = new Date(now);
            if (billing_cycle === 'yearly') {
                periodEnd.setFullYear(periodEnd.getFullYear() + 1);
            } else {
                periodEnd.setMonth(periodEnd.getMonth() + 1);
            }

            const subscription = {
                user_id: userId,
                plan_id,
                status: 'active',
                billing_cycle: billing_cycle || 'monthly',
                current_period_start: now.toISOString(),
                current_period_end: periodEnd.toISOString()
            };

            const response = await fetch(
                `${supabaseUrl}/rest/v1/user_subscriptions`,
                {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${serviceRoleKey}`,
                        'apikey': serviceRoleKey,
                        'Content-Type': 'application/json',
                        'Prefer': 'return=representation'
                    },
                    body: JSON.stringify(subscription)
                }
            );

            const subscriptionData = await response.json();

            return new Response(JSON.stringify({
                subscription: subscriptionData[0],
                message: 'Subscription created',
                success: true
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        return new Response(JSON.stringify({ error: 'Invalid action', success: false }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 400
        });
    } catch (error) {
        return new Response(JSON.stringify({ error: error.message, success: false }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 500
        });
    }
});
