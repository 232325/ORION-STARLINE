// Voice Commands Edge Function
// Ovozli buyruqlarni qayta ishlash va trading amallarini bajarish

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.3';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
};

interface VoiceCommand {
  text: string;
  audio_url?: string;
  user_id: string;
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    const { text, audio_url, user_id }: VoiceCommand = await req.json();

    if (!text || !user_id) {
      return new Response(
        JSON.stringify({ error: 'text va user_id majburiy' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Ovozli buyruqni tahlil qilish
    const command = parseVoiceCommand(text.toLowerCase());

    // Buyruqni bazaga saqlash
    const { data: savedCommand, error: saveError } = await supabase
      .from('voice_commands')
      .insert({
        user_id,
        command_text: text,
        audio_url,
        command_type: command.type,
        parameters: command.parameters,
        status: 'processed',
        confidence_score: command.confidence,
      })
      .select()
      .single();

    if (saveError) throw saveError;

    // Buyruqni bajarish
    let result;
    switch (command.type) {
      case 'BUY':
      case 'SELL':
        result = await executeTrade(supabase, user_id, command);
        break;
      case 'CHECK_BALANCE':
        result = await checkBalance(supabase, user_id);
        break;
      case 'GET_PRICE':
        result = await getPrice(command.parameters.symbol);
        break;
      case 'SET_ALERT':
        result = await setAlert(supabase, user_id, command);
        break;
      default:
        result = { message: 'Buyruq tanilmadi' };
    }

    return new Response(
      JSON.stringify({
        success: true,
        command: savedCommand,
        result,
        response_text: generateResponse(command.type, result),
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  } catch (error) {
    console.error('Voice command error:', error);
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});

function parseVoiceCommand(text: string) {
  // Oddiy NLP parsing
  const buyPatterns = ['sotib ol', 'xarid qil', 'buy', 'purchase'];
  const sellPatterns = ['sot', 'sotish', 'sell'];
  const balancePatterns = ['balans', 'qoldiq', 'balance', 'mablag'];
  const pricePatterns = ['narx', 'price', 'qiymat'];
  const alertPatterns = ['ogohlantirish', 'alert', 'xabar ber'];

  let type = 'UNKNOWN';
  let parameters: any = {};
  let confidence = 0.8;

  if (buyPatterns.some(p => text.includes(p))) {
    type = 'BUY';
    const symbol = extractSymbol(text);
    const amount = extractAmount(text);
    parameters = { symbol, amount };
  } else if (sellPatterns.some(p => text.includes(p))) {
    type = 'SELL';
    const symbol = extractSymbol(text);
    const amount = extractAmount(text);
    parameters = { symbol, amount };
  } else if (balancePatterns.some(p => text.includes(p))) {
    type = 'CHECK_BALANCE';
  } else if (pricePatterns.some(p => text.includes(p))) {
    type = 'GET_PRICE';
    parameters = { symbol: extractSymbol(text) };
  } else if (alertPatterns.some(p => text.includes(p))) {
    type = 'SET_ALERT';
    parameters = {
      symbol: extractSymbol(text),
      price: extractAmount(text),
      condition: 'above',
    };
  }

  return { type, parameters, confidence };
}

function extractSymbol(text: string): string {
  const cryptos = ['btc', 'eth', 'usdt', 'bnb', 'sol', 'xrp'];
  for (const crypto of cryptos) {
    if (text.includes(crypto)) {
      return crypto.toUpperCase();
    }
  }
  return 'BTC';
}

function extractAmount(text: string): number {
  const numbers = text.match(/\d+\.?\d*/g);
  return numbers ? parseFloat(numbers[0]) : 100;
}

async function executeTrade(supabase: any, userId: string, command: any) {
  const { symbol, amount } = command.parameters;
  const price = Math.random() * 50000 + 30000; // Mock narx
  
  await supabase.from('trades').insert({
    user_id: userId,
    symbol,
    side: command.type.toLowerCase(),
    amount,
    price,
    status: 'executed',
    source: 'voice_command',
  });

  return {
    symbol,
    amount,
    price,
    total: amount * price,
  };
}

async function checkBalance(supabase: any, userId: string) {
  const { data } = await supabase
    .from('user_balances')
    .select('*')
    .eq('user_id', userId);

  return data || [];
}

async function getPrice(symbol: string) {
  // Mock narx
  const prices: any = {
    BTC: 67234.56,
    ETH: 3421.89,
    USDT: 1.00,
    BNB: 567.23,
  };
  return { symbol, price: prices[symbol] || 0 };
}

async function setAlert(supabase: any, userId: string, command: any) {
  const { symbol, price, condition } = command.parameters;
  
  await supabase.from('price_alerts').insert({
    user_id: userId,
    symbol,
    target_price: price,
    condition,
    is_active: true,
  });

  return { symbol, price, condition };
}

function generateResponse(type: string, result: any): string {
  const responses: any = {
    BUY: `${result.amount} ${result.symbol} ${result.price} narxda sotib olindi. Jami: $${result.total.toFixed(2)}`,
    SELL: `${result.amount} ${result.symbol} ${result.price} narxda sotildi. Jami: $${result.total.toFixed(2)}`,
    CHECK_BALANCE: `Sizning balansingiz: ${result.length} ta aktiv`,
    GET_PRICE: `${result.symbol} narxi: $${result.price}`,
    SET_ALERT: `${result.symbol} uchun ${result.price} da ogohlantirish o'rnatildi`,
  };

  return responses[type] || 'Buyruq bajarildi';
}
