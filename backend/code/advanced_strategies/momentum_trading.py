"""
Momentum Trading - Trend Following Algorithms
==============================================

Momentum strategiyasi - narx yo'nalishi davom etishiga asoslangan strategiya.
Kuchli trend boshlanganida shu yo'nalishda savdo qilish.

Asosiy xususiyatlar:
- Trend detection (ADX, Moving Averages)
- Momentum indicators (MACD, ROC, Stochastic)
- Breakout detection
- Volume confirmation
- Dynamic position sizing
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MomentumSignal:
    """Momentum signal"""
    timestamp: datetime
    signal_type: str  # 'strong_buy', 'buy', 'sell', 'strong_sell', 'hold'
    trend_strength: float  # 0-100
    momentum_score: float  # -100 to +100
    price: float
    indicators: Dict


class MomentumStrategy:
    """
    Momentum Trading Strategy
    
    Trend va momentum indikatorlarini birlashtirib kuchli signallar yaratish
    """
    
    def __init__(
        self,
        symbol: str,
        trend_period: int = 20,
        momentum_period: int = 14
    ):
        self.symbol = symbol
        self.trend_period = trend_period
        self.momentum_period = momentum_period
        
        self.price_history: List[Tuple[datetime, float]] = []
        self.volume_history: List[float] = []
        
        self.signals: List[MomentumSignal] = []
        self.positions: List[Dict] = []
        
        logger.info(f"Momentum Strategy initialized for {symbol}")
    
    def add_data(
        self,
        timestamp: datetime,
        price: float,
        volume: float = 0
    ):
        """Ma'lumot qo'shish"""
        self.price_history.append((timestamp, price))
        self.volume_history.append(volume)
    
    def calculate_ema(
        self,
        period: int
    ) -> Optional[float]:
        """
        Exponential Moving Average hisoblash
        
        Args:
            period: EMA davri
            
        Returns:
            EMA qiymati
        """
        if len(self.price_history) < period:
            return None
        
        prices = [p for _, p in self.price_history]
        
        # EMA calculation
        multiplier = 2 / (period + 1)
        ema = prices[-period]  # Start with SMA
        
        for price in prices[-period + 1:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def calculate_macd(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Tuple[float, float, float]:
        """
        MACD (Moving Average Convergence Divergence) hisoblash
        
        Returns:
            (macd_line, signal_line, histogram)
        """
        if len(self.price_history) < slow_period:
            return None, None, None
        
        # Calculate EMAs
        fast_ema = self.calculate_ema(fast_period)
        slow_ema = self.calculate_ema(slow_period)
        
        if fast_ema is None or slow_ema is None:
            return None, None, None
        
        # MACD line
        macd_line = fast_ema - slow_ema
        
        # Signal line (EMA of MACD)
        # Simplified: use recent MACD values
        # In real implementation, maintain MACD history
        signal_line = macd_line * 0.9  # Approximation
        
        # Histogram
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def calculate_roc(
        self,
        period: int = 14
    ) -> float:
        """
        ROC (Rate of Change) hisoblash
        
        ROC = (current_price - price_n_periods_ago) / price_n_periods_ago * 100
        
        Args:
            period: Davr
            
        Returns:
            ROC qiymati (%)
        """
        if len(self.price_history) < period + 1:
            return 0.0
        
        current_price = self.price_history[-1][1]
        old_price = self.price_history[-(period + 1)][1]
        
        roc = ((current_price - old_price) / old_price) * 100
        
        return roc
    
    def calculate_adx(
        self,
        period: int = 14
    ) -> Tuple[float, float, float]:
        """
        ADX (Average Directional Index) hisoblash
        
        Trend kuchini o'lchaydi (0-100)
        ADX > 25: Kuchli trend
        ADX < 20: Zaif trend
        
        Returns:
            (adx, plus_di, minus_di)
        """
        if len(self.price_history) < period + 1:
            return 0.0, 0.0, 0.0
        
        # Simplified ADX calculation
        prices = [p for _, p in self.price_history[-(period + 1):]]
        
        # Calculate True Range
        tr_values = []
        for i in range(1, len(prices)):
            high_low = abs(prices[i] - prices[i-1])
            tr_values.append(high_low)
        
        atr = np.mean(tr_values)
        
        # Calculate directional movement
        plus_dm = []
        minus_dm = []
        
        for i in range(1, len(prices)):
            up_move = prices[i] - prices[i-1]
            down_move = prices[i-1] - prices[i]
            
            if up_move > down_move and up_move > 0:
                plus_dm.append(up_move)
                minus_dm.append(0)
            elif down_move > up_move and down_move > 0:
                plus_dm.append(0)
                minus_dm.append(down_move)
            else:
                plus_dm.append(0)
                minus_dm.append(0)
        
        # Calculate DI
        plus_di = (np.mean(plus_dm) / atr) * 100 if atr > 0 else 0
        minus_di = (np.mean(minus_dm) / atr) * 100 if atr > 0 else 0
        
        # Calculate ADX
        di_diff = abs(plus_di - minus_di)
        di_sum = plus_di + minus_di
        
        dx = (di_diff / di_sum) * 100 if di_sum > 0 else 0
        adx = dx  # Simplified (should be smoothed)
        
        return adx, plus_di, minus_di
    
    def calculate_stochastic(
        self,
        period: int = 14,
        smooth_k: int = 3,
        smooth_d: int = 3
    ) -> Tuple[float, float]:
        """
        Stochastic Oscillator hisoblash
        
        Returns:
            (%K, %D)
        """
        if len(self.price_history) < period:
            return 50.0, 50.0
        
        recent_prices = [p for _, p in self.price_history[-period:]]
        
        current_price = recent_prices[-1]
        lowest_low = min(recent_prices)
        highest_high = max(recent_prices)
        
        if highest_high == lowest_low:
            k = 50.0
        else:
            k = ((current_price - lowest_low) / (highest_high - lowest_low)) * 100
        
        # %D is smoothed %K
        d = k * 0.9  # Simplified
        
        return k, d
    
    def detect_breakout(
        self,
        current_price: float,
        lookback: int = 20
    ) -> Optional[Dict]:
        """
        Breakout aniqlash (resistance/support breakout)
        
        Args:
            current_price: Joriy narx
            lookback: Necha davr orqaga qarash
            
        Returns:
            Breakout ma'lumotlari
        """
        if len(self.price_history) < lookback:
            return None
        
        recent_prices = [p for _, p in self.price_history[-lookback:]]
        
        resistance = max(recent_prices[:-1])  # Exclude current
        support = min(recent_prices[:-1])
        
        breakout_type = None
        strength = 0.0
        
        # Bullish breakout
        if current_price > resistance:
            breakout_type = 'bullish'
            strength = (current_price - resistance) / resistance * 100
        
        # Bearish breakout
        elif current_price < support:
            breakout_type = 'bearish'
            strength = (support - current_price) / support * 100
        
        if breakout_type:
            return {
                'type': breakout_type,
                'strength': strength,
                'resistance': resistance,
                'support': support,
                'current_price': current_price
            }
        
        return None
    
    def calculate_volume_confirmation(
        self,
        period: int = 20
    ) -> float:
        """
        Volume confirmation hisoblash
        
        Joriy volume vs o'rtacha volume
        
        Returns:
            Volume ratio (1.0 = average)
        """
        if len(self.volume_history) < period:
            return 1.0
        
        recent_volumes = self.volume_history[-period:]
        avg_volume = np.mean(recent_volumes[:-1])  # Exclude current
        
        if avg_volume == 0:
            return 1.0
        
        current_volume = self.volume_history[-1]
        volume_ratio = current_volume / avg_volume
        
        return volume_ratio
    
    def calculate_momentum_score(
        self,
        current_price: float
    ) -> float:
        """
        Umumiy momentum score hisoblash
        
        Barcha indikatorlarni birlashtirib -100 dan +100 gacha score
        
        Returns:
            Momentum score
        """
        scores = []
        weights = []
        
        # MACD
        macd_line, signal_line, histogram = self.calculate_macd()
        if macd_line is not None:
            if macd_line > signal_line:
                macd_score = min(100, histogram * 10)  # Scale to 0-100
            else:
                macd_score = max(-100, histogram * 10)
            scores.append(macd_score)
            weights.append(0.25)
        
        # ROC
        roc = self.calculate_roc()
        roc_score = np.clip(roc * 5, -100, 100)  # Scale to -100 to +100
        scores.append(roc_score)
        weights.append(0.20)
        
        # ADX
        adx, plus_di, minus_di = self.calculate_adx()
        if plus_di > minus_di:
            adx_score = adx  # Uptrend
        else:
            adx_score = -adx  # Downtrend
        scores.append(adx_score)
        weights.append(0.25)
        
        # Stochastic
        k, d = self.calculate_stochastic()
        stoch_score = (k - 50) * 2  # Scale to -100 to +100
        scores.append(stoch_score)
        weights.append(0.15)
        
        # Breakout
        breakout = self.detect_breakout(current_price)
        if breakout:
            if breakout['type'] == 'bullish':
                breakout_score = 50 + breakout['strength'] * 10
            else:
                breakout_score = -50 - breakout['strength'] * 10
            scores.append(np.clip(breakout_score, -100, 100))
            weights.append(0.15)
        
        # Weighted average
        if scores:
            momentum_score = np.average(scores, weights=weights[:len(scores)])
        else:
            momentum_score = 0.0
        
        return momentum_score
    
    def calculate_trend_strength(self) -> float:
        """
        Trend kuchini hisoblash (0-100)
        
        Returns:
            Trend strength
        """
        adx, plus_di, minus_di = self.calculate_adx()
        
        # ADX kuchli trend ko'rsatkichi
        trend_strength = adx
        
        return trend_strength
    
    def generate_momentum_signal(
        self,
        current_price: float,
        timestamp: datetime
    ) -> Optional[MomentumSignal]:
        """
        Momentum signalini yaratish
        
        Args:
            current_price: Joriy narx
            timestamp: Vaqt
            
        Returns:
            Momentum signal
        """
        momentum_score = self.calculate_momentum_score(current_price)
        trend_strength = self.calculate_trend_strength()
        
        # Volume confirmation
        volume_ratio = self.calculate_volume_confirmation()
        
        # Signal logic
        signal_type = 'hold'
        
        # Strong buy: High momentum + strong trend + volume confirmation
        if momentum_score > 60 and trend_strength > 25 and volume_ratio > 1.2:
            signal_type = 'strong_buy'
        
        # Buy: Positive momentum + trend
        elif momentum_score > 30 and trend_strength > 20:
            signal_type = 'buy'
        
        # Strong sell: High negative momentum + strong trend
        elif momentum_score < -60 and trend_strength > 25 and volume_ratio > 1.2:
            signal_type = 'strong_sell'
        
        # Sell: Negative momentum
        elif momentum_score < -30 and trend_strength > 20:
            signal_type = 'sell'
        
        # Get all indicators
        macd_line, signal_line, histogram = self.calculate_macd()
        roc = self.calculate_roc()
        adx, plus_di, minus_di = self.calculate_adx()
        k, d = self.calculate_stochastic()
        breakout = self.detect_breakout(current_price)
        
        if signal_type != 'hold':
            signal = MomentumSignal(
                timestamp=timestamp,
                signal_type=signal_type,
                trend_strength=trend_strength,
                momentum_score=momentum_score,
                price=current_price,
                indicators={
                    'macd_line': macd_line,
                    'macd_signal': signal_line,
                    'macd_histogram': histogram,
                    'roc': roc,
                    'adx': adx,
                    'plus_di': plus_di,
                    'minus_di': minus_di,
                    'stoch_k': k,
                    'stoch_d': d,
                    'volume_ratio': volume_ratio,
                    'breakout': breakout
                }
            )
            
            self.signals.append(signal)
            
            logger.info(f"📊 Momentum Signal: {signal_type.upper()}")
            logger.info(f"   Momentum Score: {momentum_score:.2f}")
            logger.info(f"   Trend Strength: {trend_strength:.2f}")
            logger.info(f"   Volume Ratio: {volume_ratio:.2f}x")
            
            return signal
        
        return None
    
    def calculate_position_size(
        self,
        account_size: float,
        risk_per_trade: float,
        stop_loss_pct: float,
        momentum_score: float
    ) -> float:
        """
        Dynamic position sizing (momentum asosida)
        
        Args:
            account_size: Account hajmi
            risk_per_trade: Har bir trade uchun risk (%)
            stop_loss_pct: Stop loss (%)
            momentum_score: Momentum score
            
        Returns:
            Position size ($)
        """
        # Base position size
        risk_amount = account_size * (risk_per_trade / 100)
        base_position = risk_amount / (stop_loss_pct / 100)
        
        # Adjust based on momentum strength
        # Stronger momentum = larger position
        momentum_multiplier = 1.0 + (abs(momentum_score) / 100) * 0.5  # Up to 1.5x
        
        adjusted_position = base_position * momentum_multiplier
        
        # Cap at 20% of account
        max_position = account_size * 0.2
        final_position = min(adjusted_position, max_position)
        
        return final_position
    
    def calculate_trailing_stop(
        self,
        entry_price: float,
        current_price: float,
        atr: float,
        atr_multiplier: float = 2.0
    ) -> float:
        """
        Trailing stop loss hisoblash (ATR asosida)
        
        Args:
            entry_price: Kirish narxi
            current_price: Joriy narx
            atr: Average True Range
            atr_multiplier: ATR koeffitsiyenti
            
        Returns:
            Trailing stop narxi
        """
        # For long positions
        if current_price > entry_price:
            trailing_stop = current_price - (atr * atr_multiplier)
            # Ensure stop is above entry
            trailing_stop = max(trailing_stop, entry_price)
        else:
            trailing_stop = entry_price - (atr * atr_multiplier)
        
        return trailing_stop


# Multi-Timeframe Momentum Strategy
class MultiTimeframeMomentumStrategy:
    """
    Multi-timeframe momentum strategiyasi
    
    Turli vaqt oraliqlarida momentum tahlil qilish
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.timeframes = {
            '1h': MomentumStrategy(symbol, trend_period=20, momentum_period=14),
            '4h': MomentumStrategy(symbol, trend_period=20, momentum_period=14),
            '1d': MomentumStrategy(symbol, trend_period=20, momentum_period=14)
        }
    
    def add_data(
        self,
        timeframe: str,
        timestamp: datetime,
        price: float,
        volume: float = 0
    ):
        """Ma'lumot qo'shish"""
        if timeframe in self.timeframes:
            self.timeframes[timeframe].add_data(timestamp, price, volume)
    
    def get_aggregated_signal(
        self,
        current_price: float,
        timestamp: datetime
    ) -> Dict:
        """
        Barcha timeframe signallarini birlashtirib olish
        
        Returns:
            Aggregated signal
        """
        signals = {}
        momentum_scores = []
        trend_strengths = []
        
        for tf, strategy in self.timeframes.items():
            signal = strategy.generate_momentum_signal(current_price, timestamp)
            
            if signal:
                signals[tf] = signal
                momentum_scores.append(signal.momentum_score)
                trend_strengths.append(signal.trend_strength)
        
        if not signals:
            return None
        
        # Aggregate scores
        avg_momentum = np.mean(momentum_scores)
        avg_trend_strength = np.mean(trend_strengths)
        
        # Count signal types
        buy_count = sum(1 for s in signals.values() if 'buy' in s.signal_type)
        sell_count = sum(1 for s in signals.values() if 'sell' in s.signal_type)
        
        # Determine overall signal
        if buy_count >= 2:
            overall_signal = 'buy'
        elif sell_count >= 2:
            overall_signal = 'sell'
        else:
            overall_signal = 'hold'
        
        return {
            'overall_signal': overall_signal,
            'average_momentum': avg_momentum,
            'average_trend_strength': avg_trend_strength,
            'timeframe_signals': {tf: s.signal_type for tf, s in signals.items()},
            'buy_count': buy_count,
            'sell_count': sell_count
        }


# Example usage
def main():
    """Test momentum strategy"""
    import random
    
    print("="*60)
    print("MOMENTUM STRATEGY TEST")
    print("="*60)
    
    # Initialize strategy
    strategy = MomentumStrategy(
        symbol='BTC/USDT',
        trend_period=20,
        momentum_period=14
    )
    
    # Simulate trending price data
    base_price = 40000
    trend = 100  # Uptrend
    current_time = datetime.now()
    
    for i in range(100):
        # Trending price with noise
        noise = random.gauss(0, 200)
        base_price += trend + noise
        
        # Occasional trend reversal
        if i % 30 == 0:
            trend = -trend
        
        volume = random.uniform(1000, 5000)
        
        strategy.add_data(current_time, base_price, volume)
        
        # Generate signal
        if i >= 30:  # After enough data
            signal = strategy.generate_momentum_signal(base_price, current_time)
            
            if signal:
                print(f"\nDay {i}: {signal.signal_type.upper()}")
                print(f"  Price: ${base_price:.2f}")
                print(f"  Momentum Score: {signal.momentum_score:.2f}")
                print(f"  Trend Strength: {signal.trend_strength:.2f}")
        
        current_time = current_time.replace(hour=(current_time.hour + 1) % 24)
    
    # Position sizing example
    print("\n" + "="*60)
    print("DYNAMIC POSITION SIZING")
    print("="*60)
    
    account_size = 10000
    risk_per_trade = 2.0  # 2%
    stop_loss = 3.0  # 3%
    
    for momentum in [30, 60, 90]:
        position_size = strategy.calculate_position_size(
            account_size, risk_per_trade, stop_loss, momentum
        )
        print(f"Momentum {momentum}: Position size = ${position_size:.2f}")


if __name__ == '__main__':
    main()
