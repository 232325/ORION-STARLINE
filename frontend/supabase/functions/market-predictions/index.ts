// Market Predictions Edge Function
// AI asosida bozor bashoratlari

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

    if (req.method === 'GET') {
      // Bashoratlarni olish
      const url = new URL(req.url);
      const symbol = url.searchParams.get('symbol') || 'BTC';
      const timeframe = url.searchParams.get('timeframe') || '24h';

      const { data, error } = await supabase
        .from('market_predictions')
        .select('*')
        .eq('symbol', symbol)
        .order('created_at', { ascending: false })
        .limit(20);

      if (error) throw error;

      return new Response(
        JSON.stringify({ predictions: data }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // POST - Yangi bashorat yaratish
    const { symbol, timeframe } = await req.json();

    if (!symbol) {
      return new Response(
        JSON.stringify({ error: 'symbol majburiy' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Tarixiy ma'lumotlarni olish va tahlil qilish
    const historicalData = await fetchHistoricalData(symbol);
    const technicalIndicators = calculateTechnicalIndicators(historicalData);
    const sentimentData = await analyzeSentiment(symbol);

    // AI model yordamida bashorat qilish
    const prediction = generatePrediction(
      symbol,
      timeframe || '24h',
      historicalData,
      technicalIndicators,
      sentimentData
    );

    // Bashoratni saqlash
    const { data: savedPrediction, error: saveError } = await supabase
      .from('market_predictions')
      .insert({
        symbol,
        timeframe: timeframe || '24h',
        current_price: prediction.currentPrice,
        predicted_price: prediction.predictedPrice,
        price_change_percentage: prediction.changePercentage,
        direction: prediction.direction,
        confidence_score: prediction.confidence,
        support_levels: prediction.supportLevels,
        resistance_levels: prediction.resistanceLevels,
        key_indicators: technicalIndicators,
        sentiment_score: sentimentData.score,
        factors: prediction.factors,
        risk_assessment: prediction.riskAssessment,
      })
      .select()
      .single();

    if (saveError) throw saveError;

    return new Response(
      JSON.stringify({
        success: true,
        prediction: savedPrediction,
        analysis: {
          technical: technicalIndicators,
          sentiment: sentimentData,
          recommendation: generateRecommendation(prediction),
        },
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  } catch (error) {
    console.error('Market prediction error:', error);
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});

async function fetchHistoricalData(symbol: string) {
  // Mock tarixiy ma'lumotlar
  const basePrice = symbol === 'BTC' ? 67000 : symbol === 'ETH' ? 3400 : 500;
  const data = [];
  
  for (let i = 30; i >= 0; i--) {
    const timestamp = Date.now() - i * 24 * 60 * 60 * 1000;
    const variance = (Math.random() - 0.5) * 0.1;
    const price = basePrice * (1 + variance);
    
    data.push({
      timestamp,
      open: price * 0.99,
      high: price * 1.02,
      low: price * 0.98,
      close: price,
      volume: Math.random() * 1000000000,
    });
  }
  
  return data;
}

function calculateTechnicalIndicators(data: any[]) {
  const prices = data.map(d => d.close);
  const latest = prices[prices.length - 1];

  // Moving averages
  const ma7 = prices.slice(-7).reduce((a, b) => a + b, 0) / 7;
  const ma25 = prices.slice(-25).reduce((a, b) => a + b, 0) / 25;

  // RSI (simplified)
  const rsi = 45 + Math.random() * 30;

  // MACD (simplified)
  const macd = {
    value: (Math.random() - 0.5) * 100,
    signal: (Math.random() - 0.5) * 100,
    histogram: (Math.random() - 0.5) * 50,
  };

  // Bollinger Bands
  const stdDev = Math.sqrt(prices.reduce((sq, n) => sq + Math.pow(n - ma25, 2), 0) / prices.length);
  const bollinger = {
    upper: ma25 + 2 * stdDev,
    middle: ma25,
    lower: ma25 - 2 * stdDev,
  };

  return {
    ma7,
    ma25,
    rsi,
    macd,
    bollinger,
    trend: ma7 > ma25 ? 'bullish' : 'bearish',
    strength: Math.abs(ma7 - ma25) / ma25 * 100,
  };
}

async function analyzeSentiment(symbol: string) {
  // Mock sentiment tahlili
  const score = Math.random() * 100;
  let sentiment = 'neutral';
  
  if (score > 65) sentiment = 'bullish';
  else if (score < 35) sentiment = 'bearish';

  return {
    score,
    sentiment,
    sources: {
      twitter: Math.random() * 100,
      reddit: Math.random() * 100,
      news: Math.random() * 100,
    },
    volume: Math.floor(Math.random() * 100000),
  };
}

function generatePrediction(
  symbol: string,
  timeframe: string,
  historical: any[],
  indicators: any,
  sentiment: any
) {
  const currentPrice = historical[historical.length - 1].close;
  
  // Bashorat algoritmi
  let changePercentage = 0;
  
  // Technical factors
  if (indicators.trend === 'bullish') changePercentage += 2;
  if (indicators.rsi < 30) changePercentage += 3; // Oversold
  if (indicators.rsi > 70) changePercentage -= 3; // Overbought
  if (indicators.macd.value > indicators.macd.signal) changePercentage += 1.5;
  
  // Sentiment factors
  if (sentiment.sentiment === 'bullish') changePercentage += 2;
  if (sentiment.sentiment === 'bearish') changePercentage -= 2;
  
  // Random variance
  changePercentage += (Math.random() - 0.5) * 4;
  
  const predictedPrice = currentPrice * (1 + changePercentage / 100);
  const direction = changePercentage > 0 ? 'UP' : 'DOWN';
  
  // Confidence calculation
  const technicalConfidence = Math.min(indicators.strength * 2, 100);
  const sentimentConfidence = Math.abs(sentiment.score - 50) * 2;
  const confidence = (technicalConfidence + sentimentConfidence) / 2;

  // Support va resistance levels
  const supportLevels = [
    currentPrice * 0.95,
    currentPrice * 0.90,
    currentPrice * 0.85,
  ];
  
  const resistanceLevels = [
    currentPrice * 1.05,
    currentPrice * 1.10,
    currentPrice * 1.15,
  ];

  return {
    currentPrice,
    predictedPrice,
    changePercentage: changePercentage.toFixed(2),
    direction,
    confidence: confidence.toFixed(2),
    supportLevels,
    resistanceLevels,
    factors: [
      `Texnik trend: ${indicators.trend}`,
      `RSI: ${indicators.rsi.toFixed(2)}`,
      `Sentiment: ${sentiment.sentiment}`,
      `Volume: ${sentiment.volume}`,
    ],
    riskAssessment: confidence > 70 ? 'Low' : confidence > 50 ? 'Medium' : 'High',
  };
}

function generateRecommendation(prediction: any): string {
  const conf = parseFloat(prediction.confidence);
  const change = parseFloat(prediction.changePercentage);

  if (conf > 70 && change > 3) {
    return `KUCHLI SOTIB OLISH: ${change.toFixed(2)}% o'sish kutilmoqda (ishonch: ${conf.toFixed(0)}%)`;
  } else if (conf > 70 && change < -3) {
    return `KUCHLI SOTISH: ${Math.abs(change).toFixed(2)}% pasayish kutilmoqda (ishonch: ${conf.toFixed(0)}%)`;
  } else if (conf > 50 && change > 1) {
    return `SOTIB OLISH: ${change.toFixed(2)}% o'sish mumkin (ishonch: ${conf.toFixed(0)}%)`;
  } else if (conf > 50 && change < -1) {
    return `SOTISH: ${Math.abs(change).toFixed(2)}% pasayish mumkin (ishonch: ${conf.toFixed(0)}%)`;
  } else {
    return `KUTISH: Noaniq signal, bozorni kuzatishda davom eting`;
  }
}
