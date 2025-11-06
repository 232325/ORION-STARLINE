"""
Mean Reversion Strategy - Statistical Arbitrage
================================================

Mean reversion strategiyasi - narxning o'rtacha qiymatga qaytishiga asoslangan strategiya.
Narx o'rtachadan haddan tashqari yuqori yoki past ketganda savdo qilish.

Asosiy xususiyatlar:
- Bollinger Bands mean reversion
- Z-score based trading
- Pairs trading (statistical arbitrage)
- RSI mean reversion
- Moving average crossover
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Signal:
    """Trading signal"""
    timestamp: datetime
    signal_type: str  # 'buy', 'sell', 'hold'
    confidence: float  # 0-1
    price: float
    indicator_values: Dict


class MeanReversionStrategy:
    """
    Mean Reversion Trading Strategy
    
    Turli xil mean reversion indikatorlari va signallari
    """
    
    def __init__(
        self,
        symbol: str,
        lookback_period: int = 20,
        entry_threshold: float = 2.0,  # Standard deviations
        exit_threshold: float = 0.5
    ):
        self.symbol = symbol
        self.lookback_period = lookback_period
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        
        self.price_history: List[Tuple[datetime, float]] = []
        self.signals: List[Signal] = []
        self.positions: List[Dict] = []
        
        logger.info(f"Mean Reversion Strategy initialized for {symbol}")
    
    def add_price(self, timestamp: datetime, price: float):
        """Narx qo'shish"""
        self.price_history.append((timestamp, price))
    
    def calculate_bollinger_bands(
        self,
        period: int = 20,
        num_std: float = 2.0
    ) -> Tuple[float, float, float]:
        """
        Bollinger Bands hisoblash
        
        Args:
            period: MA davri
            num_std: Standard deviation koeffitsiyenti
            
        Returns:
            (upper_band, middle_band, lower_band)
        """
        if len(self.price_history) < period:
            return None, None, None
        
        recent_prices = [p for _, p in self.price_history[-period:]]
        
        middle_band = np.mean(recent_prices)
        std_dev = np.std(recent_prices)
        
        upper_band = middle_band + (num_std * std_dev)
        lower_band = middle_band - (num_std * std_dev)
        
        return upper_band, middle_band, lower_band
    
    def calculate_zscore(
        self,
        current_price: float,
        period: int = 20
    ) -> float:
        """
        Z-score hisoblash
        
        Z-score = (current_price - mean) / std_dev
        
        Args:
            current_price: Joriy narx
            period: Davr
            
        Returns:
            Z-score
        """
        if len(self.price_history) < period:
            return 0.0
        
        recent_prices = [p for _, p in self.price_history[-period:]]
        
        mean_price = np.mean(recent_prices)
        std_dev = np.std(recent_prices)
        
        if std_dev == 0:
            return 0.0
        
        zscore = (current_price - mean_price) / std_dev
        
        return zscore
    
    def calculate_rsi(
        self,
        period: int = 14
    ) -> float:
        """
        RSI (Relative Strength Index) hisoblash
        
        Args:
            period: RSI davri
            
        Returns:
            RSI qiymati (0-100)
        """
        if len(self.price_history) < period + 1:
            return 50.0  # Neutral
        
        recent_prices = [p for _, p in self.price_history[-(period + 1):]]
        
        # Calculate price changes
        deltas = np.diff(recent_prices)
        
        # Separate gains and losses
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Average gains and losses
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_moving_averages(
        self,
        short_period: int = 10,
        long_period: int = 50
    ) -> Tuple[float, float]:
        """
        Moving averages hisoblash
        
        Args:
            short_period: Qisqa MA davri
            long_period: Uzun MA davri
            
        Returns:
            (short_ma, long_ma)
        """
        if len(self.price_history) < long_period:
            return None, None
        
        prices = [p for _, p in self.price_history]
        
        short_ma = np.mean(prices[-short_period:])
        long_ma = np.mean(prices[-long_period:])
        
        return short_ma, long_ma
    
    def bollinger_bands_signal(
        self,
        current_price: float,
        timestamp: datetime
    ) -> Optional[Signal]:
        """
        Bollinger Bands asosida signal
        
        Args:
            current_price: Joriy narx
            timestamp: Vaqt
            
        Returns:
            Trading signal
        """
        upper, middle, lower = self.calculate_bollinger_bands()
        
        if upper is None:
            return None
        
        # Signal logic
        signal_type = 'hold'
        confidence = 0.0
        
        # Price touches or crosses lower band = BUY signal
        if current_price <= lower:
            signal_type = 'buy'
            # Confidence based on how far below the lower band
            deviation = (lower - current_price) / lower
            confidence = min(1.0, deviation / 0.02)  # Max confidence at 2% below
        
        # Price touches or crosses upper band = SELL signal
        elif current_price >= upper:
            signal_type = 'sell'
            deviation = (current_price - upper) / upper
            confidence = min(1.0, deviation / 0.02)
        
        # Price near middle band = EXIT signal (return to mean)
        elif abs(current_price - middle) / middle < 0.005:  # Within 0.5% of middle
            if len(self.positions) > 0:
                last_position = self.positions[-1]
                if last_position['status'] == 'open':
                    signal_type = 'close'
                    confidence = 0.7
        
        if signal_type != 'hold':
            signal = Signal(
                timestamp=timestamp,
                signal_type=signal_type,
                confidence=confidence,
                price=current_price,
                indicator_values={
                    'upper_band': upper,
                    'middle_band': middle,
                    'lower_band': lower,
                    'bb_width': (upper - lower) / middle
                }
            )
            
            self.signals.append(signal)
            return signal
        
        return None
    
    def zscore_signal(
        self,
        current_price: float,
        timestamp: datetime
    ) -> Optional[Signal]:
        """
        Z-score asosida signal
        
        Args:
            current_price: Joriy narx
            timestamp: Vaqt
            
        Returns:
            Trading signal
        """
        zscore = self.calculate_zscore(current_price)
        
        signal_type = 'hold'
        confidence = 0.0
        
        # Z-score < -entry_threshold = BUY (oversold)
        if zscore <= -self.entry_threshold:
            signal_type = 'buy'
            confidence = min(1.0, abs(zscore) / (self.entry_threshold * 2))
        
        # Z-score > +entry_threshold = SELL (overbought)
        elif zscore >= self.entry_threshold:
            signal_type = 'sell'
            confidence = min(1.0, abs(zscore) / (self.entry_threshold * 2))
        
        # Z-score near 0 = EXIT (return to mean)
        elif abs(zscore) <= self.exit_threshold:
            if len(self.positions) > 0:
                last_position = self.positions[-1]
                if last_position['status'] == 'open':
                    signal_type = 'close'
                    confidence = 0.8
        
        if signal_type != 'hold':
            signal = Signal(
                timestamp=timestamp,
                signal_type=signal_type,
                confidence=confidence,
                price=current_price,
                indicator_values={
                    'zscore': zscore,
                    'entry_threshold': self.entry_threshold,
                    'exit_threshold': self.exit_threshold
                }
            )
            
            self.signals.append(signal)
            return signal
        
        return None
    
    def rsi_signal(
        self,
        current_price: float,
        timestamp: datetime,
        oversold_level: float = 30,
        overbought_level: float = 70
    ) -> Optional[Signal]:
        """
        RSI asosida signal
        
        Args:
            current_price: Joriy narx
            timestamp: Vaqt
            oversold_level: Oversold darajasi
            overbought_level: Overbought darajasi
            
        Returns:
            Trading signal
        """
        rsi = self.calculate_rsi()
        
        signal_type = 'hold'
        confidence = 0.0
        
        # RSI < oversold_level = BUY
        if rsi <= oversold_level:
            signal_type = 'buy'
            confidence = (oversold_level - rsi) / oversold_level
        
        # RSI > overbought_level = SELL
        elif rsi >= overbought_level:
            signal_type = 'sell'
            confidence = (rsi - overbought_level) / (100 - overbought_level)
        
        # RSI near 50 = NEUTRAL/EXIT
        elif 45 <= rsi <= 55:
            if len(self.positions) > 0:
                last_position = self.positions[-1]
                if last_position['status'] == 'open':
                    signal_type = 'close'
                    confidence = 0.6
        
        if signal_type != 'hold':
            signal = Signal(
                timestamp=timestamp,
                signal_type=signal_type,
                confidence=confidence,
                price=current_price,
                indicator_values={
                    'rsi': rsi,
                    'oversold_level': oversold_level,
                    'overbought_level': overbought_level
                }
            )
            
            self.signals.append(signal)
            return signal
        
        return None
    
    def generate_combined_signal(
        self,
        current_price: float,
        timestamp: datetime
    ) -> Optional[Signal]:
        """
        Barcha indikatorlarni birlashtirib signal yaratish
        
        Args:
            current_price: Joriy narx
            timestamp: Vaqt
            
        Returns:
            Combined signal
        """
        # Get individual signals
        bb_signal = self.bollinger_bands_signal(current_price, timestamp)
        z_signal = self.zscore_signal(current_price, timestamp)
        rsi_signal = self.rsi_signal(current_price, timestamp)
        
        signals = [s for s in [bb_signal, z_signal, rsi_signal] if s is not None]
        
        if not signals:
            return None
        
        # Count signal types
        buy_signals = [s for s in signals if s.signal_type == 'buy']
        sell_signals = [s for s in signals if s.signal_type == 'sell']
        
        # Consensus logic
        if len(buy_signals) >= 2:
            # At least 2 indicators agree on BUY
            avg_confidence = np.mean([s.confidence for s in buy_signals])
            
            combined_signal = Signal(
                timestamp=timestamp,
                signal_type='buy',
                confidence=avg_confidence,
                price=current_price,
                indicator_values={
                    'num_indicators': len(signals),
                    'num_buy': len(buy_signals),
                    'num_sell': len(sell_signals)
                }
            )
            
            return combined_signal
        
        elif len(sell_signals) >= 2:
            # At least 2 indicators agree on SELL
            avg_confidence = np.mean([s.confidence for s in sell_signals])
            
            combined_signal = Signal(
                timestamp=timestamp,
                signal_type='sell',
                confidence=avg_confidence,
                price=current_price,
                indicator_values={
                    'num_indicators': len(signals),
                    'num_buy': len(buy_signals),
                    'num_sell': len(sell_signals)
                }
            )
            
            return combined_signal
        
        return None


class PairsTradingStrategy:
    """
    Pairs Trading (Statistical Arbitrage)
    
    Ikki korrelyatsiya qilgan aktivlarning narx farqini savdo qilish
    """
    
    def __init__(
        self,
        symbol1: str,
        symbol2: str,
        lookback_period: int = 60,
        entry_threshold: float = 2.0,  # Z-score
        exit_threshold: float = 0.5
    ):
        self.symbol1 = symbol1
        self.symbol2 = symbol2
        self.lookback_period = lookback_period
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        
        self.price_history1: List[float] = []
        self.price_history2: List[float] = []
        
        self.spread_history: List[float] = []
        self.positions: List[Dict] = []
        
        logger.info(f"Pairs Trading Strategy: {symbol1} vs {symbol2}")
    
    def add_prices(self, price1: float, price2: float):
        """Narxlarni qo'shish"""
        self.price_history1.append(price1)
        self.price_history2.append(price2)
        
        # Calculate spread
        if len(self.price_history1) >= 2:
            # Log spread (ratio)
            spread = np.log(price1 / price2)
            self.spread_history.append(spread)
    
    def calculate_hedge_ratio(self) -> float:
        """
        Hedge ratio hisoblash (linear regression)
        
        Returns:
            Beta koeffitsiyenti
        """
        if len(self.price_history1) < self.lookback_period:
            return 1.0
        
        prices1 = np.array(self.price_history1[-self.lookback_period:])
        prices2 = np.array(self.price_history2[-self.lookback_period:])
        
        # Linear regression: price1 = beta * price2 + alpha
        beta, alpha = np.polyfit(prices2, prices1, 1)
        
        return beta
    
    def calculate_spread_zscore(self) -> float:
        """
        Spread Z-score hisoblash
        
        Returns:
            Z-score
        """
        if len(self.spread_history) < self.lookback_period:
            return 0.0
        
        recent_spreads = self.spread_history[-self.lookback_period:]
        
        mean_spread = np.mean(recent_spreads)
        std_spread = np.std(recent_spreads)
        
        if std_spread == 0:
            return 0.0
        
        current_spread = self.spread_history[-1]
        zscore = (current_spread - mean_spread) / std_spread
        
        return zscore
    
    def generate_pairs_signal(
        self,
        timestamp: datetime
    ) -> Optional[Dict]:
        """
        Pairs trading signalini yaratish
        
        Returns:
            Signal dict
        """
        zscore = self.calculate_spread_zscore()
        hedge_ratio = self.calculate_hedge_ratio()
        
        signal_type = 'hold'
        
        # Spread too high (symbol1 overpriced relative to symbol2)
        # SHORT symbol1, LONG symbol2
        if zscore >= self.entry_threshold:
            signal_type = 'short_long'  # Short asset1, Long asset2
        
        # Spread too low (symbol1 underpriced relative to symbol2)
        # LONG symbol1, SHORT symbol2
        elif zscore <= -self.entry_threshold:
            signal_type = 'long_short'  # Long asset1, Short asset2
        
        # Spread converged to mean
        elif abs(zscore) <= self.exit_threshold:
            if len(self.positions) > 0:
                last_position = self.positions[-1]
                if last_position['status'] == 'open':
                    signal_type = 'close'
        
        if signal_type != 'hold':
            signal = {
                'timestamp': timestamp,
                'signal_type': signal_type,
                'zscore': zscore,
                'hedge_ratio': hedge_ratio,
                'spread': self.spread_history[-1],
                'price1': self.price_history1[-1],
                'price2': self.price_history2[-1]
            }
            
            logger.info(f"📊 Pairs signal: {signal_type}")
            logger.info(f"   Z-score: {zscore:.2f}")
            logger.info(f"   Hedge ratio: {hedge_ratio:.4f}")
            
            return signal
        
        return None
    
    def calculate_correlation(self) -> float:
        """
        Ikki asset orasidagi korrelyatsiya hisoblash
        
        Returns:
            Correlation coefficient
        """
        if len(self.price_history1) < self.lookback_period:
            return 0.0
        
        prices1 = np.array(self.price_history1[-self.lookback_period:])
        prices2 = np.array(self.price_history2[-self.lookback_period:])
        
        correlation = np.corrcoef(prices1, prices2)[0, 1]
        
        return correlation


# Example usage
def main():
    """Test mean reversion strategies"""
    import random
    
    print("="*60)
    print("MEAN REVERSION STRATEGY TEST")
    print("="*60)
    
    # Initialize strategy
    strategy = MeanReversionStrategy(
        symbol='BTC/USDT',
        lookback_period=20,
        entry_threshold=2.0,
        exit_threshold=0.5
    )
    
    # Simulate mean-reverting price data
    base_price = 45000
    current_time = datetime.now()
    
    for i in range(100):
        # Mean-reverting random walk
        deviation = random.gauss(0, 500)
        mean_reversion = (45000 - base_price) * 0.1  # Pull towards mean
        
        base_price += deviation + mean_reversion
        base_price = max(35000, min(55000, base_price))  # Bounds
        
        strategy.add_price(current_time, base_price)
        
        # Generate signal
        signal = strategy.generate_combined_signal(base_price, current_time)
        
        if signal:
            print(f"\nDay {i}: {signal.signal_type.upper()} signal")
            print(f"  Price: ${base_price:.2f}")
            print(f"  Confidence: {signal.confidence:.2f}")
        
        current_time = current_time.replace(day=current_time.day + 1)
    
    # Pairs trading test
    print("\n" + "="*60)
    print("PAIRS TRADING STRATEGY TEST")
    print("="*60)
    
    pairs_strategy = PairsTradingStrategy(
        symbol1='BTC',
        symbol2='ETH',
        lookback_period=30
    )
    
    # Simulate correlated prices
    btc_price = 45000
    eth_price = 3000
    
    for i in range(60):
        # Add some spread variation
        btc_change = random.gauss(0, 500)
        eth_change = btc_change / 15 + random.gauss(0, 30)  # Correlated
        
        btc_price += btc_change
        eth_price += eth_change
        
        pairs_strategy.add_prices(btc_price, eth_price)
        
        if i >= 30:  # After enough data
            signal = pairs_strategy.generate_pairs_signal(datetime.now())
    
    # Show correlation
    correlation = pairs_strategy.calculate_correlation()
    print(f"\nBTC-ETH Correlation: {correlation:.4f}")


if __name__ == '__main__':
    main()
