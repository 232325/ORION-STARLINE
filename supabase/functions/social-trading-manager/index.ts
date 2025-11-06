/**
 * Social Trading Manager Edge Function
 * Purpose: Copy Trading + Trader Profiles + Leaderboards + Social Features
 * Phase: 2 - Social Trading System
 */

Deno.serve(async (req) => {
    const corsHeaders = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
        'Access-Control-Max-Age': '86400'
    };

    if (req.method === 'OPTIONS') {
        return new Response(null, { status: 200, headers: corsHeaders });
    }

    try {
        const { action, userId, targetUserId, ...params } = await req.json();

        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

        let result: any = {};

        switch (action) {
            case 'create_profile':
                result = await createTraderProfile(supabaseUrl!, serviceRoleKey!, userId, params);
                break;
            case 'get_profile':
                result = await getTraderProfile(supabaseUrl!, serviceRoleKey!, targetUserId || userId);
                break;
            case 'follow_trader':
                result = await followTrader(supabaseUrl!, serviceRoleKey!, userId, targetUserId);
                break;
            case 'unfollow_trader':
                result = await unfollowTrader(supabaseUrl!, serviceRoleKey!, userId, targetUserId);
                break;
            case 'start_copy_trading':
                result = await startCopyTrading(supabaseUrl!, serviceRoleKey!, userId, targetUserId, params);
                break;
            case 'stop_copy_trading':
                result = await stopCopyTrading(supabaseUrl!, serviceRoleKey!, userId, targetUserId);
                break;
            case 'get_leaderboard':
                result = await getLeaderboard(supabaseUrl!, serviceRoleKey!, params.period || 'weekly');
                break;
            case 'get_top_traders':
                result = await getTopTraders(supabaseUrl!, serviceRoleKey!, params.limit || 10);
                break;
            case 'get_copy_performance':
                result = await getCopyPerformance(supabaseUrl!, serviceRoleKey!, userId);
                break;
            default:
                throw new Error('Invalid action');
        }

        return new Response(JSON.stringify({ data: result }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error: any) {
        return new Response(JSON.stringify({
            error: { code: 'SOCIAL_TRADING_ERROR', message: error.message }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

async function createTraderProfile(url: string, key: string, userId: string, params: any) {
    const response = await fetch(`${url}/rest/v1/trader_profiles`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${key}`,
            'apikey': key,
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        },
        body: JSON.stringify({
            user_id: userId,
            username: params.username,
            display_name: params.displayName,
            bio: params.bio,
            trading_style: params.tradingStyle,
            experience_level: params.experienceLevel || 'beginner'
        })
    });

    const data = await response.json();
    return Array.isArray(data) ? data[0] : data;
}

async function getTraderProfile(url: string, key: string, userId: string) {
    const response = await fetch(`${url}/rest/v1/trader_profiles?user_id=eq.${userId}`, {
        headers: { 'Authorization': `Bearer ${key}`, 'apikey': key }
    });
    const data = await response.json();
    return Array.isArray(data) && data.length > 0 ? data[0] : null;
}

async function followTrader(url: string, key: string, followerId: string, targetId: string) {
    await fetch(`${url}/rest/v1/social_follows`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${key}`,
            'apikey': key,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            follower_user_id: followerId,
            followed_user_id: targetId
        })
    });

    // Update follower count
    await fetch(`${url}/rest/v1/rpc/increment_follower_count`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${key}`,
            'apikey': key,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ target_user_id: targetId })
    });

    return { success: true, message: 'Successfully followed trader' };
}

async function unfollowTrader(url: string, key: string, followerId: string, targetId: string) {
    await fetch(`${url}/rest/v1/social_follows?follower_user_id=eq.${followerId}&followed_user_id=eq.${targetId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${key}`, 'apikey': key }
    });

    return { success: true, message: 'Successfully unfollowed trader' };
}

async function startCopyTrading(url: string, key: string, copierId: string, traderId: string, params: any) {
    const response = await fetch(`${url}/rest/v1/copy_trading_relationships`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${key}`,
            'apikey': key,
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        },
        body: JSON.stringify({
            copier_user_id: copierId,
            trader_user_id: traderId,
            copy_mode: params.copyMode || 'full',
            allocation_amount: params.allocationAmount,
            allocation_percentage: params.allocationPercentage,
            max_position_size: params.maxPositionSize,
            is_active: true,
            auto_sync: true
        })
    });

    const data = await response.json();
    return Array.isArray(data) ? data[0] : data;
}

async function stopCopyTrading(url: string, key: string, copierId: string, traderId: string) {
    await fetch(`${url}/rest/v1/copy_trading_relationships?copier_user_id=eq.${copierId}&trader_user_id=eq.${traderId}`, {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${key}`,
            'apikey': key,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ is_active: false, paused_at: new Date().toISOString() })
    });

    return { success: true, message: 'Copy trading stopped' };
}

async function getLeaderboard(url: string, key: string, period: string) {
    const response = await fetch(`${url}/rest/v1/trader_leaderboard?period=eq.${period}&order=rank.asc&limit=50`, {
        headers: { 'Authorization': `Bearer ${key}`, 'apikey': key }
    });
    let data = await response.json();
    return Array.isArray(data) ? data : [];
}

async function getTopTraders(url: string, key: string, limit: number) {
    const response = await fetch(`${url}/rest/v1/trader_profiles?is_public=eq.true&order=win_rate.desc&limit=${limit}`, {
        headers: { 'Authorization': `Bearer ${key}`, 'apikey': key }
    });
    let data = await response.json();
    return Array.isArray(data) ? data : [];
}

async function getCopyPerformance(url: string, key: string, userId: string) {
    const response = await fetch(`${url}/rest/v1/copy_trading_relationships?copier_user_id=eq.${userId}&is_active=eq.true`, {
        headers: { 'Authorization': `Bearer ${key}`, 'apikey': key }
    });
    let data = await response.json();
    return Array.isArray(data) ? data : [];
}
