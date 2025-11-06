// Advanced Security Edge Function
// Kengaytirilgan xavfsizlik funksiyalari

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.3';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
};

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    const url = new URL(req.url);
    const action = url.searchParams.get('action');

    switch (action) {
      case 'session-monitor':
        return await monitorActiveSessions(req, supabase);
      
      case 'ip-whitelist':
        return await manageIPWhitelist(req, supabase);
      
      case 'device-management':
        return await manageDevices(req, supabase);
      
      case 'security-score':
        return await calculateSecurityScore(req, supabase);
      
      case 'suspicious-activity':
        return await checkSuspiciousActivity(req, supabase);
      
      case 'withdraw-whitelist':
        return await manageWithdrawWhitelist(req, supabase);
      
      default:
        return new Response(
          JSON.stringify({ error: 'Noma\'lum action' }),
          { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
    }
  } catch (error) {
    console.error('Advanced security error:', error);
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});

async function monitorActiveSessions(req: Request, supabase: any) {
  const { user_id } = await req.json();

  if (!user_id) {
    return new Response(
      JSON.stringify({ error: 'user_id majburiy' }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  // Faol sessiyalarni olish
  const { data: sessions, error } = await supabase
    .from('user_sessions')
    .select('*')
    .eq('user_id', user_id)
    .eq('is_active', true)
    .order('last_activity', { ascending: false });

  if (error) throw error;

  // Har bir sessiya uchun lokatsiya va qurilma ma'lumotlari
  const enrichedSessions = sessions?.map((session: any) => ({
    ...session,
    location: geolocateIP(session.ip_address),
    device: parseUserAgent(session.user_agent),
    isCurrent: session.session_id === getCurrentSessionId(req),
  }));

  return new Response(
    JSON.stringify({
      sessions: enrichedSessions,
      total: enrichedSessions?.length || 0,
    }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  );
}

async function manageIPWhitelist(req: Request, supabase: any) {
  const { user_id, action, ip_address, description } = await req.json();

  if (!user_id || !action) {
    return new Response(
      JSON.stringify({ error: 'user_id va action majburiy' }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  if (action === 'add') {
    if (!ip_address) {
      return new Response(
        JSON.stringify({ error: 'ip_address majburiy' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    const { data, error } = await supabase
      .from('ip_whitelist')
      .insert({
        user_id,
        ip_address,
        description,
        is_active: true,
      })
      .select()
      .single();

    if (error) throw error;

    return new Response(
      JSON.stringify({ success: true, whitelist: data }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  } else if (action === 'remove') {
    const { error } = await supabase
      .from('ip_whitelist')
      .delete()
      .eq('user_id', user_id)
      .eq('ip_address', ip_address);

    if (error) throw error;

    return new Response(
      JSON.stringify({ success: true }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  } else if (action === 'list') {
    const { data, error } = await supabase
      .from('ip_whitelist')
      .select('*')
      .eq('user_id', user_id)
      .eq('is_active', true);

    if (error) throw error;

    return new Response(
      JSON.stringify({ whitelist: data }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  return new Response(
    JSON.stringify({ error: 'Noma\'lum action' }),
    { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  );
}

async function manageDevices(req: Request, supabase: any) {
  const { user_id, action, device_id } = await req.json();

  if (!user_id) {
    return new Response(
      JSON.stringify({ error: 'user_id majburiy' }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  if (action === 'list') {
    const { data, error } = await supabase
      .from('trusted_devices')
      .select('*')
      .eq('user_id', user_id)
      .eq('is_trusted', true)
      .order('last_used', { ascending: false });

    if (error) throw error;

    return new Response(
      JSON.stringify({ devices: data }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  } else if (action === 'revoke') {
    const { error } = await supabase
      .from('trusted_devices')
      .update({ is_trusted: false })
      .eq('user_id', user_id)
      .eq('device_id', device_id);

    if (error) throw error;

    return new Response(
      JSON.stringify({ success: true }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  return new Response(
    JSON.stringify({ error: 'Noma\'lum action' }),
    { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  );
}

async function calculateSecurityScore(req: Request, supabase: any) {
  const { user_id } = await req.json();

  if (!user_id) {
    return new Response(
      JSON.stringify({ error: 'user_id majburiy' }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  let score = 0;
  const factors = [];

  // 2FA faolligi (30 ball)
  const { data: authData } = await supabase
    .from('user_security')
    .select('two_factor_enabled')
    .eq('user_id', user_id)
    .single();

  if (authData?.two_factor_enabled) {
    score += 30;
    factors.push({ name: '2FA faol', points: 30, status: 'good' });
  } else {
    factors.push({ name: '2FA faol emas', points: 0, status: 'bad' });
  }

  // KYC verification (25 ball)
  const { data: kycData } = await supabase
    .from('kyc_verification')
    .select('verification_status')
    .eq('user_id', user_id)
    .eq('verification_status', 'approved')
    .single();

  if (kycData) {
    score += 25;
    factors.push({ name: 'KYC tasdiqlangan', points: 25, status: 'good' });
  } else {
    factors.push({ name: 'KYC tasdiqlanmagan', points: 0, status: 'warning' });
  }

  // IP Whitelist (15 ball)
  const { count: whitelistCount } = await supabase
    .from('ip_whitelist')
    .select('*', { count: 'exact', head: true })
    .eq('user_id', user_id)
    .eq('is_active', true);

  if (whitelistCount && whitelistCount > 0) {
    score += 15;
    factors.push({ name: 'IP Whitelist o\'rnatilgan', points: 15, status: 'good' });
  } else {
    factors.push({ name: 'IP Whitelist yo\'q', points: 0, status: 'warning' });
  }

  // Withdrawal whitelist (15 ball)
  const { count: withdrawCount } = await supabase
    .from('withdrawal_whitelist')
    .select('*', { count: 'exact', head: true })
    .eq('user_id', user_id)
    .eq('is_active', true);

  if (withdrawCount && withdrawCount > 0) {
    score += 15;
    factors.push({ name: 'Yechib olish manzillari cheklangan', points: 15, status: 'good' });
  } else {
    factors.push({ name: 'Yechib olish cheklanmagan', points: 0, status: 'warning' });
  }

  // Parol yangilanishi (10 ball)
  const { data: passData } = await supabase
    .from('users')
    .select('password_updated_at')
    .eq('id', user_id)
    .single();

  const daysSinceUpdate = passData?.password_updated_at
    ? Math.floor((Date.now() - new Date(passData.password_updated_at).getTime()) / (24 * 60 * 60 * 1000))
    : 999;

  if (daysSinceUpdate < 90) {
    score += 10;
    factors.push({ name: 'Parol yaqinda yangilangan', points: 10, status: 'good' });
  } else {
    factors.push({ name: 'Parolni yangilash kerak', points: 0, status: 'warning' });
  }

  // Shubhali faollik yo'qligi (5 ball)
  const { count: suspiciousCount } = await supabase
    .from('audit_logs')
    .select('*', { count: 'exact', head: true })
    .eq('user_id', user_id)
    .eq('is_suspicious', true)
    .gte('created_at', new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString());

  if (!suspiciousCount || suspiciousCount === 0) {
    score += 5;
    factors.push({ name: 'Shubhali faollik yo\'q', points: 5, status: 'good' });
  } else {
    factors.push({ name: 'Shubhali faollik aniqlangan', points: 0, status: 'bad' });
  }

  // Xavfsizlik darajasi
  let level = 'Juda zaif';
  let color = 'red';
  
  if (score >= 80) {
    level = 'Mukammal';
    color = 'green';
  } else if (score >= 60) {
    level = 'Yaxshi';
    color = 'blue';
  } else if (score >= 40) {
    level = 'O\'rtacha';
    color = 'yellow';
  } else if (score >= 20) {
    level = 'Zaif';
    color = 'orange';
  }

  return new Response(
    JSON.stringify({
      score,
      maxScore: 100,
      level,
      color,
      factors,
      recommendations: generateSecurityRecommendations(factors),
    }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  );
}

async function checkSuspiciousActivity(req: Request, supabase: any) {
  const { user_id, days = 7 } = await req.json();

  const since = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();

  const { data, error } = await supabase
    .from('audit_logs')
    .select('*')
    .eq('user_id', user_id)
    .eq('is_suspicious', true)
    .gte('created_at', since)
    .order('created_at', { ascending: false });

  if (error) throw error;

  return new Response(
    JSON.stringify({
      activities: data,
      count: data?.length || 0,
      riskLevel: data && data.length > 5 ? 'high' : data && data.length > 2 ? 'medium' : 'low',
    }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  );
}

async function manageWithdrawWhitelist(req: Request, supabase: any) {
  const { user_id, action, address, currency, label } = await req.json();

  if (action === 'add') {
    const { data, error } = await supabase
      .from('withdrawal_whitelist')
      .insert({
        user_id,
        currency,
        address,
        label,
        is_active: true,
      })
      .select()
      .single();

    if (error) throw error;

    return new Response(
      JSON.stringify({ success: true, address: data }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  } else if (action === 'list') {
    const { data, error } = await supabase
      .from('withdrawal_whitelist')
      .select('*')
      .eq('user_id', user_id)
      .eq('is_active', true);

    if (error) throw error;

    return new Response(
      JSON.stringify({ addresses: data }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  return new Response(
    JSON.stringify({ error: 'Noma\'lum action' }),
    { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  );
}

function geolocateIP(ip: string) {
  // Mock geolocation
  const locations = ['Toshkent, O\'zbekiston', 'Moskva, Rossiya', 'Nyu-York, AQSh', 'London, Buyuk Britaniya'];
  return locations[Math.floor(Math.random() * locations.length)];
}

function parseUserAgent(ua: string) {
  // Oddiy user agent parsing
  if (ua.includes('Chrome')) return 'Chrome Browser';
  if (ua.includes('Firefox')) return 'Firefox Browser';
  if (ua.includes('Safari')) return 'Safari Browser';
  if (ua.includes('Mobile')) return 'Mobile Device';
  return 'Unknown Device';
}

function getCurrentSessionId(req: Request): string {
  return req.headers.get('x-session-id') || 'current';
}

function generateSecurityRecommendations(factors: any[]): string[] {
  const recommendations = [];
  
  factors.forEach(factor => {
    if (factor.status === 'bad' || factor.status === 'warning') {
      if (factor.name.includes('2FA')) {
        recommendations.push('Ikki faktorli autentifikatsiyani yoqing');
      } else if (factor.name.includes('KYC')) {
        recommendations.push('KYC jarayonini yakunlang');
      } else if (factor.name.includes('IP')) {
        recommendations.push('Ishonchli IP manzillarni qo\'shing');
      } else if (factor.name.includes('Parol')) {
        recommendations.push('Parolingizni yangilang');
      } else if (factor.name.includes('Yechib olish')) {
        recommendations.push('Yechib olish manzillarini cheklang');
      }
    }
  });
  
  return recommendations;
}
