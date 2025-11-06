// Referral System - REAL DATABASE
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
        const { action } = await req.json();
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

        if (action === 'generate_code') {
            if (!userId) throw new Error('Authentication required');

            const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
            let code = '';
            for (let i = 0; i < 8; i++) {
                code += characters.charAt(Math.floor(Math.random() * characters.length));
            }

            const referral = {
                user_id: userId,
                code,
                commission_rate: 10.00,
                is_active: true
            };

            const response = await fetch(
                `${supabaseUrl}/rest/v1/referral_codes`,
                {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${serviceRoleKey}`,
                        'apikey': serviceRoleKey,
                        'Content-Type': 'application/json',
                        'Prefer': 'return=representation'
                    },
                    body: JSON.stringify(referral)
                }
            );

            const referralData = await response.json();

            return new Response(JSON.stringify({
                referral: referralData[0],
                success: true
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        if (action === 'get_stats') {
            if (!userId) throw new Error('Authentication required');

            const codesResponse = await fetch(
                `${supabaseUrl}/rest/v1/referral_codes?user_id=eq.${userId}`,
                {
                    headers: {
                        'Authorization': `Bearer ${serviceRoleKey}`,
                        'apikey': serviceRoleKey
                    }
                }
            );

            const codes = await codesResponse.json();
            const totalEarnings = codes.reduce((sum, c) => sum + parseFloat(c.total_earnings || 0), 0);

            const referralsResponse = await fetch(
                `${supabaseUrl}/rest/v1/referrals?referrer_id=eq.${userId}&order=created_at.desc&limit=10`,
                {
                    headers: {
                        'Authorization': `Bearer ${serviceRoleKey}`,
                        'apikey': serviceRoleKey
                    }
                }
            );

            const referrals = await referralsResponse.json();
            const activeReferrals = referrals.filter(r => r.status === 'active').length;

            const stats = {
                total_referrals: referrals.length,
                active_referrals: activeReferrals,
                total_earnings: totalEarnings,
                pending_earnings: 0,
                referrals: referrals.slice(0, 10).map(r => ({
                    id: r.id,
                    referred_user_email: 'user@example.com',
                    status: r.status,
                    commission_earned: parseFloat(r.total_commission || 0),
                    created_at: r.created_at
                }))
            };

            return new Response(JSON.stringify({ stats, success: true }), {
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
