-- =====================================================
-- AI TRADING PLATFORM - ADVANCED FEATURES DATABASE SCHEMA
-- =====================================================
-- Version: 2.0
-- Date: 2025-11-04
-- Modules: 18+ Advanced Features
-- =====================================================

-- =====================================================
-- COPY TRADING SYSTEM
-- =====================================================

-- Professional traders leaderboard
CREATE TABLE IF NOT EXISTS copy_traders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    bio TEXT,
    avatar_url TEXT,
    total_followers INTEGER DEFAULT 0,
    total_profit DECIMAL(20, 2) DEFAULT 0,
    win_rate DECIMAL(5, 2) DEFAULT 0,
    sharpe_ratio DECIMAL(10, 4) DEFAULT 0,
    max_drawdown DECIMAL(5, 2) DEFAULT 0,
    avg_trade_duration_hours INTEGER DEFAULT 0,
    total_trades INTEGER DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    commission_rate DECIMAL(5, 2) DEFAULT 10.00,
    min_copy_amount DECIMAL(20, 2) DEFAULT 100.00,
    risk_score INTEGER DEFAULT 5,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Copy trading followers
CREATE TABLE IF NOT EXISTS copy_followers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    trader_id UUID NOT NULL,
    allocation_amount DECIMAL(20, 2) NOT NULL,
    max_position_size DECIMAL(20, 2),
    risk_multiplier DECIMAL(5, 2) DEFAULT 1.00,
    stop_loss_percentage DECIMAL(5, 2),
    take_profit_percentage DECIMAL(5, 2),
    is_active BOOLEAN DEFAULT TRUE,
    total_profit DECIMAL(20, 2) DEFAULT 0,
    total_commission_paid DECIMAL(20, 2) DEFAULT 0,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    stopped_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Copy positions tracking
CREATE TABLE IF NOT EXISTS copy_positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    follower_id UUID NOT NULL,
    trader_position_id UUID,
    symbol VARCHAR(50) NOT NULL,
    side VARCHAR(20) NOT NULL,
    entry_price DECIMAL(20, 8) NOT NULL,
    current_price DECIMAL(20, 8),
    size DECIMAL(20, 8) NOT NULL,
    leverage INTEGER DEFAULT 1,
    unrealized_pnl DECIMAL(20, 2) DEFAULT 0,
    realized_pnl DECIMAL(20, 2) DEFAULT 0,
    commission_amount DECIMAL(20, 2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'open',
    opened_at TIMESTAMPTZ DEFAULT NOW(),
    closed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Copy trading performance history
CREATE TABLE IF NOT EXISTS copy_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trader_id UUID NOT NULL,
    date DATE NOT NULL,
    profit_loss DECIMAL(20, 2) DEFAULT 0,
    trades_count INTEGER DEFAULT 0,
    win_count INTEGER DEFAULT 0,
    followers_count INTEGER DEFAULT 0,
    commission_earned DECIMAL(20, 2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(trader_id, date)
);

-- =====================================================
-- SUBSCRIPTION & PAYMENT SYSTEM
-- =====================================================

-- Subscription plans
CREATE TABLE IF NOT EXISTS subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    price_monthly DECIMAL(10, 2) NOT NULL,
    price_yearly DECIMAL(10, 2),
    features JSONB DEFAULT '[]',
    limits JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User subscriptions
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    plan_id UUID NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    billing_cycle VARCHAR(20) DEFAULT 'monthly',
    current_period_start TIMESTAMPTZ NOT NULL,
    current_period_end TIMESTAMPTZ NOT NULL,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    stripe_subscription_id VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Payment transactions
CREATE TABLE IF NOT EXISTS payment_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    subscription_id UUID,
    amount DECIMAL(20, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    payment_method VARCHAR(50),
    payment_provider VARCHAR(50),
    transaction_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending',
    external_transaction_id VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Crypto payments
CREATE TABLE IF NOT EXISTS crypto_payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    cryptocurrency VARCHAR(20) NOT NULL,
    amount DECIMAL(30, 18) NOT NULL,
    usd_value DECIMAL(20, 2),
    wallet_address VARCHAR(255) NOT NULL,
    transaction_hash VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    confirmation_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    confirmed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- SECURITY & COMPLIANCE
-- =====================================================

-- Two-Factor Authentication
CREATE TABLE IF NOT EXISTS two_factor_auth (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    secret VARCHAR(255) NOT NULL,
    method VARCHAR(20) DEFAULT 'totp',
    is_enabled BOOLEAN DEFAULT FALSE,
    backup_codes JSONB DEFAULT '[]',
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- KYC Documents
CREATE TABLE IF NOT EXISTS kyc_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    document_number VARCHAR(100),
    document_file_url TEXT,
    selfie_file_url TEXT,
    verification_status VARCHAR(20) DEFAULT 'pending',
    verified_by VARCHAR(100),
    verified_at TIMESTAMPTZ,
    rejection_reason TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    changes JSONB DEFAULT '{}',
    severity VARCHAR(20) DEFAULT 'info',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Security Events
CREATE TABLE IF NOT EXISTS security_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    event_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium',
    ip_address INET,
    device_fingerprint VARCHAR(255),
    location_data JSONB,
    is_blocked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- IP Whitelist/Blacklist
CREATE TABLE IF NOT EXISTS ip_access_control (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    ip_address INET NOT NULL,
    access_type VARCHAR(20) DEFAULT 'whitelist',
    reason TEXT,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- REFERRAL SYSTEM
-- =====================================================

-- Referral Codes
CREATE TABLE IF NOT EXISTS referral_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    commission_rate DECIMAL(5, 2) DEFAULT 10.00,
    max_uses INTEGER,
    current_uses INTEGER DEFAULT 0,
    total_earnings DECIMAL(20, 2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Referrals
CREATE TABLE IF NOT EXISTS referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referrer_id UUID NOT NULL,
    referred_user_id UUID NOT NULL,
    referral_code VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    total_commission DECIMAL(20, 2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(referred_user_id)
);

-- Commission Payments
CREATE TABLE IF NOT EXISTS commission_payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    referral_id UUID,
    amount DECIMAL(20, 2) NOT NULL,
    source_transaction_id UUID,
    status VARCHAR(20) DEFAULT 'pending',
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- AI & ANALYTICS
-- =====================================================

-- AI Predictions
CREATE TABLE IF NOT EXISTS ai_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(50) NOT NULL,
    timeframe VARCHAR(20) NOT NULL,
    prediction_type VARCHAR(50) NOT NULL,
    predicted_price DECIMAL(20, 8),
    predicted_direction VARCHAR(20),
    confidence DECIMAL(5, 4),
    model_name VARCHAR(100),
    features JSONB DEFAULT '{}',
    actual_price DECIMAL(20, 8),
    accuracy DECIMAL(5, 4),
    prediction_time TIMESTAMPTZ NOT NULL,
    target_time TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Social Sentiment Data
CREATE TABLE IF NOT EXISTS social_sentiment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(50) NOT NULL,
    source VARCHAR(50) NOT NULL,
    sentiment_score DECIMAL(5, 4),
    mention_count INTEGER DEFAULT 0,
    positive_count INTEGER DEFAULT 0,
    negative_count INTEGER DEFAULT 0,
    neutral_count INTEGER DEFAULT 0,
    influencer_mentions INTEGER DEFAULT 0,
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- News Events
CREATE TABLE IF NOT EXISTS news_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT,
    source VARCHAR(100),
    url TEXT,
    symbols JSONB DEFAULT '[]',
    sentiment_score DECIMAL(5, 4),
    impact_score INTEGER,
    published_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trading Strategies
CREATE TABLE IF NOT EXISTS trading_strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    strategy_type VARCHAR(50),
    parameters JSONB DEFAULT '{}',
    performance_metrics JSONB DEFAULT '{}',
    backtesting_results JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT FALSE,
    subscribers_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Portfolio Analytics
CREATE TABLE IF NOT EXISTS portfolio_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    date DATE NOT NULL,
    total_value DECIMAL(20, 2),
    daily_return DECIMAL(10, 4),
    cumulative_return DECIMAL(10, 4),
    volatility DECIMAL(10, 4),
    sharpe_ratio DECIMAL(10, 4),
    max_drawdown DECIMAL(10, 4),
    var_95 DECIMAL(20, 2),
    allocation JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- =====================================================
-- MARKETPLACE
-- =====================================================

-- Premium Products
CREATE TABLE IF NOT EXISTS marketplace_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    seller_id UUID NOT NULL,
    product_type VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(20, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    billing_type VARCHAR(20) DEFAULT 'one_time',
    features JSONB DEFAULT '[]',
    ratings_avg DECIMAL(3, 2) DEFAULT 0,
    ratings_count INTEGER DEFAULT 0,
    sales_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Product Purchases
CREATE TABLE IF NOT EXISTS marketplace_purchases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    product_id UUID NOT NULL,
    amount DECIMAL(20, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Product Reviews
CREATE TABLE IF NOT EXISTS marketplace_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    product_id UUID NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Copy Trading Indexes
CREATE INDEX IF NOT EXISTS idx_copy_traders_user ON copy_traders(user_id);
CREATE INDEX IF NOT EXISTS idx_copy_traders_profit ON copy_traders(total_profit DESC);
CREATE INDEX IF NOT EXISTS idx_copy_followers_user ON copy_followers(user_id);
CREATE INDEX IF NOT EXISTS idx_copy_followers_trader ON copy_followers(trader_id);
CREATE INDEX IF NOT EXISTS idx_copy_positions_follower ON copy_positions(follower_id);
CREATE INDEX IF NOT EXISTS idx_copy_performance_trader ON copy_performance(trader_id, date DESC);

-- Subscription Indexes
CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_plan ON user_subscriptions(plan_id);
CREATE INDEX IF NOT EXISTS idx_payments_user ON payment_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_crypto_payments_user ON crypto_payments(user_id);

-- Security Indexes
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_security_events_user ON security_events(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_kyc_documents_user ON kyc_documents(user_id);

-- Referral Indexes
CREATE INDEX IF NOT EXISTS idx_referral_codes_user ON referral_codes(user_id);
CREATE INDEX IF NOT EXISTS idx_referrals_referrer ON referrals(referrer_id);
CREATE INDEX IF NOT EXISTS idx_referrals_referred ON referrals(referred_user_id);

-- AI Indexes
CREATE INDEX IF NOT EXISTS idx_predictions_symbol ON ai_predictions(symbol, prediction_time DESC);
CREATE INDEX IF NOT EXISTS idx_sentiment_symbol ON social_sentiment(symbol, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_news_published ON news_events(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_strategies_user ON trading_strategies(user_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_analytics ON portfolio_analytics(user_id, date DESC);

-- Marketplace Indexes
CREATE INDEX IF NOT EXISTS idx_products_type ON marketplace_products(product_type, is_active);
CREATE INDEX IF NOT EXISTS idx_purchases_user ON marketplace_purchases(user_id);

-- =====================================================
-- SAMPLE DATA FOR SUBSCRIPTION PLANS
-- =====================================================

INSERT INTO subscription_plans (name, display_name, description, price_monthly, price_yearly, features, limits, sort_order)
VALUES 
    ('free', 'Free Plan', 'Basic trading features', 0, 0, 
     '["Basic charts", "5 positions max", "Limited signals"]'::jsonb,
     '{"positions": 5, "api_calls": 100, "copy_traders": 0}'::jsonb, 1),
    ('pro', 'Pro Plan', 'Advanced trading tools', 29.99, 299.99,
     '["Advanced charts", "Unlimited positions", "AI signals", "Copy trading", "Portfolio analytics"]'::jsonb,
     '{"positions": -1, "api_calls": 10000, "copy_traders": 3}'::jsonb, 2),
    ('enterprise', 'Enterprise Plan', 'Full platform access', 99.99, 999.99,
     '["All Pro features", "Priority support", "Custom strategies", "API access", "White label"]'::jsonb,
     '{"positions": -1, "api_calls": -1, "copy_traders": -1}'::jsonb, 3)
ON CONFLICT (name) DO NOTHING;

-- =====================================================
-- END OF SCHEMA
-- =====================================================
