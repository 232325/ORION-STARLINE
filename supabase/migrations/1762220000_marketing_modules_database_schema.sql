-- Migration: marketing_modules_database_schema
-- Created at: 1762220000
-- Marketing va Growth Strategiyasi uchun database schema

-- Content Management
CREATE TABLE IF NOT EXISTS marketing_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content_type TEXT NOT NULL CHECK (content_type IN ('blog_post', 'social_media', 'email', 'video_script', 'infographic', 'white_paper', 'case_study')),
    status TEXT NOT NULL CHECK (status IN ('draft', 'review', 'approved', 'published', 'archived')),
    target_keywords TEXT[],
    target_audience TEXT,
    content_body TEXT,
    metadata JSONB,
    seo_score DECIMAL(5, 4) DEFAULT 0.0,
    created_by UUID,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Content Performance Metrics
CREATE TABLE IF NOT EXISTS content_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID REFERENCES marketing_content(id) ON DELETE CASCADE,
    views INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5, 4) DEFAULT 0.0,
    conversion_rate DECIMAL(5, 4) DEFAULT 0.0,
    bounce_rate DECIMAL(5, 4) DEFAULT 0.0,
    avg_time_on_page INTEGER DEFAULT 0,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- SEO Tracking
CREATE TABLE IF NOT EXISTS seo_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID REFERENCES marketing_content(id) ON DELETE CASCADE,
    keyword TEXT NOT NULL,
    search_volume INTEGER,
    competition_level TEXT CHECK (competition_level IN ('low', 'medium', 'high')),
    rank_position INTEGER,
    previous_rank_position INTEGER,
    search_engine TEXT DEFAULT 'google',
    country_code TEXT DEFAULT 'US',
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Social Media Accounts
CREATE TABLE IF NOT EXISTS social_media_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform TEXT NOT NULL CHECK (platform IN ('facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'tiktok')),
    account_name TEXT NOT NULL,
    account_id TEXT,
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    follower_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Social Media Posts
CREATE TABLE IF NOT EXISTS social_media_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES social_media_accounts(id),
    content_id UUID REFERENCES marketing_content(id),
    post_text TEXT NOT NULL,
    media_urls TEXT[],
    scheduled_time TIMESTAMP WITH TIME ZONE,
    posted_time TIMESTAMP WITH TIME ZONE,
    post_id TEXT,
    platform_post_id TEXT,
    status TEXT CHECK (status IN ('draft', 'scheduled', 'posted', 'failed')) DEFAULT 'draft',
    engagement_metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Referral System
CREATE TABLE IF NOT EXISTS referral_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT UNIQUE NOT NULL,
    referrer_id UUID,
    tier TEXT CHECK (tier IN ('bronze', 'silver', 'gold', 'platinum')) DEFAULT 'bronze',
    commission_rate DECIMAL(5, 4) NOT NULL,
    max_referrals INTEGER,
    expiry_date TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    total_referrals INTEGER DEFAULT 0,
    total_earnings DECIMAL(15, 2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Referral Tracking
CREATE TABLE IF NOT EXISTS referral_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referral_code_id UUID REFERENCES referral_codes(id),
    new_user_id UUID,
    new_user_email TEXT,
    conversion_type TEXT,
    commission_earned DECIMAL(15, 2) DEFAULT 0.0,
    status TEXT CHECK (status IN ('pending', 'active', 'completed', 'expired', 'cancelled')) DEFAULT 'pending',
    converted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Community Members
CREATE TABLE IF NOT EXISTS community_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    username TEXT,
    email TEXT,
    role TEXT CHECK (role IN ('member', 'moderator', 'admin')) DEFAULT 'member',
    reputation_score INTEGER DEFAULT 0,
    joined_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_banned BOOLEAN DEFAULT FALSE,
    badges TEXT[]
);

-- Community Posts
CREATE TABLE IF NOT EXISTS community_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_id UUID REFERENCES community_members(id),
    title TEXT NOT NULL,
    content TEXT,
    post_type TEXT CHECK (post_type IN ('discussion', 'question', 'tutorial', 'announcement')) DEFAULT 'discussion',
    tags TEXT[],
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    replies_count INTEGER DEFAULT 0,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_locked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Community Comments
CREATE TABLE IF NOT EXISTS community_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES community_posts(id) ON DELETE CASCADE,
    author_id UUID REFERENCES community_members(id),
    content TEXT NOT NULL,
    parent_comment_id UUID REFERENCES community_comments(id),
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- A/B Testing
CREATE TABLE IF NOT EXISTS ab_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    test_type TEXT CHECK (test_type IN ('landing_page', 'email', 'ad', 'feature')) DEFAULT 'landing_page',
    status TEXT CHECK (status IN ('draft', 'running', 'paused', 'completed')) DEFAULT 'draft',
    traffic_split DECIMAL(5, 4) DEFAULT 0.5,
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    winner_variant TEXT,
    confidence_level DECIMAL(5, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- A/B Test Variants
CREATE TABLE IF NOT EXISTS ab_test_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_id UUID REFERENCES ab_tests(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    variant_data JSONB NOT NULL,
    traffic_percentage DECIMAL(5, 4),
    conversions INTEGER DEFAULT 0,
    visitors INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5, 4) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Email Campaigns
CREATE TABLE IF NOT EXISTS email_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    subject TEXT NOT NULL,
    template_html TEXT,
    template_text TEXT,
    target_audience TEXT,
    scheduled_time TIMESTAMP WITH TIME ZONE,
    sent_time TIMESTAMP WITH TIME ZONE,
    status TEXT CHECK (status IN ('draft', 'scheduled', 'sent', 'paused', 'cancelled')) DEFAULT 'draft',
    total_recipients INTEGER DEFAULT 0,
    delivered_count INTEGER DEFAULT 0,
    opened_count INTEGER DEFAULT 0,
    clicked_count INTEGER DEFAULT 0,
    bounced_count INTEGER DEFAULT 0,
    unsubscribed_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Email Subscribers
CREATE TABLE IF NOT EXISTS email_subscribers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    first_name TEXT,
    last_name TEXT,
    status TEXT CHECK (status IN ('active', 'unsubscribed', 'bounced')) DEFAULT 'active',
    tags TEXT[],
    subscribed_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    unsubscribed_date TIMESTAMP WITH TIME ZONE,
    preferences JSONB,
    last_email_sent TIMESTAMP WITH TIME ZONE
);

-- Influencer Partnerships
CREATE TABLE IF NOT EXISTS influencer_partnerships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_name TEXT NOT NULL,
    email TEXT,
    platform TEXT NOT NULL CHECK (platform IN ('youtube', 'instagram', 'tiktok', 'twitter', 'linkedin', 'blog')),
    follower_count INTEGER,
    engagement_rate DECIMAL(5, 4),
    niche TEXT,
    contact_info JSONB,
    status TEXT CHECK (status IN ('prospect', 'contacted', 'negotiating', 'active', 'completed', 'paused')) DEFAULT 'prospect',
    contract_details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Influencer Campaigns
CREATE TABLE IF NOT EXISTS influencer_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partnership_id UUID REFERENCES influencer_partnerships(id),
    campaign_name TEXT NOT NULL,
    brief TEXT,
    deliverables JSONB,
    timeline JSONB,
    compensation DECIMAL(15, 2),
    currency TEXT DEFAULT 'USD',
    status TEXT CHECK (status IN ('planning', 'active', 'review', 'completed', 'cancelled')) DEFAULT 'planning',
    start_date DATE,
    end_date DATE,
    performance_metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Marketing Analytics
CREATE TABLE IF NOT EXISTS marketing_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name TEXT NOT NULL,
    metric_value DECIMAL(15, 4),
    metric_type TEXT CHECK (metric_type IN ('conversion', 'engagement', 'revenue', 'cost', 'roi')),
    source TEXT CHECK (source IN ('google_analytics', 'facebook_ads', 'email', 'social_media', 'referral')),
    date_recorded DATE NOT NULL,
    additional_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Conversion Funnels
CREATE TABLE IF NOT EXISTS conversion_funnels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    funnel_name TEXT NOT NULL,
    steps JSONB NOT NULL, -- Array of funnel steps with names and descriptions
    conversion_rates JSONB, -- Conversion rates for each step
    total_visitors INTEGER DEFAULT 0,
    total_conversions INTEGER DEFAULT 0,
    overall_conversion_rate DECIMAL(5, 4) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_marketing_content_type ON marketing_content(content_type);
CREATE INDEX IF NOT EXISTS idx_marketing_content_status ON marketing_content(status);
CREATE INDEX IF NOT EXISTS idx_marketing_content_created_by ON marketing_content(created_by);
CREATE INDEX IF NOT EXISTS idx_content_performance_content_id ON content_performance(content_id);
CREATE INDEX IF NOT EXISTS idx_seo_tracking_content_id ON seo_tracking(content_id);
CREATE INDEX IF NOT EXISTS idx_seo_tracking_keyword ON seo_tracking(keyword);
CREATE INDEX IF NOT EXISTS idx_social_posts_account_id ON social_media_posts(account_id);
CREATE INDEX IF NOT EXISTS idx_social_posts_status ON social_media_posts(status);
CREATE INDEX IF NOT EXISTS idx_referral_codes_code ON referral_codes(code);
CREATE INDEX IF NOT EXISTS idx_referral_tracking_code_id ON referral_tracking(referral_code_id);
CREATE INDEX IF NOT EXISTS idx_community_posts_author_id ON community_posts(author_id);
CREATE INDEX IF NOT EXISTS idx_community_posts_created_at ON community_posts(created_at);
CREATE INDEX IF NOT EXISTS idx_community_comments_post_id ON community_comments(post_id);
CREATE INDEX IF NOT EXISTS idx_ab_tests_status ON ab_tests(status);
CREATE INDEX IF NOT EXISTS idx_email_campaigns_status ON email_campaigns(status);
CREATE INDEX IF NOT EXISTS idx_email_subscribers_status ON email_subscribers(status);
CREATE INDEX IF NOT EXISTS idx_marketing_analytics_date ON marketing_analytics(date_recorded);
CREATE INDEX IF NOT EXISTS idx_marketing_analytics_metric ON marketing_analytics(metric_name);

-- Enable Row Level Security (RLS)
ALTER TABLE marketing_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_performance ENABLE ROW LEVEL SECURITY;
ALTER TABLE seo_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_media_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_media_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE referral_codes ENABLE ROW LEVEL SECURITY;
ALTER TABLE referral_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE ab_tests ENABLE ROW LEVEL SECURITY;
ALTER TABLE ab_test_variants ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_subscribers ENABLE ROW LEVEL SECURITY;
ALTER TABLE influencer_partnerships ENABLE ROW LEVEL SECURITY;
ALTER TABLE influencer_campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE marketing_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversion_funnels ENABLE ROW LEVEL SECURITY;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_marketing_content_updated_at BEFORE UPDATE ON marketing_content FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_community_posts_updated_at BEFORE UPDATE ON community_posts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_community_comments_updated_at BEFORE UPDATE ON community_comments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ab_tests_updated_at BEFORE UPDATE ON ab_tests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_email_campaigns_updated_at BEFORE UPDATE ON email_campaigns FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_influencer_partnerships_updated_at BEFORE UPDATE ON influencer_partnerships FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_influencer_campaigns_updated_at BEFORE UPDATE ON influencer_campaigns FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_conversion_funnels_updated_at BEFORE UPDATE ON conversion_funnels FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();