-- Migration: final_modules_database_schema_fixed
-- Created at: 1762217517

-- Final Modules Database Schema (Fixed)
-- 13 ta jadval yaratish: News Trading, Risk Analytics, AI Predictions, va boshqa advanced features

-- News Articles
CREATE TABLE IF NOT EXISTS news_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT,
    url TEXT UNIQUE,
    source TEXT,
    published_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    symbols TEXT[],
    sentiment_score DECIMAL(5, 4) CHECK (sentiment_score >= -1 AND sentiment_score <= 1),
    impact_score INTEGER CHECK (impact_score >= 0 AND impact_score <= 10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Social Media Sentiment
CREATE TABLE IF NOT EXISTS social_media_sentiment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform TEXT NOT NULL, -- twitter, reddit, telegram
    symbol TEXT NOT NULL,
    post_id TEXT,
    content TEXT,
    sentiment_score DECIMAL(5, 4),
    engagement_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- News Trading Signals
CREATE TABLE IF NOT EXISTS news_trading_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    news_id UUID REFERENCES news_articles(id),
    symbol TEXT NOT NULL,
    signal_type TEXT NOT NULL, -- buy, sell, hold
    confidence_score DECIMAL(5, 4),
    target_price DECIMAL(15, 8),
    stop_loss DECIMAL(15, 8),
    timeframe TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Risk Analytics Rules
CREATE TABLE IF NOT EXISTS risk_analytics_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    risk_level TEXT CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    conditions JSONB,
    actions JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Auto Strategy Templates
CREATE TABLE IF NOT EXISTS auto_strategy_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    category TEXT,
    parameters JSONB,
    backtest_results JSONB,
    success_rate DECIMAL(5, 4),
    avg_return DECIMAL(10, 4),
    max_drawdown DECIMAL(5, 4),
    is_premium BOOLEAN DEFAULT FALSE,
    creator_id UUID,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Market Predictions
CREATE TABLE IF NOT EXISTS market_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    prediction_type TEXT, -- price, volume, volatility
    predicted_value DECIMAL(15, 8),
    confidence_level DECIMAL(5, 4),
    timeframe TEXT,
    model_version TEXT,
    factors JSONB,
    actual_value DECIMAL(15, 8),
    accuracy_score DECIMAL(5, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    target_date TIMESTAMP WITH TIME ZONE
);

-- Voice Commands
CREATE TABLE IF NOT EXISTS voice_commands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    command_text TEXT,
    action_type TEXT,
    parameters JSONB,
    execution_status TEXT CHECK (execution_status IN ('pending', 'executed', 'failed')),
    audio_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    action TEXT NOT NULL,
    resource_type TEXT,
    resource_id TEXT,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- KYC Verifications
CREATE TABLE IF NOT EXISTS kyc_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    verification_type TEXT CHECK (verification_type IN ('basic', 'enhanced', 'institutional')),
    status TEXT CHECK (status IN ('pending', 'in_review', 'approved', 'rejected')),
    document_type TEXT,
    document_url TEXT,
    verification_data JSONB,
    reviewed_by UUID,
    review_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crypto Payment Transactions
CREATE TABLE IF NOT EXISTS crypto_payment_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    transaction_hash TEXT UNIQUE,
    from_address TEXT,
    to_address TEXT,
    amount DECIMAL(20, 8),
    currency TEXT NOT NULL,
    network TEXT,
    confirmations INTEGER DEFAULT 0,
    status TEXT CHECK (status IN ('pending', 'confirmed', 'failed')),
    usd_value DECIMAL(15, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    confirmed_at TIMESTAMP WITH TIME ZONE
);

-- Premium Products
CREATE TABLE IF NOT EXISTS premium_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    price DECIMAL(10, 2),
    currency TEXT DEFAULT 'USD',
    category TEXT,
    features JSONB,
    duration_days INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Premium Product Reviews
CREATE TABLE IF NOT EXISTS premium_product_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES premium_products(id),
    user_id UUID,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Marketplace Categories
CREATE TABLE IF NOT EXISTS marketplace_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    icon TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_news_articles_symbols ON news_articles USING GIN(symbols);
CREATE INDEX IF NOT EXISTS idx_news_articles_sentiment ON news_articles(sentiment_score);
CREATE INDEX IF NOT EXISTS idx_social_sentiment_platform_symbol ON social_media_sentiment(platform, symbol);
CREATE INDEX IF NOT EXISTS idx_news_trading_signals_symbol ON news_trading_signals(symbol);
CREATE INDEX IF NOT EXISTS idx_market_predictions_symbol_timeframe ON market_predictions(symbol, timeframe);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_kyc_verifications_user_id ON kyc_verifications(user_id);
CREATE INDEX IF NOT EXISTS idx_crypto_payments_user_id ON crypto_payment_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_premium_products_category ON premium_products(category);;