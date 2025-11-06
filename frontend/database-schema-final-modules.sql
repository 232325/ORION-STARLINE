-- =====================================================
-- AI TRADING PLATFORM - QOLGAN MODULLAR DATABASE SCHEMA
-- =====================================================
-- Version: 5.0 - Final Complete Schema
-- Date: 2025-11-04
-- =====================================================

-- =====================================================
-- NEWS TRADING & SOCIAL SENTIMENT
-- =====================================================

-- News articles
CREATE TABLE IF NOT EXISTS news_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT,
    source VARCHAR(100),
    url TEXT,
    author VARCHAR(200),
    symbols TEXT[],
    sentiment_score DECIMAL(5, 4),
    impact_score INTEGER CHECK (impact_score >= 0 AND impact_score <= 10),
    category VARCHAR(50),
    language VARCHAR(10) DEFAULT 'en',
    published_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Social media sentiment
CREATE TABLE IF NOT EXISTS social_media_sentiment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform VARCHAR(50) NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    sentiment_score DECIMAL(5, 4),
    mention_count INTEGER DEFAULT 0,
    positive_mentions INTEGER DEFAULT 0,
    negative_mentions INTEGER DEFAULT 0,
    neutral_mentions INTEGER DEFAULT 0,
    influencer_mentions INTEGER DEFAULT 0,
    trending_rank INTEGER,
    fear_greed_index DECIMAL(5, 2),
    volume_24h BIGINT DEFAULT 0,
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- News trading signals
CREATE TABLE IF NOT EXISTS news_trading_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    news_id UUID,
    symbol VARCHAR(50) NOT NULL,
    signal_type VARCHAR(20) NOT NULL,
    confidence DECIMAL(5, 4),
    expected_impact VARCHAR(50),
    recommended_action TEXT,
    time_sensitivity INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- RISK ANALYTICS
-- =====================================================

-- Portfolio risk metrics
CREATE TABLE IF NOT EXISTS portfolio_risk_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    date DATE NOT NULL,
    var_95 DECIMAL(20, 2),
    var_99 DECIMAL(20, 2),
    cvar_95 DECIMAL(20, 2),
    max_drawdown DECIMAL(10, 4),
    volatility DECIMAL(10, 4),
    beta DECIMAL(10, 4),
    correlation_matrix JSONB,
    stress_test_results JSONB,
    risk_score INTEGER CHECK (risk_score >= 0 AND risk_score <= 100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- Risk alerts
CREATE TABLE IF NOT EXISTS risk_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium',
    message TEXT NOT NULL,
    threshold_value DECIMAL(20, 4),
    current_value DECIMAL(20, 4),
    is_read BOOLEAN DEFAULT FALSE,
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Asset correlations
CREATE TABLE IF NOT EXISTS asset_correlations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol1 VARCHAR(50) NOT NULL,
    symbol2 VARCHAR(50) NOT NULL,
    correlation DECIMAL(5, 4),
    period_days INTEGER DEFAULT 30,
    calculated_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- KYC/AML COMPLIANCE
-- =====================================================

-- KYC verification levels
CREATE TABLE IF NOT EXISTS kyc_verification_levels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    level INTEGER DEFAULT 0,
    identity_verified BOOLEAN DEFAULT FALSE,
    address_verified BOOLEAN DEFAULT FALSE,
    income_verified BOOLEAN DEFAULT FALSE,
    accredited_investor BOOLEAN DEFAULT FALSE,
    aml_screened BOOLEAN DEFAULT FALSE,
    sanctions_checked BOOLEAN DEFAULT FALSE,
    pep_checked BOOLEAN DEFAULT FALSE,
    verification_date TIMESTAMPTZ,
    next_review_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- AML screening results
CREATE TABLE IF NOT EXISTS aml_screening_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    screening_type VARCHAR(50) NOT NULL,
    result VARCHAR(20) DEFAULT 'clear',
    risk_level VARCHAR(20),
    matches_found INTEGER DEFAULT 0,
    match_details JSONB,
    screened_at TIMESTAMPTZ NOT NULL,
    screened_by VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- AUDIT & LOGGING
-- =====================================================

-- Enhanced audit logs
CREATE TABLE IF NOT EXISTS enhanced_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    session_id VARCHAR(255),
    action_type VARCHAR(100) NOT NULL,
    action_category VARCHAR(50),
    resource_type VARCHAR(50),
    resource_id UUID,
    old_value JSONB,
    new_value JSONB,
    ip_address INET,
    user_agent TEXT,
    device_info JSONB,
    geo_location JSONB,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    duration_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Compliance reports
CREATE TABLE IF NOT EXISTS compliance_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_type VARCHAR(50) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_users INTEGER,
    verified_users INTEGER,
    suspicious_activities INTEGER,
    report_data JSONB,
    generated_by VARCHAR(100),
    generated_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- VOICE COMMANDS & AI ASSISTANTS
-- =====================================================

-- Voice commands history
CREATE TABLE IF NOT EXISTS voice_commands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    command_text TEXT NOT NULL,
    command_type VARCHAR(50),
    language VARCHAR(10) DEFAULT 'en',
    confidence DECIMAL(5, 4),
    intent VARCHAR(100),
    entities JSONB,
    action_taken TEXT,
    success BOOLEAN DEFAULT TRUE,
    response_text TEXT,
    audio_duration_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- AI chat conversations
CREATE TABLE IF NOT EXISTS ai_chat_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    message_type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    tokens_used INTEGER,
    model_name VARCHAR(50),
    context JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- AI generated strategies
CREATE TABLE IF NOT EXISTS ai_generated_strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    strategy_name VARCHAR(200) NOT NULL,
    description TEXT,
    strategy_code TEXT,
    parameters JSONB,
    backtesting_results JSONB,
    performance_score DECIMAL(5, 2),
    risk_score INTEGER,
    is_approved BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT FALSE,
    generated_by VARCHAR(50) DEFAULT 'ai',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- CRYPTO PAYMENTS
-- =====================================================

-- Crypto wallet addresses
CREATE TABLE IF NOT EXISTS crypto_wallet_addresses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    cryptocurrency VARCHAR(20) NOT NULL,
    wallet_address VARCHAR(255) NOT NULL UNIQUE,
    network VARCHAR(50),
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Crypto payment transactions
CREATE TABLE IF NOT EXISTS crypto_payment_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    cryptocurrency VARCHAR(20) NOT NULL,
    amount DECIMAL(30, 18) NOT NULL,
    usd_equivalent DECIMAL(20, 2),
    from_address VARCHAR(255),
    to_address VARCHAR(255) NOT NULL,
    transaction_hash VARCHAR(255) UNIQUE,
    network VARCHAR(50),
    confirmations INTEGER DEFAULT 0,
    required_confirmations INTEGER DEFAULT 6,
    status VARCHAR(20) DEFAULT 'pending',
    purpose VARCHAR(100),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    confirmed_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

-- =====================================================
-- MARKETPLACE
-- =====================================================

-- Marketplace categories
CREATE TABLE IF NOT EXISTS marketplace_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Marketplace product downloads
CREATE TABLE IF NOT EXISTS marketplace_downloads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    product_id UUID NOT NULL,
    download_count INTEGER DEFAULT 1,
    last_downloaded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Product ratings
CREATE TABLE IF NOT EXISTS marketplace_product_ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    product_id UUID NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review TEXT,
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    helpful_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

-- =====================================================
-- ADVANCED PORTFOLIO ANALYTICS
-- =====================================================

-- Portfolio allocation history
CREATE TABLE IF NOT EXISTS portfolio_allocation_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    date DATE NOT NULL,
    asset_class VARCHAR(50) NOT NULL,
    symbol VARCHAR(50),
    allocation_percentage DECIMAL(5, 2),
    value_usd DECIMAL(20, 2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Portfolio rebalancing suggestions
CREATE TABLE IF NOT EXISTS portfolio_rebalancing_suggestions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    current_allocation JSONB NOT NULL,
    suggested_allocation JSONB NOT NULL,
    reason TEXT,
    expected_improvement DECIMAL(5, 2),
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    applied_at TIMESTAMPTZ
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- News & Sentiment
CREATE INDEX IF NOT EXISTS idx_news_published ON news_articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_news_symbols ON news_articles USING GIN(symbols);
CREATE INDEX IF NOT EXISTS idx_social_sentiment_symbol ON social_media_sentiment(symbol, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_news_signals_symbol ON news_trading_signals(symbol, created_at DESC);

-- Risk Analytics
CREATE INDEX IF NOT EXISTS idx_portfolio_risk_user ON portfolio_risk_metrics(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_risk_alerts_user ON risk_alerts(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_correlations_symbols ON asset_correlations(symbol1, symbol2);

-- KYC/AML
CREATE INDEX IF NOT EXISTS idx_kyc_user ON kyc_verification_levels(user_id);
CREATE INDEX IF NOT EXISTS idx_aml_screening_user ON aml_screening_results(user_id, screened_at DESC);

-- Audit
CREATE INDEX IF NOT EXISTS idx_audit_user ON enhanced_audit_logs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_action ON enhanced_audit_logs(action_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_compliance_period ON compliance_reports(period_start, period_end);

-- Voice & AI
CREATE INDEX IF NOT EXISTS idx_voice_user ON voice_commands(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_chat_session ON ai_chat_conversations(session_id, created_at);
CREATE INDEX IF NOT EXISTS idx_ai_strategies_user ON ai_generated_strategies(user_id);

-- Crypto Payments
CREATE INDEX IF NOT EXISTS idx_crypto_wallets_user ON crypto_wallet_addresses(user_id);
CREATE INDEX IF NOT EXISTS idx_crypto_payments_user ON crypto_payment_transactions(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_crypto_payments_hash ON crypto_payment_transactions(transaction_hash);

-- Marketplace
CREATE INDEX IF NOT EXISTS idx_marketplace_downloads ON marketplace_downloads(user_id, product_id);
CREATE INDEX IF NOT EXISTS idx_marketplace_ratings ON marketplace_product_ratings(product_id);

-- Portfolio
CREATE INDEX IF NOT EXISTS idx_portfolio_allocation ON portfolio_allocation_history(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_rebalancing_user ON portfolio_rebalancing_suggestions(user_id, status);

-- =====================================================
-- SAMPLE DATA
-- =====================================================

-- Insert marketplace categories
INSERT INTO marketplace_categories (name, description, icon, sort_order)
VALUES 
    ('Trading Strategies', 'Professional trading strategies and algorithms', 'chart', 1),
    ('Indicators', 'Technical indicators and custom tools', 'trending', 2),
    ('Themes', 'Custom dashboard themes and UI packs', 'palette', 3),
    ('Analytics', 'Advanced analytics and reporting tools', 'analytics', 4),
    ('Educational', 'Trading courses and educational content', 'book', 5)
ON CONFLICT (name) DO NOTHING;

-- =====================================================
-- END OF SCHEMA
-- =====================================================
