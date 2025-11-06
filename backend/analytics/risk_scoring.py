"""
Advanced Risk Scoring System
VaR, CVaR, Sharpe ratio, Maximum drawdown calculations
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
import statistics
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RiskMetrics:
    """Risk metrikalari to'plami"""
    # Volatility metrics
    volatility_daily: Decimal
    volatility_annual: Decimal
    
    # Value at Risk
    var_95: Decimal  # 95% confidence level
    var_99: Decimal  # 99% confidence level
    
    # Conditional Value at Risk (Expected Shortfall)
    cvar_95: Decimal
    cvar_99: Decimal
    
    # Performance metrics
    sharpe_ratio: Decimal
    sortino_ratio: Decimal
    calmar_ratio: Decimal
    
    # Drawdown metrics
    max_drawdown: Decimal
    current_drawdown: Decimal
    avg_drawdown: Decimal
    drawdown_duration_days: int
    
    # Risk ratios
    risk_reward_ratio: Decimal
    win_loss_ratio: Decimal
    kelly_criterion: Decimal
    
    # Correlation
    beta: Decimal  # Market beta
    correlation_btc: Decimal
    
    # Other metrics
    skewness: Decimal
    kurtosis: Decimal
    tail_risk_score: Decimal


@dataclass
class PositionRisk:
    """Bitta pozitsiya uchun risk metrikalari"""
    symbol: str
    position_size_usd: Decimal
    portfolio_allocation_percent: Decimal
    leverage: Decimal
    liquidation_distance_percent: Decimal
    stop_loss_distance_percent: Decimal
    risk_amount_usd: Decimal
    risk_reward_ratio: Decimal
    risk_score: Decimal  # 0-100
    risk_level: str  # 'low', 'medium', 'high', 'critical'


class RiskScoringSystem:
    """Keng qamrovli risk tahlili va scoring tizimi"""
    
    def __init__(
        self,
        risk_free_rate: Decimal = Decimal('0.02'),  # 2% yillik
        confidence_levels: List[Decimal] = None
    ):
        self.risk_free_rate = risk_free_rate
        self.confidence_levels = confidence_levels or [
            Decimal('0.95'),
            Decimal('0.99')
        ]
        
        self.price_history: Dict[str, List[Tuple[datetime, Decimal]]] = {}
        self.return_history: List[Decimal] = []
        self.drawdown_history: List[Tuple[datetime, Decimal]] = []
    
    async def calculate_portfolio_risk(
        self,
        returns: List[Decimal],
        portfolio_value: Decimal,
        benchmark_returns: Optional[List[Decimal]] = None
    ) -> RiskMetrics:
        """Portfolio uchun to'liq risk tahlili"""
        try:
            if not returns:
                logger.warning("No returns data provided")
                return None
            
            # Convert to float for calculations
            returns_float = [float(r) for r in returns]
            
            # Volatility
            volatility_daily = Decimal(str(statistics.stdev(returns_float)))
            volatility_annual = volatility_daily * Decimal(str(math.sqrt(252)))
            
            # Value at Risk
            var_95 = await self._calculate_var(returns, Decimal('0.95'))
            var_99 = await self._calculate_var(returns, Decimal('0.99'))
            
            # Conditional VaR
            cvar_95 = await self._calculate_cvar(returns, Decimal('0.95'))
            cvar_99 = await self._calculate_cvar(returns, Decimal('0.99'))
            
            # Sharpe Ratio
            sharpe_ratio = await self._calculate_sharpe_ratio(returns)
            
            # Sortino Ratio
            sortino_ratio = await self._calculate_sortino_ratio(returns)
            
            # Calmar Ratio
            calmar_ratio = await self._calculate_calmar_ratio(returns)
            
            # Drawdown metrics
            max_dd, current_dd, avg_dd, dd_duration = await self._calculate_drawdown_metrics(returns)
            
            # Risk-Reward
            risk_reward = await self._calculate_risk_reward_ratio(returns)
            
            # Win-Loss Ratio
            win_loss = await self._calculate_win_loss_ratio(returns)
            
            # Kelly Criterion
            kelly = await self._calculate_kelly_criterion(returns)
            
            # Beta and Correlation
            beta = Decimal('1')
            correlation_btc = Decimal('0')
            if benchmark_returns:
                beta = await self._calculate_beta(returns, benchmark_returns)
                correlation_btc = await self._calculate_correlation(returns, benchmark_returns)
            
            # Distribution metrics
            skewness = Decimal(str(self._calculate_skewness(returns_float)))
            kurtosis = Decimal(str(self._calculate_kurtosis(returns_float)))
            
            # Tail risk score (0-100)
            tail_risk = await self._calculate_tail_risk_score(
                var_99, cvar_99, skewness, kurtosis
            )
            
            metrics = RiskMetrics(
                volatility_daily=volatility_daily,
                volatility_annual=volatility_annual,
                var_95=var_95,
                var_99=var_99,
                cvar_95=cvar_95,
                cvar_99=cvar_99,
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=sortino_ratio,
                calmar_ratio=calmar_ratio,
                max_drawdown=max_dd,
                current_drawdown=current_dd,
                avg_drawdown=avg_dd,
                drawdown_duration_days=dd_duration,
                risk_reward_ratio=risk_reward,
                win_loss_ratio=win_loss,
                kelly_criterion=kelly,
                beta=beta,
                correlation_btc=correlation_btc,
                skewness=skewness,
                kurtosis=kurtosis,
                tail_risk_score=tail_risk
            )
            
            logger.info("Calculated comprehensive risk metrics")
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating portfolio risk: {e}")
            return None
    
    async def _calculate_var(
        self,
        returns: List[Decimal],
        confidence_level: Decimal
    ) -> Decimal:
        """Value at Risk hisoblash (Historical method)"""
        try:
            returns_sorted = sorted([float(r) for r in returns])
            
            # Index for percentile
            index = int((1 - float(confidence_level)) * len(returns_sorted))
            
            if index >= len(returns_sorted):
                index = len(returns_sorted) - 1
            
            var = abs(Decimal(str(returns_sorted[index])))
            
            return var
            
        except Exception as e:
            logger.error(f"Error calculating VaR: {e}")
            return Decimal('0')
    
    async def _calculate_cvar(
        self,
        returns: List[Decimal],
        confidence_level: Decimal
    ) -> Decimal:
        """Conditional VaR (Expected Shortfall) hisoblash"""
        try:
            returns_sorted = sorted([float(r) for r in returns])
            
            # Index for percentile
            index = int((1 - float(confidence_level)) * len(returns_sorted))
            
            # Average of tail losses
            tail_losses = returns_sorted[:index] if index > 0 else returns_sorted[:1]
            
            if tail_losses:
                cvar = abs(Decimal(str(statistics.mean(tail_losses))))
            else:
                cvar = Decimal('0')
            
            return cvar
            
        except Exception as e:
            logger.error(f"Error calculating CVaR: {e}")
            return Decimal('0')
    
    async def _calculate_sharpe_ratio(
        self,
        returns: List[Decimal],
        periods_per_year: int = 252
    ) -> Decimal:
        """Sharpe Ratio hisoblash"""
        try:
            returns_float = [float(r) for r in returns]
            
            if not returns_float:
                return Decimal('0')
            
            mean_return = statistics.mean(returns_float)
            std_return = statistics.stdev(returns_float) if len(returns_float) > 1 else 0
            
            if std_return == 0:
                return Decimal('0')
            
            # Annualize
            annual_return = mean_return * periods_per_year
            annual_std = std_return * math.sqrt(periods_per_year)
            
            # Sharpe ratio
            sharpe = (annual_return - float(self.risk_free_rate)) / annual_std
            
            return Decimal(str(sharpe))
            
        except Exception as e:
            logger.error(f"Error calculating Sharpe ratio: {e}")
            return Decimal('0')
    
    async def _calculate_sortino_ratio(
        self,
        returns: List[Decimal],
        periods_per_year: int = 252
    ) -> Decimal:
        """Sortino Ratio hisoblash (faqat downside volatility)"""
        try:
            returns_float = [float(r) for r in returns]
            
            if not returns_float:
                return Decimal('0')
            
            mean_return = statistics.mean(returns_float)
            
            # Downside deviation
            downside_returns = [r for r in returns_float if r < 0]
            
            if not downside_returns:
                return Decimal('100')  # No downside
            
            downside_std = statistics.stdev(downside_returns)
            
            if downside_std == 0:
                return Decimal('0')
            
            # Annualize
            annual_return = mean_return * periods_per_year
            annual_downside_std = downside_std * math.sqrt(periods_per_year)
            
            sortino = (annual_return - float(self.risk_free_rate)) / annual_downside_std
            
            return Decimal(str(sortino))
            
        except Exception as e:
            logger.error(f"Error calculating Sortino ratio: {e}")
            return Decimal('0')
    
    async def _calculate_calmar_ratio(
        self,
        returns: List[Decimal],
        periods_per_year: int = 252
    ) -> Decimal:
        """Calmar Ratio hisoblash (return / max drawdown)"""
        try:
            returns_float = [float(r) for r in returns]
            
            if not returns_float:
                return Decimal('0')
            
            # Annualized return
            mean_return = statistics.mean(returns_float)
            annual_return = mean_return * periods_per_year
            
            # Max drawdown
            max_dd, _, _, _ = await self._calculate_drawdown_metrics(returns)
            
            if max_dd == 0:
                return Decimal('100')
            
            calmar = annual_return / float(max_dd)
            
            return Decimal(str(abs(calmar)))
            
        except Exception as e:
            logger.error(f"Error calculating Calmar ratio: {e}")
            return Decimal('0')
    
    async def _calculate_drawdown_metrics(
        self,
        returns: List[Decimal]
    ) -> Tuple[Decimal, Decimal, Decimal, int]:
        """Drawdown metrikalari"""
        try:
            # Calculate cumulative returns
            cumulative = [Decimal('1')]
            for ret in returns:
                cumulative.append(cumulative[-1] * (Decimal('1') + ret))
            
            # Calculate drawdowns
            drawdowns = []
            peak = cumulative[0]
            drawdown_start = 0
            current_dd_duration = 0
            max_dd_duration = 0
            
            for i, value in enumerate(cumulative):
                if value > peak:
                    peak = value
                    drawdown_start = i
                    if current_dd_duration > max_dd_duration:
                        max_dd_duration = current_dd_duration
                    current_dd_duration = 0
                else:
                    current_dd_duration = i - drawdown_start
                
                dd = (peak - value) / peak if peak > 0 else Decimal('0')
                drawdowns.append(dd)
            
            # Metrics
            max_drawdown = max(drawdowns) if drawdowns else Decimal('0')
            current_drawdown = drawdowns[-1] if drawdowns else Decimal('0')
            avg_drawdown = sum(drawdowns) / len(drawdowns) if drawdowns else Decimal('0')
            
            return max_drawdown, current_drawdown, avg_drawdown, max_dd_duration
            
        except Exception as e:
            logger.error(f"Error calculating drawdown metrics: {e}")
            return Decimal('0'), Decimal('0'), Decimal('0'), 0
    
    async def _calculate_risk_reward_ratio(self, returns: List[Decimal]) -> Decimal:
        """Risk-Reward ratio hisoblash"""
        try:
            returns_float = [float(r) for r in returns]
            
            wins = [r for r in returns_float if r > 0]
            losses = [abs(r) for r in returns_float if r < 0]
            
            if not wins or not losses:
                return Decimal('0')
            
            avg_win = statistics.mean(wins)
            avg_loss = statistics.mean(losses)
            
            if avg_loss == 0:
                return Decimal('100')
            
            ratio = avg_win / avg_loss
            
            return Decimal(str(ratio))
            
        except Exception as e:
            logger.error(f"Error calculating risk-reward ratio: {e}")
            return Decimal('0')
    
    async def _calculate_win_loss_ratio(self, returns: List[Decimal]) -> Decimal:
        """Win/Loss ratio hisoblash"""
        try:
            returns_float = [float(r) for r in returns]
            
            wins = sum(1 for r in returns_float if r > 0)
            losses = sum(1 for r in returns_float if r < 0)
            
            if losses == 0:
                return Decimal('100')
            
            ratio = wins / losses
            
            return Decimal(str(ratio))
            
        except Exception as e:
            logger.error(f"Error calculating win-loss ratio: {e}")
            return Decimal('0')
    
    async def _calculate_kelly_criterion(self, returns: List[Decimal]) -> Decimal:
        """Kelly Criterion (optimal position sizing)"""
        try:
            returns_float = [float(r) for r in returns]
            
            wins = [r for r in returns_float if r > 0]
            losses = [abs(r) for r in returns_float if r < 0]
            
            if not wins or not losses:
                return Decimal('0')
            
            win_rate = len(wins) / len(returns_float)
            avg_win = statistics.mean(wins)
            avg_loss = statistics.mean(losses)
            
            if avg_loss == 0:
                return Decimal('0')
            
            # Kelly formula: (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
            kelly = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
            
            # Cap at 25% for safety
            kelly = max(0, min(kelly, 0.25))
            
            return Decimal(str(kelly))
            
        except Exception as e:
            logger.error(f"Error calculating Kelly criterion: {e}")
            return Decimal('0')
    
    async def _calculate_beta(
        self,
        returns: List[Decimal],
        benchmark_returns: List[Decimal]
    ) -> Decimal:
        """Portfolio beta (market sensitivity)"""
        try:
            if len(returns) != len(benchmark_returns):
                return Decimal('1')
            
            returns_float = [float(r) for r in returns]
            benchmark_float = [float(r) for r in benchmark_returns]
            
            # Covariance
            mean_ret = statistics.mean(returns_float)
            mean_bench = statistics.mean(benchmark_float)
            
            covariance = sum(
                (r - mean_ret) * (b - mean_bench)
                for r, b in zip(returns_float, benchmark_float)
            ) / len(returns_float)
            
            # Benchmark variance
            variance = statistics.variance(benchmark_float)
            
            if variance == 0:
                return Decimal('1')
            
            beta = covariance / variance
            
            return Decimal(str(beta))
            
        except Exception as e:
            logger.error(f"Error calculating beta: {e}")
            return Decimal('1')
    
    async def _calculate_correlation(
        self,
        returns: List[Decimal],
        benchmark_returns: List[Decimal]
    ) -> Decimal:
        """Correlation coefficient"""
        try:
            if len(returns) != len(benchmark_returns) or len(returns) < 2:
                return Decimal('0')
            
            returns_float = [float(r) for r in returns]
            benchmark_float = [float(r) for r in benchmark_returns]
            
            # Pearson correlation
            mean_ret = statistics.mean(returns_float)
            mean_bench = statistics.mean(benchmark_float)
            
            numerator = sum(
                (r - mean_ret) * (b - mean_bench)
                for r, b in zip(returns_float, benchmark_float)
            )
            
            std_ret = statistics.stdev(returns_float)
            std_bench = statistics.stdev(benchmark_float)
            
            if std_ret == 0 or std_bench == 0:
                return Decimal('0')
            
            denominator = len(returns_float) * std_ret * std_bench
            
            correlation = numerator / denominator
            
            return Decimal(str(correlation))
            
        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return Decimal('0')
    
    def _calculate_skewness(self, returns: List[float]) -> float:
        """Skewness (distribution asymmetry)"""
        try:
            if len(returns) < 3:
                return 0.0
            
            mean = statistics.mean(returns)
            std = statistics.stdev(returns)
            
            if std == 0:
                return 0.0
            
            n = len(returns)
            skewness = (
                sum((r - mean) ** 3 for r in returns) / n
            ) / (std ** 3)
            
            return skewness
            
        except Exception as e:
            logger.error(f"Error calculating skewness: {e}")
            return 0.0
    
    def _calculate_kurtosis(self, returns: List[float]) -> float:
        """Kurtosis (tail heaviness)"""
        try:
            if len(returns) < 4:
                return 0.0
            
            mean = statistics.mean(returns)
            std = statistics.stdev(returns)
            
            if std == 0:
                return 0.0
            
            n = len(returns)
            kurtosis = (
                sum((r - mean) ** 4 for r in returns) / n
            ) / (std ** 4) - 3  # Excess kurtosis
            
            return kurtosis
            
        except Exception as e:
            logger.error(f"Error calculating kurtosis: {e}")
            return 0.0
    
    async def _calculate_tail_risk_score(
        self,
        var_99: Decimal,
        cvar_99: Decimal,
        skewness: Decimal,
        kurtosis: Decimal
    ) -> Decimal:
        """Tail risk composite score (0-100)"""
        try:
            score = Decimal('0')
            
            # VaR contribution (0-30)
            var_score = min(float(var_99) * 100, 30)
            score += Decimal(str(var_score))
            
            # CVaR contribution (0-30)
            cvar_score = min(float(cvar_99) * 100, 30)
            score += Decimal(str(cvar_score))
            
            # Skewness contribution (0-20)
            # Negative skew is bad (left tail)
            skew_score = max(0, -float(skewness) * 10)
            score += Decimal(str(min(skew_score, 20)))
            
            # Kurtosis contribution (0-20)
            # High kurtosis = fat tails
            kurt_score = max(0, float(kurtosis) * 5)
            score += Decimal(str(min(kurt_score, 20)))
            
            return min(score, Decimal('100'))
            
        except Exception as e:
            logger.error(f"Error calculating tail risk score: {e}")
            return Decimal('0')
    
    async def calculate_position_risk(
        self,
        symbol: str,
        position_size_usd: Decimal,
        portfolio_value: Decimal,
        entry_price: Decimal,
        current_price: Decimal,
        leverage: Decimal = Decimal('1'),
        stop_loss: Optional[Decimal] = None,
        liquidation_price: Optional[Decimal] = None
    ) -> PositionRisk:
        """Bitta pozitsiya uchun risk tahlili"""
        try:
            # Portfolio allocation
            allocation_percent = (position_size_usd / portfolio_value) * Decimal('100')
            
            # Liquidation distance
            liq_distance = Decimal('0')
            if liquidation_price:
                liq_distance = abs(
                    (current_price - liquidation_price) / current_price
                ) * Decimal('100')
            
            # Stop loss distance
            sl_distance = Decimal('0')
            if stop_loss:
                sl_distance = abs(
                    (current_price - stop_loss) / current_price
                ) * Decimal('100')
            
            # Risk amount
            risk_amount = Decimal('0')
            if stop_loss:
                risk_amount = abs(current_price - stop_loss) * (position_size_usd / current_price)
            
            # Risk-reward ratio
            risk_reward = Decimal('0')
            # This would need take_profit price to calculate
            
            # Risk score (0-100)
            risk_score = await self._calculate_position_risk_score(
                allocation_percent, leverage, liq_distance, sl_distance
            )
            
            # Risk level
            if risk_score >= 75:
                risk_level = 'critical'
            elif risk_score >= 50:
                risk_level = 'high'
            elif risk_score >= 25:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            position_risk = PositionRisk(
                symbol=symbol,
                position_size_usd=position_size_usd,
                portfolio_allocation_percent=allocation_percent,
                leverage=leverage,
                liquidation_distance_percent=liq_distance,
                stop_loss_distance_percent=sl_distance,
                risk_amount_usd=risk_amount,
                risk_reward_ratio=risk_reward,
                risk_score=risk_score,
                risk_level=risk_level
            )
            
            logger.info(f"Calculated risk for {symbol}: {risk_level} ({risk_score:.1f}/100)")
            return position_risk
            
        except Exception as e:
            logger.error(f"Error calculating position risk: {e}")
            return None
    
    async def _calculate_position_risk_score(
        self,
        allocation_percent: Decimal,
        leverage: Decimal,
        liquidation_distance: Decimal,
        stop_loss_distance: Decimal
    ) -> Decimal:
        """Pozitsiya risk score hisoblash"""
        try:
            score = Decimal('0')
            
            # Allocation risk (0-25)
            # > 20% = high risk
            alloc_score = min(float(allocation_percent) * 1.25, 25)
            score += Decimal(str(alloc_score))
            
            # Leverage risk (0-25)
            # > 5x = high risk
            lev_score = min(float(leverage) * 5, 25)
            score += Decimal(str(lev_score))
            
            # Liquidation risk (0-25)
            # < 10% distance = critical
            if liquidation_distance > 0:
                liq_score = max(0, 25 - float(liquidation_distance) * 2)
                score += Decimal(str(liq_score))
            
            # Stop loss risk (0-25)
            # < 5% distance = tight stop
            if stop_loss_distance > 0:
                sl_score = max(0, 25 - float(stop_loss_distance) * 5)
                score += Decimal(str(sl_score))
            else:
                # No stop loss = high risk
                score += Decimal('25')
            
            return min(score, Decimal('100'))
            
        except Exception as e:
            logger.error(f"Error calculating position risk score: {e}")
            return Decimal('50')


async def main():
    """Test function"""
    risk_system = RiskScoringSystem()
    
    # Sample returns data
    returns = [
        Decimal('0.02'), Decimal('-0.01'), Decimal('0.03'),
        Decimal('-0.02'), Decimal('0.01'), Decimal('0.04'),
        Decimal('-0.03'), Decimal('0.02'), Decimal('0.01'),
        Decimal('-0.01')
    ]
    
    # Calculate portfolio risk
    metrics = await risk_system.calculate_portfolio_risk(
        returns=returns,
        portfolio_value=Decimal('100000')
    )
    
    if metrics:
        print("=== Portfolio Risk Metrics ===")
        print(f"Volatility (Annual): {metrics.volatility_annual:.4f}")
        print(f"VaR (95%): {metrics.var_95:.4f}")
        print(f"CVaR (95%): {metrics.cvar_95:.4f}")
        print(f"Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
        print(f"Sortino Ratio: {metrics.sortino_ratio:.2f}")
        print(f"Max Drawdown: {metrics.max_drawdown:.2%}")
        print(f"Tail Risk Score: {metrics.tail_risk_score:.1f}/100")
    
    # Calculate position risk
    position_risk = await risk_system.calculate_position_risk(
        symbol='BTC/USDT',
        position_size_usd=Decimal('10000'),
        portfolio_value=Decimal('100000'),
        entry_price=Decimal('50000'),
        current_price=Decimal('51000'),
        leverage=Decimal('5'),
        stop_loss=Decimal('49000'),
        liquidation_price=Decimal('40000')
    )
    
    if position_risk:
        print(f"\n=== Position Risk ({position_risk.symbol}) ===")
        print(f"Risk Level: {position_risk.risk_level.upper()}")
        print(f"Risk Score: {position_risk.risk_score:.1f}/100")
        print(f"Portfolio Allocation: {position_risk.portfolio_allocation_percent:.1f}%")
        print(f"Liquidation Distance: {position_risk.liquidation_distance_percent:.1f}%")


if __name__ == '__main__':
    asyncio.run(main())
