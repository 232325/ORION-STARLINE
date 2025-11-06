-- Migration: add_missing_columns_and_tables
-- Created at: 1762180703

-- Add role column to profiles if not exists
DO $$ 
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'profiles' AND column_name = 'role') THEN
    ALTER TABLE public.profiles ADD COLUMN role text DEFAULT 'user';
  END IF;
END $$;

-- Add missing columns to positions
DO $$ 
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'positions' AND column_name = 'leverage') THEN
    ALTER TABLE public.positions ADD COLUMN leverage numeric DEFAULT 1;
  END IF;
  
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'positions' AND column_name = 'side') THEN
    ALTER TABLE public.positions ADD COLUMN side text;
  END IF;
  
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'positions' AND column_name = 'status') THEN
    ALTER TABLE public.positions ADD COLUMN status text DEFAULT 'open';
  END IF;
  
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'positions' AND column_name = 'strategy') THEN
    ALTER TABLE public.positions ADD COLUMN strategy text;
  END IF;
  
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'positions' AND column_name = 'closed_at') THEN
    ALTER TABLE public.positions ADD COLUMN closed_at timestamp with time zone;
  END IF;
END $$;

-- Create system_logs table if not exists
CREATE TABLE IF NOT EXISTS public.system_logs (
  id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
  level text NOT NULL,
  message text NOT NULL,
  details jsonb,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now())
);

-- Create performance_history table if not exists
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

-- Enable RLS on new tables
ALTER TABLE public.system_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.performance_history ENABLE ROW LEVEL SECURITY;

-- Drop and recreate policies for system_logs
DROP POLICY IF EXISTS "Admins can view all logs" ON public.system_logs;
DROP POLICY IF EXISTS "System can insert logs" ON public.system_logs;

CREATE POLICY "Admins can view all logs" ON public.system_logs 
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM public.profiles WHERE user_id = auth.uid() AND role = 'admin')
  );

CREATE POLICY "System can insert logs" ON public.system_logs 
  FOR INSERT WITH CHECK (auth.role() IN ('anon', 'service_role'));

-- Drop and recreate policies for performance_history
DROP POLICY IF EXISTS "Users can view own performance" ON public.performance_history;
DROP POLICY IF EXISTS "Users can insert own performance" ON public.performance_history;

CREATE POLICY "Users can view own performance" ON public.performance_history 
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own performance" ON public.performance_history 
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Drop and recreate policies for alerts
DROP POLICY IF EXISTS "System can insert alerts" ON public.alerts;

CREATE POLICY "System can insert alerts" ON public.alerts 
  FOR INSERT WITH CHECK (auth.role() IN ('anon', 'service_role'));;