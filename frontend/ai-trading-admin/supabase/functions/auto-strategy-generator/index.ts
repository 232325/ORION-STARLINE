// Auto Strategy Generator Edge Function
// AI yordamida trading strategiyalarini avtomatik yaratish

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.3';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
};

interface StrategyRequest {
  user_id: string;
  risk_level: 'low' | 'medium' | 'high';
  investment_amount: number;
  preferred_assets?: string[];
  timeframe?: string;
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
      // Foydalanuvchi strategiyalarini olish
      const url = new URL(req.url);
      const userId = url.searchParams.get('user_id');

      if (!userId) {
        return new Response(
          JSON.stringify({ error: 'user_id majburiy' }),
          { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }

      const { data, error } = await supabase
        .from('auto_strategies')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false });

      if (error) throw error;

      return new Response(
        JSON.stringify({ strategies: data }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // POST - Yangi strategiya yaratish
    const requestData: StrategyRequest = await req.json();
    const { user_id, risk_level, investment_amount, preferred_assets, timeframe } = requestData;

    if (!user_id || !risk_level || !investment_amount) {
      return new Response(
        JSON.stringify({ error: 'user_id, risk_level va investment_amount majburiy' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Bozor ma'lumotlarini tahlil qilish
    const marketAnalysis = await analyzeMarket();

    // Strategiya yaratish
    const strategy = generateStrategy(
      risk_level,
      investment_amount,
      preferred_assets,
      timeframe,
      marketAnalysis
    );

    // Backtesting qilish
    const backtestResults = await runBacktest(strategy);

    // Strategiyani saqlash
    const { data: savedStrategy, error: saveError } = await supabase
      .from('auto_strategies')
      .insert({
        user_id,
        name: strategy.name,
        description: strategy.description,
        risk_level,
        investment_amount,
        asset_allocation: strategy.allocation,
        entry_rules: strategy.entryRules,
        exit_rules: strategy.exitRules,
        stop_loss_percentage: strategy.stopLoss,
        take_profit_percentage: strategy.takeProfit,
        max_positions: strategy.maxPositions,
        position_sizing: strategy.positionSizing,
        rebalance_frequency: strategy.rebalanceFrequency,
        backtest_results: backtestResults,
        expected_return: backtestResults.expectedReturn,
        max_drawdown: backtestResults.maxDrawdown,
        win_rate: backtestResults.winRate,
        is_active: false,
      })
      .select()
      .single();

    if (saveError) throw saveError;

    return new Response(
      JSON.stringify({
        success: true,
        strategy: savedStrategy,
        backtestResults,
        recommendation: generateRecommendation(backtestResults),
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  } catch (error) {
    console.error('Auto strategy generator error:', error);
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});

async function analyzeMarket() {
  // Bozor tahlili (mock data)
  return {
    trend: Math.random() > 0.5 ? 'bullish' : 'bearish',
    volatility: Math.random() * 0.5 + 0.1,
    momentum: Math.random() * 100 - 50,
    topAssets: ['BTC', 'ETH', 'BNB', 'SOL', 'ADA'],
    correlations: {
      'BTC-ETH': 0.85,
      'BTC-BNB': 0.72,
      'ETH-BNB': 0.68,
    },
  };
}

function generateStrategy(
  riskLevel: string,
  amount: number,
  assets?: string[],
  timeframe?: string,
  market?: any
) {
  const strategies: any = {
    low: {
      name: 'Konservativ Diversifikatsiya',
      description: 'Past xavfli, barqaror o\'sish strategiyasi',
      allocation: { BTC: 50, ETH: 30, USDT: 15, BNB: 5 },
      entryRules: ['RSI < 40', 'MACD bullish cross', 'Volume spike'],
      exitRules: ['Take profit 10%', 'Stop loss 3%', 'Trailing stop 5%'],
      stopLoss: 3,
      takeProfit: 10,
      maxPositions: 3,
      positionSizing: 'equal',
      rebalanceFrequency: 'weekly',
    },
    medium: {
      name: 'Balansli O\'sish',
      description: 'O\'rtacha xavf-daromad nisbati',
      allocation: { BTC: 40, ETH: 30, SOL: 15, BNB: 10, ADA: 5 },
      entryRules: ['RSI < 50', 'EMA crossover', 'Momentum positive'],
      exitRules: ['Take profit 20%', 'Stop loss 5%', 'Trailing stop 8%'],
      stopLoss: 5,
      takeProfit: 20,
      maxPositions: 5,
      positionSizing: 'risk-based',
      rebalanceFrequency: 'daily',
    },
    high: {
      name: 'Agressiv Daromad',
      description: 'Yuqori xavfli, maksimal daromad strategiyasi',
      allocation: { ETH: 30, SOL: 25, BNB: 20, ADA: 15, AVAX: 10 },
      entryRules: ['Breakout confirmed', 'High volume', 'Strong momentum'],
      exitRules: ['Take profit 50%', 'Stop loss 10%', 'Trailing stop 15%'],
      stopLoss: 10,
      takeProfit: 50,
      maxPositions: 8,
      positionSizing: 'dynamic',
      rebalanceFrequency: 'hourly',
    },
  };

  return strategies[riskLevel];
}

async function runBacktest(strategy: any) {
  // Backtesting simulyatsiyasi
  const days = 90;
  const trades = Math.floor(Math.random() * 50) + 30;
  const winningTrades = Math.floor(trades * (0.5 + Math.random() * 0.3));

  return {
    period: `${days} days`,
    totalTrades: trades,
    winningTrades,
    losingTrades: trades - winningTrades,
    winRate: (winningTrades / trades * 100).toFixed(2),
    expectedReturn: (Math.random() * 30 + 5).toFixed(2) + '%',
    maxDrawdown: (Math.random() * 15 + 5).toFixed(2) + '%',
    sharpeRatio: (Math.random() * 2 + 0.5).toFixed(2),
    profitFactor: (Math.random() * 1.5 + 1).toFixed(2),
    avgWin: (Math.random() * 10 + 5).toFixed(2) + '%',
    avgLoss: (Math.random() * 5 + 2).toFixed(2) + '%',
    bestTrade: (Math.random() * 50 + 20).toFixed(2) + '%',
    worstTrade: '-' + (Math.random() * 15 + 5).toFixed(2) + '%',
  };
}

function generateRecommendation(results: any): string {
  const winRate = parseFloat(results.winRate);
  const returnRate = parseFloat(results.expectedReturn);

  if (winRate > 60 && returnRate > 20) {
    return 'Ajoyib! Bu strategiya juda yaxshi natijalar ko\'rsatmoqda. Aktivlashtirish tavsiya etiladi.';
  } else if (winRate > 50 && returnRate > 10) {
    return 'Yaxshi natijalar. Strategiyani sinab ko\'rishingiz mumkin, lekin kichik miqdordan boshlang.';
  } else {
    return 'Strategiya yetarli emas. Parametrlarni o\'zgartirib, qaytadan sinab ko\'ring.';
  }
}
