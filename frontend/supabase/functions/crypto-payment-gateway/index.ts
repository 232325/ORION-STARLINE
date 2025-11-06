// Crypto Payment Gateway Edge Function
// Kripto to'lovlarni qayta ishlash

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.3';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
};

interface PaymentRequest {
  user_id: string;
  currency: string;
  amount: number;
  purpose: string;
  callback_url?: string;
}

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
      case 'create-payment':
        return await createPayment(req, supabase);
      
      case 'check-payment':
        return await checkPaymentStatus(req, supabase);
      
      case 'payment-history':
        return await getPaymentHistory(req, supabase);
      
      case 'supported-currencies':
        return await getSupportedCurrencies(req, supabase);
      
      case 'exchange-rate':
        return await getExchangeRate(req, supabase);
      
      case 'webhook':
        return await handleWebhook(req, supabase);
      
      default:
        return new Response(
          JSON.stringify({ error: 'Noma\'lum action' }),
          { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
    }
  } catch (error) {
    console.error('Crypto payment error:', error);
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});

async function createPayment(req: Request, supabase: any) {
  const paymentReq: PaymentRequest = await req.json();

  if (!paymentReq.user_id || !paymentReq.currency || !paymentReq.amount) {
    return new Response(
      JSON.stringify({ error: 'user_id, currency va amount majburiy' }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  // To'lov manzilini yaratish
  const paymentAddress = generateCryptoAddress(paymentReq.currency);
  
  // Exchange rate olish
  const rate = await fetchExchangeRate(paymentReq.currency, 'USD');
  const usdAmount = paymentReq.amount * rate;

  // To'lovni bazaga saqlash
  const { data: payment, error } = await supabase
    .from('crypto_payments')
    .insert({
      user_id: paymentReq.user_id,
      currency: paymentReq.currency,
      amount: paymentReq.amount,
      usd_amount: usdAmount,
      payment_address: paymentAddress,
      purpose: paymentReq.purpose,
      callback_url: paymentReq.callback_url,
      status: 'pending',
      expires_at: new Date(Date.now() + 30 * 60 * 1000).toISOString(), // 30 daqiqa
    })
    .select()
    .single();

  if (error) throw error;

  // QR code uchun ma'lumot
  const paymentUri = generatePaymentURI(paymentReq.currency, paymentAddress, paymentReq.amount);

  return new Response(
    JSON.stringify({
      success: true,
      payment: {
        ...payment,
        payment_uri: paymentUri,
        qr_code_url: `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(paymentUri)}`,
      },
      instructions: generatePaymentInstructions(paymentReq.currency),
    }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  );
}

async function checkPaymentStatus(req: Request, supabase: any) {
  const { payment_id } = await req.json();

  if (!payment_id) {
    return new Response(
      JSON.stringify({ error: 'payment_id majburiy' }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  // To'lov ma'lumotlarini olish
  const { data: payment, error } = await supabase
    .from('crypto_payments')
    .select('*')
    .eq('id', payment_id)
    .single();

  if (error) throw error;

  // Blockchain'dan to'lovni tekshirish
  const blockchainStatus = await checkBlockchainTransaction(
    payment.currency,
    payment.payment_address
  );

  // Agar to'lov kelgan bo'lsa, statusni yangilash
  if (blockchainStatus.confirmed && payment.status === 'pending') {
    const { data: updated, error: updateError } = await supabase
      .from('crypto_payments')
      .update({
        status: 'completed',
        transaction_hash: blockchainStatus.txHash,
        confirmed_at: new Date().toISOString(),
        confirmations: blockchainStatus.confirmations,
      })
      .eq('id', payment_id)
      .select()
      .single();

    if (updateError) throw updateError;

    // Callback chaqirish
    if (payment.callback_url) {
      await notifyCallback(payment.callback_url, updated);
    }

    // Foydalanuvchi balansini yangilash
    await creditUserBalance(supabase, payment.user_id, payment.amount, payment.currency);

    return new Response(
      JSON.stringify({
        status: 'completed',
        payment: updated,
        blockchainStatus,
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  return new Response(
    JSON.stringify({
      status: payment.status,
      payment,
      blockchainStatus,
    }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  );
}

async function getPaymentHistory(req: Request, supabase: any) {
  const { user_id, limit = 20, offset = 0 } = await req.json();

  if (!user_id) {
    return new Response(
      JSON.stringify({ error: 'user_id majburiy' }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  const { data, error, count } = await supabase
    .from('crypto_payments')
    .select('*', { count: 'exact' })
    .eq('user_id', user_id)
    .order('created_at', { ascending: false })
    .range(offset, offset + limit - 1);

  if (error) throw error;

  return new Response(
    JSON.stringify({
      payments: data,
      total: count,
      limit,
      offset,
    }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  );
}

async function getSupportedCurrencies(req: Request, supabase: any) {
  const currencies = [
    { symbol: 'BTC', name: 'Bitcoin', network: 'Bitcoin', fee: 0.0001, min_amount: 0.001 },
    { symbol: 'ETH', name: 'Ethereum', network: 'Ethereum', fee: 0.001, min_amount: 0.01 },
    { symbol: 'USDT', name: 'Tether', network: 'TRC20', fee: 1, min_amount: 10 },
    { symbol: 'BNB', name: 'Binance Coin', network: 'BSC', fee: 0.0005, min_amount: 0.01 },
    { symbol: 'USDC', name: 'USD Coin', network: 'Ethereum', fee: 1, min_amount: 10 },
    { symbol: 'TRX', name: 'Tron', network: 'Tron', fee: 1, min_amount: 10 },
  ];

  return new Response(
    JSON.stringify({ currencies }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  );
}

async function getExchangeRate(req: Request, supabase: any) {
  const { from, to = 'USD' } = await req.json();

  if (!from) {
    return new Response(
      JSON.stringify({ error: 'from currency majburiy' }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  const rate = await fetchExchangeRate(from, to);

  return new Response(
    JSON.stringify({
      from,
      to,
      rate,
      updated_at: new Date().toISOString(),
    }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  );
}

async function handleWebhook(req: Request, supabase: any) {
  // Blockchain webhook'larini qayta ishlash
  const webhookData = await req.json();

  console.log('Webhook received:', webhookData);

  // Webhook verification (signature check)
  // Real implementation: verify webhook signature

  // To'lovni topish va yangilash
  if (webhookData.address && webhookData.amount) {
    const { data: payment } = await supabase
      .from('crypto_payments')
      .select('*')
      .eq('payment_address', webhookData.address)
      .eq('status', 'pending')
      .single();

    if (payment && webhookData.amount >= payment.amount) {
      await supabase
        .from('crypto_payments')
        .update({
          status: 'completed',
          transaction_hash: webhookData.tx_hash,
          confirmed_at: new Date().toISOString(),
        })
        .eq('id', payment.id);

      await creditUserBalance(supabase, payment.user_id, payment.amount, payment.currency);
    }
  }

  return new Response(
    JSON.stringify({ received: true }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  );
}

function generateCryptoAddress(currency: string): string {
  // Mock manzil generatsiyasi
  // Real implementation: generate real address from wallet API
  const prefixes: any = {
    BTC: '1',
    ETH: '0x',
    USDT: 'T',
    BNB: '0x',
    TRX: 'T',
  };

  const prefix = prefixes[currency] || '0x';
  const randomHex = Array.from({ length: 40 }, () => 
    Math.floor(Math.random() * 16).toString(16)
  ).join('');

  return `${prefix}${randomHex}`;
}

function generatePaymentURI(currency: string, address: string, amount: number): string {
  // Kripto to'lov URI yaratish (BIP21, EIP681, etc.)
  const uriSchemes: any = {
    BTC: 'bitcoin',
    ETH: 'ethereum',
    BNB: 'bnb',
  };

  const scheme = uriSchemes[currency] || currency.toLowerCase();
  return `${scheme}:${address}?amount=${amount}`;
}

async function fetchExchangeRate(from: string, to: string): Promise<number> {
  // Mock exchange rate
  // Real implementation: fetch from CoinGecko, Binance API, etc.
  const rates: any = {
    BTC: 67234.56,
    ETH: 3421.89,
    USDT: 1.0,
    BNB: 567.23,
    USDC: 1.0,
    TRX: 0.12,
  };

  return rates[from] || 1;
}

async function checkBlockchainTransaction(currency: string, address: string) {
  // Mock blockchain check
  // Real implementation: query blockchain explorer API
  
  // Tasodifiy to'lov kelishi (demo uchun)
  const isConfirmed = Math.random() < 0.3; // 30% ehtimol

  return {
    confirmed: isConfirmed,
    txHash: isConfirmed ? '0x' + Array.from({ length: 64 }, () => 
      Math.floor(Math.random() * 16).toString(16)
    ).join('') : null,
    confirmations: isConfirmed ? Math.floor(Math.random() * 20) + 1 : 0,
  };
}

async function creditUserBalance(supabase: any, userId: string, amount: number, currency: string) {
  // Foydalanuvchi balansini yangilash
  const { data: existing } = await supabase
    .from('user_balances')
    .select('*')
    .eq('user_id', userId)
    .eq('currency', currency)
    .single();

  if (existing) {
    await supabase
      .from('user_balances')
      .update({ balance: existing.balance + amount })
      .eq('id', existing.id);
  } else {
    await supabase
      .from('user_balances')
      .insert({
        user_id: userId,
        currency,
        balance: amount,
      });
  }
}

async function notifyCallback(url: string, payment: any) {
  try {
    await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payment),
    });
  } catch (error) {
    console.error('Callback notification failed:', error);
  }
}

function generatePaymentInstructions(currency: string): string[] {
  return [
    `1. ${currency} hamyoningizni oching`,
    `2. Ko'rsatilgan manzilga to'lovni yuboring`,
    `3. To'g'ri miqdor yuborilganiga ishonch hosil qiling`,
    `4. To'lov tasdiqlangan (1-3 daqiqa) ortidan balansingiz yangilanadi`,
    `5. To'lov 30 daqiqa ichida amalga oshirilishi kerak`,
  ];
}
