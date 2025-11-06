# API Integration Guide - Mock to Real Conversion

## Overview
Ushbu qo'llanma barcha mock ma'lumotlarni haqiqiy API integratsiyalariga almashtirish uchun zarur.

---

## 1. MARKET DATA INTEGRATION

### CoinGecko API (Free Tier - 50 calls/min)
**Use Case:** Kripto narxlari, tarixiy ma'lumotlar

```typescript
// market-predictions/index.ts - fetchHistoricalData
async function fetchHistoricalData(symbol: string) {
  const apiKey = Deno.env.get('COINGECKO_API_KEY');
  const coinId = symbolToCoinId(symbol); // BTC -> bitcoin
  
  const response = await fetch(
    `https://api.coingecko.com/api/v3/coins/${coinId}/market_chart?vs_currency=usd&days=30&interval=daily`,
    { headers: { 'x-cg-api-key': apiKey } }
  );
  
  const data = await response.json();
  return data.prices.map((item: any) => ({
    timestamp: item[0],
    price: item[1],
    // Calculate OHLC from prices
  }));
}

// Helper function
function symbolToCoinId(symbol: string): string {
  const map: any = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'BNB': 'binancecoin',
    'SOL': 'solana',
    'ADA': 'cardano',
  };
  return map[symbol] || 'bitcoin';
}
```

### Binance API (No API key for public endpoints)
**Use Case:** Real-time narxlar, trading data

```typescript
// risk-analytics/index.ts
async function fetchCurrentPrice(symbol: string): Promise<number> {
  const binanceSymbol = `${symbol}USDT`;
  const response = await fetch(
    `https://api.binance.com/api/v3/ticker/price?symbol=${binanceSymbol}`
  );
  const data = await response.json();
  return parseFloat(data.price);
}
```

---

## 2. NEWS INTEGRATION

### NewsAPI.org (Free: 100 calls/day)
**Use Case:** Kripto yangiliklari

```typescript
// news-trading-bot/index.ts - fetchNews
async function fetchNews(symbol: string) {
  const apiKey = Deno.env.get('NEWS_API_KEY');
  const query = `${symbol} cryptocurrency OR crypto`;
  
  const response = await fetch(
    `https://newsapi.org/v2/everything?q=${encodeURIComponent(query)}&sortBy=publishedAt&language=en&apiKey=${apiKey}`
  );
  
  const data = await response.json();
  
  return data.articles.map((article: any) => ({
    title: article.title,
    content: article.description,
    source: article.source.name,
    url: article.url,
    published_at: article.publishedAt,
  }));
}
```

### Alternative: CryptoPanic API (Free tier available)
**Kripto-specific yangiliklar**

```typescript
async function fetchCryptoNews() {
  const apiKey = Deno.env.get('CRYPTOPANIC_API_KEY');
  const response = await fetch(
    `https://cryptopanic.com/api/v1/posts/?auth_token=${apiKey}&public=true&kind=news`
  );
  return await response.json();
}
```

---

## 3. SENTIMENT ANALYSIS

### Twitter API v2 (Essential: $100/month)
**Use Case:** Social sentiment tahlili

```typescript
// social-sentiment-analysis/index.ts
async function fetchTwitterSentiment(symbol: string) {
  const bearerToken = Deno.env.get('TWITTER_BEARER_TOKEN');
  const query = `${symbol} (cryptocurrency OR crypto) -is:retweet lang:en`;
  
  const response = await fetch(
    `https://api.twitter.com/2/tweets/search/recent?query=${encodeURIComponent(query)}&max_results=100`,
    {
      headers: {
        'Authorization': `Bearer ${bearerToken}`,
      },
    }
  );
  
  const data = await response.json();
  
  // Sentiment tahlili (external API yoki local ML model)
  const sentimentResults = await analyzeTweetsSentiment(data.data);
  
  return sentimentResults;
}
```

### Alternative: Reddit API (Free with OAuth)
```typescript
async function fetchRedditSentiment(symbol: string) {
  const accessToken = Deno.env.get('REDDIT_ACCESS_TOKEN');
  const subreddit = 'cryptocurrency';
  
  const response = await fetch(
    `https://oauth.reddit.com/r/${subreddit}/search?q=${symbol}&limit=100&sort=new`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'User-Agent': 'AITradingBot/1.0',
      },
    }
  );
  
  const data = await response.json();
  return data.data.children.map((post: any) => post.data);
}
```

### Sentiment Analysis Service
**TextRazor, MeaningCloud, or local model**

```typescript
async function analyzeSentiment(text: string): Promise<number> {
  // Option 1: TextRazor API
  const apiKey = Deno.env.get('TEXTRAZOR_API_KEY');
  const response = await fetch('https://api.textrazor.com', {
    method: 'POST',
    headers: {
      'x-textrazor-key': apiKey,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: `text=${encodeURIComponent(text)}&extractors=entities,sentiment`,
  });
  
  const data = await response.json();
  return data.response.sentiment; // -1 to 1
  
  // Option 2: Local sentiment library (simpler but less accurate)
  // return simpleSentimentAnalysis(text);
}
```

---

## 4. KYC/AML INTEGRATION

### Onfido API (Paid service)
**Document verification, face matching**

```typescript
// kyc-aml-verification/index.ts
async function verifyDocument(submission: KYCSubmission) {
  const apiKey = Deno.env.get('ONFIDO_API_KEY');
  
  // 1. Create applicant
  const applicant = await fetch('https://api.onfido.com/v3/applicants', {
    method: 'POST',
    headers: {
      'Authorization': `Token token=${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      first_name: submission.full_name.split(' ')[0],
      last_name: submission.full_name.split(' ')[1],
    }),
  });
  
  const applicantData = await applicant.json();
  
  // 2. Upload document
  const formData = new FormData();
  formData.append('applicant_id', applicantData.id);
  formData.append('type', submission.document_type);
  formData.append('file', submission.document_front);
  
  const uploadDoc = await fetch('https://api.onfido.com/v3/documents', {
    method: 'POST',
    headers: {
      'Authorization': `Token token=${apiKey}`,
    },
    body: formData,
  });
  
  // 3. Create check
  const check = await fetch('https://api.onfido.com/v3/checks', {
    method: 'POST',
    headers: {
      'Authorization': `Token token=${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      applicant_id: applicantData.id,
      report_names: ['document', 'facial_similarity_photo'],
    }),
  });
  
  return await check.json();
}
```

### ComplyAdvantage API (AML screening)
```typescript
async function performAMLScreening(fullName: string, dateOfBirth: string) {
  const apiKey = Deno.env.get('COMPLY_ADVANTAGE_API_KEY');
  
  const response = await fetch('https://api.complyadvantage.com/searches', {
    method: 'POST',
    headers: {
      'Authorization': `Token ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      search_term: fullName,
      fuzziness: 0.8,
      filters: {
        birth_year: new Date(dateOfBirth).getFullYear(),
      },
    }),
  });
  
  const data = await response.json();
  return {
    sanctionsMatch: data.total_hits > 0,
    pepMatch: data.content.data.some((hit: any) => hit.types.includes('pep')),
    riskLevel: data.total_hits > 0 ? 'high' : 'low',
  };
}
```

---

## 5. CRYPTO PAYMENT INTEGRATION

### CoinPayments API
```typescript
// crypto-payment-gateway/index.ts
async function createPayment(request: PaymentRequest) {
  const apiKey = Deno.env.get('COINPAYMENTS_API_KEY');
  const apiSecret = Deno.env.get('COINPAYMENTS_API_SECRET');
  
  const params = {
    version: 1,
    cmd: 'create_transaction',
    amount: request.amount,
    currency1: request.currency,
    currency2: request.currency,
    buyer_email: request.user_email,
  };
  
  // Sign request (HMAC)
  const hmac = await crypto.subtle.sign(
    'HMAC',
    await crypto.subtle.importKey(
      'raw',
      new TextEncoder().encode(apiSecret),
      { name: 'HMAC', hash: 'SHA-512' },
      false,
      ['sign']
    ),
    new TextEncoder().encode(new URLSearchParams(params).toString())
  );
  
  const response = await fetch('https://www.coinpayments.net/api.php', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'HMAC': Buffer.from(hmac).toString('hex'),
    },
    body: new URLSearchParams(params),
  });
  
  return await response.json();
}
```

---

## 6. GPT INTEGRATION

### OpenAI API
```typescript
// gpt-trading-assistant/index.ts
async function generateGPTResponse(message: string, conversationHistory: any[]) {
  const apiKey = Deno.env.get('OPENAI_API_KEY');
  
  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'gpt-4',
      messages: [
        {
          role: 'system',
          content: 'You are a professional cryptocurrency trading advisor. Provide accurate, helpful advice about trading strategies, market analysis, and risk management.',
        },
        ...conversationHistory,
        { role: 'user', content: message },
      ],
      temperature: 0.7,
      max_tokens: 500,
    }),
  });
  
  const data = await response.json();
  return data.choices[0].message.content;
}
```

---

## ENVIRONMENT VARIABLES TO ADD

```bash
# Market Data
COINGECKO_API_KEY=your_key_here

# News
NEWS_API_KEY=your_key_here
CRYPTOPANIC_API_KEY=your_key_here

# Social Media
TWITTER_BEARER_TOKEN=your_token_here
REDDIT_ACCESS_TOKEN=your_token_here

# Sentiment Analysis
TEXTRAZOR_API_KEY=your_key_here

# KYC/AML
ONFIDO_API_KEY=your_key_here
COMPLY_ADVANTAGE_API_KEY=your_key_here

# Payments
COINPAYMENTS_API_KEY=your_key_here
COINPAYMENTS_API_SECRET=your_secret_here

# AI
OPENAI_API_KEY=your_key_here
```

---

## IMPLEMENTATION PRIORITY

### Phase 1 (Critical):
1. ✅ Market Data (CoinGecko, Binance) - bepul
2. ✅ News (NewsAPI) - 100 calls/day bepul
3. ✅ GPT (OpenAI) - zarur

### Phase 2 (Important):
4. Social Sentiment (Twitter, Reddit)
5. Payment Gateway (CoinPayments)

### Phase 3 (Can wait):
6. KYC/AML (Onfido, ComplyAdvantage) - qimmat, demo rejimda qoldirish mumkin

---

## TESTING STRATEGY

1. **Mock Mode** (development)
2. **Sandbox Mode** (test API keys)
3. **Production Mode** (real API keys)

Har bir integration uchun environment variable orqali mode'ni o'zgartirish:
```typescript
const USE_MOCK_DATA = Deno.env.get('USE_MOCK_DATA') === 'true';

if (USE_MOCK_DATA) {
  return mockData;
} else {
  return await fetchRealData();
}
```
