"""
Cross-Chain Asset Management
Ko'p zanjirli portfolio boshqaruv, likvidlik va yield farming tizimi
"""

import asyncio
import json
import time
import statistics
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

class AssetType(Enum):
    """Asset turlari"""
    NATIVE = "native"
    WRAPPED = "wrapped"
    SYNTHETIC = "synthetic"
    LP_TOKEN = "lp_token"
    YIELD_TOKEN = "yield_token"

class RebalanceTrigger(Enum):
    """Rebalans triggerlari"""
    THRESHOLD_BREACH = "threshold_breach"
    TIME_BASED = "time_based"
    VOLATILITY_HIGH = "volatility_high"
    LIQUIDITY_LOW = "liquidity_low"
    YIELD_OPPORTUNITY = "yield_opportunity"

@dataclass
class Asset:
    """Asset ma'lumotlari"""
    symbol: str
    name: str
    asset_type: AssetType
    chains: List[str]  # Mavjud zanjirlar
    contract_addresses: Dict[str, str]  # chain -> address
    decimals: int
    total_supply: int
    price: Optional[float] = None
    last_price_update: Optional[int] = None
    metadata: Optional[Dict] = None

@dataclass
class Portfolio:
    """Portfolio ma'lumotlari"""
    owner: str
    assets: Dict[str, Asset]
    chains: Dict[str, Dict[str, float]]  # chain -> symbol -> amount
    total_value_usd: float
    last_rebalance: Optional[int] = None
    target_allocation: Optional[Dict[str, float]] = None
    risk_score: float = 0.0

@dataclass
class LiquidityPool:
    """Likvidlik pooli ma'lumotlari"""
    pool_id: str
    asset_a: str
    asset_b: str
    chain: str
    total_liquidity: float
    apy: float
    impermanent_loss: float
    volume_24h: float
    fee_tier: float
    contract_address: str

@dataclass
class YieldOpportunity:
    """Yield farming imkoniyati"""
    strategy_id: str
    name: str
    chains: List[str]
    assets: List[str]
    apy: float
    risk_level: float
    min_investment: float
    lock_period: int  # seconds
    protocol: str
    description: str

class CrossChainAssetManager:
    """Cross-chain asset boshqaruvchisi"""
    
    def __init__(self):
        self.portfolios = {}
        self.assets = {}
        self.liquidity_pools = {}
        self.yield_opportunities = {}
        self.rebalance_rules = {}
        
        self.logger = logging.getLogger(__name__)
        self.max_portfolio_assets = 20
        self.min_liquidity_ratio = 0.1  # 10%
        self.max_slippage = 0.005  # 0.5%
        self.rebalance_threshold = 0.05  # 5%
        
        self._initialize_default_assets()
        self._initialize_liquidity_pools()
        self._initialize_yield_strategies()
    
    def _initialize_default_assets(self):
        """Standart assetlarni ishga tushirish"""
        
        # ETH - barcha zanjirlarda
        self.assets["ETH"] = Asset(
            symbol="ETH",
            name="Ethereum",
            asset_type=AssetType.NATIVE,
            chains=["ethereum", "bsc", "polygon", "arbitrum", "optimism"],
            contract_addresses={
                "ethereum": "0x0000000000000000000000000000000000000000",
                "bsc": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
                "polygon": "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",
                "arbitrum": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
                "optimism": "0xDeadDeAddeAddEAddeadDEaDDEAdDeaDDeAD0000"
            },
            decimals=18,
            total_supply=120_000_000,
            metadata={"category": "Layer 1", "staking_available": True}
        )
        
        # USDC - stablecoin
        self.assets["USDC"] = Asset(
            symbol="USDC",
            name="USD Coin",
            asset_type=AssetType.WRAPPED,
            chains=["ethereum", "bsc", "polygon", "arbitrum", "optimism"],
            contract_addresses={
                "ethereum": "0xA0b86a33E6441E8d16B43B82cE5b8a14a4B1F8B9",
                "bsc": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
                "polygon": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
                "arbitrum": "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",
                "optimism": "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85"
            },
            decimals=6,
            total_supply=50_000_000_000,
            metadata={"category": "Stablecoin", "peg": "USD"}
        )
        
        # USDT
        self.assets["USDT"] = Asset(
            symbol="USDT",
            name="Tether",
            asset_type=AssetType.WRAPPED,
            chains=["ethereum", "bsc", "polygon", "arbitrum"],
            contract_addresses={
                "ethereum": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                "bsc": "0x55d398326f99059fF775485246999027B3197955",
                "polygon": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
                "arbitrum": "0xFD086bc7CD5C481DCC9C85ebE478A1C0b69FCbb9"
            },
            decimals=6,
            total_supply=75_000_000_000,
            metadata={"category": "Stablecoin", "peg": "USD"}
        )
        
        # WBTC - wrapped Bitcoin
        self.assets["WBTC"] = Asset(
            symbol="WBTC",
            name="Wrapped Bitcoin",
            asset_type=AssetType.WRAPPED,
            chains=["ethereum", "polygon", "arbitrum"],
            contract_addresses={
                "ethereum": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
                "polygon": "0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6",
                "arbitrum": "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f"
            },
            decimals=8,
            total_supply=150_000,
            metadata={"category": "Wrapped Asset", "underlying": "BTC"}
        )
        
        print(f"✅ {len(self.assets)} standart asset yuklandi")
    
    def _initialize_liquidity_pools(self):
        """Likvidlik poolini ishga tushirish"""
        
        self.liquidity_pools = {
            "ETH_USDC_ethereum": LiquidityPool(
                pool_id="ETH_USDC_ethereum",
                asset_a="ETH",
                asset_b="USDC",
                chain="ethereum",
                total_liquidity=10_000_000,  # $10M
                apy=0.12,  # 12%
                impermanent_loss=0.02,  # 2%
                volume_24h=2_000_000,  # $2M
                fee_tier=0.003,  # 0.3%
                contract_address="0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc"
            ),
            "ETH_USDC_bsc": LiquidityPool(
                pool_id="ETH_USDC_bsc",
                asset_a="ETH",
                asset_b="USDC",
                chain="bsc",
                total_liquidity=8_000_000,  # $8M
                apy=0.15,  # 15%
                impermanent_loss=0.025,  # 2.5%
                volume_24h=1_500_000,  # $1.5M
                fee_tier=0.0025,  # 0.25%
                contract_address="0x16b9a82891338f9bA80E2D96Ff04E44c0648a71"
            ),
            "USDC_USDT_polygon": LiquidityPool(
                pool_id="USDC_USDT_polygon",
                asset_a="USDC",
                asset_b="USDT",
                chain="polygon",
                total_liquidity=5_000_000,  # $5M
                apy=0.08,  # 8%
                impermanent_loss=0.001,  # 0.1% (stable-stable)
                volume_24h=1_000_000,  # $1M
                fee_tier=0.001,  # 0.1%
                contract_address="0xA374094527e1673A86dE6253Bdbb0Dda9698E4F9"
            )
        }
        
        print(f"✅ {len(self.liquidity_pools)} likvidlik pool yuklandi")
    
    def _initialize_yield_strategies(self):
        """Yield farming strategiyalarini ishga tushirish"""
        
        self.yield_opportunities = {
            "eth_staking_ethereum": YieldOpportunity(
                strategy_id="eth_staking_ethereum",
                name="ETH Staking Ethereum",
                chains=["ethereum"],
                assets=["ETH"],
                apy=0.04,  # 4%
                risk_level=0.2,  # Low risk
                min_investment=0.1,  # 0.1 ETH
                lock_period=0,  # No lock
                protocol="Lido",
                description="ETH'ni Lido orqali stake qilish, 4% yillik daromad"
            ),
            "eth_usdc_lp_pancakeswap": YieldOpportunity(
                strategy_id="eth_usdc_lp_pancakeswap",
                name="ETH-USDC LP PancakeSwap",
                chains=["bsc"],
                assets=["ETH", "USDC"],
                apy=0.25,  # 25%
                risk_level=0.6,  # Medium-high risk
                min_investment=100,  # $100
                lock_period=604800,  # 7 days
                protocol="PancakeSwap",
                description="PancakeSwap'da ETH-USDC LP token, farming qilish"
            ),
            "usdc_lending_compound": YieldOpportunity(
                strategy_id="usdc_lending_compound",
                name="USDC Lending Compound",
                chains=["ethereum"],
                assets=["USDC"],
                apy=0.03,  # 3%
                risk_level=0.15,  # Low risk
                min_investment=50,  # $50
                lock_period=0,  # Flexible
                protocol="Compound",
                description="USDC'ni Compound'da qarz berish, stable daromad"
            ),
            "multi_chain_yield": YieldOpportunity(
                strategy_id="multi_chain_yield",
                name="Multi-Chain Yield Farming",
                chains=["ethereum", "polygon", "arbitrum"],
                assets=["ETH", "USDC"],
                apy=0.18,  # 18%
                risk_level=0.5,  # Medium risk
                min_investment=200,  # $200
                lock_period=2592000,  # 30 days
                protocol="Yearn Finance",
                description="Ko'p zanjirli yield farming, Yearn Finance orqali"
            )
        }
        
        print(f"✅ {len(self.yield_opportunities)} yield strategiya yuklandi")
    
    async def create_portfolio(self, owner: str, initial_assets: Dict[str, Dict[str, float]]) -> Portfolio:
        """Portfolio yaratish"""
        
        portfolio = Portfolio(
            owner=owner,
            assets={},
            chains={},
            total_value_usd=0.0
        )
        
        # Asset'larni qo'shish
        for symbol, chain_balances in initial_assets.items():
            if symbol in self.assets:
                asset = self.assets[symbol]
                portfolio.assets[symbol] = asset
                
                for chain, amount in chain_balances.items():
                    if chain not in portfolio.chains:
                        portfolio.chains[chain] = {}
                    
                    portfolio.chains[chain][symbol] = amount
        
        # Jami qiymatni hisoblash
        await self._calculate_portfolio_value(portfolio)
        
        self.portfolios[owner] = portfolio
        
        print(f"✅ Portfolio yaratildi: {owner}")
        print(f"   Jami qiymat: ${portfolio.total_value_usd:,.2f}")
        print(f"   Asset soni: {len(portfolio.assets)}")
        print(f"   Zanjirlar: {list(portfolio.chains.keys())}")
        
        return portfolio
    
    async def _calculate_portfolio_value(self, portfolio: Portfolio):
        """Portfolio qiymatini hisoblash"""
        
        total_value = 0.0
        
        for chain, assets in portfolio.chains.items():
            for symbol, amount in assets.items():
                if symbol in self.assets:
                    asset = self.assets[symbol]
                    
                    # Narx olish (simulated)
                    if asset.symbol == "ETH":
                        price = 2345.67
                    elif asset.symbol == "USDC":
                        price = 1.0
                    elif asset.symbol == "USDT":
                        price = 1.0
                    elif asset.symbol == "WBTC":
                        price = 45678.90
                    else:
                        price = 0.0
                    
                    # USD qiymat
                    usd_value = amount * price / (10 ** asset.decimals)
                    total_value += usd_value
        
        portfolio.total_value_usd = total_value
    
    async def rebalance_portfolio(
        self,
        owner: str,
        target_allocation: Dict[str, float],
        trigger: RebalanceTrigger = RebalanceTrigger.THRESHOLD_BREACH
    ) -> Dict:
        """Portfolio rebalancing"""
        
        if owner not in self.portfolios:
            raise ValueError("Portfolio topilmadi")
        
        portfolio = self.portfolios[owner]
        portfolio.target_allocation = target_allocation
        
        # Rebalans analizi
        analysis = await self._analyze_rebalance_needs(portfolio, target_allocation)
        
        if not analysis["needs_rebalance"]:
            return {
                "success": True,
                "message": "Rebalans kerak emas",
                "actions": []
            }
        
        # Rebalans harakatlari
        actions = await self._execute_rebalance(portfolio, analysis)
        
        portfolio.last_rebalance = int(time.time())
        
        # Yangi qiymatni hisoblash
        await self._calculate_portfolio_value(portfolio)
        
        result = {
            "success": True,
            "message": "Rebalans tugallandi",
            "actions": actions,
            "old_value": analysis["old_value"],
            "new_value": portfolio.total_value_usd,
            "cost_usd": analysis["rebalance_cost"],
            "trigger": trigger.value
        }
        
        print(f"🔄 Portfolio rebalanced: {owner}")
        print(f"   Harakatlar soni: {len(actions)}")
        print(f"   Xarajat: ${analysis['rebalance_cost']:.2f}")
        
        return result
    
    async def _analyze_rebalance_needs(self, portfolio: Portfolio, target_allocation: Dict[str, float]) -> Dict:
        """Rebalans ehtiyojini tahlil qilish"""
        
        await self._calculate_portfolio_value(portfolio)
        current_value = portfolio.total_value_usd
        
        # Current allocation
        current_allocation = {}
        for chain, assets in portfolio.chains.items():
            for symbol, amount in assets.items():
                if symbol in self.assets:
                    asset = self.assets[symbol]
                    # Simple price assumption
                    price = self._get_mock_price(symbol)
                    usd_value = amount * price / (10 ** asset.decimals)
                    current_allocation[symbol] = current_allocation.get(symbol, 0) + usd_value
        
        # Convert to percentages
        for symbol in current_allocation:
            current_allocation[symbol] = current_allocation[symbol] / current_value
        
        # Compare with target
        needs_rebalance = False
        rebalance_actions = []
        total_deviation = 0.0
        
        # Check deviations
        for symbol, target_pct in target_allocation.items():
            current_pct = current_allocation.get(symbol, 0)
            deviation = abs(current_pct - target_pct)
            total_deviation += deviation
            
            if deviation > self.rebalance_threshold:
                needs_rebalance = True
                rebalance_actions.append({
                    "symbol": symbol,
                    "current_allocation": current_pct,
                    "target_allocation": target_pct,
                    "deviation": deviation,
                    "action": "buy" if current_pct < target_pct else "sell"
                })
        
        # Estimate rebalance cost
        rebalance_cost = total_deviation * current_value * 0.002  # 0.2% fee estimate
        
        return {
            "needs_rebalance": needs_rebalance,
            "actions": rebalance_actions,
            "current_allocation": current_allocation,
            "target_allocation": target_allocation,
            "old_value": current_value,
            "rebalance_cost": rebalance_cost,
            "total_deviation": total_deviation
        }
    
    def _get_mock_price(self, symbol: str) -> float:
        """Mock narx olish"""
        prices = {
            "ETH": 2345.67,
            "USDC": 1.0,
            "USDT": 1.0,
            "WBTC": 45678.90
        }
        return prices.get(symbol, 0.0)
    
    async def _execute_rebalance(self, portfolio: Portfolio, analysis: Dict) -> List[Dict]:
        """Rebalans harakatlarini bajarish"""
        
        actions = []
        rebalance_actions = analysis["actions"]
        
        for action in rebalance_actions:
            symbol = action["symbol"]
            action_type = action["action"]
            
            # Simple rebalance logic
            if action_type == "sell" and symbol in portfolio.chains:
                # Sell excess amount
                chain = list(portfolio.chains.keys())[0]  # Simple
                current_amount = portfolio.chains[chain].get(symbol, 0)
                
                # Calculate sell amount based on deviation
                target_value = analysis["old_value"] * action["target_allocation"]
                current_value = current_amount * self._get_mock_price(symbol) / (10 ** self.assets[symbol].decimals)
                excess_value = current_value - target_value
                
                if excess_value > 0:
                    sell_amount = excess_value * (10 ** self.assets[symbol].decimals) / self._get_mock_price(symbol)
                    portfolio.chains[chain][symbol] -= sell_amount
                    
                    actions.append({
                        "type": "sell",
                        "symbol": symbol,
                        "chain": chain,
                        "amount": sell_amount,
                        "estimated_value_usd": excess_value
                    })
            
            elif action_type == "buy":
                # Buy missing amount
                target_value = analysis["old_value"] * action["target_allocation"]
                current_value = 0  # Assume zero if not holding
                missing_value = target_value - current_value
                
                if missing_value > 0:
                    buy_amount = missing_value * (10 ** self.assets[symbol].decimals) / self._get_mock_price(symbol)
                    
                    # Add to first available chain
                    if symbol in self.assets:
                        first_chain = self.assets[symbol].chains[0]
                        if first_chain not in portfolio.chains:
                            portfolio.chains[first_chain] = {}
                        
                        portfolio.chains[first_chain][symbol] = portfolio.chains[first_chain].get(symbol, 0) + buy_amount
                        
                        actions.append({
                            "type": "buy",
                            "symbol": symbol,
                            "chain": first_chain,
                            "amount": buy_amount,
                            "estimated_value_usd": missing_value
                        })
        
        return actions
    
    async def optimize_yield_farming(self, owner: str, risk_tolerance: float = 0.5) -> Dict:
        """Yield farming optimizatsiyasi"""
        
        if owner not in self.portfolios:
            raise ValueError("Portfolio topilmadi")
        
        portfolio = self.portfolios[owner]
        await self._calculate_portfolio_value(portfolio)
        
        # Available yield opportunities (filtered by risk tolerance)
        suitable_opportunities = []
        for strategy in self.yield_opportunities.values():
            if strategy.risk_level <= risk_tolerance:
                suitable_opportunities.append(strategy)
        
        # Sort by risk-adjusted return
        suitable_opportunities.sort(
            key=lambda x: (x.apy * (1 - x.risk_level)), 
            reverse=True
        )
        
        # Generate optimization recommendations
        recommendations = []
        total_allocation = 0.0
        max_allocation = min(portfolio.total_value_usd * 0.3, 10000)  # Max 30% of portfolio or $10k
        
        for strategy in suitable_opportunities[:5]:  # Top 5 strategies
            if total_allocation >= max_allocation:
                break
            
            # Calculate allocation based on APY and risk
            allocation = min(
                max_allocation * (strategy.apy * (1 - strategy.risk_level)),
                strategy.min_investment * 3
            )
            
            if allocation >= strategy.min_investment:
                recommendations.append({
                    "strategy_id": strategy.strategy_id,
                    "name": strategy.name,
                    "recommended_allocation_usd": allocation,
                    "expected_apy": strategy.apy,
                    "risk_level": strategy.risk_level,
                    "protocol": strategy.protocol,
                    "chains": strategy.chains,
                    "lock_period_days": strategy.lock_period // 86400
                })
                
                total_allocation += allocation
        
        result = {
            "success": True,
            "total_portfolio_value": portfolio.total_value_usd,
            "risk_tolerance": risk_tolerance,
            "total_recommended_allocation": total_allocation,
            "allocation_percentage": (total_allocation / portfolio.total_value_usd) * 100,
            "strategies": recommendations,
            "expected_total_apy": sum(r["expected_apy"] * r["recommended_allocation_usd"] / total_allocation 
                                   for r in recommendations) if total_allocation > 0 else 0
        }
        
        print(f"🎯 Yield farming optimizatsiyasi: {owner}")
        print(f"   Tavsiya qilingan strategiya: {len(recommendations)}")
        print(f"   Umumiy allocation: ${total_allocation:,.2f}")
        
        return result
    
    async def add_liquidity(
        self,
        owner: str,
        pool_id: str,
        amount_a: float,
        amount_b: float,
        chain: str
    ) -> Dict:
        """Likvidlik qo'shish"""
        
        if owner not in self.portfolios:
            raise ValueError("Portfolio topilmadi")
        
        if pool_id not in self.liquidity_pools:
            raise ValueError("Pool topilmadi")
        
        pool = self.liquidity_pools[pool_id]
        portfolio = self.portfolios[owner]
        
        # Check if user has sufficient balance
        asset_a_balance = portfolio.chains.get(chain, {}).get(pool.asset_a, 0)
        asset_b_balance = portfolio.chains.get(chain, {}).get(pool.asset_b, 0)
        
        if asset_a_balance < amount_a or asset_b_balance < amount_b:
            raise ValueError("Yetarli balans yo'q")
        
        # Add liquidity simulation
        shares_minted = self._calculate_lp_shares(amount_a, amount_b, pool)
        
        # Update portfolio
        portfolio.chains[chain][pool.asset_a] -= amount_a
        portfolio.chains[chain][pool.asset_b] -= amount_b
        
        # Add LP tokens (if we tracked them)
        if "LP_TOKENS" not in portfolio.chains:
            portfolio.chains["LP_TOKENS"] = {}
        
        lp_token_id = f"{pool_id}_SHARE"
        portfolio.chains["LP_TOKENS"][lp_token_id] = portfolio.chains["LP_TOKENS"].get(lp_token_id, 0) + shares_minted
        
        # Update pool liquidity
        pool.total_liquidity += (amount_a + amount_b) / 2  # Simplified
        
        result = {
            "success": True,
            "pool_id": pool_id,
            "chain": chain,
            "amount_a": amount_a,
            "amount_b": amount_b,
            "shares_minted": shares_minted,
            "pool_apy": pool.apy,
            "impermanent_loss": pool.impermanent_loss
        }
        
        print(f"💧 Likvidlik qo'shildi: {pool_id}")
        print(f"   LP token: {shares_minted:.4f}")
        
        return result
    
    def _calculate_lp_shares(self, amount_a: float, amount_b: float, pool: LiquidityPool) -> float:
        """LP token hisoblash"""
        # Simplified calculation
        total_value = amount_a * 2 + amount_b  # Simplified
        shares = total_value * 0.95  # 5% fee
        
        return shares
    
    def get_portfolio_analytics(self, owner: str) -> Dict:
        """Portfolio tahlili"""
        
        if owner not in self.portfolios:
            raise ValueError("Portfolio topilmadi")
        
        portfolio = self.portfolios[owner]
        
        # Basic analytics
        total_value = portfolio.total_value_usd
        asset_count = len(portfolio.assets)
        chain_count = len(portfolio.chains)
        
        # Risk metrics
        risk_score = self._calculate_risk_score(portfolio)
        
        # Performance metrics
        performance = self._calculate_performance_metrics(portfolio)
        
        # Diversification
        diversification = self._calculate_diversification(portfolio)
        
        return {
            "owner": owner,
            "total_value_usd": total_value,
            "asset_count": asset_count,
            "chain_count": chain_count,
            "risk_score": risk_score,
            "performance": performance,
            "diversification": diversification,
            "last_rebalance": portfolio.last_rebalance,
            "chains": list(portfolio.chains.keys())
        }
    
    def _calculate_risk_score(self, portfolio: Portfolio) -> float:
        """Risk ball hisoblash"""
        
        # Simplified risk calculation
        # Har bir asset uchun risk ball, so'ngra weighted average
        
        asset_risks = {
            "ETH": 0.3,
            "USDC": 0.1,
            "USDT": 0.15,
            "WBTC": 0.4
        }
        
        total_value = portfolio.total_value_usd
        if total_value == 0:
            return 0.0
        
        weighted_risk = 0.0
        
        for chain, assets in portfolio.chains.items():
            for symbol, amount in assets.items():
                if symbol in asset_risks and symbol != "LP_TOKENS":
                    asset_value = amount * self._get_mock_price(symbol) / (10 ** self.assets[symbol].decimals)
                    weight = asset_value / total_value
                    weighted_risk += asset_risks[symbol] * weight
        
        return weighted_risk
    
    def _calculate_performance_metrics(self, portfolio: Portfolio) -> Dict:
        """Performance metrikalar"""
        
        # Simplified performance calculation
        # Haqiqiy implementatsiyada tarixiy narx ma'lumotlari kerak
        
        return {
            "daily_return": 0.001,  # 0.1%
            "weekly_return": 0.007,  # 0.7%
            "monthly_return": 0.031,  # 3.1%
            "sharpe_ratio": 1.5,
            "max_drawdown": 0.05,  # 5%
            "volatility": 0.12  # 12%
        }
    
    def _calculate_diversification(self, portfolio: Portfolio) -> Dict:
        """Diversifikatsiya metrikalari"""
        
        total_value = portfolio.total_value_usd
        
        # Asset diversification
        asset_values = {}
        for chain, assets in portfolio.chains.items():
            for symbol, amount in assets.items():
                if symbol != "LP_TOKENS":
                    asset_value = amount * self._get_mock_price(symbol) / (10 ** self.assets[symbol].decimals)
                    asset_values[symbol] = asset_values.get(symbol, 0) + asset_value
        
        # Chain diversification
        chain_values = {}
        for chain, assets in portfolio.chains.items():
            if chain != "LP_TOKENS":
                chain_value = sum(
                    amount * self._get_mock_price(symbol) / (10 ** self.assets[symbol].decimals)
                    for symbol, amount in assets.items() if symbol in self.assets
                )
                chain_values[chain] = chain_value
        
        return {
            "asset_diversification": {
                "concentration_ratio": max(asset_values.values()) / total_value if total_value > 0 else 0,
                "num_assets": len(asset_values),
                "largest_allocation": max(asset_values.values()) / total_value if total_value > 0 else 0
            },
            "chain_diversification": {
                "concentration_ratio": max(chain_values.values()) / total_value if total_value > 0 else 0,
                "num_chains": len(chain_values),
                "largest_allocation": max(chain_values.values()) / total_value if total_value > 0 else 0
            }
        }
    
    def get_all_pools(self) -> List[Dict]:
        """Barcha poolarni olish"""
        
        return [asdict(pool) for pool in self.liquidity_pools.values()]
    
    def get_all_yield_strategies(self) -> List[Dict]:
        """Barcha yield strategiyalarni olish"""
        
        return [asdict(strategy) for strategy in self.yield_opportunities.values()]
    
    def get_portfolio_summary(self, owner: str) -> Optional[Dict]:
        """Portfolio xulosasi"""
        
        if owner not in self.portfolios:
            return None
        
        portfolio = self.portfolios[owner]
        
        # Calculate holdings by chain
        chain_summary = {}
        for chain, assets in portfolio.chains.items():
            if chain != "LP_TOKENS":
                chain_value = sum(
                    amount * self._get_mock_price(symbol) / (10 ** self.assets[symbol].decimals)
                    for symbol, amount in assets.items() if symbol in self.assets
                )
                chain_summary[chain] = {
                    "value_usd": chain_value,
                    "assets": list(assets.keys())
                }
        
        return {
            "owner": owner,
            "total_value_usd": portfolio.total_value_usd,
            "chains": chain_summary,
            "last_updated": int(time.time())
        }