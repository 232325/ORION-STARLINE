// Premium Marketplace Edge Function
// Premium strategiya va signal bozori

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.3';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
};

interface MarketplaceItem {
  seller_id: string;
  title: string;
  description: string;
  item_type: 'strategy' | 'signal' | 'bot' | 'indicator';
  price: number;
  currency: string;
  performance_data?: any;
  features?: string[];
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
      case 'list-items':
        return await listMarketplaceItems(req, supabase);
      
      case 'get-item':
        return await getItemDetails(req, supabase);
      
      case 'publish-item':
        return await publishItem(req, supabase);
      
      case 'purchase-item':
        return await purchaseItem(req, supabase);
      
      case 'my-items':
        return await getMyItems(req, supabase);
      
      case 'my-purchases':
        return await getMyPurchases(req, supabase);
      
      case 'top-sellers':
        return await getTopSellers(req, supabase);
      
      case 'leave-review':
        return await leaveReview(req, supabase);
      
      default:
        return new Response(
          JSON.stringify({ error: 'Noma\'lum action' }),
          { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
    }
  } catch (error) {
    console.error('Marketplace error:', error);
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});

async function listMarketplaceItems(req: Request, supabase: any) {
  const url = new URL(req.url);
  const itemType = url.searchParams.get('type');
  const sortBy = url.searchParams.get('sort') || 'popularity';
  const limit = parseInt(url.searchParams.get('limit') || '20');
  const offset = parseInt(url.searchParams.get('offset') || '0');

  let query = supabase
    .from('premium_marketplace')
    .select('*, seller:users!seller_id(id, username, avatar_url)', { count: 'exact' })
    .eq('is_active', true);

  if (itemType) {
    query = query.eq('item_type', itemType);
  }

  // Saralash
  switch (sortBy) {
    case 'price-low':
      query = query.order('price', { ascending: true });
      break;
    case 'price-high':
      query = query.order('price', { ascending: false });
      break;
    case 'rating':
      query = query.order('average_rating', { ascending: false });
      break;
    case 'newest':
      query = query.order('created_at', { ascending: false });
      break;
    default: // popularity
      query = query.order('total_sales', { ascending: false });
  }

  const { data, error, count } = await query.range(offset, offset + limit - 1);

  if (error) throw error;

  return new Response(
    JSON.stringify({
      items: data,
      total: count,
      limit,
      offset,
    }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  );
}

async function getItemDetails(req: Request, supabase: any) {
  const url = new URL(req.url);
  const itemId = url.searchParams.get('item_id');

  if (!itemId) {
    return new Response(
      JSON.stringify({ error: 'item_id majburiy' }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  // Item ma'lumotlari
  const { data: item, error } = await supabase
    .from('premium_marketplace')
    .select('*, seller:users!seller_id(id, username, avatar_url, created_at)')
    .eq('id', itemId)
    .single();

  if (error) throw error;

  // Reviews olish
  const { data: reviews } = await supabase
    .from('marketplace_reviews')
    .select('*, reviewer:users!reviewer_id(username, avatar_url)')
    .eq('item_id', itemId)
    .order('created_at', { ascending: false })
    .limit(10);

  // Ko'rishlar sonini oshirish
  await supabase
    .from('premium_marketplace')
    .update({ views_count: (item.views_count || 0) + 1 })
    .eq('id', itemId);

  return new Response(
    JSON.stringify({
      item,
      reviews: reviews || [],
    }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  );
}

async function publishItem(req: Request, supabase: any) {
  const itemData: MarketplaceItem = await req.json();

  if (!itemData.seller_id || !itemData.title || !itemData.price) {
    return new Response(
      JSON.stringify({ error: 'seller_id, title va price majburiy' }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  // Sotuvchining KYC statusini tekshirish
  const { data: kyc } = await supabase
    .from('kyc_verification')
    .select('verification_status')
    .eq('user_id', itemData.seller_id)
    .eq('verification_status', 'approved')
    .single();

  if (!kyc) {
    return new Response(
      JSON.stringify({ error: 'Marketplace\'da sotish uchun KYC tasdiqlanishi kerak' }),
      { status: 403, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  // Item'ni saqlash
  const { data: item, error } = await supabase
    .from('premium_marketplace')
    .insert({
      seller_id: itemData.seller_id,
      title: itemData.title,
      description: itemData.description,
      item_type: itemData.item_type,
      price: itemData.price,
      currency: itemData.currency || 'USD',
      performance_data: itemData.performance_data,
      features: itemData.features,
      is_active: true,
      total_sales: 0,
      views_count: 0,
    })
    .select()
    .single();

  if (error) throw error;

  return new Response(
    JSON.stringify({
      success: true,
      item,
      message: 'Item muvaffaqiyatli e\'lon qilindi!',
    }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  );
}

async function purchaseItem(req: Request, supabase: any) {
  const { item_id, buyer_id, payment_method } = await req.json();

  if (!item_id || !buyer_id) {
    return new Response(
      JSON.stringify({ error: 'item_id va buyer_id majburiy' }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  // Item ma'lumotlarini olish
  const { data: item, error: itemError } = await supabase
    .from('premium_marketplace')
    .select('*')
    .eq('id', item_id)
    .single();

  if (itemError) throw itemError;

  // Oldin sotib olinganligini tekshirish
  const { data: existing } = await supabase
    .from('marketplace_purchases')
    .select('id')
    .eq('item_id', item_id)
    .eq('buyer_id', buyer_id)
    .single();

  if (existing) {
    return new Response(
      JSON.stringify({ error: 'Siz bu item\'ni allaqachon sotib olgansiz' }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  // Foydalanuvchi balansini tekshirish
  const { data: balance } = await supabase
    .from('user_balances')
    .select('balance')
    .eq('user_id', buyer_id)
    .eq('currency', item.currency)
    .single();

  if (!balance || balance.balance < item.price) {
    return new Response(
      JSON.stringify({ error: 'Yetarli mablag\' yo\'q' }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  // Transaction yaratish
  const commission = item.price * 0.05; // 5% komissiya
  const sellerAmount = item.price - commission;

  // Xaridni saqlash
  const { data: purchase, error: purchaseError } = await supabase
    .from('marketplace_purchases')
    .insert({
      item_id,
      buyer_id,
      seller_id: item.seller_id,
      price: item.price,
      currency: item.currency,
      commission,
      seller_amount: sellerAmount,
      payment_method,
      status: 'completed',
    })
    .select()
    .single();

  if (purchaseError) throw purchaseError;

  // Balanslarni yangilash
  await supabase
    .from('user_balances')
    .update({ balance: balance.balance - item.price })
    .eq('user_id', buyer_id)
    .eq('currency', item.currency);

  // Sotuvchiga pul qo'shish
  const { data: sellerBalance } = await supabase
    .from('user_balances')
    .select('balance')
    .eq('user_id', item.seller_id)
    .eq('currency', item.currency)
    .single();

  if (sellerBalance) {
    await supabase
      .from('user_balances')
      .update({ balance: sellerBalance.balance + sellerAmount })
      .eq('user_id', item.seller_id)
      .eq('currency', item.currency);
  }

  // Item statistikasini yangilash
  await supabase
    .from('premium_marketplace')
    .update({ total_sales: (item.total_sales || 0) + 1 })
    .eq('id', item_id);

  return new Response(
    JSON.stringify({
      success: true,
      purchase,
      message: 'Xarid muvaffaqiyatli amalga oshirildi!',
    }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  );
}

async function getMyItems(req: Request, supabase: any) {
  const { user_id } = await req.json();

  const { data, error } = await supabase
    .from('premium_marketplace')
    .select('*')
    .eq('seller_id', user_id)
    .order('created_at', { ascending: false });

  if (error) throw error;

  return new Response(
    JSON.stringify({ items: data }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  );
}

async function getMyPurchases(req: Request, supabase: any) {
  const { user_id } = await req.json();

  const { data, error } = await supabase
    .from('marketplace_purchases')
    .select('*, item:premium_marketplace(*), seller:users!seller_id(username)')
    .eq('buyer_id', user_id)
    .order('created_at', { ascending: false });

  if (error) throw error;

  return new Response(
    JSON.stringify({ purchases: data }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  );
}

async function getTopSellers(req: Request, supabase: any) {
  const { data, error } = await supabase
    .from('users')
    .select(`
      id,
      username,
      avatar_url,
      items:premium_marketplace(count),
      sales:marketplace_purchases!seller_id(count)
    `)
    .order('sales(count)', { ascending: false })
    .limit(10);

  if (error) throw error;

  return new Response(
    JSON.stringify({ sellers: data }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  );
}

async function leaveReview(req: Request, supabase: any) {
  const { item_id, reviewer_id, rating, comment } = await req.json();

  if (!item_id || !reviewer_id || !rating) {
    return new Response(
      JSON.stringify({ error: 'item_id, reviewer_id va rating majburiy' }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  // Xaridni tekshirish
  const { data: purchase } = await supabase
    .from('marketplace_purchases')
    .select('id')
    .eq('item_id', item_id)
    .eq('buyer_id', reviewer_id)
    .single();

  if (!purchase) {
    return new Response(
      JSON.stringify({ error: 'Faqat sotib olgan foydalanuvchilar sharh qoldirishi mumkin' }),
      { status: 403, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  // Review saqlash
  const { data: review, error } = await supabase
    .from('marketplace_reviews')
    .insert({
      item_id,
      reviewer_id,
      rating,
      comment,
    })
    .select()
    .single();

  if (error) throw error;

  // Item reytingini yangilash
  const { data: allReviews } = await supabase
    .from('marketplace_reviews')
    .select('rating')
    .eq('item_id', item_id);

  if (allReviews && allReviews.length > 0) {
    const avgRating = allReviews.reduce((sum: number, r: any) => sum + r.rating, 0) / allReviews.length;
    
    await supabase
      .from('premium_marketplace')
      .update({
        average_rating: avgRating,
        reviews_count: allReviews.length,
      })
      .eq('id', item_id);
  }

  return new Response(
    JSON.stringify({
      success: true,
      review,
      message: 'Sharh qoldirildi!',
    }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  );
}
