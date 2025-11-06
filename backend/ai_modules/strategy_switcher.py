"""
Strategy Switcher System
Strategiya almashtirish tizimi
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta
import json
from market_regime_detector import MarketRegimeDetector, MarketRegime, RegimeConfig, MarketRegimeResult

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StrategyType(Enum):
    """Strategiya turlari"""
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    MOMENTUM = "momentum"
    BREAKOUT = "breakout"
    SCALPING = "scalping"
    SWING_TRADING = "swing_trading"
    HIGH_FREQUENCY = "high_frequency"
    RISK_PARITY = "risk_parity"
    DOLLAR_COST_AVERAGING = "dca"
    VOLATILITY_ARBITRAGE = "vol_arbitrage"

@dataclass
class StrategyConfig:
    """Strategiya konfiguratsiyasi"""
    name: str
    type: StrategyType
    min_confidence: float = 0.6
    max_position_size: float = 0.1
    stop_loss_pct: float = 0.02
    take_profit_pct: float = 0.06
    lookback_period: int = 20
    rebalance_frequency: str = 'daily'
    max_drawdown_limit: float = 0.15
    sharpe_target: float = 1.0
    enabled: bool = True
    risk_multiplier: float = 1.0
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Position:
    """Trading pozitsiyasi"""
    symbol: str
    size: float
    entry_price: float
    current_price: float
    side: str  # 'long' or 'short'
    stop_loss: float
    take_profit: float
    timestamp: datetime
    strategy: str
    pnl: float = 0.0
    pnl_pct: float = 0.0

@dataclass
class StrategyPerformance:
    """Strategiya natijalari"""
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    avg_trade_duration: float
    volatility: float
    calmar_ratio: float
    sortino_ratio: float
    var_95: float  # Value at Risk 95%

class StrategySwitcher:
    """Strategiya almashtirish tizimi"""
    
    def __init__(self, regime_detector: MarketRegimeDetector = None):
        self.regime_detector = regime_detector or MarketRegimeDetector()
        self.strategies = {}
        self.positions = {}
        self.performance_history = {}
        self.current_regime = None
        self.risk_manager = RiskManager()
        self.capital_allocator = CapitalAllocator()
        self.active_strategy = None
        
        # Default strategiya konfiguratsiyasi
        self._initialize_default_strategies()
    
    def _initialize_default_strategies(self):
        """Default strategiyalarni yaratish"""
        
        # Trend Following Strategy
        self.strategies[StrategyType.TREND_FOLLOWING] = StrategyConfig(
            name="Trend Following",
            type=StrategyType.TREND_FOLLOWING,
            min_confidence=0.7,
            max_position_size=0.15,
            stop_loss_pct=0.03,
            take_profit_pct=0.09,
            parameters={'ma_fast': 10, 'ma_slow': 50, 'adx_threshold': 25}
        )
        
        # Mean Reversion Strategy
        self.strategies[StrategyType.MEAN_REVERSION] = StrategyConfig(
            name="Mean Reversion",
            type=StrategyType.MEAN_REVERSION,
            min_confidence=0.6,
            max_position_size=0.1,
            stop_loss_pct=0.025,
            take_profit_pct=0.05,
            parameters={'rsi_oversold': 30, 'rsi_overbought': 70, 'bb_std': 2.0}
        )
        
        # Momentum Strategy
        self.strategies[StrategyType.MOMENTUM] = StrategyConfig(
            name="Momentum",
            type=StrategyType.MOMENTUM,
            min_confidence=0.65,
            max_position_size=0.12,
            stop_loss_pct=0.035,
            take_profit_pct=0.08,
            parameters={'momentum_period': 10, 'volume_threshold': 1.5}
        )
        
        # Breakout Strategy
        self.strategies[StrategyType.BREAKOUT] = StrategyConfig(
            name="Breakout",
            type=StrategyType.BREAKOUT,
            min_confidence=0.7,
            max_position_size=0.08,
            stop_loss_pct=0.02,
            take_profit_pct=0.1,
            parameters={'volatility_period': 20, 'breakout_threshold': 2.0}
        )
        
        # Scalping Strategy
        self.strategies[StrategyType.SCALPING] = StrategyConfig(
            name="Scalping",
            type=StrategyType.SCALPING,
            min_confidence=0.8,
            max_position_size=0.05,
            stop_loss_pct=0.01,
            take_profit_pct=0.02,
            parameters={'timeframe': '1m', 'tick_size': 0.001}
        )
        
        # Swing Trading Strategy
        self.strategies[StrategyType.SWING_TRADING] = StrategyConfig(
            name="Swing Trading",
            type=StrategyType.SWING_TRADING,
            min_confidence=0.6,
            max_position_size=0.2,
            stop_loss_pct=0.05,
            take_profit_pct=0.15,
            parameters={'swing_period': 14, 'trend_strength': 0.7}
        )
        
        # Risk Parity Strategy
        self.strategies[StrategyType.RISK_PARITY] = StrategyConfig(
            name="Risk Parity",
            type=StrategyType.RISK_PARITY,
            min_confidence=0.5,
            max_position_size=0.08,
            stop_loss_pct=0.04,
            take_profit_pct=0.08,
            parameters={'risk_budget': 0.25, 'correlation_threshold': 0.7}
        )
        
        # DCA Strategy
        self.strategies[StrategyType.DOLLAR_COST_AVERAGING] = StrategyConfig(
            name="Dollar Cost Averaging",
            type=StrategyType.DOLLAR_COST_AVERAGING,
            min_confidence=0.4,
            max_position_size=0.25,
            stop_loss_pct=0.1,
            take_profit_pct=0.2,
            parameters={'dca_frequency': 'weekly', 'dca_amount': 0.1}
        )
        
        # Volatility Arbitrage Strategy
        self.strategies[StrategyType.VOLATILITY_ARBITRAGE] = StrategyConfig(
            name="Volatility Arbitrage",
            type=StrategyType.VOLATILITY_ARBITRAGE,
            min_confidence=0.7,
            max_position_size=0.1,
            stop_loss_pct=0.03,
            take_profit_pct=0.06,
            parameters={'vol_window': 20, 'vol_threshold': 2.0}
        )
    
    def select_strategy(self, market_data: pd.DataFrame, current_time: datetime = None) -> Optional[StrategyConfig]:
        """
        Bozor sharoitiga qarab eng yaxshi strategiyani tanlash
        
        Args:
            market_data: OHLCV ma'lumotlari
            current_time: Joriy vaqt
            
        Returns:
            StrategyConfig: Tanlangan strategiya
        """
        try:
            # Rejim aniqlash
            regime_result = self.regime_detector.detect_regime(market_data)
            self.current_regime = regime_result
            
            # Potentsial strategiyalar
            candidate_strategies = self._get_candidate_strategies(regime_result)
            
            # Eng yaxshi strategiyani tanlash
            best_strategy = self._rank_strategies(candidate_strategies, market_data, regime_result)
            
            if best_strategy and best_strategy.min_confidence <= regime_result.confidence:
                self.active_strategy = best_strategy
                logger.info(f"Tanlangan strategiya: {best_strategy.name} (rejim: {regime_result.regime.value})")
                return best_strategy
            
            return None
            
        except Exception as e:
            logger.error(f"Strategiya tanlashda xatolik: {e}")
            return None
    
    def _get_candidate_strategies(self, regime_result: MarketRegimeResult) -> List[StrategyConfig]:
        """Rejimga mos strategiyalarni tanlash"""
        candidates = []
        regime = regime_result.regime
        
        # Rejim asosida strategiya mapping
        regime_strategy_map = {
            MarketRegime.BULL_MARKET: [
                StrategyType.TREND_FOLLOWING,
                StrategyType.MOMENTUM,
                StrategyType.BREAKOUT,
                StrategyType.SWING_TRADING
            ],
            MarketRegime.BEAR_MARKET: [
                StrategyType.RISK_PARITY,
                StrategyType.VOLATILITY_ARBITRAGE,
                StrategyType.MEAN_REVERSION
            ],
            MarketRegime.SIDEWAYS_MARKET: [
                StrategyType.MEAN_REVERSION,
                StrategyType.SCALPING,
                StrategyType.RISK_PARITY
            ],
            MarketRegime.HIGH_VOLATILITY: [
                StrategyType.VOLATILITY_ARBITRAGE,
                StrategyType.SCALPING,
                StrategyType.MEAN_REVERSION
            ],
            MarketRegime.LOW_VOLATILITY: [
                StrategyType.TREND_FOLLOWING,
                StrategyType.BREAKOUT,
                StrategyType.SWING_TRADING
            ],
            MarketRegime.BREAKOUT_MARKET: [
                StrategyType.BREAKOUT,
                StrategyType.MOMENTUM,
                StrategyType.TREND_FOLLOWING
            ],
            MarketRegime.REVERSAL_MARKET: [
                StrategyType.MEAN_REVERSION,
                StrategyType.VOLATILITY_ARBITRAGE
            ],
            MarketRegime.CONSOLIDATION: [
                StrategyType.SCALPING,
                StrategyType.RISK_PARITY,
                StrategyType.DOLLAR_COST_AVERAGING
            ]
        }
        
        # Ishonchlilik darajasiga qarab filter
        for strategy_type in regime_strategy_map.get(regime, []):
            strategy_config = self.strategies.get(strategy_type)
            if strategy_config and strategy_config.enabled:
                candidates.append(strategy_config)
        
        return candidates
    
    def _rank_strategies(self, candidates: List[StrategyConfig], market_data: pd.DataFrame, 
                        regime_result: MarketRegimeResult) -> Optional[StrategyConfig]:
        """Strategiyalarni reytinglash"""
        if not candidates:
            return None
        
        scores = []
        indicators = regime_result.indicators
        
        for strategy in candidates:
            score = 0.0
            
            # Rejim mosligi
            score += 0.3
            
            # Indikatorlarga asoslangan ball
            if strategy.type == StrategyType.TREND_FOLLOWING:
                if indicators.get('adx', 0) > 25:
                    score += 0.3
                if indicators.get('sma_10', 0) > indicators.get('sma_50', 0):
                    score += 0.2
                    
            elif strategy.type == StrategyType.MEAN_REVERSION:
                rsi = indicators.get('rsi', 50)
                if rsi < 30 or rsi > 70:
                    score += 0.4
                if indicators.get('adx', 0) < 25:
                    score += 0.2
                    
            elif strategy.type == StrategyType.MOMENTUM:
                if indicators.get('momentum', 0) > 0:
                    score += 0.3
                if indicators.get('volume_ratio', 1) > 1.2:
                    score += 0.3
                    
            elif strategy.type == StrategyType.BREAKOUT:
                bb_position = indicators.get('price_position', 0.5)
                if bb_position > 0.8 or bb_position < 0.2:
                    score += 0.4
                if indicators.get('volume_ratio', 1) > 1.5:
                    score += 0.2
                    
            elif strategy.type == StrategyType.SCALPING:
                volatility = indicators.get('volatility', 0)
                if 0.01 < volatility < 0.03:
                    score += 0.3
                if indicators.get('adx', 0) < 30:
                    score += 0.3
                    
            # Historical performance bonus
            if strategy.type.value in self.performance_history:
                perf = self.performance_history[strategy.type.value]
                if perf.get('sharpe_ratio', 0) > 1.0:
                    score += 0.2
                if perf.get('win_rate', 0) > 0.6:
                    score += 0.1
            
            scores.append((strategy, score))
        
        # Eng yuqori ballni olgan strategiya
        if scores:
            best_strategy = max(scores, key=lambda x: x[1])[0]
            return best_strategy
        
        return None
    
    def calculate_position_size(self, strategy: StrategyConfig, market_data: pd.DataFrame, 
                              account_value: float) -> float:
        """Pozitsiya hajmini hisoblash"""
        try:
            base_size = min(strategy.max_position_size, account_value * 0.1)
            
            # Risk adjustment
            risk_multiplier = self.risk_manager.calculate_risk_multiplier(
                self.current_regime, strategy, market_data
            )
            
            # Volatility adjustment
            volatility = market_data['close'].pct_change().rolling(20).std().iloc[-1]
            vol_adjustment = 1.0 / (1.0 + volatility * 10)  # Yuqori volatility -> kam pozitsiya
            
            # Confidence adjustment
            confidence = self.current_regime.confidence if self.current_regime else 0.5
            confidence_adjustment = min(confidence * 1.5, 1.2)
            
            final_size = base_size * risk_multiplier * vol_adjustment * confidence_adjustment
            
            return max(min(final_size, strategy.max_position_size), 0.01)
            
        except Exception as e:
            logger.error(f"Pozitsiya hajmi hisoblashda xatolik: {e}")
            return 0.05  # Default 5%
    
    def generate_trade_signals(self, strategy: StrategyConfig, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Trading signallarini yaratish"""
        signals = []
        
        try:
            indicators = self.regime_detector._calculate_all_indicators(market_data)
            current_price = market_data['close'].iloc[-1]
            
            if strategy.type == StrategyType.TREND_FOLLOWING:
                signals = self._generate_trend_signals(market_data, indicators, current_price)
            elif strategy.type == StrategyType.MEAN_REVERSION:
                signals = self._generate_mean_reversion_signals(market_data, indicators, current_price)
            elif strategy.type == StrategyType.MOMENTUM:
                signals = self._generate_momentum_signals(market_data, indicators, current_price)
            elif strategy.type == StrategyType.BREAKOUT:
                signals = self._generate_breakout_signals(market_data, indicators, current_price)
            elif strategy.type == StrategyType.SCALPING:
                signals = self._generate_scalping_signals(market_data, indicators, current_price)
            
            # Stop loss va take profit darajalarini hisoblash
            for signal in signals:
                if signal['side'] == 'long':
                    signal['stop_loss'] = current_price * (1 - strategy.stop_loss_pct)
                    signal['take_profit'] = current_price * (1 + strategy.take_profit_pct)
                else:
                    signal['stop_loss'] = current_price * (1 + strategy.stop_loss_pct)
                    signal['take_profit'] = current_price * (1 - strategy.take_profit_pct)
                
                signal['strategy'] = strategy.name
                signal['timestamp'] = datetime.now()
                
        except Exception as e:
            logger.error(f"Signal yaratishda xatolik: {e}")
            
        return signals
    
    def _generate_trend_signals(self, data: pd.DataFrame, indicators: Dict, price: float) -> List[Dict]:
        """Trend following signallar"""
        signals = []
        
        # MA crossover
        sma_10 = indicators.get('sma_10', 0)
        sma_50 = indicators.get('sma_50', 0)
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        adx = indicators.get('adx', 0)
        
        if sma_10 > sma_50 and macd > macd_signal and adx > 25:
            signals.append({
                'symbol': 'BTCUSDT',
                'side': 'long',
                'price': price,
                'signal_type': 'trend_following_buy',
                'strength': min(adx / 100, 1.0)
            })
        elif sma_10 < sma_50 and macd < macd_signal and adx > 25:
            signals.append({
                'symbol': 'BTCUSDT',
                'side': 'short',
                'price': price,
                'signal_type': 'trend_following_sell',
                'strength': min(adx / 100, 1.0)
            })
            
        return signals
    
    def _generate_mean_reversion_signals(self, data: pd.DataFrame, indicators: Dict, price: float) -> List[Dict]:
        """Mean reversion signallar"""
        signals = []
        
        rsi = indicators.get('rsi', 50)
        bb_upper = indicators.get('bollinger_upper', 0)
        bb_lower = indicators.get('bollinger_lower', 0)
        adx = indicators.get('adx', 0)
        
        # Oversold signal
        if rsi < 30 and price <= bb_lower and adx < 25:
            signals.append({
                'symbol': 'BTCUSDT',
                'side': 'long',
                'price': price,
                'signal_type': 'mean_reversion_buy',
                'strength': max((30 - rsi) / 30, 0.5)
            })
        
        # Overbought signal  
        elif rsi > 70 and price >= bb_upper and adx < 25:
            signals.append({
                'symbol': 'BTCUSDT',
                'side': 'short',
                'price': price,
                'signal_type': 'mean_reversion_sell',
                'strength': min((rsi - 70) / 30, 1.0)
            })
            
        return signals
    
    def _generate_momentum_signals(self, data: pd.DataFrame, indicators: Dict, price: float) -> List[Dict]:
        """Momentum signallar"""
        signals = []
        
        momentum = indicators.get('momentum', 0)
        volume_ratio = indicators.get('volume_ratio', 1)
        rsi = indicators.get('rsi', 50)
        
        if momentum > 0 and volume_ratio > 1.2 and 50 < rsi < 80:
            signals.append({
                'symbol': 'BTCUSDT',
                'side': 'long',
                'price': price,
                'signal_type': 'momentum_buy',
                'strength': min(momentum * 10, 1.0) * min(volume_ratio / 2, 1.0)
            })
        elif momentum < 0 and volume_ratio > 1.2 and 20 < rsi < 50:
            signals.append({
                'symbol': 'BTCUSDT',
                'side': 'short',
                'price': price,
                'signal_type': 'momentum_sell',
                'strength': min(abs(momentum) * 10, 1.0) * min(volume_ratio / 2, 1.0)
            })
            
        return signals
    
    def _generate_breakout_signals(self, data: pd.DataFrame, indicators: Dict, price: float) -> List[Dict]:
        """Breakout signallar"""
        signals = []
        
        bb_position = indicators.get('price_position', 0.5)
        volume_ratio = indicators.get('volume_ratio', 1)
        resistance = indicators.get('resistance_level', 0)
        support = indicators.get('support_level', 0)
        
        # Resistance breakout
        if bb_position > 0.8 and price > resistance * 0.999 and volume_ratio > 1.5:
            signals.append({
                'symbol': 'BTCUSDT',
                'side': 'long',
                'price': price,
                'signal_type': 'breakout_buy',
                'strength': min(volume_ratio / 2, 1.0)
            })
        
        # Support breakdown
        elif bb_position < 0.2 and price < support * 1.001 and volume_ratio > 1.5:
            signals.append({
                'symbol': 'BTCUSDT',
                'side': 'short',
                'price': price,
                'signal_type': 'breakout_sell',
                'strength': min(volume_ratio / 2, 1.0)
            })
            
        return signals
    
    def _generate_scalping_signals(self, data: pd.DataFrame, indicators: Dict, price: float) -> List[Dict]:
        """Scalping signallar"""
        signals = []
        
        # Scalping - tezkor kichik harakatlar
        rsi = indicators.get('rsi', 50)
        volatility = indicators.get('volatility', 0.02)
        adx = indicators.get('adx', 0)
        
        # Past volatility va past trend
        if 0.005 < volatility < 0.025 and adx < 30:
            if 35 < rsi < 65:  # Neutral zone
                # Kichik correction signallar
                price_change = (data['close'].iloc[-1] - data['close'].iloc[-5]) / data['close'].iloc[-5]
                
                if price_change < -0.002:  # Kichik tushish
                    signals.append({
                        'symbol': 'BTCUSDT',
                        'side': 'long',
                        'price': price,
                        'signal_type': 'scalping_buy',
                        'strength': 0.6
                    })
                elif price_change > 0.002:  # Kichik ko'tarilish
                    signals.append({
                        'symbol': 'BTCUSDT',
                        'side': 'short',
                        'price': price,
                        'signal_type': 'scalping_sell',
                        'strength': 0.6
                    })
                    
        return signals
    
    def execute_trade(self, signal: Dict[str, Any], position_size: float, 
                     account_value: float) -> Optional[Position]:
        """Trading operatsiyasini bajarish"""
        try:
            # Risk check
            if not self.risk_manager.check_risk_limits(signal, position_size, account_value):
                logger.warning("Risk limit oshdi, trade amalga oshirilmadi")
                return None
            
            # Position yaratish
            position = Position(
                symbol=signal['symbol'],
                size=position_size * account_value / signal['price'],
                entry_price=signal['price'],
                current_price=signal['price'],
                side=signal['side'],
                stop_loss=signal['stop_loss'],
                take_profit=signal['take_profit'],
                timestamp=datetime.now(),
                strategy=signal['strategy']
            )
            
            # Pozitsiyalar ro'yxatiga qo'shish
            position_id = f"{position.symbol}_{position.timestamp.strftime('%Y%m%d_%H%M%S')}"
            self.positions[position_id] = position
            
            logger.info(f"Trade amalga oshirildi: {signal['side']} {position.size:.4f} {position.symbol}")
            return position
            
        except Exception as e:
            logger.error(f"Trade bajarishda xatolik: {e}")
            return None
    
    def update_positions(self, current_prices: Dict[str, float]):
        """Pozitsiyalarni yangilash"""
        for position_id, position in self.positions.items():
            if position.symbol in current_prices:
                position.current_price = current_prices[position.symbol]
                
                # PnL hisoblash
                if position.side == 'long':
                    position.pnl = (position.current_price - position.entry_price) * position.size
                    position.pnl_pct = (position.current_price - position.entry_price) / position.entry_price
                else:
                    position.pnl = (position.entry_price - position.current_price) * position.size
                    position.pnl_pct = (position.entry_price - position.current_price) / position.entry_price
                
                # Stop loss / Take profit check
                if self._should_close_position(position):
                    self._close_position(position_id)
    
    def _should_close_position(self, position: Position) -> bool:
        """Pozitsiyani yopish kerakligini tekshirish"""
        if position.side == 'long':
            return position.current_price <= position.stop_loss or position.current_price >= position.take_profit
        else:
            return position.current_price >= position.stop_loss or position.current_price <= position.take_profit
    
    def _close_position(self, position_id: str):
        """Pozitsiyani yopish"""
        if position_id in self.positions:
            position = self.positions[position_id]
            logger.info(f"Pozitsiya yopildi: {position.symbol} PnL: {position.pnl:.2f} ({position.pnl_pct:.2%})")
            del self.positions[position_id]
    
    def calculate_portfolio_metrics(self) -> Dict[str, float]:
        """Portfolio metrikalarini hisoblash"""
        if not self.positions:
            return {
                'total_value': 0.0,
                'total_pnl': 0.0,
                'total_pnl_pct': 0.0,
                'open_positions': 0
            }
        
        total_value = sum(p.current_price * p.size for p in self.positions.values())
        total_pnl = sum(p.pnl for p in self.positions.values())
        total_entry_value = sum(p.entry_price * p.size for p in self.positions.values())
        total_pnl_pct = total_pnl / total_entry_value if total_entry_value > 0 else 0.0
        
        return {
            'total_value': total_value,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct,
            'open_positions': len(self.positions),
            'avg_position_size': total_value / len(self.positions) if self.positions else 0.0
        }
    
    def get_strategy_performance(self, strategy_name: str) -> Optional[StrategyPerformance]:
        """Strategiya natijalarini olish"""
        if strategy_name not in self.performance_history:
            return None
        
        data = self.performance_history[strategy_name]
        return StrategyPerformance(**data)
    
    def update_performance_history(self, strategy_name: str, trade_results: List[Dict]):
        """Performance tarixini yangilash"""
        if not trade_results:
            return
        
        # Returns hisoblash
        returns = [trade['pnl_pct'] for trade in trade_results]
        
        if not returns:
            return
        
        # Performance metrikalar
        total_return = sum(returns)
        avg_return = np.mean(returns)
        volatility = np.std(returns)
        sharpe_ratio = avg_return / volatility if volatility > 0 else 0.0
        
        # Win rate
        winning_trades = [r for r in returns if r > 0]
        win_rate = len(winning_trades) / len(returns)
        
        # Max drawdown
        cumulative_returns = np.cumsum(returns)
        peak = np.maximum.accumulate(cumulative_returns)
        drawdown = peak - cumulative_returns
        max_drawdown = np.max(drawdown)
        
        # Profit factor
        gross_profit = sum(winning_trades)
        gross_loss = abs(sum([r for r in returns if r < 0]))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # VaR 95%
        var_95 = np.percentile(returns, 5)
        
        performance = StrategyPerformance(
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=len(returns),
            avg_trade_duration=1.0,  # Simplified
            volatility=volatility,
            calmar_ratio=total_return / max_drawdown if max_drawdown > 0 else 0.0,
            sortino_ratio=avg_return / np.std([r for r in returns if r < 0]) if any(r < 0 for r in returns) else float('inf'),
            var_95=var_95
        )
        
        self.performance_history[strategy_name] = {
            'total_return': performance.total_return,
            'sharpe_ratio': performance.sharpe_ratio,
            'max_drawdown': performance.max_drawdown,
            'win_rate': performance.win_rate,
            'profit_factor': performance.profit_factor,
            'total_trades': performance.total_trades,
            'avg_trade_duration': performance.avg_trade_duration,
            'volatility': performance.volatility,
            'calmar_ratio': performance.calmar_ratio,
            'sortino_ratio': performance.sortino_ratio,
            'var_95': performance.var_95
        }
    
    def export_performance_report(self) -> Dict[str, Any]:
        """Performance hisobotini eksport qilish"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'current_regime': self.current_regime.regime.value if self.current_regime else None,
            'active_strategy': self.active_strategy.name if self.active_strategy else None,
            'portfolio_metrics': self.calculate_portfolio_metrics(),
            'strategy_performances': {},
            'position_summary': len(self.positions),
            'regime_history': self.regime_detector.get_regime_statistics()
        }
        
        # Har bir strategiya uchun performance
        for strategy_name, perf_data in self.performance_history.items():
            report['strategy_performances'][strategy_name] = perf_data
        
        return report


class RiskManager:
    """Risk boshqaruvchi tizim"""
    
    def __init__(self):
        self.max_portfolio_risk = 0.02  # 2% portfolio risk per trade
        self.max_correlation = 0.7
        self.max_sector_exposure = 0.3
    
    def calculate_risk_multiplier(self, regime: MarketRegimeResult, strategy: StrategyConfig, 
                                market_data: pd.DataFrame) -> float:
        """Risk ko'paytiruvchisini hisoblash"""
        base_multiplier = strategy.risk_multiplier
        
        # Rejimga asoslangan risk adjustment
        regime_risk_adjustments = {
            MarketRegime.HIGH_VOLATILITY: 0.7,
            MarketRegime.LOW_VOLATILITY: 1.2,
            MarketRegime.BEAR_MARKET: 0.8,
            MarketRegime.BULL_MARKET: 1.1,
            MarketRegime.SIDEWAYS_MARKET: 1.0
        }
        
        regime_multiplier = regime_risk_adjustments.get(regime.regime, 1.0)
        
        # Volatility adjustment
        volatility = market_data['close'].pct_change().rolling(20).std().iloc[-1]
        vol_multiplier = 1.0 / (1.0 + volatility * 5)
        
        return base_multiplier * regime_multiplier * vol_multiplier
    
    def check_risk_limits(self, signal: Dict, position_size: float, account_value: float) -> bool:
        """Risk limitlarni tekshirish"""
        position_value = position_size * account_value
        position_risk = position_value / account_value
        
        # Portfolio risk limit
        if position_risk > self.max_portfolio_risk:
            return False
        
        # Maximum position size
        if position_size > 0.25:  # 25% max position
            return False
        
        return True


class CapitalAllocator:
    """Kapital taqsimlash tizimi"""
    
    def __init__(self):
        self.allocation_model = "risk_parity"  # Default model
    
    def calculate_allocation(self, strategies: List[StrategyConfig], 
                           performance_history: Dict[str, Dict]) -> Dict[str, float]:
        """Strategiyalar o'rtasida kapital taqsimlash"""
        if self.allocation_model == "equal_weight":
            return self._equal_weight_allocation(strategies)
        elif self.allocation_model == "risk_parity":
            return self._risk_parity_allocation(strategies, performance_history)
        elif self.allocation_model == "performance_weighted":
            return self._performance_weighted_allocation(strategies, performance_history)
        else:
            return self._equal_weight_allocation(strategies)
    
    def _equal_weight_allocation(self, strategies: List[StrategyConfig]) -> Dict[str, float]:
        """Teng og'irlikli taqsimlash"""
        if not strategies:
            return {}
        
        weight = 1.0 / len(strategies)
        return {strategy.name: weight for strategy in strategies}
    
    def _risk_parity_allocation(self, strategies: List[StrategyConfig], 
                              performance_history: Dict[str, Dict]) -> Dict[str, float]:
        """Risk parity taqsimlash"""
        weights = {}
        
        for strategy in strategies:
            # Risk score based on historical volatility
            strategy_name = strategy.name
            if strategy_name in performance_history:
                volatility = performance_history[strategy_name].get('volatility', 0.02)
                risk_score = 1.0 / (volatility + 0.01)  # Inverse volatility
            else:
                risk_score = 1.0  # Default
            
            weights[strategy_name] = risk_score
        
        # Normalize
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
        
        return weights
    
    def _performance_weighted_allocation(self, strategies: List[StrategyConfig], 
                                      performance_history: Dict[str, Dict]) -> Dict[str, float]:
        """Performance asosida og'irlikli taqsimlash"""
        weights = {}
        
        for strategy in strategies:
            strategy_name = strategy.name
            if strategy_name in performance_history:
                sharpe = performance_history[strategy_name].get('sharpe_ratio', 0)
                performance_score = max(sharpe, 0)  # Negative Sharpe ni 0 qilish
            else:
                performance_score = 0.1  # Default
            
            weights[strategy_name] = performance_score
        
        # Normalize
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
        
        return weights


# Test function
def test_strategy_switcher():
    """Strategy Switcher ni test qilish"""
    print("Strategy Switcher test qilish...")
    
    # Sample data
    from market_regime_detector import create_sample_data
    data = create_sample_data(100)
    
    # Switcher yaratish
    switcher = StrategySwitcher()
    
    # Strategiya tanlash
    strategy = switcher.select_strategy(data)
    if strategy:
        print(f"Tanlangan strategiya: {strategy.name}")
        
        # Trade signals
        signals = switcher.generate_trade_signals(strategy, data)
        print(f"Yaratilgan signallar: {len(signals)}")
        for signal in signals:
            print(f"  - {signal['signal_type']}: {signal['side']} @ {signal['price']:.2f}")
    
    # Performance report
    report = switcher.export_performance_report()
    print(f"Performance report: {report['current_regime']}")
    
    return switcher

if __name__ == "__main__":
    test_strategy_switcher()