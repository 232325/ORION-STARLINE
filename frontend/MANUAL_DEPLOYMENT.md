# AI Trading Platform - Manual Deployment Guide

## Supabase Token Muammosi

Hozirda Supabase auth token'i eskicha va avtomatik deployment amalga oshirilmayapti. Quyida qo'lda sozlash bo'yicha to'liq ko'rsatma berilgan.

## Deployment Qadamlari

### 1. Supabase Database Setup

1. Supabase Dashboard'ga kiring: https://supabase.com/dashboard
2. Proyektingizni tanlang: `bgrmoxpwfbuqszmmeodo`
3. SQL Editor'ga o'ting (chap menyu)
4. `supabase-setup.sql` faylini oching va to'liq SQL ni execute qiling

SQL fayl joylashuvi: `/workspace/ai-trading-admin/supabase-setup.sql`

### 2. Edge Functions Deploy

Edge Functions joylashuvi:
- `/workspace/ai-trading-admin/supabase/functions/close-position/index.ts`
- `/workspace/ai-trading-admin/supabase/functions/manage-strategy/index.ts`

Deploy qilish uchun:

```bash
cd /workspace/ai-trading-admin
supabase functions deploy close-position
supabase functions deploy manage-strategy
```

Yoki Supabase Dashboard orqali:
1. Edge Functions bo'limiga o'ting
2. "Create Function" tugmasini bosing
3. Function nomini kiriting: `close-position`
4. Function kodini `/workspace/ai-trading-admin/supabase/functions/close-position/index.ts` dan ko'chiring
5. Deploy qiling
6. Xuddi shunday `manage-strategy` uchun takrorlang

### 3. Environment Variables

Edge Functions uchun quyidagi environment variables kerak:

- `SUPABASE_URL`: https://bgrmoxpwfbuqszmmeodo.supabase.co
- `SUPABASE_SERVICE_ROLE_KEY`: (Supabase Dashboard > Settings > API dan oling)

Bu variables'larni Supabase Dashboard'da sozlang:
1. Edge Functions > Settings
2. Secrets qo'shing

### 4. Frontend Deployment

Frontend allaqachon build qilingan va tayyor:
- Joylashuvi: `/workspace/ai-trading-admin/dist/`

Frontend'ni deploy qilish uchun quyidagi buyruqni ishga tushiring:

```bash
cd /workspace
# Frontend'ni deploy qilish
```

Yoki deploy scriptni yarating.

## Test Foydalanuvchilari

Tizimni test qilish uchun:
1. Frontend'ga kiring
2. Sign up orqali yangi akkaunt yarating
3. Dashboard'ni tekshiring

Har bir yangi foydalanuvchi avtomatik ravishda:
- Profile yaratiladi (boshlang'ich balans: $10,000)
- Database'da saqlanadi

## Kerakli Ma'lumotlar

- Supabase URL: https://bgrmoxpwfbuqszmmeodo.supabase.co
- Supabase Anon Key: (supabase.ts faylida)
- Project ID: bgrmoxpwfbuqszmmeodo

## Troubleshooting

### Database Xatoliklari
- Barcha jadvallar to'g'ri yaratilganligini tekshiring
- RLS policies faol ekanligini tasdiqlang

### Edge Functions Xatoliklari
- Function logs'larni tekshiring
- Environment variables to'g'ri sozlanganligini tekshiring

### Frontend Xatoliklari
- Browser console'ni tekshiring
- Network tab'da API request'larni kuzating

## Qo'shimcha Ma'lumot

Backend API kodi (FastAPI): `/workspace/code/api/`
Bu Python backend hozirda ishlatilmayapti, chunki Supabase Edge Functions bilan almashtirilgan.

Barcha kerakli feature'lar Supabase orqali amalga oshiriladi:
- Database: PostgreSQL (Supabase)
- Authentication: Supabase Auth
- API: Edge Functions (Deno)
- Real-time: Supabase Realtime
- Storage: Supabase Storage

## Support

Savollar bo'lsa yoki qo'shimcha yordam kerak bo'lsa, xabar bering.
