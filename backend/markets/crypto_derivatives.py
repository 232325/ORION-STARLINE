"""
AI Trading Evolution - Crypto Derivatives Module
================================================

Kripto derivatives savdosi:
- Perpetual futures (funding rate arbitrage)
- Dated futures (contango/backwardation)
- Options (calls, puts, strategies)
- Leveraged positions (long/short up to 100x)
- Multi-exchange arbitrage
- Greeks calculation (Delta, Gamma, Vega, Theta)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import numpy as np
import pandas as pd
from collections import defaultdict
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DerivativeType(Enum):
    """Derivative turlari"""
    PERPETUAL_FUTURE = "perpetual"
    DATED_FUTURE = "dated_future"
    CALL_OPTION = "call"
    PUT_OPTION = "put"


class Exchange(Enum):
    """Birjalar"""
    BINANCE = "binance"
    BYBIT = "bybit"
    OKX = "okx"
    DERIBIT = "deribit"  # Options uchun mashhur
    BITMEX = "bitmex"


class OptionStyle(Enum):
    """Option uslubi"""
    EUROPEAN = "european"  # Faqat expiry kuni
    AMERICAN = "american"  # Istalgan vaqt


@dataclass
class PerpetualContract:
    """Perpetual futures kontrakt"""
    symbol: str  # BTC-PERP, ETH-PERP
    exchange: Exchange
    mark_price: float
    index_price: float
    funding_rate: float  # 8 soatlik funding rate
    next_funding_time: datetime
    open_interest: float  # USD
    volume_24h: float
    bid: float
    ask: float
    max_leverage: int
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def funding_rate_annual(self) -> float:
        """Yillik funding rate"""
        # 8 soatda 3 marta, kuniga 3x, yilda 365 kun
        return self.funding_rate * 3 * 365
    
    @property
    def basis(self) -> float:
        """Perpetual vs Spot basis"""
        return self.mark_price - self.index_price
    
    @property
    def basis_pct(self) -> float:
        """Basis foizda"""
        return (self.basis / self.index_price) * 100 if self.index_price > 0 else 0


@dataclass
class FuturesContract:
    """Dated futures kontrakt"""
    symbol: str  # BTC-0329 (29 March)
    exchange: Exchange
    mark_price: float
    index_price: float
    expiry_date: datetime
    open_interest: float
    volume_24h: float
    bid: float
    ask: float
    max_leverage: int
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def days_to_expiry(self) -> int:
        """Muddati tugashiga qolgan kunlar"""
        return (self.expiry_date - datetime.now()).days
    
    @property
    def annualized_basis(self) -> float:
        """Yillik basis (contango/backwardation)"""
        basis = self.mark_price - self.index_price
        basis_pct = (basis / self.index_price) if self.index_price > 0 else 0
        
        if self.days_to_expiry > 0:
            return basis_pct * (365 / self.days_to_expiry)
        return 0


@dataclass
class OptionContract:
    """Options kontrakt"""
    symbol: str  # BTC-70000-C-0329 (Call, Strike 70k, 29 March)
    exchange: Exchange
    option_type: DerivativeType  # CALL or PUT
    strike_price: float
    expiry_date: datetime
    mark_price: float
    underlying_price: float
    implied_volatility: float  # IV (%)
    delta: float
    gamma: float
    vega: float
    theta: float
    volume_24h: float
    open_interest: float
    bid: float
    ask: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def days_to_expiry(self) -> int:
        """Muddati tugashiga qolgan kunlar"""
        return max(0, (self.expiry_date - datetime.now()).days)
    
    @property
    def intrinsic_value(self) -> float:
        """Ichki qiymat"""
        if self.option_type == DerivativeType.CALL_OPTION:
            return max(0, self.underlying_price - self.strike_price)
        else:  # PUT
            return max(0, self.strike_price - self.underlying_price)
    
    @property
    def time_value(self) -> float:
        """Vaqt qiymati"""
        return self.mark_price - self.intrinsic_value
    
    @property
    def is_itm(self) -> bool:
        """In The Money?"""
        return self.intrinsic_value > 0
    
    @property
    def is_otm(self) -> bool:
        """Out of The Money?"""
        return self.intrinsic_value == 0


class CryptoDerivativesDataProvider:
    """
    Crypto derivatives uchun ma'lumot provayderi
    Real API'lar: Binance Futures, Bybit, Deribit
    """
    
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, Tuple[datetime, any]] = {}
        self.cache_ttl = 30  # 30 soniya
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _is_cache_valid(self, key: str) -> bool:
        if key not in self.cache:
            return False
        timestamp, _ = self.cache[key]
        return (datetime.now() - timestamp).seconds < self.cache_ttl
    
    async def get_perpetual_contract(
        self,
        symbol: str,
        exchange: Exchange
    ) -> Optional[PerpetualContract]:
        """Perpetual kontrakt ma'lumotlarini olish"""
        cache_key = f"perp_{symbol}_{exchange.value}"
        
        if self._is_cache_valid(cache_key):
            _, data = self.cache[cache_key]
            return data
        
        try:
            # Demo data
            base_prices = {
                'BTC': 68500.0,
                'ETH': 3450.0,
                'SOL': 145.0,
                'BNB': 580.0
            }
            
            coin = symbol.split('-')[0]
            index_price = base_prices.get(coin, 1000.0)
            
            # Perpetual usually trades slightly above spot (funding rate effect)
            mark_price = index_price * np.random.uniform(1.0001, 1.0005)
            
            # Funding rate: usually -0.01% to +0.01% per 8h
            funding_rate = np.random.uniform(-0.0001, 0.0001)
            
            contract = PerpetualContract(
                symbol=symbol,
                exchange=exchange,
                mark_price=mark_price,
                index_price=index_price,
                funding_rate=funding_rate,
                next_funding_time=datetime.now() + timedelta(hours=np.random.randint(1, 8)),
                open_interest=np.random.uniform(100e6, 2e9),
                volume_24h=np.random.uniform(500e6, 10e9),
                bid=mark_price * 0.9998,
                ask=mark_price * 1.0002,
                max_leverage=100 if exchange == Exchange.BINANCE else 125
            )
            
            self.cache[cache_key] = (datetime.now(), contract)
            return contract
            
        except Exception as e:
            logger.error(f"Perpetual kontrakt olishda xato ({symbol}): {e}")
            return None
    
    async def get_dated_futures(
        self,
        symbol: str,
        exchange: Exchange
    ) -> List[FuturesContract]:
        """Dated futures kontraktlar"""
        cache_key = f"futures_{symbol}_{exchange.value}"
        
        if self._is_cache_valid(cache_key):
            _, data = self.cache[cache_key]
            return data
        
        try:
            contracts = []
            
            base_prices = {
                'BTC': 68500.0,
                'ETH': 3450.0,
                'SOL': 145.0
            }
            
            coin = symbol.split('-')[0]
            index_price = base_prices.get(coin, 1000.0)
            
            # Generate quarterly futures
            quarters = [
                datetime.now() + timedelta(days=30),   # 1 month
                datetime.now() + timedelta(days=90),   # 3 months (Q1)
                datetime.now() + timedelta(days=180),  # 6 months (Q2)
            ]
            
            for expiry in quarters:
                days_to_expiry = (expiry - datetime.now()).days
                
                # Contango: futures > spot (usually)
                # Annualized contango ~5-15%
                annual_contango = np.random.uniform(0.05, 0.15)
                basis = index_price * annual_contango * (days_to_expiry / 365)
                mark_price = index_price + basis
                
                contract_symbol = f"{symbol}-{expiry.strftime('%m%d')}"
                
                contract = FuturesContract(
                    symbol=contract_symbol,
                    exchange=exchange,
                    mark_price=mark_price,
                    index_price=index_price,
                    expiry_date=expiry,
                    open_interest=np.random.uniform(50e6, 500e6),
                    volume_24h=np.random.uniform(100e6, 1e9),
                    bid=mark_price * 0.9995,
                    ask=mark_price * 1.0005,
                    max_leverage=50
                )
                
                contracts.append(contract)
            
            self.cache[cache_key] = (datetime.now(), contracts)
            return contracts
            
        except Exception as e:
            logger.error(f"Dated futures olishda xato ({symbol}): {e}")
            return []
    
    async def get_option_chain(
        self,
        symbol: str,
        expiry_date: datetime
    ) -> List[OptionContract]:
        """Option chain (calls and puts)"""
        cache_key = f"options_{symbol}_{expiry_date.strftime('%Y%m%d')}"
        
        if self._is_cache_valid(cache_key):
            _, data = self.cache[cache_key]
            return data
        
        try:
            options = []
            
            base_prices = {
                'BTC': 68500.0,
                'ETH': 3450.0
            }
            
            coin = symbol.split('-')[0]
            underlying = base_prices.get(coin, 1000.0)
            
            # Generate strikes around current price
            strikes = [
                underlying * 0.80,
                underlying * 0.90,
                underlying * 0.95,
                underlying,
                underlying * 1.05,
                underlying * 1.10,
                underlying * 1.20
            ]
            
            days_to_expiry = (expiry_date - datetime.now()).days
            time_to_expiry = days_to_expiry / 365
            
            # Implied volatility (crypto: 60-100%)
            iv = np.random.uniform(0.60, 1.00)
            
            for strike in strikes:
                # CALL option
                call_price, call_greeks = self._calculate_option_price(
                    underlying, strike, time_to_expiry, iv, is_call=True
                )
                
                call = OptionContract(
                    symbol=f"{symbol}-{int(strike)}-C-{expiry_date.strftime('%m%d')}",
                    exchange=Exchange.DERIBIT,
                    option_type=DerivativeType.CALL_OPTION,
                    strike_price=strike,
                    expiry_date=expiry_date,
                    mark_price=call_price,
                    underlying_price=underlying,
                    implied_volatility=iv * 100,
                    delta=call_greeks['delta'],
                    gamma=call_greeks['gamma'],
                    vega=call_greeks['vega'],
                    theta=call_greeks['theta'],
                    volume_24h=np.random.uniform(1e5, 1e7),
                    open_interest=np.random.uniform(5e5, 5e7),
                    bid=call_price * 0.98,
                    ask=call_price * 1.02
                )
                options.append(call)
                
                # PUT option
                put_price, put_greeks = self._calculate_option_price(
                    underlying, strike, time_to_expiry, iv, is_call=False
                )
                
                put = OptionContract(
                    symbol=f"{symbol}-{int(strike)}-P-{expiry_date.strftime('%m%d')}",
                    exchange=Exchange.DERIBIT,
                    option_type=DerivativeType.PUT_OPTION,
                    strike_price=strike,
                    expiry_date=expiry_date,
                    mark_price=put_price,
                    underlying_price=underlying,
                    implied_volatility=iv * 100,
                    delta=put_greeks['delta'],
                    gamma=put_greeks['gamma'],
                    vega=put_greeks['vega'],
                    theta=put_greeks['theta'],
                    volume_24h=np.random.uniform(1e5, 1e7),
                    open_interest=np.random.uniform(5e5, 5e7),
                    bid=put_price * 0.98,
                    ask=put_price * 1.02
                )
                options.append(put)
            
            self.cache[cache_key] = (datetime.now(), options)
            return options
            
        except Exception as e:
            logger.error(f"Option chain olishda xato ({symbol}): {e}")
            return []
    
    def _calculate_option_price(
        self,
        spot: float,
        strike: float,
        time: float,
        volatility: float,
        is_call: bool,
        risk_free_rate: float = 0.05
    ) -> Tuple[float, Dict[str, float]]:
        """
        Black-Scholes option pricing
        Greeks calculation
        """
        if time <= 0:
            # Expired
            if is_call:
                price = max(0, spot - strike)
            else:
                price = max(0, strike - spot)
            greeks = {'delta': 0, 'gamma': 0, 'vega': 0, 'theta': 0}
            return price, greeks
        
        # Black-Scholes
        d1 = (math.log(spot / strike) + (risk_free_rate + 0.5 * volatility**2) * time) / (volatility * math.sqrt(time))
        d2 = d1 - volatility * math.sqrt(time)
        
        # Standard normal CDF
        from scipy.stats import norm
        
        if is_call:
            price = spot * norm.cdf(d1) - strike * math.exp(-risk_free_rate * time) * norm.cdf(d2)
            delta = norm.cdf(d1)
        else:
            price = strike * math.exp(-risk_free_rate * time) * norm.cdf(-d2) - spot * norm.cdf(-d1)
            delta = -norm.cdf(-d1)
        
        # Greeks
        gamma = norm.pdf(d1) / (spot * volatility * math.sqrt(time))
        vega = spot * norm.pdf(d1) * math.sqrt(time) / 100  # Per 1% change in IV
        theta = -(spot * norm.pdf(d1) * volatility) / (2 * math.sqrt(time)) / 365  # Per day
        
        greeks = {
            'delta': delta,
            'gamma': gamma,
            'vega': vega,
            'theta': theta
        }
        
        return price, greeks


class FundingRateArbitrage:
    """
    Funding rate arbitrage strategiyasi
    Musbat funding: short perp + long spot
    Manfiy funding: long perp + short spot
    """
    
    def __init__(self, data_provider: CryptoDerivativesDataProvider):
        self.data_provider = data_provider
    
    async def detect_funding_arbitrage(
        self,
        symbols: List[str],
        min_funding_annual: float = 20.0  # 20% yillik
    ) -> List[Dict]:
        """Funding rate arbitrage imkoniyatlarini topish"""
        opportunities = []
        
        for symbol in symbols:
            contracts = []
            
            # Turli birjalardan perpetual kontraktlarni olish
            for exchange in [Exchange.BINANCE, Exchange.BYBIT, Exchange.OKX]:
                contract = await self.data_provider.get_perpetual_contract(symbol, exchange)
                if contract:
                    contracts.append(contract)
            
            for contract in contracts:
                annual_funding = contract.funding_rate_annual * 100
                
                if abs(annual_funding) > min_funding_annual:
                    if annual_funding > min_funding_annual:
                        # Musbat funding: longs pay shorts
                        strategy = 'SHORT_PERP_LONG_SPOT'
                        description = 'Perpetual short, Spot long'
                        expected_return = annual_funding
                    else:
                        # Manfiy funding: shorts pay longs
                        strategy = 'LONG_PERP_SHORT_SPOT'
                        description = 'Perpetual long, Spot short'
                        expected_return = abs(annual_funding)
                    
                    opportunities.append({
                        'symbol': contract.symbol,
                        'exchange': contract.exchange.value,
                        'funding_rate_8h': contract.funding_rate * 100,
                        'funding_rate_annual': annual_funding,
                        'strategy': strategy,
                        'description': description,
                        'expected_return': expected_return,
                        'confidence': min(abs(annual_funding) / 50, 1.0)
                    })
        
        opportunities.sort(key=lambda x: abs(x['funding_rate_annual']), reverse=True)
        return opportunities


class BasisTradingStrategy:
    """
    Basis trading: futures vs spot arbitrage
    Contango: sell futures, buy spot
    Backwardation: buy futures, sell spot
    """
    
    def __init__(self, data_provider: CryptoDerivativesDataProvider):
        self.data_provider = data_provider
    
    async def detect_basis_opportunities(
        self,
        symbols: List[str],
        min_annual_basis: float = 10.0  # 10% yillik
    ) -> List[Dict]:
        """Basis arbitrage imkoniyatlarini topish"""
        opportunities = []
        
        for symbol in symbols:
            for exchange in [Exchange.BINANCE, Exchange.BYBIT]:
                futures = await self.data_provider.get_dated_futures(symbol, exchange)
                
                for future in futures:
                    annual_basis = future.annualized_basis * 100
                    
                    if abs(annual_basis) > min_annual_basis:
                        if annual_basis > min_annual_basis:
                            # Contango
                            strategy = 'SELL_FUTURES_BUY_SPOT'
                            description = 'Futures overpriced, short futures + long spot'
                        else:
                            # Backwardation
                            strategy = 'BUY_FUTURES_SELL_SPOT'
                            description = 'Futures underpriced, long futures + short spot'
                        
                        opportunities.append({
                            'symbol': future.symbol,
                            'exchange': exchange.value,
                            'expiry_date': future.expiry_date.strftime('%Y-%m-%d'),
                            'days_to_expiry': future.days_to_expiry,
                            'futures_price': future.mark_price,
                            'spot_price': future.index_price,
                            'annual_basis': annual_basis,
                            'strategy': strategy,
                            'description': description,
                            'confidence': min(abs(annual_basis) / 20, 1.0)
                        })
        
        opportunities.sort(key=lambda x: abs(x['annual_basis']), reverse=True)
        return opportunities


class OptionsStrategies:
    """
    Options trading strategiyalari
    - Covered Call
    - Protective Put
    - Straddle
    - Iron Condor
    """
    
    def __init__(self, data_provider: CryptoDerivativesDataProvider):
        self.data_provider = data_provider
    
    async def covered_call_analysis(
        self,
        symbol: str,
        expiry_date: datetime
    ) -> List[Dict]:
        """
        Covered Call: Spot long + Call short
        Premium collection strategy
        """
        options = await self.data_provider.get_option_chain(symbol, expiry_date)
        
        # Faqat OTM calllarni tanlaymiz
        otm_calls = [opt for opt in options 
                     if opt.option_type == DerivativeType.CALL_OPTION 
                     and opt.is_otm]
        
        results = []
        
        for call in otm_calls:
            # Premium as % of spot
            premium_pct = (call.mark_price / call.underlying_price) * 100
            
            # Annualized return
            days = call.days_to_expiry
            if days > 0:
                annual_return = premium_pct * (365 / days)
            else:
                annual_return = 0
            
            results.append({
                'strategy': 'COVERED_CALL',
                'symbol': call.symbol,
                'strike': call.strike_price,
                'premium': call.mark_price,
                'premium_pct': premium_pct,
                'annual_return': annual_return,
                'max_profit_pct': ((call.strike_price - call.underlying_price) / call.underlying_price + premium_pct / 100) * 100,
                'breakeven': call.underlying_price - call.mark_price,
                'days_to_expiry': days
            })
        
        results.sort(key=lambda x: x['annual_return'], reverse=True)
        return results[:5]
    
    async def straddle_analysis(
        self,
        symbol: str,
        expiry_date: datetime
    ) -> Dict:
        """
        Straddle: ATM Call + ATM Put
        Volatility play - narx katta harakat qilishini kutish
        """
        options = await self.data_provider.get_option_chain(symbol, expiry_date)
        
        if not options:
            return {}
        
        # ATM strike topish
        underlying = options[0].underlying_price
        atm_strike = min(options, key=lambda x: abs(x.strike_price - underlying)).strike_price
        
        # ATM call va put
        atm_call = next((opt for opt in options 
                        if opt.option_type == DerivativeType.CALL_OPTION 
                        and opt.strike_price == atm_strike), None)
        atm_put = next((opt for opt in options 
                       if opt.option_type == DerivativeType.PUT_OPTION 
                       and opt.strike_price == atm_strike), None)
        
        if not atm_call or not atm_put:
            return {}
        
        total_cost = atm_call.mark_price + atm_put.mark_price
        breakeven_up = atm_strike + total_cost
        breakeven_down = atm_strike - total_cost
        
        # Required move for profit
        required_move_pct = (total_cost / underlying) * 100
        
        return {
            'strategy': 'LONG_STRADDLE',
            'strike': atm_strike,
            'call_premium': atm_call.mark_price,
            'put_premium': atm_put.mark_price,
            'total_cost': total_cost,
            'breakeven_up': breakeven_up,
            'breakeven_down': breakeven_down,
            'required_move_pct': required_move_pct,
            'max_loss': total_cost,
            'avg_iv': (atm_call.implied_volatility + atm_put.implied_volatility) / 2,
            'interpretation': f"Narx {required_move_pct:.1f}% dan ko'proq harakat qilishi kerak"
        }


class LeverageRiskManager:
    """
    Leverage risk management
    - Position sizing
    - Liquidation price calculation
    - Risk/Reward analysis
    """
    
    def calculate_liquidation_price(
        self,
        entry_price: float,
        leverage: int,
        is_long: bool,
        maintenance_margin: float = 0.005  # 0.5%
    ) -> float:
        """Liquidation narxini hisoblash"""
        if is_long:
            # Long: liq price = entry * (1 - 1/leverage + maintenance)
            liq_price = entry_price * (1 - 1/leverage + maintenance_margin)
        else:
            # Short: liq price = entry * (1 + 1/leverage - maintenance)
            liq_price = entry_price * (1 + 1/leverage - maintenance_margin)
        
        return liq_price
    
    def calculate_position_size(
        self,
        capital: float,
        risk_pct: float,
        entry_price: float,
        stop_loss_price: float,
        leverage: int
    ) -> Dict:
        """Optimal pozitsiya hajmini hisoblash"""
        # Risk amount
        risk_amount = capital * (risk_pct / 100)
        
        # Price risk per unit
        price_risk = abs(entry_price - stop_loss_price)
        
        # Quantity without leverage
        quantity_base = risk_amount / price_risk
        
        # With leverage
        quantity = quantity_base * leverage
        
        # Position value
        position_value = quantity * entry_price
        
        # Required margin
        margin_required = position_value / leverage
        
        return {
            'quantity': quantity,
            'position_value': position_value,
            'margin_required': margin_required,
            'leverage': leverage,
            'risk_amount': risk_amount,
            'risk_pct': risk_pct
        }


async def main():
    """Test funksiyasi"""
    api_keys = {}
    
    async with CryptoDerivativesDataProvider(api_keys) as provider:
        print("=" * 80)
        print("AI TRADING EVOLUTION - CRYPTO DERIVATIVES MODULE")
        print("=" * 80)
        print()
        
        # 1. Perpetual Contracts
        print("⚡ PERPETUAL FUTURES:")
        print("-" * 80)
        
        perp_btc = await provider.get_perpetual_contract('BTC-PERP', Exchange.BINANCE)
        if perp_btc:
            print(f"BTC-PERP (Binance)")
            print(f"  Mark: ${perp_btc.mark_price:,.2f}")
            print(f"  Index: ${perp_btc.index_price:,.2f}")
            print(f"  Funding (8h): {perp_btc.funding_rate*100:.4f}%")
            print(f"  Funding (Annual): {perp_btc.funding_rate_annual*100:.2f}%")
            print(f"  OI: ${perp_btc.open_interest/1e9:.2f}B")
        print()
        
        # 2. Funding Rate Arbitrage
        print("💰 FUNDING RATE ARBITRAGE:")
        print("-" * 80)
        funding_arb = FundingRateArbitrage(provider)
        opportunities = await funding_arb.detect_funding_arbitrage(['BTC-PERP', 'ETH-PERP', 'SOL-PERP'])
        
        for i, opp in enumerate(opportunities[:3], 1):
            print(f"{i}. {opp['symbol']} ({opp['exchange']})")
            print(f"   Funding (Annual): {opp['funding_rate_annual']:.2f}%")
            print(f"   Strategy: {opp['strategy']}")
            print(f"   Expected Return: {opp['expected_return']:.2f}%")
            print()
        
        # 3. Dated Futures - Basis Trading
        print("📅 DATED FUTURES - BASIS TRADING:")
        print("-" * 80)
        basis_strategy = BasisTradingStrategy(provider)
        basis_opps = await basis_strategy.detect_basis_opportunities(['BTC', 'ETH'])
        
        for i, opp in enumerate(basis_opps[:3], 1):
            print(f"{i}. {opp['symbol']}")
            print(f"   Expiry: {opp['expiry_date']} ({opp['days_to_expiry']} days)")
            print(f"   Annual Basis: {opp['annual_basis']:.2f}%")
            print(f"   Strategy: {opp['strategy']}")
            print()
        
        # 4. Options - Covered Call
        print("📊 OPTIONS - COVERED CALL STRATEGIYASI:")
        print("-" * 80)
        options_strat = OptionsStrategies(provider)
        expiry = datetime.now() + timedelta(days=30)
        
        covered_calls = await options_strat.covered_call_analysis('BTC', expiry)
        
        for i, cc in enumerate(covered_calls[:3], 1):
            print(f"{i}. Strike: ${cc['strike']:,.0f}")
            print(f"   Premium: ${cc['premium']:,.2f} ({cc['premium_pct']:.2f}%)")
            print(f"   Annual Return: {cc['annual_return']:.1f}%")
            print(f"   Max Profit: {cc['max_profit_pct']:.1f}%")
            print()
        
        # 5. Straddle
        print("🎯 LONG STRADDLE TAHLILI:")
        print("-" * 80)
        straddle = await options_strat.straddle_analysis('BTC', expiry)
        
        if straddle:
            print(f"Strike: ${straddle['strike']:,.0f}")
            print(f"Total Cost: ${straddle['total_cost']:,.2f}")
            print(f"Breakeven Up: ${straddle['breakeven_up']:,.2f}")
            print(f"Breakeven Down: ${straddle['breakeven_down']:,.2f}")
            print(f"Required Move: {straddle['required_move_pct']:.1f}%")
            print(f"Avg IV: {straddle['avg_iv']:.1f}%")
            print(f"Note: {straddle['interpretation']}")
        print()
        
        # 6. Leverage Risk Management
        print("⚠️  LEVERAGE RISK MANAGEMENT:")
        print("-" * 80)
        risk_mgr = LeverageRiskManager()
        
        entry = 68500
        leverage = 10
        
        liq_long = risk_mgr.calculate_liquidation_price(entry, leverage, is_long=True)
        liq_short = risk_mgr.calculate_liquidation_price(entry, leverage, is_long=False)
        
        print(f"Entry Price: ${entry:,.0f}")
        print(f"Leverage: {leverage}x")
        print(f"Liquidation (Long): ${liq_long:,.2f} ({(liq_long-entry)/entry*100:.2f}% down)")
        print(f"Liquidation (Short): ${liq_short:,.2f} ({(liq_short-entry)/entry*100:.2f}% up)")
        print()
        
        # Position sizing
        position = risk_mgr.calculate_position_size(
            capital=10000,
            risk_pct=2,
            entry_price=entry,
            stop_loss_price=entry * 0.95,
            leverage=10
        )
        
        print("Position Sizing (10x leverage, 2% risk):")
        print(f"  Quantity: {position['quantity']:.4f} BTC")
        print(f"  Position Value: ${position['position_value']:,.2f}")
        print(f"  Margin Required: ${position['margin_required']:,.2f}")
        print(f"  Risk Amount: ${position['risk_amount']:,.2f}")
        
        print()
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
