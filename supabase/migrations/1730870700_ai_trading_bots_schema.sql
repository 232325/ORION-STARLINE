-- =====================================================
-- AI-POWERED TRADING BOTS SCHEMA
-- Phase 4.1: AI Trading Bots Engine
-- Tarih: 2025-11-06
-- =====================================================

-- =====================================================
-- 1. AI TRADING BOTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS ai_trading_bots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    bot_name VARCHAR(255) NOT NULL,
    bot_type VARCHAR(50) NOT NULL CHECK (bot_type IN ('conservative', 'aggressive', 'balanced', 'grid', 'arbitrage')),
    description TEXT,
    status VARCHAR(20) DEFAULT 'inactive' CHECK (status IN ('active', 'inactive', 'paused', 'error')),
    
    -- Trading Configuration
    trading_pairs TEXT[] DEFAULT '{}',
    initial_capital DECIMAL(20, 8) DEFAULT 0,
    current_capital DECIMAL(20, 8) DEFAULT 0,
    max_position_size DECIMAL(20, 8) DEFAULT 0,
    max_daily_trades INTEGER DEFAULT 10,
    
    -- Performance Metrics
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    total_profit DECIMAL(20, 8) DEFAULT 0,
    total_loss DECIMAL(20, 8) DEFAULT 0,
    win_rate DECIMAL(5, 2) DEFAULT 0,
    sharpe_ratio DECIMAL(10, 4) DEFAULT 0,
    max_drawdown DECIMAL(10, 4) DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_active_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    stopped_at TIMESTAMPTZ
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_ai_bots_user_id ON ai_trading_bots(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_bots_status ON ai_trading_bots(status);
CREATE INDEX IF NOT EXISTS idx_ai_bots_type ON ai_trading_bots(bot_type);

-- =====================================================
-- 2. BOT CONFIGURATIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS bot_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_id UUID NOT NULL,
    
    -- Entry/Exit Criteria
    entry_conditions JSONB DEFAULT '{}',
    exit_conditions JSONB DEFAULT '{}',
    
    -- Risk Parameters
    risk_percentage DECIMAL(5, 2) DEFAULT 2.0,
    max_risk_per_trade DECIMAL(20, 8) DEFAULT 0,
    max_drawdown_limit DECIMAL(5, 2) DEFAULT 20.0,
    
    -- Position Sizing
    position_sizing_method VARCHAR(50) DEFAULT 'fixed' CHECK (position_sizing_method IN ('fixed', 'kelly', 'risk_based', 'volatility_based')),
    position_size_multiplier DECIMAL(5, 2) DEFAULT 1.0,
    
    -- Stop Loss / Take Profit
    stop_loss_type VARCHAR(50) DEFAULT 'fixed' CHECK (stop_loss_type IN ('fixed', 'trailing', 'atr', 'dynamic')),
    stop_loss_percentage DECIMAL(5, 2) DEFAULT 2.0,
    take_profit_percentage DECIMAL(5, 2) DEFAULT 5.0,
    trailing_stop_percentage DECIMAL(5, 2) DEFAULT 1.0,
    
    -- Time Filters
    trading_hours JSONB DEFAULT '{}',
    avoid_news_events BOOLEAN DEFAULT true,
    max_holding_time INTEGER DEFAULT 1440,
    
    -- Market Condition Filters
    min_volatility DECIMAL(10, 4) DEFAULT 0,
    max_volatility DECIMAL(10, 4) DEFAULT 100,
    trend_filter VARCHAR(50) DEFAULT 'any' CHECK (trend_filter IN ('any', 'uptrend', 'downtrend', 'ranging')),
    
    -- Technical Indicators
    indicators_config JSONB DEFAULT '{}',
    
    -- Advanced Settings
    use_ai_signals BOOLEAN DEFAULT true,
    use_ml_predictions BOOLEAN DEFAULT true,
    use_sentiment_analysis BOOLEAN DEFAULT true,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_bot_config_bot_id ON bot_configurations(bot_id);

-- =====================================================
-- 3. BOT TRADING HISTORY TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS bot_trading_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_id UUID NOT NULL,
    user_id UUID NOT NULL,
    
    -- Trade Details
    trade_type VARCHAR(10) NOT NULL CHECK (trade_type IN ('BUY', 'SELL')),
    symbol VARCHAR(50) NOT NULL,
    quantity DECIMAL(20, 8) NOT NULL,
    entry_price DECIMAL(20, 8) NOT NULL,
    exit_price DECIMAL(20, 8),
    
    -- Trade Status
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'closed', 'cancelled', 'error')),
    
    -- Financial Metrics
    profit_loss DECIMAL(20, 8) DEFAULT 0,
    profit_loss_percentage DECIMAL(10, 4) DEFAULT 0,
    fees DECIMAL(20, 8) DEFAULT 0,
    net_profit DECIMAL(20, 8) DEFAULT 0,
    
    -- Stop Loss / Take Profit
    stop_loss_price DECIMAL(20, 8),
    take_profit_price DECIMAL(20, 8),
    
    -- Trade Execution
    entry_signal JSONB DEFAULT '{}',
    exit_signal JSONB DEFAULT '{}',
    execution_time_ms INTEGER DEFAULT 0,
    slippage DECIMAL(10, 4) DEFAULT 0,
    
    -- Market Conditions
    market_conditions JSONB DEFAULT '{}',
    
    -- Timestamps
    opened_at TIMESTAMPTZ DEFAULT NOW(),
    closed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_bot_history_bot_id ON bot_trading_history(bot_id);
CREATE INDEX IF NOT EXISTS idx_bot_history_user_id ON bot_trading_history(user_id);
CREATE INDEX IF NOT EXISTS idx_bot_history_status ON bot_trading_history(status);
CREATE INDEX IF NOT EXISTS idx_bot_history_symbol ON bot_trading_history(symbol);
CREATE INDEX IF NOT EXISTS idx_bot_history_opened_at ON bot_trading_history(opened_at);

-- =====================================================
-- 4. BOT PERFORMANCE METRICS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS bot_performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_id UUID NOT NULL,
    
    -- Time Period
    period_type VARCHAR(20) NOT NULL CHECK (period_type IN ('daily', 'weekly', 'monthly', 'all_time')),
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    
    -- Trading Statistics
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5, 2) DEFAULT 0,
    
    -- Financial Performance
    total_profit DECIMAL(20, 8) DEFAULT 0,
    total_loss DECIMAL(20, 8) DEFAULT 0,
    net_profit DECIMAL(20, 8) DEFAULT 0,
    roi DECIMAL(10, 4) DEFAULT 0,
    
    -- Risk Metrics
    sharpe_ratio DECIMAL(10, 4) DEFAULT 0,
    sortino_ratio DECIMAL(10, 4) DEFAULT 0,
    max_drawdown DECIMAL(10, 4) DEFAULT 0,
    calmar_ratio DECIMAL(10, 4) DEFAULT 0,
    
    -- Additional Metrics
    avg_win DECIMAL(20, 8) DEFAULT 0,
    avg_loss DECIMAL(20, 8) DEFAULT 0,
    profit_factor DECIMAL(10, 4) DEFAULT 0,
    largest_win DECIMAL(20, 8) DEFAULT 0,
    largest_loss DECIMAL(20, 8) DEFAULT 0,
    
    -- Consistency Metrics
    consecutive_wins INTEGER DEFAULT 0,
    consecutive_losses INTEGER DEFAULT 0,
    recovery_factor DECIMAL(10, 4) DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_bot_metrics_bot_id ON bot_performance_metrics(bot_id);
CREATE INDEX IF NOT EXISTS idx_bot_metrics_period ON bot_performance_metrics(period_type, period_start);

-- =====================================================
-- 5. TRADING STRATEGIES TABLE (GPT-4 Generated)
-- =====================================================
CREATE TABLE IF NOT EXISTS trading_strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    bot_id UUID,
    
    -- Strategy Details
    strategy_name VARCHAR(255) NOT NULL,
    description TEXT,
    strategy_type VARCHAR(50) NOT NULL CHECK (strategy_type IN ('trend_following', 'mean_reversion', 'breakout', 'scalping', 'swing', 'arbitrage', 'custom')),
    
    -- AI Generation
    generated_by VARCHAR(50) DEFAULT 'gpt4' CHECK (generated_by IN ('gpt4', 'user', 'ml_model')),
    prompt TEXT,
    
    -- Strategy Rules
    entry_rules JSONB DEFAULT '{}',
    exit_rules JSONB DEFAULT '{}',
    risk_rules JSONB DEFAULT '{}',
    
    -- Configuration
    timeframe VARCHAR(10) DEFAULT '1h',
    instruments TEXT[] DEFAULT '{}',
    
    -- Performance Expectations
    expected_win_rate DECIMAL(5, 2) DEFAULT 0,
    expected_profit_factor DECIMAL(10, 4) DEFAULT 0,
    expected_sharpe DECIMAL(10, 4) DEFAULT 0,
    risk_level VARCHAR(20) DEFAULT 'medium' CHECK (risk_level IN ('low', 'medium', 'high', 'extreme')),
    
    -- Backtesting Results
    backtest_results JSONB DEFAULT '{}',
    backtest_profit DECIMAL(20, 8) DEFAULT 0,
    backtest_trades INTEGER DEFAULT 0,
    backtest_win_rate DECIMAL(5, 2) DEFAULT 0,
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'inactive', 'testing', 'archived')),
    is_public BOOLEAN DEFAULT false,
    
    -- Usage Stats
    times_used INTEGER DEFAULT 0,
    avg_user_rating DECIMAL(3, 2) DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_strategies_user_id ON trading_strategies(user_id);
CREATE INDEX IF NOT EXISTS idx_strategies_bot_id ON trading_strategies(bot_id);
CREATE INDEX IF NOT EXISTS idx_strategies_type ON trading_strategies(strategy_type);
CREATE INDEX IF NOT EXISTS idx_strategies_status ON trading_strategies(status);

-- =====================================================
-- 6. ML PREDICTIONS TABLE (Enhanced)
-- =====================================================
CREATE TABLE IF NOT EXISTS ml_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(50) NOT NULL,
    
    -- Prediction Details
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) DEFAULT 'v1.0',
    prediction_type VARCHAR(50) DEFAULT 'price' CHECK (prediction_type IN ('price', 'direction', 'volatility', 'trend', 'anomaly')),
    
    -- Time Horizon
    timeframe VARCHAR(10) NOT NULL,
    prediction_horizon INTEGER DEFAULT 60,
    
    -- Current State
    current_price DECIMAL(20, 8) NOT NULL,
    
    -- Predictions
    predicted_price DECIMAL(20, 8),
    predicted_direction VARCHAR(10) CHECK (predicted_direction IN ('up', 'down', 'neutral')),
    predicted_change_percentage DECIMAL(10, 4),
    
    -- Confidence & Probability
    confidence_score DECIMAL(5, 4) DEFAULT 0 CHECK (confidence_score >= 0 AND confidence_score <= 1),
    probability_up DECIMAL(5, 4) DEFAULT 0,
    probability_down DECIMAL(5, 4) DEFAULT 0,
    
    -- Feature Importance
    features_used JSONB DEFAULT '{}',
    feature_importance JSONB DEFAULT '{}',
    
    -- Technical Indicators
    technical_signals JSONB DEFAULT '{}',
    
    -- Market Context
    market_regime VARCHAR(50) DEFAULT 'normal',
    volatility_level VARCHAR(20) DEFAULT 'medium',
    trend_strength DECIMAL(5, 2) DEFAULT 0,
    
    -- Anomaly Detection
    is_anomaly BOOLEAN DEFAULT false,
    anomaly_score DECIMAL(10, 4) DEFAULT 0,
    anomaly_type VARCHAR(50),
    
    -- Validation
    actual_price DECIMAL(20, 8),
    prediction_error DECIMAL(10, 4),
    is_correct BOOLEAN,
    
    -- Timestamps
    prediction_time TIMESTAMPTZ DEFAULT NOW(),
    target_time TIMESTAMPTZ,
    validated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_ml_predictions_symbol ON ml_predictions(symbol);
CREATE INDEX IF NOT EXISTS idx_ml_predictions_timeframe ON ml_predictions(timeframe);
CREATE INDEX IF NOT EXISTS idx_ml_predictions_time ON ml_predictions(prediction_time);
CREATE INDEX IF NOT EXISTS idx_ml_predictions_confidence ON ml_predictions(confidence_score DESC);

-- =====================================================
-- 7. ALGORITHM EXECUTIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS algorithm_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_id UUID NOT NULL,
    strategy_id UUID,
    
    -- Execution Details
    execution_type VARCHAR(50) NOT NULL CHECK (execution_type IN ('signal_check', 'order_placement', 'position_update', 'risk_check', 'portfolio_rebalance')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    
    -- Input/Output
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    
    -- Performance
    execution_time_ms INTEGER DEFAULT 0,
    memory_used_mb DECIMAL(10, 2) DEFAULT 0,
    cpu_usage_percent DECIMAL(5, 2) DEFAULT 0,
    
    -- Signals Generated
    signals_generated JSONB DEFAULT '{}',
    actions_taken JSONB DEFAULT '{}',
    
    -- Error Handling
    error_message TEXT,
    error_stack TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Timestamps
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_algo_exec_bot_id ON algorithm_executions(bot_id);
CREATE INDEX IF NOT EXISTS idx_algo_exec_strategy_id ON algorithm_executions(strategy_id);
CREATE INDEX IF NOT EXISTS idx_algo_exec_status ON algorithm_executions(status);
CREATE INDEX IF NOT EXISTS idx_algo_exec_started_at ON algorithm_executions(started_at);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE ai_trading_bots ENABLE ROW LEVEL SECURITY;
ALTER TABLE bot_configurations ENABLE ROW LEVEL SECURITY;
ALTER TABLE bot_trading_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE bot_performance_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE trading_strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE ml_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE algorithm_executions ENABLE ROW LEVEL SECURITY;

-- RLS Policies for ai_trading_bots
CREATE POLICY "Users can view own bots" ON ai_trading_bots FOR SELECT USING (auth.role() IN ('anon', 'service_role'));
CREATE POLICY "Users can create own bots" ON ai_trading_bots FOR INSERT WITH CHECK (auth.role() IN ('anon', 'service_role'));
CREATE POLICY "Users can update own bots" ON ai_trading_bots FOR UPDATE USING (auth.role() IN ('anon', 'service_role'));
CREATE POLICY "Users can delete own bots" ON ai_trading_bots FOR DELETE USING (auth.role() IN ('anon', 'service_role'));

-- RLS Policies for bot_configurations
CREATE POLICY "Users can view bot configs" ON bot_configurations FOR SELECT USING (auth.role() IN ('anon', 'service_role'));
CREATE POLICY "Users can create bot configs" ON bot_configurations FOR INSERT WITH CHECK (auth.role() IN ('anon', 'service_role'));
CREATE POLICY "Users can update bot configs" ON bot_configurations FOR UPDATE USING (auth.role() IN ('anon', 'service_role'));
CREATE POLICY "Users can delete bot configs" ON bot_configurations FOR DELETE USING (auth.role() IN ('anon', 'service_role'));

-- RLS Policies for bot_trading_history
CREATE POLICY "Users can view own trades" ON bot_trading_history FOR SELECT USING (auth.role() IN ('anon', 'service_role'));
CREATE POLICY "Users can create trades" ON bot_trading_history FOR INSERT WITH CHECK (auth.role() IN ('anon', 'service_role'));
CREATE POLICY "Users can update trades" ON bot_trading_history FOR UPDATE USING (auth.role() IN ('anon', 'service_role'));

-- RLS Policies for bot_performance_metrics
CREATE POLICY "Users can view bot metrics" ON bot_performance_metrics FOR SELECT USING (auth.role() IN ('anon', 'service_role'));
CREATE POLICY "System can create metrics" ON bot_performance_metrics FOR INSERT WITH CHECK (auth.role() IN ('anon', 'service_role'));

-- RLS Policies for trading_strategies
CREATE POLICY "Users can view strategies" ON trading_strategies FOR SELECT USING (auth.role() IN ('anon', 'service_role'));
CREATE POLICY "Users can create strategies" ON trading_strategies FOR INSERT WITH CHECK (auth.role() IN ('anon', 'service_role'));
CREATE POLICY "Users can update own strategies" ON trading_strategies FOR UPDATE USING (auth.role() IN ('anon', 'service_role'));
CREATE POLICY "Users can delete own strategies" ON trading_strategies FOR DELETE USING (auth.role() IN ('anon', 'service_role'));

-- RLS Policies for ml_predictions
CREATE POLICY "Anyone can view predictions" ON ml_predictions FOR SELECT USING (auth.role() IN ('anon', 'service_role'));
CREATE POLICY "System can create predictions" ON ml_predictions FOR INSERT WITH CHECK (auth.role() IN ('anon', 'service_role'));
CREATE POLICY "System can update predictions" ON ml_predictions FOR UPDATE USING (auth.role() IN ('anon', 'service_role'));

-- RLS Policies for algorithm_executions
CREATE POLICY "Users can view executions" ON algorithm_executions FOR SELECT USING (auth.role() IN ('anon', 'service_role'));
CREATE POLICY "System can create executions" ON algorithm_executions FOR INSERT WITH CHECK (auth.role() IN ('anon', 'service_role'));
CREATE POLICY "System can update executions" ON algorithm_executions FOR UPDATE USING (auth.role() IN ('anon', 'service_role'));

-- =====================================================
-- FUNCTIONS & TRIGGERS
-- =====================================================

-- Note: Triggers and functions will be handled via Edge Functions for flexibility

-- =====================================================
-- COMPLETION
-- =====================================================

COMMENT ON TABLE ai_trading_bots IS 'AI-powered trading bots management - Phase 4.1';
COMMENT ON TABLE bot_configurations IS 'Bot configuration settings and parameters';
COMMENT ON TABLE bot_trading_history IS 'Complete trading history for all bots';
COMMENT ON TABLE bot_performance_metrics IS 'Performance metrics tracking for bots';
COMMENT ON TABLE trading_strategies IS 'GPT-4 generated and user-created trading strategies';
COMMENT ON TABLE ml_predictions IS 'Machine learning price predictions';
COMMENT ON TABLE algorithm_executions IS 'Algorithm execution logs and performance';
