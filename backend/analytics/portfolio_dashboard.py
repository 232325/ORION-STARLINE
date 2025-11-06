"""
Portfolio Performance Dashboard
Real-time PnL tracking, risk metrics, position monitoring
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Trading pozitsiya ma'lumotlari"""
    symbol: str
    side: str  # 'long' or 'short'
    size: Decimal
    entry_price: Decimal
    current_price: Decimal
    leverage: Decimal = Decimal('1')
    entry_time: datetime = field(default_factory=datetime.now)
    unrealized_pnl: Decimal = Decimal('0')
    unrealized_pnl_percent: Decimal = Decimal('0')
    liquidation_price: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None


@dataclass
class Trade:
    """Yakunlangan trade ma'lumotlari"""
    symbol: str
    side: str
    entry_price: Decimal
    exit_price: Decimal
    size: Decimal
    realized_pnl: Decimal
    realized_pnl_percent: Decimal
    entry_time: datetime
    exit_time: datetime
    duration_minutes: int
    fees: Decimal = Decimal('0')
    strategy: str = 'manual'


@dataclass
class PortfolioMetrics:
    """Portfolio performance metrikalari"""
    total_balance: Decimal
    available_balance: Decimal
    margin_used: Decimal
    total_unrealized_pnl: Decimal
    total_realized_pnl: Decimal
    total_pnl: Decimal
    total_pnl_percent: Decimal
    win_rate: Decimal
    profit_factor: Decimal
    sharpe_ratio: Decimal
    max_drawdown: Decimal
    current_drawdown: Decimal
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: Decimal
    avg_loss: Decimal
    largest_win: Decimal
    largest_loss: Decimal
    avg_trade_duration_minutes: int
    total_fees: Decimal


class PortfolioDashboard:
    """Portfolio monitoring va performance tracking"""
    
    def __init__(
        self,
        initial_balance: Decimal,
        risk_free_rate: Decimal = Decimal('0.02')  # 2% yillik
    ):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.risk_free_rate = risk_free_rate
        
        self.positions: Dict[str, Position] = {}
        self.closed_trades: List[Trade] = []
        self.balance_history: List[Tuple[datetime, Decimal]] = [
            (datetime.now(), initial_balance)
        ]
        
        self.peak_balance = initial_balance
        self.max_drawdown = Decimal('0')
        
        # Performance tracking
        self.daily_pnl: Dict[str, Decimal] = defaultdict(lambda: Decimal('0'))
        self.strategy_performance: Dict[str, Dict] = defaultdict(lambda: {
            'pnl': Decimal('0'),
            'trades': 0,
            'wins': 0
        })
    
    async def update_positions(self, market_prices: Dict[str, Decimal]):
        """Pozitsiyalarni yangilash va PnL hisoblash"""
        try:
            total_unrealized_pnl = Decimal('0')
            
            for symbol, position in self.positions.items():
                if symbol not in market_prices:
                    logger.warning(f"No market price for {symbol}")
                    continue
                
                position.current_price = market_prices[symbol]
                
                # Calculate unrealized PnL
                if position.side == 'long':
                    pnl = (position.current_price - position.entry_price) * position.size
                else:  # short
                    pnl = (position.entry_price - position.current_price) * position.size
                
                # Apply leverage
                pnl *= position.leverage
                
                position.unrealized_pnl = pnl
                
                # Calculate percentage
                if position.entry_price > 0:
                    position.unrealized_pnl_percent = (
                        (pnl / (position.entry_price * position.size)) * Decimal('100')
                    )
                
                total_unrealized_pnl += pnl
                
                # Check stop loss / take profit
                await self._check_exit_conditions(position)
            
            # Update balance
            self.current_balance = self.initial_balance + sum(
                t.realized_pnl for t in self.closed_trades
            ) + total_unrealized_pnl
            
            # Update peak and drawdown
            if self.current_balance > self.peak_balance:
                self.peak_balance = self.current_balance
            
            current_drawdown = (
                (self.peak_balance - self.current_balance) / self.peak_balance
                if self.peak_balance > 0 else Decimal('0')
            )
            
            if current_drawdown > self.max_drawdown:
                self.max_drawdown = current_drawdown
            
            # Record balance history
            self.balance_history.append((datetime.now(), self.current_balance))
            
            logger.info(f"Updated {len(self.positions)} positions, Total PnL: ${total_unrealized_pnl:.2f}")
            
        except Exception as e:
            logger.error(f"Error updating positions: {e}")
    
    async def _check_exit_conditions(self, position: Position):
        """Stop loss va take profit tekshirish"""
        try:
            should_close = False
            reason = ""
            
            # Check stop loss
            if position.stop_loss:
                if position.side == 'long' and position.current_price <= position.stop_loss:
                    should_close = True
                    reason = "Stop Loss"
                elif position.side == 'short' and position.current_price >= position.stop_loss:
                    should_close = True
                    reason = "Stop Loss"
            
            # Check take profit
            if position.take_profit:
                if position.side == 'long' and position.current_price >= position.take_profit:
                    should_close = True
                    reason = "Take Profit"
                elif position.side == 'short' and position.current_price <= position.take_profit:
                    should_close = True
                    reason = "Take Profit"
            
            # Check liquidation
            if position.liquidation_price:
                if position.side == 'long' and position.current_price <= position.liquidation_price:
                    should_close = True
                    reason = "Liquidation"
                elif position.side == 'short' and position.current_price >= position.liquidation_price:
                    should_close = True
                    reason = "Liquidation"
            
            if should_close:
                logger.warning(f"Auto-closing position {position.symbol} due to {reason}")
                await self.close_position(position.symbol, position.current_price)
            
        except Exception as e:
            logger.error(f"Error checking exit conditions: {e}")
    
    async def open_position(
        self,
        symbol: str,
        side: str,
        size: Decimal,
        entry_price: Decimal,
        leverage: Decimal = Decimal('1'),
        stop_loss: Optional[Decimal] = None,
        take_profit: Optional[Decimal] = None
    ) -> Optional[Position]:
        """Yangi pozitsiya ochish"""
        try:
            if symbol in self.positions:
                logger.warning(f"Position already exists for {symbol}")
                return None
            
            # Calculate liquidation price
            liquidation_price = None
            if leverage > 1:
                if side == 'long':
                    liquidation_price = entry_price * (1 - 1 / leverage)
                else:
                    liquidation_price = entry_price * (1 + 1 / leverage)
            
            position = Position(
                symbol=symbol,
                side=side,
                size=size,
                entry_price=entry_price,
                current_price=entry_price,
                leverage=leverage,
                liquidation_price=liquidation_price,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
            self.positions[symbol] = position
            logger.info(f"Opened {side} position: {symbol} @ ${entry_price}, size: {size}")
            
            return position
            
        except Exception as e:
            logger.error(f"Error opening position: {e}")
            return None
    
    async def close_position(
        self,
        symbol: str,
        exit_price: Decimal,
        strategy: str = 'manual'
    ) -> Optional[Trade]:
        """Pozitsiyani yopish"""
        try:
            if symbol not in self.positions:
                logger.warning(f"No position found for {symbol}")
                return None
            
            position = self.positions[symbol]
            
            # Calculate realized PnL
            if position.side == 'long':
                pnl = (exit_price - position.entry_price) * position.size
            else:
                pnl = (position.entry_price - exit_price) * position.size
            
            # Apply leverage
            pnl *= position.leverage
            
            # Calculate fees (0.1% for example)
            fees = (position.entry_price + exit_price) * position.size * Decimal('0.001')
            pnl -= fees
            
            # Calculate duration
            duration = (datetime.now() - position.entry_time).total_seconds() / 60
            
            # Calculate percentage
            pnl_percent = Decimal('0')
            if position.entry_price > 0:
                pnl_percent = (pnl / (position.entry_price * position.size)) * Decimal('100')
            
            # Create trade record
            trade = Trade(
                symbol=symbol,
                side=position.side,
                entry_price=position.entry_price,
                exit_price=exit_price,
                size=position.size,
                realized_pnl=pnl,
                realized_pnl_percent=pnl_percent,
                entry_time=position.entry_time,
                exit_time=datetime.now(),
                duration_minutes=int(duration),
                fees=fees,
                strategy=strategy
            )
            
            self.closed_trades.append(trade)
            
            # Update daily PnL
            today = datetime.now().strftime('%Y-%m-%d')
            self.daily_pnl[today] += pnl
            
            # Update strategy performance
            self.strategy_performance[strategy]['pnl'] += pnl
            self.strategy_performance[strategy]['trades'] += 1
            if pnl > 0:
                self.strategy_performance[strategy]['wins'] += 1
            
            # Remove position
            del self.positions[symbol]
            
            logger.info(f"Closed position: {symbol} @ ${exit_price}, PnL: ${pnl:.2f} ({pnl_percent:.2f}%)")
            
            return trade
            
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return None
    
    async def get_metrics(self) -> PortfolioMetrics:
        """Portfolio metrikalarini hisoblash"""
        try:
            # Basic metrics
            total_unrealized_pnl = sum(p.unrealized_pnl for p in self.positions.values())
            total_realized_pnl = sum(t.realized_pnl for t in self.closed_trades)
            total_pnl = total_realized_pnl + total_unrealized_pnl
            
            # Calculate total PnL percentage
            total_pnl_percent = Decimal('0')
            if self.initial_balance > 0:
                total_pnl_percent = (total_pnl / self.initial_balance) * Decimal('100')
            
            # Trade statistics
            total_trades = len(self.closed_trades)
            winning_trades = sum(1 for t in self.closed_trades if t.realized_pnl > 0)
            losing_trades = total_trades - winning_trades
            
            # Win rate
            win_rate = Decimal('0')
            if total_trades > 0:
                win_rate = (Decimal(winning_trades) / Decimal(total_trades)) * Decimal('100')
            
            # Average win/loss
            wins = [t.realized_pnl for t in self.closed_trades if t.realized_pnl > 0]
            losses = [abs(t.realized_pnl) for t in self.closed_trades if t.realized_pnl < 0]
            
            avg_win = sum(wins) / len(wins) if wins else Decimal('0')
            avg_loss = sum(losses) / len(losses) if losses else Decimal('0')
            
            # Profit factor
            profit_factor = Decimal('0')
            if sum(losses) > 0:
                profit_factor = sum(wins) / sum(losses)
            
            # Largest win/loss
            largest_win = max(wins) if wins else Decimal('0')
            largest_loss = max(losses) if losses else Decimal('0')
            
            # Average trade duration
            avg_duration = 0
            if self.closed_trades:
                avg_duration = sum(t.duration_minutes for t in self.closed_trades) // len(self.closed_trades)
            
            # Total fees
            total_fees = sum(t.fees for t in self.closed_trades)
            
            # Sharpe ratio
            sharpe_ratio = await self._calculate_sharpe_ratio()
            
            # Current drawdown
            current_drawdown = Decimal('0')
            if self.peak_balance > 0:
                current_drawdown = (
                    (self.peak_balance - self.current_balance) / self.peak_balance
                ) * Decimal('100')
            
            # Margin used
            margin_used = sum(
                (p.entry_price * p.size / p.leverage)
                for p in self.positions.values()
            )
            
            available_balance = self.current_balance - margin_used
            
            metrics = PortfolioMetrics(
                total_balance=self.current_balance,
                available_balance=available_balance,
                margin_used=margin_used,
                total_unrealized_pnl=total_unrealized_pnl,
                total_realized_pnl=total_realized_pnl,
                total_pnl=total_pnl,
                total_pnl_percent=total_pnl_percent,
                win_rate=win_rate,
                profit_factor=profit_factor,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=self.max_drawdown * Decimal('100'),
                current_drawdown=current_drawdown,
                total_trades=total_trades,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                avg_win=avg_win,
                avg_loss=avg_loss,
                largest_win=largest_win,
                largest_loss=largest_loss,
                avg_trade_duration_minutes=avg_duration,
                total_fees=total_fees
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return None
    
    async def _calculate_sharpe_ratio(self, periods_per_year: int = 365) -> Decimal:
        """Sharpe ratio hisoblash"""
        try:
            if len(self.balance_history) < 2:
                return Decimal('0')
            
            # Calculate daily returns
            returns = []
            for i in range(1, len(self.balance_history)):
                prev_balance = self.balance_history[i-1][1]
                curr_balance = self.balance_history[i][1]
                
                if prev_balance > 0:
                    ret = (curr_balance - prev_balance) / prev_balance
                    returns.append(float(ret))
            
            if not returns:
                return Decimal('0')
            
            # Calculate mean and std
            import statistics
            mean_return = statistics.mean(returns)
            std_return = statistics.stdev(returns) if len(returns) > 1 else 0
            
            if std_return == 0:
                return Decimal('0')
            
            # Annualize
            annual_return = mean_return * periods_per_year
            annual_std = std_return * (periods_per_year ** 0.5)
            
            # Sharpe ratio
            risk_free = float(self.risk_free_rate)
            sharpe = (annual_return - risk_free) / annual_std if annual_std > 0 else 0
            
            return Decimal(str(sharpe))
            
        except Exception as e:
            logger.error(f"Error calculating Sharpe ratio: {e}")
            return Decimal('0')
    
    async def get_position_summary(self) -> Dict:
        """Pozitsiyalar xulosasi"""
        try:
            summary = {
                'total_positions': len(self.positions),
                'long_positions': sum(1 for p in self.positions.values() if p.side == 'long'),
                'short_positions': sum(1 for p in self.positions.values() if p.side == 'short'),
                'positions': []
            }
            
            for symbol, position in self.positions.items():
                summary['positions'].append({
                    'symbol': symbol,
                    'side': position.side,
                    'size': float(position.size),
                    'entry_price': float(position.entry_price),
                    'current_price': float(position.current_price),
                    'unrealized_pnl': float(position.unrealized_pnl),
                    'unrealized_pnl_percent': float(position.unrealized_pnl_percent),
                    'leverage': float(position.leverage)
                })
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting position summary: {e}")
            return {}
    
    async def get_performance_report(self, days: int = 30) -> Dict:
        """Performance hisoboti"""
        try:
            since = datetime.now() - timedelta(days=days)
            recent_trades = [
                t for t in self.closed_trades
                if t.exit_time >= since
            ]
            
            report = {
                'period_days': days,
                'total_trades': len(recent_trades),
                'total_pnl': sum(t.realized_pnl for t in recent_trades),
                'winning_trades': sum(1 for t in recent_trades if t.realized_pnl > 0),
                'losing_trades': sum(1 for t in recent_trades if t.realized_pnl < 0),
                'win_rate': 0,
                'best_trade': None,
                'worst_trade': None,
                'daily_pnl': {},
                'strategy_breakdown': {}
            }
            
            if recent_trades:
                report['win_rate'] = (
                    report['winning_trades'] / len(recent_trades)
                ) * 100
                
                # Best and worst trades
                best = max(recent_trades, key=lambda t: t.realized_pnl)
                worst = min(recent_trades, key=lambda t: t.realized_pnl)
                
                report['best_trade'] = {
                    'symbol': best.symbol,
                    'pnl': float(best.realized_pnl),
                    'percent': float(best.realized_pnl_percent)
                }
                
                report['worst_trade'] = {
                    'symbol': worst.symbol,
                    'pnl': float(worst.realized_pnl),
                    'percent': float(worst.realized_pnl_percent)
                }
            
            # Daily PnL for period
            for i in range(days):
                date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                report['daily_pnl'][date] = float(self.daily_pnl.get(date, Decimal('0')))
            
            # Strategy breakdown
            for strategy, perf in self.strategy_performance.items():
                report['strategy_breakdown'][strategy] = {
                    'pnl': float(perf['pnl']),
                    'trades': perf['trades'],
                    'wins': perf['wins'],
                    'win_rate': (perf['wins'] / perf['trades'] * 100) if perf['trades'] > 0 else 0
                }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return {}
    
    def export_to_json(self, filepath: str):
        """Ma'lumotlarni JSON formatda eksport qilish"""
        try:
            data = {
                'initial_balance': float(self.initial_balance),
                'current_balance': float(self.current_balance),
                'positions': [
                    {
                        'symbol': p.symbol,
                        'side': p.side,
                        'size': float(p.size),
                        'entry_price': float(p.entry_price),
                        'current_price': float(p.current_price),
                        'unrealized_pnl': float(p.unrealized_pnl)
                    }
                    for p in self.positions.values()
                ],
                'closed_trades': [
                    {
                        'symbol': t.symbol,
                        'side': t.side,
                        'entry_price': float(t.entry_price),
                        'exit_price': float(t.exit_price),
                        'realized_pnl': float(t.realized_pnl),
                        'duration_minutes': t.duration_minutes
                    }
                    for t in self.closed_trades
                ]
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Exported portfolio data to {filepath}")
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")


async def main():
    """Test function"""
    dashboard = PortfolioDashboard(initial_balance=Decimal('10000'))
    
    # Open positions
    await dashboard.open_position(
        'BTC/USDT', 'long', Decimal('0.1'), Decimal('50000'),
        leverage=Decimal('2'), stop_loss=Decimal('48000'), take_profit=Decimal('55000')
    )
    
    await dashboard.open_position(
        'ETH/USDT', 'short', Decimal('1'), Decimal('3000'),
        leverage=Decimal('3')
    )
    
    # Update prices
    await dashboard.update_positions({
        'BTC/USDT': Decimal('51000'),
        'ETH/USDT': Decimal('2950')
    })
    
    # Get metrics
    metrics = await dashboard.get_metrics()
    print(f"Total Balance: ${metrics.total_balance:.2f}")
    print(f"Total PnL: ${metrics.total_pnl:.2f} ({metrics.total_pnl_percent:.2f}%)")
    print(f"Win Rate: {metrics.win_rate:.2f}%")
    print(f"Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
    
    # Close position
    await dashboard.close_position('BTC/USDT', Decimal('52000'))
    
    # Get report
    report = await dashboard.get_performance_report(days=7)
    print(f"\nPerformance Report (7 days):")
    print(f"Total Trades: {report['total_trades']}")
    print(f"Win Rate: {report['win_rate']:.2f}%")


if __name__ == '__main__':
    asyncio.run(main())
