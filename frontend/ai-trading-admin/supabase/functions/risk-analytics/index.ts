// Risk Analytics Dashboard
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

        if (!userId) {
            throw new Error('Authentication required');
        }

        // Get latest risk metrics
        const metricsResponse = await fetch(
            `${supabaseUrl}/rest/v1/portfolio_risk_metrics?user_id=eq.${userId}&order=date.desc&limit=30`,
            {
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            }
        );

        let metrics = [];
        if (metricsResponse.ok) {
            metrics = await metricsResponse.json();
        }

        // Get active alerts
        const alertsResponse = await fetch(
            `${supabaseUrl}/rest/v1/risk_alerts?user_id=eq.${userId}&is_resolved=eq.false&order=created_at.desc&limit=10`,
            {
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            }
        );

        let alerts = [];
        if (alertsResponse.ok) {
            alerts = await alertsResponse.json();
        }

        // Calculate current risk score
        const latestMetric = metrics[0];
        const riskScore = latestMetric ? latestMetric.risk_score : 50;

        // Generate risk recommendations
        const recommendations = [];
        if (riskScore > 70) {
            recommendations.push({
                type: 'reduce_exposure',
                message: 'Yuqori risk darajasi. Pozitsiyalarni kamaytiring.',
                priority: 'high'
            });
        }
        if (latestMetric && parseFloat(latestMetric.max_drawdown) > 0.20) {
            recommendations.push({
                type: 'diversify',
                message: 'Maksimal drawdown haddan oshgan. Diversifikatsiya qiling.',
                priority: 'high'
            });
        }

        return new Response(JSON.stringify({
            current_risk: {
                risk_score: riskScore,
                var_95: latestMetric ? latestMetric.var_95 : null,
                var_99: latestMetric ? latestMetric.var_99 : null,
                max_drawdown: latestMetric ? latestMetric.max_drawdown : null,
                volatility: latestMetric ? latestMetric.volatility : null,
                beta: latestMetric ? latestMetric.beta : null
            },
            historical_metrics: metrics,
            active_alerts: alerts,
            recommendations,
            risk_level: riskScore > 70 ? 'high' : riskScore > 40 ? 'medium' : 'low',
            success: true
        }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    } catch (error) {
        return new Response(JSON.stringify({ error: error.message, success: false }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 500
        });
    }
});
