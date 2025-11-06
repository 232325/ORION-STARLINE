"""
Forex Hedging NFT Management System
NFT yaratish, boshqarish va tokenization
"""

import json
import hashlib
import base64
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import asyncio
import aiofiles
import logging

from config import ForexPair, HedgeType, NFTMetadata, config
from core.forex_hedge_core import ForexHedgeManager, MarketDataManager

@dataclass
class ForexNFTToken:
    """Forex NFT token"""
    token_id: str
    contract_address: Optional[str]
    owner: str
    metadata_uri: str
    created_at: int
    hedge_details: Dict
    performance_history: List[Dict]
    quantum_enhanced: bool

@dataclass
class HedgeInstrument:
    """Hedge instrument specification"""
    instrument_id: str
    pair: ForexPair
    hedge_type: HedgeType
    notional_amount: float
    entry_conditions: Dict
    exit_conditions: Dict
    risk_parameters: Dict
    quantum_features: Dict

class NFTTokenizationEngine:
    """NFT tokenization dvijogi"""
    
    def __init__(self, hedge_manager: ForexHedgeManager):
        self.hedge_manager = hedge_manager
        self.created_tokens: Dict[str, ForexNFTToken] = {}
        self.metadata_registry: Dict[str, Dict] = {}
        self.logger = logging.getLogger(__name__)
        
    async def tokenize_hedge_strategy(
        self,
        hedge_id: str,
        owner_address: str = "0x0000000000000000000000000000000000000000"
    ) -> ForexNFTToken:
        """Hedge strategiyasini NFT ga aylantirish"""
        
        # Hedge ma'lumotlarini olish
        # Bu yerda real hedge manager dan ma'lumot olish kerak
        hedge_data = await self._get_hedge_data(hedge_id)
        
        if not hedge_data:
            raise ValueError(f"Hedge {hedge_id} topilmadi")
        
        # NFT token yaratish
        token_id = await self._generate_unique_token_id(hedge_id, owner_address)
        metadata_uri = await self._create_metadata_uri(hedge_data)
        
        token = ForexNFTToken(
            token_id=token_id,
            contract_address=None,  # Real deploy qilishda to'ldiriladi
            owner=owner_address,
            metadata_uri=metadata_uri,
            created_at=int(datetime.now().timestamp()),
            hedge_details=hedge_data,
            performance_history=[],
            quantum_enhanced=hedge_data.get("quantum_enhanced", False)
        )
        
        self.created_tokens[token_id] = token
        self.metadata_registry[token_id] = hedge_data
        
        self.logger.info(f"Tokenized hedge strategy: {token_id}")
        
        return token
    
    async def _get_hedge_data(self, hedge_id: str) -> Optional[Dict]:
        """Hedge ma'lumotlarini olish"""
        # Bu yerda real hedge manager dan ma'lumot olish
        # Hozircha simulatsiya
        default_hedge_data = {
            "hedge_id": hedge_id,
            "pair": "EUR/USD",
            "hedge_type": "pair_hedge",
            "notional_amount": 100000,
            "entry_price": 1.0850,
            "hedge_ratio": 0.7,
            "quantum_enhanced": True,
            "adaptive_features": True,
            "risk_management": {
                "max_drawdown": 0.15,
                "stop_loss": 0.05,
                "take_profit": 0.10
            },
            "performance_metrics": {
                "total_return": 0.0,
                "sharpe_ratio": 0.0,
                "volatility": 0.12,
                "win_rate": 0.0
            }
        }
        
        return default_hedge_data
    
    async def _generate_unique_token_id(self, hedge_id: str, owner: str) -> str:
        """Unique token ID yaratish"""
        seed_data = f"{hedge_id}_{owner}_{datetime.now().timestamp()}"
        hash_object = hashlib.sha256(seed_data.encode())
        return f"FOREX_HEDGE_{hash_object.hexdigest()[:16]}"
    
    async def _create_metadata_uri(self, hedge_data: Dict) -> str:
        """NFT metadata URI yaratish"""
        
        # Standard NFT metadata yaratish
        metadata = {
            "name": f"Forex Hedge {hedge_data['pair']} - {hedge_data['hedge_type']}",
            "description": f"Dynamic forex hedging NFT for {hedge_data['pair']} currency pair",
            "external_url": f"https://forexhedge.io/nft/{hedge_data['hedge_id']}",
            "attributes": [
                {
                    "trait_type": "Currency Pair",
                    "value": hedge_data["pair"]
                },
                {
                    "trait_type": "Hedge Type",
                    "value": hedge_data["hedge_type"]
                },
                {
                    "trait_type": "Notional Amount",
                    "value": hedge_data["notional_amount"]
                },
                {
                    "trait_type": "Quantum Enhanced",
                    "value": hedge_data.get("quantum_enhanced", False)
                },
                {
                    "trait_type": "Adaptive Features",
                    "value": hedge_data.get("adaptive_features", True)
                }
            ],
            "hedge_specification": {
                "pair": hedge_data["pair"],
                "hedge_type": hedge_data["hedge_type"],
                "notional_amount": hedge_data["notional_amount"],
                "entry_price": hedge_data["entry_price"],
                "hedge_ratio": hedge_data["hedge_ratio"],
                "risk_parameters": hedge_data.get("risk_management", {}),
                "performance_metrics": hedge_data.get("performance_metrics", {})
            }
        }
        
        # JSON format ga o'tkazish
        metadata_json = json.dumps(metadata, indent=2)
        metadata_bytes = base64.b64encode(metadata_json.encode()).decode()
        
        return f"data:application/json;base64,{metadata_bytes}"
    
    async def get_token_metadata(self, token_id: str) -> Optional[Dict]:
        """Token metadata olish"""
        return self.metadata_registry.get(token_id)
    
    async def update_performance(
        self, 
        token_id: str, 
        performance_data: Dict
    ):
        """Token performance ma'lumotlarini yangilash"""
        if token_id in self.created_tokens:
            token = self.created_tokens[token_id]
            
            # Performance history ga qo'shish
            performance_record = {
                "timestamp": int(datetime.now().timestamp()),
                "metrics": performance_data
            }
            token.performance_history.append(performance_record)
            
            # Metadata yangilash
            if token_id in self.metadata_registry:
                self.metadata_registry[token_id]["performance_metrics"].update(performance_data)

class DynamicHedgeNFT:
    """Dynamic Hedge NFT - o'zgaruvchi hedge strategiyasi"""
    
    def __init__(self, token_id: str):
        self.token_id = token_id
        self.market_conditions = {}
        self.adaptive_parameters = {}
        self.rebalance_triggers = []
        self.logger = logging.getLogger(__name__)
        
    async def update_market_conditions(
        self, 
        market_data: Dict
    ):
        """Bozor sharoitlarini yangilash"""
        self.market_conditions.update(market_data)
        
        # Adaptive parameter adjustment
        await self._adjust_adaptive_parameters()
        
        # Rebalance check
        await self._check_rebalance_triggers()
    
    async def _adjust_adaptive_parameters(self):
        """Adaptive parametrlarni sozlash"""
        volatility = self.market_conditions.get("volatility", 0.12)
        
        # Volatillik asosida hedge ratio ni sozash
        if volatility > 0.20:
            # Yuqori volatillik - qo'pol hedge
            self.adaptive_parameters["hedge_ratio"] = 0.8
        elif volatility < 0.08:
            # Past volatillik - yengil hedge
            self.adaptive_parameters["hedge_ratio"] = 0.6
        else:
            # Normal volatillik
            self.adaptive_parameters["hedge_ratio"] = 0.7
    
    async def _check_rebalance_triggers(self):
        """Rebalance triggerlarni tekshirish"""
        current_time = int(datetime.now().timestamp())
        
        # Volatillik triggeri
        volatility = self.market_conditions.get("volatility", 0.12)
        if volatility > 0.25:  # Yuqori volatillik
            self.rebalance_triggers.append({
                "trigger_type": "high_volatility",
                "timestamp": current_time,
                "volatility": volatility
            })
        
        # Economic event triggeri
        if self.market_conditions.get("economic_event"):
            self.rebalance_triggers.append({
                "trigger_type": "economic_event",
                "timestamp": current_time,
                "event": self.market_conditions["economic_event"]
            })
        
        # Time-based rebalance
        last_rebalance = self.market_conditions.get("last_rebalance", 0)
        hours_since_rebalance = (current_time - last_rebalance) / 3600
        
        if hours_since_rebalance > 24:  # Har 24 soatda
            self.rebalance_triggers.append({
                "trigger_type": "time_based",
                "timestamp": current_time,
                "hours_elapsed": hours_since_rebalance
            })
    
    async def get_rebalance_recommendations(self) -> List[Dict]:
        """Rebalance tavsiyalarini olish"""
        recommendations = []
        
        for trigger in self.rebalance_triggers:
            if trigger["trigger_type"] == "high_volatility":
                recommendations.append({
                    "action": "increase_hedge_ratio",
                    "new_ratio": 0.8,
                    "reason": "High volatility detected",
                    "priority": "high"
                })
            elif trigger["trigger_type"] == "economic_event":
                recommendations.append({
                    "action": "adjust_position_size",
                    "adjustment": 0.1,
                    "reason": "Economic event impact",
                    "priority": "medium"
                })
            elif trigger["trigger_type"] == "time_based":
                recommendations.append({
                    "action": "routine_rebalance",
                    "timestamp": trigger["timestamp"],
                    "reason": "Scheduled rebalancing",
                    "priority": "low"
                })
        
        return recommendations

class CrossCurrencyHedgeNFT:
    """Cross Currency Hedge NFT - ko'p valyutali hedge"""
    
    def __init__(self, token_id: str, currency_pairs: List[ForexPair]):
        self.token_id = token_id
        self.currency_pairs = currency_pairs
        self.correlation_matrix = {}
        self.multi_hedge_strategy = {}
        self.logger = logging.getLogger(__name__)
        
    async def calculate_cross_currency_hedge(self) -> Dict:
        """Cross currency hedge hisoblash"""
        
        hedge_ratios = {}
        risk_contribution = {}
        
        for pair in self.currency_pairs:
            # Individual hedge ratio
            hedge_ratios[pair.value] = 0.7
            
            # Cross-currency correlation adjustment
            correlation_factor = await self._get_correlation_factor(pair)
            adjusted_ratio = hedge_ratios[pair.value] * correlation_factor
            
            hedge_ratios[pair.value] = adjusted_ratio
            
            # Risk contribution
            risk_contribution[pair.value] = await self._calculate_risk_contribution(pair)
        
        # Optimal allocation across currencies
        total_notional = 100000  # Default
        allocation = {}
        for pair, ratio in hedge_ratios.items():
            allocation[pair] = total_notional * ratio
        
        return {
            "hedge_ratios": hedge_ratios,
            "allocation": allocation,
            "risk_contribution": risk_contribution,
            "expected_hedge_effectiveness": 0.85
        }
    
    async def _get_correlation_factor(self, pair: ForexPair) -> float:
        """Korrelatsiya omilini hisoblash"""
        # Bu yerda real correlation matrix ishlatiladi
        base_correlation = config.correlation_matrix.get(
            (pair, ForexPair.EURUSD), 0.30
        )
        
        # Correlation asosida adjustment factor
        if base_correlation > 0.7:
            return 1.1  # Yuqori korrelatsiya - ko'proq hedge
        elif base_correlation < 0.3:
            return 0.9  # Past korrelatsiya - kamroq hedge
        else:
            return 1.0
    
    async def _calculate_risk_contribution(self, pair: ForexPair) -> float:
        """Risk contribution hisoblash"""
        # Volatility-based risk contribution
        volatility = config.volatility_matrix.get(pair.value, 0.12)
        
        # Risk contribution formula
        return volatility * 0.7  # Base hedge ratio bilan

class CarryTradeNFT:
    """Carry Trade NFT - foiz stavka arbitrage"""
    
    def __init__(self, token_id: str):
        self.token_id = token_id
        self.interest_rate_matrix = {}
        self.carry_opportunities = []
        self.risk_adjustments = {}
        self.logger = logging.getLogger(__name__)
        
    async def identify_carry_opportunities(self) -> List[Dict]:
        """Carry trade imkoniyatlarini aniqlash"""
        
        # Asosiy interest rate pairs
        major_pairs = [
            (ForexPair.EURUSD, "EUR", "USD"),
            (ForexPair.GBPUSD, "GBP", "USD"),
            (ForexPair.USDJPY, "USD", "JPY"),
            (ForexPair.AUDUSD, "AUD", "USD")
        ]
        
        opportunities = []
        
        for pair, base_currency, quote_currency in major_pairs:
            # Interest rate differentials
            base_rate = await self._get_interest_rate(base_currency)
            quote_rate = await self._get_interest_rate(quote_currency)
            
            carry = base_rate - quote_rate
            
            # Only profitable opportunities
            if carry > 0.02:  # 2% minimum carry
                opportunities.append({
                    "pair": pair.value,
                    "currency": f"{base_currency}/{quote_currency}",
                    "carry": carry,
                    "annualized_carry": carry * 4,  # Quarterly
                    "risk_score": await self._assess_carry_risk(base_currency, quote_currency),
                    "recommendation": "buy" if carry > 0 else "sell"
                })
        
        return opportunities
    
    async def _get_interest_rate(self, currency: str) -> float:
        """Valyuta interest rate olish"""
        # Real implementatsiyada central bank rates dan olinadi
        rates = {
            "USD": 0.0525,  # 5.25%
            "EUR": 0.0450,  # 4.50%
            "GBP": 0.0550,  # 5.50%
            "JPY": -0.0010, # -0.10%
            "AUD": 0.0475,  # 4.75%
            "CAD": 0.0500,  # 5.00%
            "CHF": 0.0125,  # 1.25%
            "NZD": 0.0550   # 5.50%
        }
        
        return rates.get(currency, 0.03)
    
    async def _assess_carry_risk(self, base_currency: str, quote_currency: str) -> float:
        """Carry trade risk baholash"""
        # Risk factors
        volatility_risk = 0.3
        currency_risk = 0.2
        liquidity_risk = 0.1
        
        # Central bank policy risk
        policy_risk = await self._assess_policy_risk(base_currency, quote_currency)
        
        total_risk = volatility_risk + currency_risk + liquidity_risk + policy_risk
        
        return min(total_risk, 1.0)
    
    async def _assess_policy_risk(self, base_currency: str, quote_currency: str) -> float:
        """Central bank policy risk baholash"""
        # Bu yerda real central bank policy analysis
        # Hozircha default values
        policy_risks = {
            "USD": 0.15,
            "EUR": 0.20,
            "GBP": 0.25,
            "JPY": 0.10,
            "AUD": 0.30,
            "CAD": 0.20,
            "CHF": 0.05,
            "NZD": 0.35
        }
        
        base_risk = policy_risks.get(base_currency, 0.20)
        quote_risk = policy_risks.get(quote_currency, 0.20)
        
        return (base_risk + quote_risk) / 2

class VolatilityHedgeNFT:
    """Volatility Hedge NFT - volatillik hedge"""
    
    def __init__(self, token_id: str):
        self.token_id = token_id
        self.volatility_surface = {}
        self.option_strategies = []
        self.volatility_forecasts = {}
        self.logger = logging.getLogger(__name__)
    
    async def create_volatility_hedge(self, pair: ForexPair) -> Dict:
        """Volatillik hedge yaratish"""
        
        current_vol = await self._get_current_volatility(pair)
        forecast_vol = await self._forecast_volatility(pair)
        
        # Volatillik skew va smile analysis
        vol_skew = await self._analyze_volatility_skew(pair)
        
        hedge_strategy = {
            "pair": pair.value,
            "current_volatility": current_vol,
            "forecasted_volatility": forecast_vol,
            "volatility_forecast": vol_skew,
            "hedge_instruments": await self._select_hedge_instruments(pair, current_vol, forecast_vol),
            "recommended_vega_exposure": await self._calculate_vega_exposure(current_vol, forecast_vol)
        }
        
        return hedge_strategy
    
    async def _get_current_volatility(self, pair: ForexPair) -> float:
        """Joriy volatillik olish"""
        # Real volatility calculation
        return config.volatility_matrix.get(pair.value, 0.12)
    
    async def _forecast_volatility(self, pair: ForexPair) -> float:
        """Volatillik prognozi"""
        # Bu yerda GARCH, ARIMA yoki boshqa volatility model ishlatiladi
        current_vol = await self._get_current_volatility(pair)
        
        # Simple forecast - volatillik mean reversion
        mean_reversion_speed = 0.1
        long_term_vol = 0.12
        
        forecast = current_vol + mean_reversion_speed * (long_term_vol - current_vol)
        
        return forecast
    
    async def _analyze_volatility_skew(self, pair: ForexPair) -> Dict:
        """Volatillik skew tahlili"""
        # Real volatility surface analysis
        current_vol = await self._get_current_volatility(pair)
        
        return {
            "atm_volatility": current_vol,
            "25d_put_volatility": current_vol * 1.05,
            "25d_call_volatility": current_vol * 0.95,
            "10d_put_volatility": current_vol * 1.15,
            "10d_call_volatility": current_vol * 0.85,
            "skew_25d": 0.05,
            "skew_10d": 0.15
        }
    
    async def _select_hedge_instruments(self, pair: ForexPair, current_vol: float, forecast_vol: float) -> List[Dict]:
        """Hedge instrumentlarini tanlash"""
        instruments = []
        
        # ATM straddle
        instruments.append({
            "instrument": "straddle",
            "strike": "atm",
            "expiry": "1M",
            "vega_exposure": 0.5,
            "cost": current_vol * 0.1
        })
        
        # Risk reversal
        if current_vol < forecast_vol:
            # Volatillik oshishi prognozi - long volatility
            instruments.append({
                "instrument": "strangle",
                "strike": "25d",
                "expiry": "3M",
                "vega_exposure": 0.8,
                "cost": current_vol * 0.15
            })
        else:
            # Volatillik kamayishi prognozi - short volatility
            instruments.append({
                "instrument": "iron_condor",
                "strike": "25d",
                "expiry": "1M",
                "vega_exposure": -0.6,
                "cost": -current_vol * 0.05
            })
        
        return instruments
    
    async def _calculate_vega_exposure(self, current_vol: float, forecast_vol: float) -> float:
        """Vega exposure hisoblash"""
        vol_change = forecast_vol - current_vol
        
        # Vega exposure formula
        if vol_change > 0:
            return 0.5  # Long volatility
        else:
            return -0.3  # Short volatility

class QuantumForexNFTManager:
    """Quantum-enhanced Forex NFT Manager"""
    
    def __init__(self):
        self.nft_engine = None
        self.dynamic_nfts = {}
        self.cross_currency_nfts = {}
        self.carry_trade_nfts = {}
        self.volatility_nfts = {}
        self.logger = logging.getLogger(__name__)
    
    async def create_quantum_enhanced_nft(
        self,
        hedge_type: HedgeType,
        pair: ForexPair,
        notional_amount: float,
        owner: str = "0x0000000000000000000000000000000000000000"
    ) -> str:
        """Quantum-enhanced NFT yaratish"""
        
        token_id = f"QUANTUM_{hedge_type.value}_{pair.value}_{int(datetime.now().timestamp())}"
        
        if hedge_type == HedgeType.PAIR_HEDGE:
            nft = DynamicHedgeNFT(token_id)
            self.dynamic_nfts[token_id] = nft
        elif hedge_type == HedgeType.CROSS_CURRENCY:
            # Cross-currency pairs tanlash
            related_pairs = await self._get_related_pairs(pair)
            nft = CrossCurrencyHedgeNFT(token_id, related_pairs)
            self.cross_currency_nfts[token_id] = nft
        elif hedge_type == HedgeType.CARRY_TRADE:
            nft = CarryTradeNFT(token_id)
            self.carry_trade_nfts[token_id] = nft
        elif hedge_type == HedgeType.VOLATILITY:
            nft = VolatilityHedgeNFT(token_id)
            self.volatility_nfts[token_id] = nft
        
        self.logger.info(f"Created quantum-enhanced NFT: {token_id}")
        
        return token_id
    
    async def _get_related_pairs(self, pair: ForexPair) -> List[ForexPair]:
        """Bog'liq valyuta juftliklarini topish"""
        related_map = {
            ForexPair.EURUSD: [ForexPair.GBPUSD, ForexPair.AUDUSD],
            ForexPair.GBPUSD: [ForexPair.EURUSD, ForexPair.NZDUSD],
            ForexPair.USDJPY: [ForexPair.USDCHF],
            ForexPair.AUDUSD: [ForexPair.EURUSD, ForexPair.NZDUSD],
        }
        
        return related_map.get(pair, [ForexPair.EURUSD])
    
    async def get_nft_status(self, token_id: str) -> Dict:
        """NFT status olish"""
        status = {
            "token_id": token_id,
            "type": "unknown",
            "features": [],
            "quantum_enhanced": True,
            "last_updated": int(datetime.now().timestamp())
        }
        
        if token_id in self.dynamic_nfts:
            nft = self.dynamic_nfts[token_id]
            status.update({
                "type": "dynamic_hedge",
                "features": ["adaptive_parameters", "rebalance_triggers"],
                "current_triggers": len(nft.rebalance_triggers)
            })
        elif token_id in self.cross_currency_nfts:
            nft = self.cross_currency_nfts[token_id]
            status.update({
                "type": "cross_currency",
                "features": ["multi_currency", "correlation_analysis"],
                "currency_pairs": [p.value for p in nft.currency_pairs]
            })
        elif token_id in self.carry_trade_nfts:
            nft = self.carry_trade_nfts[token_id]
            status.update({
                "type": "carry_trade",
                "features": ["interest_rate_arbitrage", "policy_risk"],
                "carry_opportunities": len(nft.carry_opportunities)
            })
        elif token_id in self.volatility_nfts:
            nft = self.volatility_nfts[token_id]
            status.update({
                "type": "volatility_hedge",
                "features": ["volatility_forecasting", "option_strategies"],
                "hedge_instruments": len(nft.option_strategies)
            })
        
        return status