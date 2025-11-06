"""
Oracle Verification System
Cross-chain asset management uchun oracle va narx ma'lumotlar tizimi
"""

import asyncio
import json
import time
import hashlib
import requests
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import logging

class OracleType(Enum):
    """Oracle turlari"""
    CHAINLINK = "chainlink"
    BAND_PROTOCOL = "band_protocol"
    API3 = "api3"
    TELLOR = "tellor"
    DIA_DATA = "dia_data"
    CUSTOM = "custom"

class PriceStatus(Enum):
    """Narx holatlari"""
    ACTIVE = "active"
    STALE = "stale"
    INVALID = "invalid"
    DISPUTED = "disputed"

@dataclass
class OraclePrice:
    """Oracle narx ma'lumotlari"""
    symbol: str
    price: float
    timestamp: int
    source: OracleType
    confidence: float
    volume_24h: Optional[float] = None
    market_cap: Optional[float] = None
    extra_data: Optional[Dict] = None

@dataclass
class ChainlinkPrice:
    """Chainlink oracle narx ma'lumotlari"""
    asset_pair: str
    price: int  # Chainlink returns int with decimals
    decimals: int
    timestamp: int
    round_id: int
    source: str

@dataclass
class CrossChainStateProof:
    """Cross-chain state proof ma'lumotlari"""
    chain_id: int
    contract_address: str
    state_root: str
    proof_data: bytes
    block_number: int
    timestamp: int
    signature: str

class OracleManager:
    """Oracle ma'lumotlar boshqaruvchisi"""
    
    def __init__(self):
        self.oracles = {}
        self.price_feeds = {}
        self.price_history = {}
        self.consensus_threshold = 0.7  # 70% consensus required
        self.price_tolerance = 0.02     # 2% price tolerance
        self.stale_threshold = 3600     # 1 hour
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
    
    async def initialize_oracles(self):
        """Barcha oraclarni ishga tushirish"""
        
        # Chainlink
        self.oracles[OracleType.CHAINLINK] = ChainlinkOracle()
        
        # Band Protocol
        self.oracles[OracleType.BAND_PROTOCOL] = BandProtocolOracle()
        
        # API3
        self.oracles[OracleType.API3] = API3Oracle()
        
        # Custom aggregators
        self.oracles[OracleType.CUSTOM] = CustomAggregatorOracle()
        
        print("✅ Barcha oracllar ishga tushirildi")
    
    async def get_consensus_price(self, symbol: str) -> Optional[OraclePrice]:
        """Konsensus narx olish (barcha oraclardan)"""
        
        try:
            # Barcha oraclardan narx olish
            oracle_prices = []
            
            for oracle_type, oracle in self.oracles.items():
                try:
                    price_data = await oracle.get_price(symbol)
                    if price_data and self._is_price_valid(price_data):
                        oracle_prices.append(price_data)
                except Exception as e:
                    self.logger.warning(f"Oracle {oracle_type.value} xatolik: {e}")
            
            if len(oracle_prices) < 2:
                self.logger.error("Yetarli oracle ma'lumotlari yo'q")
                return None
            
            # Konsensus hisoblash
            consensus_price = self._calculate_consensus(oracle_prices)
            
            if consensus_price:
                # Natijani saqlash
                self.price_feeds[symbol] = consensus_price
                
                # History ga qo'shish
                if symbol not in self.price_history:
                    self.price_history[symbol] = []
                
                self.price_history[symbol].append(consensus_price)
                
                # History ni cheklash (oxirgi 100 ta)
                if len(self.price_history[symbol]) > 100:
                    self.price_history[symbol] = self.price_history[symbol][-100:]
                
                print(f"💰 {symbol} konsensus narxi: ${consensus_price.price:.4f}")
            
            return consensus_price
            
        except Exception as e:
            self.logger.error(f"Konsensus narx hisoblashda xatolik: {e}")
            return None
    
    def _is_price_valid(self, price: OraclePrice) -> bool:
        """Narx ma'lumotlarining to'g'riligini tekshirish"""
        
        # Vaqt cheklovi
        current_time = int(time.time())
        if current_time - price.timestamp > self.stale_threshold:
            return False
        
        # Musbat narx
        if price.price <= 0:
            return False
        
        # Confidence balandlik
        if price.confidence < 0.5:
            return False
        
        return True
    
    def _calculate_consensus(self, prices: List[OraclePrice]) -> Optional[OraclePrice]:
        """Konsensus narx hisoblash"""
        
        if len(prices) == 0:
            return None
        
        # Narxlarni ajratish
        price_values = [p.price for p in prices]
        confidence_values = [p.confidence for p in prices]
        
        # Outlier'ları olib tashlash
        median_price = statistics.median(price_values)
        tolerance = median_price * self.price_tolerance
        
        filtered_prices = []
        filtered_confidences = []
        
        for i, price in enumerate(price_values):
            if abs(price - median_price) <= tolerance:
                filtered_prices.append(price)
                filtered_confidences.append(confidence_values[i])
        
        if len(filtered_prices) < len(prices) * self.consensus_threshold:
            self.logger.warning("Konsensus uchun yetarli ma'lumot yo'q")
            return None
        
        # Confidence-weighted average
        total_weight = sum(filtered_confidences)
        weighted_sum = sum(p * c for p, c in zip(filtered_prices, filtered_confidences))
        avg_price = weighted_sum / total_weight
        
        # Avg confidence
        avg_confidence = sum(filtered_confidences) / len(filtered_confidences)
        
        # Eng ishonchli oracle'ni topish
        best_oracle = max(prices, key=lambda p: p.confidence)
        
        return OraclePrice(
            symbol=prices[0].symbol,
            price=avg_price,
            timestamp=int(time.time()),
            source=best_oracle.source,
            confidence=avg_confidence,
            volume_24h=best_oracle.volume_24h,
            market_cap=best_oracle.market_cap
        )
    
    async def verify_cross_chain_state(
        self,
        source_chain: int,
        target_chain: int,
        contract_address: str,
        expected_state: Dict
    ) -> bool:
        """Cross-chain state'ni tekshirish"""
        
        try:
            # Source chain dan state proof olish
            source_proof = await self._get_state_proof(source_chain, contract_address)
            
            # Target chain dan state proof olish
            target_proof = await self._get_state_proof(target_chain, contract_address)
            
            # State'ni tekshirish
            is_valid = await self._verify_state_consistency(source_proof, target_proof, expected_state)
            
            print(f"✅ Cross-chain state tekshirildi: {is_valid}")
            
            return is_valid
            
        except Exception as e:
            self.logger.error(f"Cross-chain state tekshirishda xatolik: {e}")
            return False
    
    async def _get_state_proof(self, chain_id: int, contract_address: str) -> CrossChainStateProof:
        """State proof olish"""
        
        # Simulated proof generation
        proof_data = f"proof_{chain_id}_{contract_address}_{int(time.time())}".encode()
        state_root = hashlib.sha256(proof_data).hexdigest()
        
        signature = self._sign_proof(proof_data)
        
        return CrossChainStateProof(
            chain_id=chain_id,
            contract_address=contract_address,
            state_root=state_root,
            proof_data=proof_data,
            block_number=12345678,
            timestamp=int(time.time()),
            signature=signature
        )
    
    def _sign_proof(self, proof_data: bytes) -> str:
        """Proof'ni imzolash"""
        # Simplified signing
        return hashlib.sha256(proof_data).hexdigest()
    
    async def _verify_state_consistency(
        self,
        source_proof: CrossChainStateProof,
        target_proof: CrossChainStateProof,
        expected_state: Dict
    ) -> bool:
        """State konsistensiyasini tekshirish"""
        
        # Simple state verification logic
        # Haqiqiy implementatsiyada Merkle proof verification kerak
        
        return True
    
    async def get_price_alerts(self, symbol: str, threshold: float) -> List[Dict]:
        """Narx o'zgarishlari uchun alertlar"""
        
        if symbol not in self.price_history or len(self.price_history[symbol]) < 2:
            return []
        
        alerts = []
        prices = self.price_history[symbol]
        
        # Oxirgi narxlarni tekshirish
        for i in range(1, len(prices)):
            prev_price = prices[i-1].price
            curr_price = prices[i].price
            
            change_percent = abs((curr_price - prev_price) / prev_price) * 100
            
            if change_percent >= threshold * 100:
                alerts.append({
                    "symbol": symbol,
                    "previous_price": prev_price,
                    "current_price": curr_price,
                    "change_percent": change_percent,
                    "timestamp": curr_price.timestamp,
                    "alert_type": "price_spike" if change_percent >= threshold * 100 else "price_change"
                })
        
        return alerts
    
    def get_oracle_stats(self) -> Dict:
        """Oracle statistikasini olish"""
        
        stats = {
            "total_oracles": len(self.oracles),
            "active_feeds": len(self.price_feeds),
            "total_symbols": len(self.price_history),
            "oracle_types": [o.value for o in self.oracles.keys()]
        }
        
        # Har bir symbol uchun narx ma'lumotlari
        for symbol, prices in self.price_history.items():
            if len(prices) > 0:
                latest = prices[-1]
                stats[f"{symbol}_latest_price"] = latest.price
                stats[f"{symbol}_last_update"] = latest.timestamp
                stats[f"{symbol}_confidence"] = latest.confidence
        
        return stats

class ChainlinkOracle:
    """Chainlink oracle implementatsiyasi"""
    
    def __init__(self):
        self.api_endpoint = "https://api.chain.link/v1"
        self.fallback_endpoints = [
            "https://min-api.cryptocompare.com/data/v2",
            "https://api.coingecko.com/api/v3"
        ]
    
    async def get_price(self, symbol: str) -> Optional[OraclePrice]:
        """Chainlink'dan narx olish"""
        
        try:
            # Simulatsiya uchun ma'lumot
            if symbol == "ETH":
                price = 2345.67
            elif symbol == "BTC":
                price = 45678.90
            elif symbol == "USDC":
                price = 1.0001
            elif symbol == "USDT":
                price = 0.9998
            else:
                return None
            
            return OraclePrice(
                symbol=symbol,
                price=price,
                timestamp=int(time.time()),
                source=OracleType.CHAINLINK,
                confidence=0.95,
                volume_24h=1000000000,  # $1B
                market_cap=500000000000  # $500B
            )
            
        except Exception as e:
            self.logger.error(f"Chainlink oracle xatolik: {e}")
            return None

class BandProtocolOracle:
    """Band Protocol oracle implementatsiyasi"""
    
    def __init__(self):
        self.api_endpoint = "https://api.thebandprotocol.com"
    
    async def get_price(self, symbol: str) -> Optional[OraclePrice]:
        """Band Protocol'dan narx olish"""
        
        try:
            # Simulatsiya uchun ma'lumot (2% farq)
            if symbol == "ETH":
                price = 2298.76  # 2% less than Chainlink
            elif symbol == "BTC":
                price = 44845.32  # 2% less
            elif symbol == "USDC":
                price = 0.9999
            elif symbol == "USDT":
                price = 1.0002
            else:
                return None
            
            return OraclePrice(
                symbol=symbol,
                price=price,
                timestamp=int(time.time()),
                source=OracleType.BAND_PROTOCOL,
                confidence=0.88,
                volume_24h=800000000,
                market_cap=480000000000
            )
            
        except Exception as e:
            self.logger.error(f"Band Protocol oracle xatolik: {e}")
            return None

class API3Oracle:
    """API3 oracle implementatsiyasi"""
    
    def __init__(self):
        self.api_endpoint = "https://api.api3.org"
    
    async def get_price(self, symbol: str) -> Optional[OraclePrice]:
        """API3'dan narx olish"""
        
        try:
            # Simulatsiya uchun ma'lumot (1% farq)
            if symbol == "ETH":
                price = 2369.12  # 1% more
            elif symbol == "BTC":
                price = 46135.69  # 1% more
            elif symbol == "USDC":
                price = 1.0000
            elif symbol == "USDT":
                price = 0.9999
            else:
                return None
            
            return OraclePrice(
                symbol=symbol,
                price=price,
                timestamp=int(time.time()),
                source=OracleType.API3,
                confidence=0.92,
                volume_24h=950000000,
                market_cap=505000000000
            )
            
        except Exception as e:
            self.logger.error(f"API3 oracle xatolik: {e}")
            return None

class CustomAggregatorOracle:
    """Custom aggregator oracle"""
    
    def __init__(self):
        self.sources = [
            "coinbase",
            "binance",
            "kraken",
            "huobi"
        ]
    
    async def get_price(self, symbol: str) -> Optional[OraclePrice]:
        """Custom aggregator'dan narx olish"""
        
        try:
            # Multiple exchange'lardan average
            exchange_prices = []
            
            # Simulatsiya uchun ma'lumot
            for exchange in self.sources:
                if symbol == "ETH":
                    price = 2340.0 + (hash(exchange + symbol) % 100)  # Random-ish price
                elif symbol == "BTC":
                    price = 45500.0 + (hash(exchange + symbol) % 1000)
                elif symbol == "USDC":
                    price = 0.9998 + (hash(exchange + symbol) % 100) / 100000.0
                elif symbol == "USDT":
                    price = 1.0001 - (hash(exchange + symbol) % 100) / 100000.0
                else:
                    continue
                
                exchange_prices.append(price)
            
            if not exchange_prices:
                return None
            
            avg_price = statistics.mean(exchange_prices)
            
            return OraclePrice(
                symbol=symbol,
                price=avg_price,
                timestamp=int(time.time()),
                source=OracleType.CUSTOM,
                confidence=0.85,
                volume_24h=sum(exchange_prices) * 1000,
                market_cap=avg_price * 100000000
            )
            
        except Exception as e:
            self.logger.error(f"Custom aggregator oracle xatolik: {e}")
            return None

class PriceDisputeManager:
    """Narx bahs-munozarasi boshqaruvchisi"""
    
    def __init__(self, oracle_manager: OracleManager):
        self.oracle_manager = oracle_manager
        self.disputes = {}
        self.resolution_threshold = 0.8  # 80% consensus for resolution
    
    async def create_dispute(self, symbol: str, claimed_price: float, evidence: Dict) -> str:
        """Bahs-munozara yaratish"""
        
        dispute_id = f"dispute_{symbol}_{int(time.time())}"
        
        self.disputes[dispute_id] = {
            "symbol": symbol,
            "claimed_price": claimed_price,
            "evidence": evidence,
            "created_at": int(time.time()),
            "votes": [],
            "status": "open"
        }
        
        print(f"⚖️ Bahs-munozara yaratildi: {dispute_id}")
        
        return dispute_id
    
    async def vote_dispute(self, dispute_id: str, validator: str, vote: bool) -> bool:
        """Bahs-munozaraga ovoz berish"""
        
        if dispute_id not in self.disputes:
            return False
        
        dispute = self.disputes[dispute_id]
        
        if dispute["status"] != "open":
            return False
        
        # Validator ovozini qo'shish
        dispute["votes"].append({
            "validator": validator,
            "vote": vote,
            "timestamp": int(time.time())
        })
        
        print(f"🗳️ {validator} ovoz berdi: {vote}")
        
        # Resolution check
        await self._check_dispute_resolution(dispute_id)
        
        return True
    
    async def _check_dispute_resolution(self, dispute_id: str):
        """Bahs-munozara hal qilishini tekshirish"""
        
        dispute = self.disputes[dispute_id]
        votes = dispute["votes"]
        
        if len(votes) < 5:  # Minimum votes required
            return
        
        # Consensus hisoblash
        yes_votes = sum(1 for v in votes if v["vote"])
        consensus_ratio = yes_votes / len(votes)
        
        if consensus_ratio >= self.resolution_threshold:
            dispute["status"] = "resolved"
            dispute["resolution"] = "approved"
            print(f"✅ Bahs-munozara hal qilindi: approved")
        elif 1 - consensus_ratio >= self.resolution_threshold:
            dispute["status"] = "resolved"
            dispute["resolution"] = "rejected"
            print(f"❌ Bahs-munozara hal qilindi: rejected")
    
    def get_dispute_status(self, dispute_id: str) -> Optional[Dict]:
        """Bahs-munozara holatini olish"""
        return self.disputes.get(dispute_id)
    
    def get_all_disputes(self) -> List[Dict]:
        """Barcha bahs-munozaralarni olish"""
        return list(self.disputes.values())

# Global oracle manager instance
oracle_manager = OracleManager()

async def initialize_oracle_system():
    """Oracle tizimini ishga tushirish"""
    await oracle_manager.initialize_oracles()
    print("🔮 Oracle tizimi ishga tushirildi")

async def get_asset_price(symbol: str) -> Optional[float]:
    """Asset narxini olish"""
    price_data = await oracle_manager.get_consensus_price(symbol)
    return price_data.price if price_data else None

async def verify_bridge_state(source_chain: int, target_chain: int, contract_address: str) -> bool:
    """Bridge state'ni tekshirish"""
    expected_state = {"locked_amount": 0, "minted_amount": 0}
    return await oracle_manager.verify_cross_chain_state(source_chain, target_chain, contract_address, expected_state)