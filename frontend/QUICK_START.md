# AI Trading Platform - Tezkor Qo'llanma

## Platform URL
https://096l9ute938z.space.minimax.io

## Tez Boshlash (15 daqiqa)

### 1. Database (5 daqiqa)
```
1. https://supabase.com/dashboard/project/bgrmoxpwfbuqszmmeodo
2. SQL Editor > New Query
3. Copy-paste supabase-setup.sql fayl kodi
4. Run qiling
```

### 2. Edge Functions (10 daqiqa)
```
1. Edge Functions > Create Function > close-position
2. Copy-paste supabase/functions/close-position/index.ts
3. Deploy

4. Edge Functions > Create Function > manage-strategy  
5. Copy-paste supabase/functions/manage-strategy/index.ts
6. Deploy

7. Edge Functions > Settings > Secrets:
   - SUPABASE_URL: https://bgrmoxpwfbuqszmmeodo.supabase.co
   - SUPABASE_SERVICE_ROLE_KEY: (Settings > API dan oling)
```

### 3. Test
```
1. https://096l9ute938z.space.minimax.io
2. Sign Up
3. Dashboard'ni ko'ring
```

## Batafsil
DEPLOYMENT_REPORT.md faylini o'qing
