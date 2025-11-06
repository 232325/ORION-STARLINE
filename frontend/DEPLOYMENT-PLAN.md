# Edge Functions Deployment Plan

## MAVJUD FUNCTIONLAR (18 ta):

### Yangi modullar (12 ta):
1. ✅ advanced-security - Kengaytirilgan xavfsizlik
2. ✅ audit-logging - Audit loglar
3. ✅ auto-strategy-generator - Avtomatik strategiya
4. ✅ crypto-payment-gateway - Kripto to'lovlar
5. ✅ gpt-trading-assistant - GPT chat yordamchisi
6. ✅ kyc-aml-verification - KYC/AML tekshiruvi
7. ✅ market-predictions - Bozor bashoratlari
8. ✅ news-trading-bot - Yangiliklar trading
9. ✅ premium-marketplace - Premium bozor
10. ✅ risk-analytics - Risk tahlili
11. ✅ social-sentiment-analysis - Social sentiment
12. ✅ voice-commands - Ovozli buyruqlar

### Avvalgi modullar (6 ta):
13. ✅ close-position - Pozitsiyani yopish
14. ✅ copy-trading-leaderboard - Copy trading
15. ✅ manage-strategy - Strategiya boshqaruvi
16. ✅ referral-system - Referral tizimi
17. ✅ subscription-manage - Obuna boshqaruvi
18. ✅ two-factor-auth - 2FA

## DEPLOYMENT BUYRUQI:

Token yangilangandan keyin quyidagi buyruqni bajarish:

```typescript
await batch_deploy_edge_functions({
  functions: [
    // Yangi modullar
    {
      slug: "advanced-security",
      file_path: "/workspace/ai-trading-admin/supabase/functions/advanced-security/index.ts",
      type: "normal",
      description: "Kengaytirilgan xavfsizlik - IP whitelist, device management, security score"
    },
    {
      slug: "audit-logging",
      file_path: "/workspace/ai-trading-admin/supabase/functions/audit-logging/index.ts",
      type: "normal",
      description: "Audit loglar - faoliyat kuzatuvi va xavf tahlili"
    },
    {
      slug: "auto-strategy-generator",
      file_path: "/workspace/ai-trading-admin/supabase/functions/auto-strategy-generator/index.ts",
      type: "normal",
      description: "AI asosida avtomatik trading strategiya yaratuvchi"
    },
    {
      slug: "crypto-payment-gateway",
      file_path: "/workspace/ai-trading-admin/supabase/functions/crypto-payment-gateway/index.ts",
      type: "normal",
      description: "Kripto to'lovlar gateway - BTC, ETH, USDT"
    },
    {
      slug: "gpt-trading-assistant",
      file_path: "/workspace/ai-trading-admin/supabase/functions/gpt-trading-assistant/index.ts",
      type: "normal",
      description: "GPT-4 yordamida trading maslahat beruvchi chat bot"
    },
    {
      slug: "kyc-aml-verification",
      file_path: "/workspace/ai-trading-admin/supabase/functions/kyc-aml-verification/index.ts",
      type: "normal",
      description: "KYC verifikatsiya va AML screening"
    },
    {
      slug: "market-predictions",
      file_path: "/workspace/ai-trading-admin/supabase/functions/market-predictions/index.ts",
      type: "normal",
      description: "AI asosida bozor bashoratlari va narx taxminlari"
    },
    {
      slug: "news-trading-bot",
      file_path: "/workspace/ai-trading-admin/supabase/functions/news-trading-bot/index.ts",
      type: "normal",
      description: "Yangiliklar asosida avtomatik trading signallari"
    },
    {
      slug: "premium-marketplace",
      file_path: "/workspace/ai-trading-admin/supabase/functions/premium-marketplace/index.ts",
      type: "normal",
      description: "Premium strategiya va signal bozori"
    },
    {
      slug: "risk-analytics",
      file_path: "/workspace/ai-trading-admin/supabase/functions/risk-analytics/index.ts",
      type: "normal",
      description: "Portfolio xavf tahlili - VaR, Sharpe ratio, drawdown"
    },
    {
      slug: "social-sentiment-analysis",
      file_path: "/workspace/ai-trading-admin/supabase/functions/social-sentiment-analysis/index.ts",
      type: "normal",
      description: "Twitter va Reddit sentiment tahlili"
    },
    {
      slug: "voice-commands",
      file_path: "/workspace/ai-trading-admin/supabase/functions/voice-commands/index.ts",
      type: "normal",
      description: "Ovozli buyruqlar - trading operations"
    }
  ]
});
```

## DEPLOYMENT KETMA-KETLIGI:

1. ✅ Supabase tokenini yangilash
2. ✅ Database migration'ni apply qilish
3. ✅ 12 ta yangi Edge Function'ni deploy qilish
4. ✅ Testing - har bir function'ni test qilish
5. ✅ Frontend bilan integratsiyani test qilish

## TESTING PLAN (Har bir function):

### 1. news-trading-bot
```bash
curl -X POST https://[project-ref].supabase.co/functions/v1/news-trading-bot \
  -H "Authorization: Bearer [anon-key]"
```
Expected: Yangiliklar va signallar ro'yxati

### 2. social-sentiment-analysis
```bash
curl -X GET "https://[project-ref].supabase.co/functions/v1/social-sentiment-analysis"
```
Expected: Sentiment data

### 3. risk-analytics
```bash
curl -X POST https://[project-ref].supabase.co/functions/v1/risk-analytics \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user-id"}'
```
Expected: Risk tahlili

... (har bir function uchun test)

## ENVIRONMENT VARIABLES KERAK:

Hozirda:
- ✅ SUPABASE_URL
- ✅ SUPABASE_SERVICE_ROLE_KEY

Keyinchalik (Real API integration uchun):
- COINGECKO_API_KEY
- NEWS_API_KEY
- OPENAI_API_KEY
- TWITTER_BEARER_TOKEN
- REDDIT_ACCESS_TOKEN
- ... (API-INTEGRATION-GUIDE.md ga qarang)

## HOLAT:

🟡 **WAITING FOR SUPABASE TOKEN REFRESH**

Token yangilangandan keyin avtomatik ravishda deployment boshlaydi.
