-- ORION STARLINE PHASE 4.2: DeFi 2.0 DATABASE SCHEMA
-- Enterprise-grade DeFi protocol integration
-- Cross-chain bridge, yield optimization, arbitrage tracking
-- Generated: 2025-11-06 05:42:17

-- ============================================
-- CROSS-CHAIN BRIDGE TABLES
-- ============================================

-- Bridge transactions tracking
CREATE TABLE IF NOT EXISTS bridge_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Bridge details
    source_chain VARCHAR(50) NOT NULL,
    destination_chain VARCHAR(50) NOT NULL,
    bridge_protocol VARCHAR(100) NOT NULL, -- Hop, Across, Multichain
    
    -- Transaction details
    token_symbol VARCHAR(20) NOT NULL,
    amount DECIMAL(36, 18) NOT NULL,
    source_tx_hash VARCHAR(255),
    destination_tx_hash VARCHAR(255),
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
    bridge_fee DECIMAL(18, 8),
    estimated_time INTEGER, -- minutes
    actual_time INTEGER,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Cross-chain arbitrage opportunities
CREATE TABLE IF NOT EXISTS cross_chain_arbitrage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Opportunity details
    token_symbol VARCHAR(20) NOT NULL,
    source_chain VARCHAR(50) NOT NULL,
    source_dex VARCHAR(100) NOT NULL,
    source_price DECIMAL(18, 8) NOT NULL,
    
    destination_chain VARCHAR(50) NOT NULL,
    destination_dex VARCHAR(100) NOT NULL,
    destination_price DECIMAL(18, 8) NOT NULL,
    
    -- Profit calculation
    price_difference DECIMAL(10, 4) NOT NULL, -- percentage
    estimated_profit DECIMAL(18, 8),
    total_fees DECIMAL(18, 8), -- gas + bridge fees
    net_profit DECIMAL(18, 8),
    
    -- Risk assessment
    risk_level VARCHAR(20), -- low, medium, high
    liquidity_score DECIMAL(5, 2),
    
    -- Metadata
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '5 minutes'
);

-- ============================================
-- YIELD OPTIMIZATION TABLES
-- ============================================

-- DeFi protocol yield tracking
CREATE TABLE IF NOT EXISTS defi_protocol_yields (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Protocol details
    protocol_name VARCHAR(100) NOT NULL,
    protocol_type VARCHAR(50) NOT NULL, -- lending, farming, staking
    chain VARCHAR(50) NOT NULL,
    pool_address VARCHAR(255),
    
    -- Token details
    token_symbol VARCHAR(20) NOT NULL,
    token_pair VARCHAR(50), -- for LP tokens
    
    -- Yield metrics
    apy DECIMAL(10, 4) NOT NULL,
    tvl DECIMAL(36, 18),
    daily_volume DECIMAL(36, 18),
    
    -- Risk metrics
    risk_score DECIMAL(5, 2),
    impermanent_loss_risk DECIMAL(10, 4),
    smart_contract_risk VARCHAR(20),
    
    -- Additional info
    min_deposit DECIMAL(18, 8),
    lock_period INTEGER, -- days
    auto_compound BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User yield positions
CREATE TABLE IF NOT EXISTS user_yield_positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    protocol_yield_id UUID REFERENCES defi_protocol_yields(id),
    
    -- Position details
    amount_deposited DECIMAL(36, 18) NOT NULL,
    current_value DECIMAL(36, 18),
    
    -- Performance tracking
    total_earned DECIMAL(36, 18) DEFAULT 0,
    apy_at_entry DECIMAL(10, 4),
    current_apy DECIMAL(10, 4),
    
    -- Status
    status VARCHAR(50) DEFAULT 'active', -- active, withdrawn, rebalancing
    auto_rebalance BOOLEAN DEFAULT true,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_compounded_at TIMESTAMPTZ,
    withdrawn_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Yield optimization strategies
CREATE TABLE IF NOT EXISTS yield_strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Strategy details
    name VARCHAR(200) NOT NULL,
    strategy_type VARCHAR(50) NOT NULL, -- conservative, balanced, aggressive
    
    -- Allocation rules
    min_apy DECIMAL(10, 4),
    max_risk_score DECIMAL(5, 2),
    preferred_protocols JSONB, -- array of protocol names
    preferred_chains JSONB, -- array of chains
    
    -- Rebalancing rules
    auto_rebalance BOOLEAN DEFAULT true,
    rebalance_threshold DECIMAL(10, 4), -- percentage difference
    min_rebalance_amount DECIMAL(18, 8),
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    total_allocated DECIMAL(36, 18) DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- MULTI-CHAIN WALLET TABLES
-- ============================================

-- Multi-chain wallet connections
CREATE TABLE IF NOT EXISTS user_wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Wallet details
    wallet_address VARCHAR(255) NOT NULL,
    wallet_type VARCHAR(50) NOT NULL, -- metamask, walletconnect, phantom, ledger
    chain VARCHAR(50) NOT NULL,
    
    -- Status
    is_primary BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    
    -- Metadata
    label VARCHAR(100),
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id, wallet_address, chain)
);

-- Multi-chain balances
CREATE TABLE IF NOT EXISTS wallet_balances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wallet_id UUID REFERENCES user_wallets(id) ON DELETE CASCADE,
    
    -- Asset details
    token_symbol VARCHAR(20) NOT NULL,
    token_address VARCHAR(255),
    chain VARCHAR(50) NOT NULL,
    
    -- Balance
    balance DECIMAL(36, 18) NOT NULL,
    usd_value DECIMAL(18, 8),
    
    -- Metadata
    last_synced_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Cross-chain transaction history
CREATE TABLE IF NOT EXISTS wallet_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wallet_id UUID REFERENCES user_wallets(id) ON DELETE CASCADE,
    
    -- Transaction details
    tx_hash VARCHAR(255) NOT NULL,
    chain VARCHAR(50) NOT NULL,
    tx_type VARCHAR(50) NOT NULL, -- transfer, swap, bridge, stake, farm
    
    -- Amounts
    from_token VARCHAR(20),
    from_amount DECIMAL(36, 18),
    to_token VARCHAR(20),
    to_amount DECIMAL(36, 18),
    
    -- Gas tracking
    gas_used DECIMAL(18, 8),
    gas_price_gwei DECIMAL(18, 8),
    total_fee_usd DECIMAL(18, 8),
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    block_number BIGINT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(tx_hash, chain)
);

-- ============================================
-- DEFI PROTOCOL INTEGRATION TABLES
-- ============================================

-- Supported DeFi protocols
CREATE TABLE IF NOT EXISTS defi_protocols (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Protocol info
    name VARCHAR(100) NOT NULL UNIQUE,
    protocol_type VARCHAR(50) NOT NULL, -- dex, lending, yield, bridge, staking
    chain VARCHAR(50) NOT NULL,
    
    -- Contract addresses
    router_address VARCHAR(255),
    factory_address VARCHAR(255),
    staking_address VARCHAR(255),
    
    -- Metadata
    website_url VARCHAR(255),
    api_endpoint VARCHAR(255),
    logo_url VARCHAR(255),
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    tvl DECIMAL(36, 18),
    daily_volume DECIMAL(36, 18),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Flash loan opportunities
CREATE TABLE IF NOT EXISTS flash_loan_opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Opportunity details
    protocol VARCHAR(100) NOT NULL, -- Aave, dYdX
    chain VARCHAR(50) NOT NULL,
    token_symbol VARCHAR(20) NOT NULL,
    
    -- Loan details
    max_loan_amount DECIMAL(36, 18),
    fee_percentage DECIMAL(10, 4),
    
    -- Arbitrage path
    dex_path JSONB, -- array of DEX steps
    estimated_profit DECIMAL(18, 8),
    profit_percentage DECIMAL(10, 4),
    
    -- Risk assessment
    risk_level VARCHAR(20),
    execution_probability DECIMAL(5, 2),
    
    -- Status
    is_executable BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '2 minutes'
);

-- MEV protection tracking
CREATE TABLE IF NOT EXISTS mev_protection_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Transaction details
    tx_hash VARCHAR(255),
    chain VARCHAR(50) NOT NULL,
    
    -- MEV details
    mev_type VARCHAR(50), -- frontrun, backrun, sandwich
    protected BOOLEAN DEFAULT false,
    protection_method VARCHAR(100), -- flashbots, private_mempool
    
    -- Impact
    potential_loss DECIMAL(18, 8),
    actual_loss DECIMAL(18, 8),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Gas optimization tracking
CREATE TABLE IF NOT EXISTS gas_optimization_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Transaction details
    tx_hash VARCHAR(255),
    chain VARCHAR(50) NOT NULL,
    operation_type VARCHAR(50), -- swap, bridge, stake
    
    -- Gas metrics
    estimated_gas DECIMAL(18, 8),
    actual_gas DECIMAL(18, 8),
    gas_price_gwei DECIMAL(18, 8),
    
    -- Optimization
    optimization_applied BOOLEAN DEFAULT false,
    optimization_method VARCHAR(100),
    gas_saved DECIMAL(18, 8),
    cost_saved_usd DECIMAL(18, 8),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Bridge transactions
CREATE INDEX idx_bridge_tx_user ON bridge_transactions(user_id);
CREATE INDEX idx_bridge_tx_status ON bridge_transactions(status);
CREATE INDEX idx_bridge_tx_created ON bridge_transactions(created_at DESC);

-- Cross-chain arbitrage
CREATE INDEX idx_arbitrage_active ON cross_chain_arbitrage(is_active, created_at DESC);
CREATE INDEX idx_arbitrage_profit ON cross_chain_arbitrage(net_profit DESC);
CREATE INDEX idx_arbitrage_expires ON cross_chain_arbitrage(expires_at);

-- Protocol yields
CREATE INDEX idx_protocol_yields_chain ON defi_protocol_yields(chain);
CREATE INDEX idx_protocol_yields_apy ON defi_protocol_yields(apy DESC);
CREATE INDEX idx_protocol_yields_updated ON defi_protocol_yields(updated_at DESC);

-- User positions
CREATE INDEX idx_user_positions_user ON user_yield_positions(user_id);
CREATE INDEX idx_user_positions_status ON user_yield_positions(status);

-- Wallets
CREATE INDEX idx_wallets_user ON user_wallets(user_id);
CREATE INDEX idx_wallets_chain ON user_wallets(chain);

-- Transactions
CREATE INDEX idx_wallet_tx_wallet ON wallet_transactions(wallet_id);
CREATE INDEX idx_wallet_tx_timestamp ON wallet_transactions(timestamp DESC);

-- Protocols
CREATE INDEX idx_protocols_type ON defi_protocols(protocol_type);
CREATE INDEX idx_protocols_chain ON defi_protocols(chain);

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================

-- Enable RLS
ALTER TABLE bridge_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_yield_positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE yield_strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE wallet_balances ENABLE ROW LEVEL SECURITY;
ALTER TABLE wallet_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE mev_protection_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE gas_optimization_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for user data
CREATE POLICY "Users can view own bridge transactions"
    ON bridge_transactions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own bridge transactions"
    ON bridge_transactions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own yield positions"
    ON user_yield_positions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own yield positions"
    ON user_yield_positions FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "Users can view own wallets"
    ON user_wallets FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own wallets"
    ON user_wallets FOR ALL
    USING (auth.uid() = user_id);

-- Public read for protocol data
CREATE POLICY "Anyone can view protocol yields"
    ON defi_protocol_yields FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Anyone can view arbitrage opportunities"
    ON cross_chain_arbitrage FOR SELECT
    TO authenticated
    USING (is_active = true);

CREATE POLICY "Anyone can view protocols"
    ON defi_protocols FOR SELECT
    TO authenticated
    USING (is_active = true);

-- ============================================
-- FUNCTIONS AND TRIGGERS
-- ============================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_bridge_transactions_updated_at
    BEFORE UPDATE ON bridge_transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_defi_protocol_yields_updated_at
    BEFORE UPDATE ON defi_protocol_yields
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_yield_positions_updated_at
    BEFORE UPDATE ON user_yield_positions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_yield_strategies_updated_at
    BEFORE UPDATE ON yield_strategies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Clean expired arbitrage opportunities
CREATE OR REPLACE FUNCTION clean_expired_arbitrage()
RETURNS void AS $$
BEGIN
    UPDATE cross_chain_arbitrage
    SET is_active = false
    WHERE expires_at < NOW() AND is_active = true;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- SEED DATA (Sample protocols)
-- ============================================

INSERT INTO defi_protocols (name, protocol_type, chain, is_active) VALUES
('Uniswap V3', 'dex', 'Ethereum', true),
('PancakeSwap', 'dex', 'BSC', true),
('SushiSwap', 'dex', 'Ethereum', true),
('Curve Finance', 'dex', 'Ethereum', true),
('Aave V3', 'lending', 'Ethereum', true),
('Compound V3', 'lending', 'Ethereum', true),
('MakerDAO', 'lending', 'Ethereum', true),
('Yearn Finance', 'yield', 'Ethereum', true),
('Convex Finance', 'yield', 'Ethereum', true),
('Beefy Finance', 'yield', 'BSC', true),
('Hop Protocol', 'bridge', 'Ethereum', true),
('Across Protocol', 'bridge', 'Ethereum', true),
('Multichain', 'bridge', 'Ethereum', true),
('Lido', 'staking', 'Ethereum', true),
('Rocket Pool', 'staking', 'Ethereum', true)
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- COMMENTS
-- ============================================

COMMENT ON TABLE bridge_transactions IS 'Cross-chain bridge transaction tracking';
COMMENT ON TABLE cross_chain_arbitrage IS 'Real-time cross-chain arbitrage opportunities';
COMMENT ON TABLE defi_protocol_yields IS 'DeFi protocol yield tracking across chains';
COMMENT ON TABLE user_yield_positions IS 'User positions in yield farming protocols';
COMMENT ON TABLE yield_strategies IS 'Automated yield optimization strategies';
COMMENT ON TABLE user_wallets IS 'Multi-chain wallet connections';
COMMENT ON TABLE wallet_balances IS 'Cross-chain token balances';
COMMENT ON TABLE wallet_transactions IS 'Multi-chain transaction history';
COMMENT ON TABLE defi_protocols IS 'Supported DeFi protocols registry';
COMMENT ON TABLE flash_loan_opportunities IS 'Flash loan arbitrage opportunities';
COMMENT ON TABLE mev_protection_logs IS 'MEV protection tracking and analysis';
COMMENT ON TABLE gas_optimization_logs IS 'Gas optimization metrics and savings';
