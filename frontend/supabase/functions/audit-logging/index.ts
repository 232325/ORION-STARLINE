// Audit Logging Edge Function
// Tizim va foydalanuvchi faoliyatini kuzatish

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.3';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
};

interface AuditLog {
  user_id?: string;
  action_type: string;
  resource_type: string;
  resource_id?: string;
  details?: any;
  ip_address?: string;
  user_agent?: string;
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    if (req.method === 'GET') {
      // Audit loglarni olish
      const url = new URL(req.url);
      const userId = url.searchParams.get('user_id');
      const actionType = url.searchParams.get('action_type');
      const resourceType = url.searchParams.get('resource_type');
      const limit = parseInt(url.searchParams.get('limit') || '50');
      const offset = parseInt(url.searchParams.get('offset') || '0');

      let query = supabase
        .from('audit_logs')
        .select('*', { count: 'exact' })
        .order('created_at', { ascending: false })
        .range(offset, offset + limit - 1);

      if (userId) query = query.eq('user_id', userId);
      if (actionType) query = query.eq('action_type', actionType);
      if (resourceType) query = query.eq('resource_type', resourceType);

      const { data, error, count } = await query;

      if (error) throw error;

      // Statistika
      const stats = await getAuditStats(supabase, userId);

      return new Response(
        JSON.stringify({
          logs: data,
          total: count,
          limit,
          offset,
          stats,
        }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // POST - Yangi audit log yozish
    const logData: AuditLog = await req.json();

    if (!logData.action_type || !logData.resource_type) {
      return new Response(
        JSON.stringify({ error: 'action_type va resource_type majburiy' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // IP va User Agent olish
    const ip = req.headers.get('x-forwarded-for') || 
               req.headers.get('x-real-ip') || 
               'unknown';
    const userAgent = req.headers.get('user-agent') || 'unknown';

    // Risk tahlili
    const riskAnalysis = analyzeRisk(logData, ip);

    // Log yozish
    const { data: savedLog, error: saveError } = await supabase
      .from('audit_logs')
      .insert({
        user_id: logData.user_id,
        action_type: logData.action_type,
        resource_type: logData.resource_type,
        resource_id: logData.resource_id,
        details: logData.details,
        ip_address: ip,
        user_agent: userAgent,
        risk_level: riskAnalysis.level,
        is_suspicious: riskAnalysis.isSuspicious,
      })
      .select()
      .single();

    if (saveError) throw saveError;

    // Agar shubhali bo'lsa, ogohlantirish yuborish
    if (riskAnalysis.isSuspicious) {
      await sendSecurityAlert(supabase, logData, riskAnalysis);
    }

    return new Response(
      JSON.stringify({
        success: true,
        log: savedLog,
        riskAnalysis,
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  } catch (error) {
    console.error('Audit logging error:', error);
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});

async function getAuditStats(supabase: any, userId?: string) {
  const last24h = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
  const last7d = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();

  let baseQuery = supabase.from('audit_logs');
  if (userId) baseQuery = baseQuery.eq('user_id', userId);

  // Oxirgi 24 soat
  const { count: count24h } = await baseQuery
    .select('*', { count: 'exact', head: true })
    .gte('created_at', last24h);

  // Oxirgi 7 kun
  const { count: count7d } = await baseQuery
    .select('*', { count: 'exact', head: true })
    .gte('created_at', last7d);

  // Harakat turlari bo'yicha
  const { data: actionTypes } = await baseQuery
    .select('action_type')
    .gte('created_at', last7d);

  const actionCounts: any = {};
  actionTypes?.forEach((log: any) => {
    actionCounts[log.action_type] = (actionCounts[log.action_type] || 0) + 1;
  });

  // Shubhali harakatlar
  const { count: suspiciousCount } = await baseQuery
    .select('*', { count: 'exact', head: true })
    .eq('is_suspicious', true)
    .gte('created_at', last7d);

  return {
    last24h: count24h || 0,
    last7d: count7d || 0,
    byActionType: actionCounts,
    suspicious: suspiciousCount || 0,
  };
}

function analyzeRisk(logData: AuditLog, ip: string) {
  let riskScore = 0;
  const flags = [];

  // Xavfli harakatlar
  const highRiskActions = [
    'user_deleted',
    'funds_withdrawn',
    'api_key_created',
    'password_changed',
    'settings_modified',
    '2fa_disabled',
  ];

  const mediumRiskActions = [
    'login_attempt',
    'trade_executed',
    'transfer_initiated',
  ];

  if (highRiskActions.includes(logData.action_type)) {
    riskScore += 30;
    flags.push('Yuqori xavfli harakat');
  } else if (mediumRiskActions.includes(logData.action_type)) {
    riskScore += 15;
    flags.push('O\'rtacha xavfli harakat');
  }

  // IP tekshiruvi (oddiy check)
  if (ip.includes('unknown') || ip === '127.0.0.1') {
    riskScore += 10;
    flags.push('Noma\'lum IP manzil');
  }

  // Tunda faollik
  const hour = new Date().getUTCHours();
  if (hour >= 2 && hour <= 5) {
    riskScore += 5;
    flags.push('Tunda faollik');
  }

  // Risk darajasini aniqlash
  let level = 'low';
  if (riskScore >= 40) level = 'high';
  else if (riskScore >= 20) level = 'medium';

  return {
    level,
    score: riskScore,
    isSuspicious: riskScore >= 30,
    flags,
  };
}

async function sendSecurityAlert(supabase: any, logData: AuditLog, riskAnalysis: any) {
  // Security alert yuborish (notification system'ga)
  try {
    await supabase.from('notifications').insert({
      user_id: logData.user_id,
      type: 'security_alert',
      title: 'Shubhali faollik aniqlandi',
      message: `${logData.action_type} harakati shubhali deb topildi. Risk darajasi: ${riskAnalysis.level}`,
      priority: 'high',
      data: {
        action: logData.action_type,
        riskScore: riskAnalysis.score,
        flags: riskAnalysis.flags,
      },
    });
  } catch (error) {
    console.error('Failed to send security alert:', error);
  }
}
