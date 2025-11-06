-- Migration: create_trading_tables
-- Created at: 1762180664

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.user_profiles (
  id uuid REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
  email text NOT NULL,
  full_name text,
  role text DEFAULT 'user',
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
  updated_at timestamp with time zone DEFAULT timezone('utc'::text, now())
);

-- Trading positions
CREATE TABLE IF NOT EXISTS public.positions (
  id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id uuid NOT NULL,
  symbol text NOT NULL,
  side text NOT NULL,
  size numeric NOT NULL,
  entry_price numeric NOT NULL,
  current_price numeric,
  leverage numeric DEFAULT 1,
  unrealized_pnl numeric DEFAULT 0,
  status text DEFAULT 'open',
  entry_time timestamp with time zone DEFAULT timezone('utc'::text, now()),
  exit_time timestamp with time zone,
  stop_loss numeric,
  take_profit numeric,
  strategy text
);

-- Trading strategies configuration
CREATE TABLE IF NOT EXISTS public.strategies (
  id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id uuid NOT NULL,
  name text NOT NULL,
  type text NOT NULL,
  config jsonb NOT NULL,
  status text DEFAULT 'stopped',
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
  updated_at timestamp with time zone DEFAULT timezone('utc'::text, now())
);

-- System logs
CREATE TABLE IF NOT EXISTS public.system_logs (
  id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
  level text NOT NULL,
  message text NOT NULL,
  details jsonb,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now())
);

-- Alerts/Notifications
CREATE TABLE IF NOT EXISTS public.alerts (
  id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id uuid NOT NULL,
  type text NOT NULL,
  severity text NOT NULL,
  message text NOT NULL,
  details jsonb,
  read boolean DEFAULT false,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now())
);

-- Performance metrics history
CREATE TABLE IF NOT EXISTS public.performance_history (
  id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id uuid NOT NULL,
  total_balance numeric NOT NULL,
  total_pnl numeric NOT NULL,
  win_rate numeric,
  sharpe_ratio numeric,
  max_drawdown numeric,
  recorded_at timestamp with time zone DEFAULT timezone('utc'::text, now())
);

-- Enable RLS
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.system_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.performance_history ENABLE ROW LEVEL SECURITY;

-- RLS Policies for user_profiles
CREATE POLICY "Users can view own profile" ON public.user_profiles 
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.user_profiles 
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON public.user_profiles 
  FOR INSERT WITH CHECK (auth.uid() = id);

-- RLS Policies for positions
CREATE POLICY "Users can view own positions" ON public.positions 
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own positions" ON public.positions 
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own positions" ON public.positions 
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all positions" ON public.positions 
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM public.user_profiles WHERE id = auth.uid() AND role = 'admin')
  );

-- RLS Policies for strategies
CREATE POLICY "Users can view own strategies" ON public.strategies 
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own strategies" ON public.strategies 
  FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all strategies" ON public.strategies 
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM public.user_profiles WHERE id = auth.uid() AND role = 'admin')
  );

-- RLS Policies for system_logs
CREATE POLICY "Admins can view all logs" ON public.system_logs 
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM public.user_profiles WHERE id = auth.uid() AND role = 'admin')
  );

CREATE POLICY "System can insert logs" ON public.system_logs 
  FOR INSERT WITH CHECK (auth.role() IN ('anon', 'service_role'));

-- RLS Policies for alerts
CREATE POLICY "Users can view own alerts" ON public.alerts 
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own alerts" ON public.alerts 
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "System can insert alerts" ON public.alerts 
  FOR INSERT WITH CHECK (auth.role() IN ('anon', 'service_role'));

-- RLS Policies for performance_history
CREATE POLICY "Users can view own performance" ON public.performance_history 
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own performance" ON public.performance_history 
  FOR INSERT WITH CHECK (auth.uid() = user_id);;