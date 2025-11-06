-- Phase 2 Database Schema Enhancement
-- New tables for GPT-4 Advanced AI, Social Trading, and Multi-language Support

-- ================================================================
-- AI CONVERSATIONS & VOICE COMMANDS
-- ================================================================

CREATE TABLE IF NOT EXISTS ai_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id TEXT NOT NULL,
    user_id UUID NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    function_call JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_ai_conversations_conv_id ON ai_conversations(conversation_id);
CREATE INDEX idx_ai_conversations_user_id ON ai_conversations(user_id);
CREATE INDEX idx_ai_conversations_timestamp ON ai_conversations(created_at DESC);

CREATE TABLE IF NOT EXISTS voice_commands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    command_text TEXT NOT NULL,
    parsed_action TEXT,
    parameters JSONB,
    confidence DECIMAL(3,2),
    executed BOOLEAN DEFAULT FALSE,
    execution_result JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_voice_commands_user_id ON voice_commands(user_id);
CREATE INDEX idx_voice_commands_created_at ON voice_commands(created_at DESC);

-- ================================================================
-- SOCIAL TRADING SYSTEM
-- ================================================================

CREATE TABLE IF NOT EXISTS trader_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    display_name TEXT,
    bio TEXT,
    avatar_url TEXT,
    trading_style TEXT,
    experience_level TEXT CHECK (experience_level IN ('beginner', 'intermediate', 'advanced', 'expert')),
    verified BOOLEAN DEFAULT FALSE,
    
    -- Performance metrics
    total_followers INTEGER DEFAULT 0,
    total_copiers INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2),
    avg_return DECIMAL(10,2),
    total_trades INTEGER DEFAULT 0,
    profitable_trades INTEGER DEFAULT 0,
    
    -- Risk metrics
    risk_score DECIMAL(3,2),
    max_drawdown DECIMAL(10,2),
    sharpe_ratio DECIMAL(10,4),
    
    -- Social metrics
    social_score INTEGER DEFAULT 0,
    reputation_points INTEGER DEFAULT 0,
    
    -- Visibility
    is_public BOOLEAN DEFAULT TRUE,
    allow_copying BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_trader_profiles_user_id ON trader_profiles(user_id);
CREATE INDEX idx_trader_profiles_username ON trader_profiles(username);
CREATE INDEX idx_trader_profiles_followers ON trader_profiles(total_followers DESC);
CREATE INDEX idx_trader_profiles_win_rate ON trader_profiles(win_rate DESC);

CREATE TABLE IF NOT EXISTS social_follows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    follower_user_id UUID NOT NULL,
    followed_user_id UUID NOT NULL,
    notification_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(follower_user_id, followed_user_id)
);

CREATE INDEX idx_social_follows_follower ON social_follows(follower_user_id);
CREATE INDEX idx_social_follows_followed ON social_follows(followed_user_id);

CREATE TABLE IF NOT EXISTS copy_trading_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    copier_user_id UUID NOT NULL,
    trader_user_id UUID NOT NULL,
    
    -- Copy settings
    copy_mode TEXT CHECK (copy_mode IN ('full', 'partial', 'manual_approve')),
    allocation_amount DECIMAL(18,2),
    allocation_percentage DECIMAL(5,2),
    max_position_size DECIMAL(18,2),
    
    -- Filters
    min_trade_size DECIMAL(18,2),
    max_trade_size DECIMAL(18,2),
    allowed_symbols TEXT[],
    excluded_symbols TEXT[],
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    auto_sync BOOLEAN DEFAULT TRUE,
    
    -- Performance tracking
    total_copied_trades INTEGER DEFAULT 0,
    profitable_copied_trades INTEGER DEFAULT 0,
    total_profit_loss DECIMAL(18,2) DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    paused_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(copier_user_id, trader_user_id)
);

CREATE INDEX idx_copy_trading_copier ON copy_trading_relationships(copier_user_id);
CREATE INDEX idx_copy_trading_trader ON copy_trading_relationships(trader_user_id);
CREATE INDEX idx_copy_trading_active ON copy_trading_relationships(is_active);

CREATE TABLE IF NOT EXISTS copied_trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    copy_relationship_id UUID NOT NULL REFERENCES copy_trading_relationships(id),
    original_trade_id UUID,
    copier_user_id UUID NOT NULL,
    trader_user_id UUID NOT NULL,
    
    -- Trade details
    symbol TEXT NOT NULL,
    action TEXT CHECK (action IN ('buy', 'sell')),
    quantity DECIMAL(18,8),
    entry_price DECIMAL(18,8),
    exit_price DECIMAL(18,8),
    
    -- Status
    status TEXT CHECK (status IN ('pending', 'executed', 'failed', 'closed')),
    execution_delay_ms INTEGER,
    
    -- Performance
    profit_loss DECIMAL(18,2),
    profit_loss_percentage DECIMAL(10,4),
    
    executed_at TIMESTAMP WITH TIME ZONE,
    closed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_copied_trades_relationship ON copied_trades(copy_relationship_id);
CREATE INDEX idx_copied_trades_copier ON copied_trades(copier_user_id);
CREATE INDEX idx_copied_trades_status ON copied_trades(status);

CREATE TABLE IF NOT EXISTS trader_leaderboard (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    period TEXT CHECK (period IN ('daily', 'weekly', 'monthly', 'all_time')),
    
    -- Rankings
    rank INTEGER,
    previous_rank INTEGER,
    
    -- Performance metrics
    total_return DECIMAL(10,2),
    win_rate DECIMAL(5,2),
    total_trades INTEGER,
    avg_trade_size DECIMAL(18,2),
    
    -- Scores
    performance_score DECIMAL(10,2),
    consistency_score DECIMAL(10,2),
    risk_adjusted_score DECIMAL(10,2),
    
    period_start TIMESTAMP WITH TIME ZONE,
    period_end TIMESTAMP WITH TIME ZONE,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, period, period_start)
);

CREATE INDEX idx_trader_leaderboard_period ON trader_leaderboard(period, rank);
CREATE INDEX idx_trader_leaderboard_user ON trader_leaderboard(user_id);

CREATE TABLE IF NOT EXISTS social_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    post_type TEXT CHECK (post_type IN ('analysis', 'idea', 'achievement', 'news')),
    content TEXT NOT NULL,
    
    -- Related data
    related_symbol TEXT,
    related_trade_id UUID,
    
    -- Media
    images TEXT[],
    charts JSONB,
    
    -- Engagement
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    views_count INTEGER DEFAULT 0,
    
    -- Visibility
    is_public BOOLEAN DEFAULT TRUE,
    is_pinned BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_social_posts_user ON social_posts(user_id);
CREATE INDEX idx_social_posts_created ON social_posts(created_at DESC);
CREATE INDEX idx_social_posts_type ON social_posts(post_type);

CREATE TABLE IF NOT EXISTS social_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    post_id UUID NOT NULL,
    interaction_type TEXT CHECK (interaction_type IN ('like', 'comment', 'share', 'view')),
    comment_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, post_id, interaction_type)
);

CREATE INDEX idx_social_interactions_post ON social_interactions(post_id);
CREATE INDEX idx_social_interactions_user ON social_interactions(user_id);

-- ================================================================
-- GAMIFICATION SYSTEM
-- ================================================================

CREATE TABLE IF NOT EXISTS achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    achievement_code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    icon_url TEXT,
    category TEXT,
    
    -- Requirements
    requirement_type TEXT,
    requirement_value INTEGER,
    
    -- Rewards
    points_reward INTEGER DEFAULT 0,
    badge_tier TEXT CHECK (badge_tier IN ('bronze', 'silver', 'gold', 'platinum', 'diamond')),
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_achievements_code ON achievements(achievement_code);
CREATE INDEX idx_achievements_category ON achievements(category);

CREATE TABLE IF NOT EXISTS user_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    achievement_id UUID NOT NULL REFERENCES achievements(id),
    progress INTEGER DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, achievement_id)
);

CREATE INDEX idx_user_achievements_user ON user_achievements(user_id);
CREATE INDEX idx_user_achievements_completed ON user_achievements(completed);

CREATE TABLE IF NOT EXISTS user_points (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    total_points INTEGER DEFAULT 0,
    current_level INTEGER DEFAULT 1,
    points_to_next_level INTEGER,
    
    -- Point breakdown
    trading_points INTEGER DEFAULT 0,
    social_points INTEGER DEFAULT 0,
    learning_points INTEGER DEFAULT 0,
    referral_points INTEGER DEFAULT 0,
    
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_user_points_user ON user_points(user_id);
CREATE INDEX idx_user_points_total ON user_points(total_points DESC);

CREATE TABLE IF NOT EXISTS trading_challenges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    challenge_code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    
    -- Challenge parameters
    challenge_type TEXT CHECK (challenge_type IN ('profit_target', 'trade_count', 'win_rate', 'consistency')),
    target_value DECIMAL(18,2),
    duration_days INTEGER,
    
    -- Rewards
    points_reward INTEGER,
    prize_pool DECIMAL(18,2),
    badge_reward TEXT,
    
    -- Timing
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    max_participants INTEGER,
    current_participants INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_trading_challenges_active ON trading_challenges(is_active, start_date);

CREATE TABLE IF NOT EXISTS challenge_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    challenge_id UUID NOT NULL REFERENCES trading_challenges(id),
    user_id UUID NOT NULL,
    
    -- Progress
    current_value DECIMAL(18,2) DEFAULT 0,
    progress_percentage DECIMAL(5,2) DEFAULT 0,
    rank INTEGER,
    
    -- Status
    completed BOOLEAN DEFAULT FALSE,
    won_prize BOOLEAN DEFAULT FALSE,
    prize_amount DECIMAL(18,2),
    
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(challenge_id, user_id)
);

CREATE INDEX idx_challenge_participants_challenge ON challenge_participants(challenge_id);
CREATE INDEX idx_challenge_participants_user ON challenge_participants(user_id);
CREATE INDEX idx_challenge_participants_rank ON challenge_participants(challenge_id, rank);

-- ================================================================
-- MULTI-LANGUAGE SUPPORT
-- ================================================================

CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    
    -- Language & Localization
    preferred_language TEXT DEFAULT 'en',
    timezone TEXT DEFAULT 'UTC',
    date_format TEXT DEFAULT 'YYYY-MM-DD',
    number_format TEXT DEFAULT 'en-US',
    
    -- Trading preferences
    default_currency TEXT DEFAULT 'USD',
    risk_tolerance TEXT CHECK (risk_tolerance IN ('conservative', 'moderate', 'aggressive')),
    
    -- Notification preferences
    email_notifications BOOLEAN DEFAULT TRUE,
    push_notifications BOOLEAN DEFAULT TRUE,
    sms_notifications BOOLEAN DEFAULT FALSE,
    
    -- UI preferences
    theme TEXT DEFAULT 'dark',
    dashboard_layout JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_user_preferences_user ON user_preferences(user_id);

CREATE TABLE IF NOT EXISTS translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    translation_key TEXT NOT NULL,
    language_code TEXT NOT NULL,
    translated_text TEXT NOT NULL,
    context TEXT,
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(translation_key, language_code)
);

CREATE INDEX idx_translations_key ON translations(translation_key);
CREATE INDEX idx_translations_language ON translations(language_code);

-- ================================================================
-- RLS POLICIES
-- ================================================================

-- AI Conversations
ALTER TABLE ai_conversations ENABLE ROW LEVEL SECURITY;
CREATE POLICY ai_conversations_policy ON ai_conversations 
    FOR ALL USING (auth.role() = 'anon' OR auth.role() = 'service_role');

-- Voice Commands
ALTER TABLE voice_commands ENABLE ROW LEVEL SECURITY;
CREATE POLICY voice_commands_policy ON voice_commands 
    FOR ALL USING (auth.role() = 'anon' OR auth.role() = 'service_role');

-- Trader Profiles
ALTER TABLE trader_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY trader_profiles_policy ON trader_profiles 
    FOR ALL USING (auth.role() = 'anon' OR auth.role() = 'service_role');

-- Social Follows
ALTER TABLE social_follows ENABLE ROW LEVEL SECURITY;
CREATE POLICY social_follows_policy ON social_follows 
    FOR ALL USING (auth.role() = 'anon' OR auth.role() = 'service_role');

-- Copy Trading
ALTER TABLE copy_trading_relationships ENABLE ROW LEVEL SECURITY;
CREATE POLICY copy_trading_policy ON copy_trading_relationships 
    FOR ALL USING (auth.role() = 'anon' OR auth.role() = 'service_role');

-- Copied Trades
ALTER TABLE copied_trades ENABLE ROW LEVEL SECURITY;
CREATE POLICY copied_trades_policy ON copied_trades 
    FOR ALL USING (auth.role() = 'anon' OR auth.role() = 'service_role');

-- Leaderboard
ALTER TABLE trader_leaderboard ENABLE ROW LEVEL SECURITY;
CREATE POLICY trader_leaderboard_policy ON trader_leaderboard 
    FOR ALL USING (auth.role() = 'anon' OR auth.role() = 'service_role');

-- Social Posts
ALTER TABLE social_posts ENABLE ROW LEVEL SECURITY;
CREATE POLICY social_posts_policy ON social_posts 
    FOR ALL USING (auth.role() = 'anon' OR auth.role() = 'service_role');

-- Achievements
ALTER TABLE achievements ENABLE ROW LEVEL SECURITY;
CREATE POLICY achievements_policy ON achievements 
    FOR ALL USING (auth.role() = 'anon' OR auth.role() = 'service_role');

-- User Achievements
ALTER TABLE user_achievements ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_achievements_policy ON user_achievements 
    FOR ALL USING (auth.role() = 'anon' OR auth.role() = 'service_role');

-- User Points
ALTER TABLE user_points ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_points_policy ON user_points 
    FOR ALL USING (auth.role() = 'anon' OR auth.role() = 'service_role');

-- Challenges
ALTER TABLE trading_challenges ENABLE ROW LEVEL SECURITY;
CREATE POLICY trading_challenges_policy ON trading_challenges 
    FOR ALL USING (auth.role() = 'anon' OR auth.role() = 'service_role');

-- User Preferences
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_preferences_policy ON user_preferences 
    FOR ALL USING (auth.role() = 'anon' OR auth.role() = 'service_role');

-- Translations
ALTER TABLE translations ENABLE ROW LEVEL SECURITY;
CREATE POLICY translations_policy ON translations 
    FOR ALL USING (auth.role() = 'anon' OR auth.role() = 'service_role');
