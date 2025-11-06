"""
Arbitrage Execution Module
Arbitrage savdolarni bajarish moduli
"""
import asyncio
import aiohttp
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone, timedelta
import logging
import threading
import json
from concurrent.futures import ThreadPoolExecutor
import time
import uuid

from ..utils.data_models import ArbitrageOpportunity, TradeExecution, MarketData, ArbitrageType
from ..config.config import config

logger = logging.getLogger(__name__)

class TradeManager:
    """Trade management and execution"""
    
    def __init__(self, arbitrage_config):
        self.config = arbitrage_config
        self.active_positions = {}
        self.trade_history = []
        self.execution_queue = asyncio.Queue(maxsize=100)
        self.position_limits = {
            'max_position_size': config.arbitrage_config.max_position_size,
            'max_leverage': config.arbitrage_config.leverage,
            'stop_loss_level': config.arbitrage_config.stop_loss
        }
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Performance tracking
        self.execution_metrics = {
            'total_trades': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'total_profit': 0.0,
            'total_loss': 0.0,
            'avg_execution_time': 0.0,
            'slippage_avg': 0.0
        }
        
        # Risk management
        self.risk_limits = RiskLimits()
        
        logger.info("Trade Manager initialized")
    
    async def execute_arbitrage(self, opportunity: ArbitrageOpportunity, market_data: MarketData) -> TradeExecution:
        """Execute arbitrage trade"""
        try:
            start_time = datetime.now(timezone.utc)
            
            # Create execution object
            execution = TradeExecution(
                opportunity_id=opportunity.id,
                start_time=start_time,
                trades=[]
            )
            
            # Pre-execution validation
            if not await self._validate_execution(opportunity, market_data):
                execution.success = False
                execution.error_message = "Pre-execution validation failed"
                return execution
            
            # Risk assessment
            risk_assessment = await self._assess_execution_risk(opportunity, market_data)
            if risk_assessment['exceeds_limits']:
                execution.success = False
                execution.error_message = f"Risk limits exceeded: {risk_assessment['reason']}"
                return execution
            
            # Execute based on arbitrage type
            if opportunity.arbitrage_type == ArbitrageType.TRIANGULAR:
                execution = await self._execute_triangular_arbitrage(opportunity, market_data, execution)
            elif opportunity.arbitrage_type == ArbitrageType.CROSS_CURRENCY:
                execution = await self._execute_cross_currency_arbitrage(opportunity, market_data, execution)
            elif opportunity.arbitrage_type == ArbitrageType.CORRELATION:
                execution = await self._execute_correlation_arbitrage(opportunity, market_data, execution)
            elif opportunity.arbitrage_type == ArbitrageType.TIME_ZONE:
                execution = await self._execute_timezone_arbitrage(opportunity, market_data, execution)
            elif opportunity.arbitrage_type == ArbitrageType.VOLATILITY:
                execution = await self._execute_volatility_arbitrage(opportunity, market_data, execution)
            else:
                execution.success = False
                execution.error_message = f"Unknown arbitrage type: {opportunity.arbitrage_type}"
            
            # Calculate metrics
            execution.end_time = datetime.now(timezone.utc)
            execution.execution_time = (execution.end_time - execution.start_time).total_seconds()
            execution.calculate_net_profit()
            
            # Update metrics
            self._update_execution_metrics(execution)
            
            # Post-execution risk management
            if execution.success:
                await self._manage_position_risk(execution, market_data)
            
            logger.info(f"Arbitrage execution completed: {execution.success}, Profit: {execution.net_profit:.4f}")
            return execution
            
        except Exception as e:
            logger.error(f"Arbitrage execution failed: {e}")
            return TradeExecution(
                opportunity_id=opportunity.id,
                success=False,
                error_message=str(e),
                start_time=start_time,
                end_time=datetime.now(timezone.utc)
            )
    
    async def _validate_execution(self, opportunity: ArbitrageOpportunity, market_data: MarketData) -> bool:
        """Pre-execution validation"""
        try:
            # Check time window
            current_time = datetime.now(timezone.utc)
            if opportunity.time_window and opportunity.time_window < 1:
                logger.warning(f"Opportunity time window expired: {opportunity.time_window}s")
                return False
            
            # Check required pairs availability
            for pair in opportunity.pairs:
                if pair not in market_data.prices:
                    logger.error(f"Required pair {pair} not available in market data")
                    return False
                
                # Check price validity
                price = market_data.prices[pair]
                if price.bid <= 0 or price.ask <= 0 or price.ask <= price.bid:
                    logger.error(f"Invalid price data for {pair}: bid={price.bid}, ask={price.ask}")
                    return False
            
            # Check profit threshold
            if opportunity.calculations and opportunity.calculations.profit_potential < self.config.min_profit_threshold:
                logger.warning(f"Profit potential below threshold: {opportunity.calculations.profit_potential}")
                return False
            
            # Check risk level
            if opportunity.risk_level > self.config.risk_limit:
                logger.warning(f"Risk level too high: {opportunity.risk_level}")
                return False
            
            # Check market hours
            if not market_data.market_hours:
                logger.warning("Markets are closed")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Execution validation failed: {e}")
            return False
    
    async def _assess_execution_risk(self, opportunity: ArbitrageOpportunity, market_data: MarketData) -> Dict[str, Any]:
        """Execution risk assessment"""
        risk_assessment = {
            'exceeds_limits': False,
            'reason': '',
            'risk_score': 0.0
        }
        
        try:
            # Position size risk
            required_capital = opportunity.required_capital if opportunity.required_capital else 100000
            if required_capital > self.position_limits['max_position_size']:
                risk_assessment['exceeds_limits'] = True
                risk_assessment['reason'] = "Position size exceeds limit"
                return risk_assessment
            
            # Leverage risk
            if self.position_limits['max_leverage'] > 10 and opportunity.risk_level > 0.5:
                risk_assessment['exceeds_limits'] = True
                risk_assessment['reason'] = "High leverage with high risk"
                return risk_assessment
            
            # Market liquidity risk
            min_liquidity = float('inf')
            for pair in opportunity.pairs:
                if pair in market_data.volume:
                    liquidity = market_data.volume[pair]
                    min_liquidity = min(min_liquidity, liquidity)
            
            if min_liquidity < 100000:  # Less than $100k liquidity
                risk_assessment['exceeds_limits'] = True
                risk_assessment['reason'] = "Insufficient market liquidity"
                return risk_assessment
            
            # Execution complexity risk
            execution_complexity = len(opportunity.pairs) * 0.2 + opportunity.risk_level
            if execution_complexity > 1.0:
                risk_assessment['exceeds_limits'] = True
                risk_assessment['reason'] = "Execution complexity too high"
                return risk_assessment
            
            risk_assessment['risk_score'] = execution_complexity
            return risk_assessment
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            risk_assessment['exceeds_limits'] = True
            risk_assessment['reason'] = f"Risk assessment error: {str(e)}"
            return risk_assessment
    
    async def _execute_triangular_arbitrage(self, opportunity: ArbitrageOpportunity, market_data: MarketData, execution: TradeExecution) -> TradeExecution:
        """Execute triangular arbitrage"""
        try:
            pair1, pair2, pair3 = opportunity.pairs
            
            # Trade execution sequence
            trades = []
            
            # Step 1: Trade pair1 (e.g., EUR/USD)
            trade1 = await self._execute_single_trade(pair1, 'buy', 10000, market_data)  # $10k
            if not trade1['success']:
                execution.failed_steps.append(f"Trade 1 failed: {pair1}")
                return execution
            trades.append(trade1)
            
            # Step 2: Trade pair2 (e.g., USD/JPY) 
            trade2 = await self._execute_single_trade(pair2, 'buy', trade1['amount'] * trade1['rate'], market_data)
            if not trade2['success']:
                execution.failed_steps.append(f"Trade 2 failed: {pair2}")
                return execution
            trades.append(trade2)
            
            # Step 3: Trade pair3 (e.g., EUR/JPY) - opposite direction
            final_amount = trade2['amount'] * trade2['rate']
            trade3 = await self._execute_single_trade(pair3, 'sell', final_amount, market_data)
            if not trade3['success']:
                execution.failed_steps.append(f"Trade 3 failed: {pair3}")
                return execution
            trades.append(trade3)
            
            # Calculate profit
            initial_amount = 10000
            final_amount = trade3['amount']
            
            execution.success = True
            execution.profit = final_amount - initial_amount
            execution.trades = trades
            execution.total_cost = sum(trade['cost'] for trade in trades)
            
            # Calculate slippage
            execution.slippage = sum(trade.get('slippage', 0) for trade in trades)
            
            logger.info(f"Triangular arbitrage successful: {initial_amount} -> {final_amount}, Profit: {execution.profit}")
            return execution
            
        except Exception as e:
            logger.error(f"Triangular arbitrage execution failed: {e}")
            execution.success = False
            execution.error_message = str(e)
            return execution
    
    async def _execute_cross_currency_arbitrage(self, opportunity: ArbitrageOpportunity, market_data: MarketData, execution: TradeExecution) -> TradeExecution:
        """Execute cross-currency arbitrage"""
        try:
            pair = opportunity.pairs[0]
            
            # Compare direct vs implied rate
            direct_rate = opportunity.rates.get('direct_rate')
            implied_rate = opportunity.rates.get('implied_rate')
            
            if not direct_rate or not implied_rate:
                execution.success = False
                execution.error_message = "Missing rate data"
                return execution
            
            # Determine trade direction
            if direct_rate > implied_rate:
                # Buy through direct route, sell through implied route
                buy_trade = await self._execute_single_trade(pair, 'buy', 10000, market_data)
                sell_trade = await self._execute_single_trade(pair, 'sell', buy_trade['amount'], market_data)
            else:
                # Sell through direct route, buy through implied route
                sell_trade = await self._execute_single_trade(pair, 'sell', 10000, market_data)
                buy_trade = await self._execute_single_trade(pair, 'buy', sell_trade['amount'], market_data)
            
            if not (buy_trade['success'] and sell_trade['success']):
                execution.success = False
                execution.error_message = "Cross-currency trade execution failed"
                return execution
            
            execution.success = True
            execution.profit = abs(buy_trade['amount'] - sell_trade['amount']) / 2
            execution.trades = [buy_trade, sell_trade]
            execution.total_cost = buy_trade['cost'] + sell_trade['cost']
            execution.slippage = buy_trade.get('slippage', 0) + sell_trade.get('slippage', 0)
            
            return execution
            
        except Exception as e:
            logger.error(f"Cross-currency arbitrage execution failed: {e}")
            execution.success = False
            execution.error_message = str(e)
            return execution
    
    async def _execute_correlation_arbitrage(self, opportunity: ArbitrageOpportunity, market_data: MarketData, execution: TradeExecution) -> TradeExecution:
        """Execute correlation arbitrage"""
        try:
            pair1, pair2 = opportunity.pairs
            
            # Statistical arbitrage based on correlation
            rate1 = market_data.prices[pair1].mid_price
            rate2 = market_data.prices[pair2].mid_price
            
            # Calculate expected rate ratio
            expected_ratio = opportunity.rates.get('expected_ratio', 1.0)
            actual_ratio = rate1 / rate2
            
            # Determine trade direction based on ratio deviation
            if actual_ratio > expected_ratio:
                # Pair1 overvalued relative to pair2
                trade1 = await self._execute_single_trade(pair1, 'sell', 5000, market_data)
                trade2 = await self._execute_single_trade(pair2, 'buy', 5000, market_data)
            else:
                # Pair2 overvalued relative to pair1
                trade1 = await self._execute_single_trade(pair1, 'buy', 5000, market_data)
                trade2 = await self._execute_single_trade(pair2, 'sell', 5000, market_data)
            
            if not (trade1['success'] and trade2['success']):
                execution.success = False
                execution.error_message = "Correlation arbitrage trade execution failed"
                return execution
            
            execution.success = True
            execution.profit = abs(trade1['amount'] - trade2['amount']) / 2
            execution.trades = [trade1, trade2]
            execution.total_cost = trade1['cost'] + trade2['cost']
            execution.slippage = trade1.get('slippage', 0) + trade2.get('slippage', 0)
            
            return execution
            
        except Exception as e:
            logger.error(f"Correlation arbitrage execution failed: {e}")
            execution.success = False
            execution.error_message = str(e)
            return execution
    
    async def _execute_timezone_arbitrage(self, opportunity: ArbitrageOpportunity, market_data: MarketData, execution: TradeExecution) -> TradeExecution:
        """Execute time-zone arbitrage"""
        try:
            pair = opportunity.pairs[0]
            
            # Time-zone arbitrage during market overlaps
            profit_rate = opportunity.calculations.profit_potential / 100
            
            # Execute trades based on timezone overlap
            if opportunity.calculations.time_sensitivity > 0.8:
                # High time sensitivity - quick execution
                trade = await self._execute_single_trade(pair, 'buy', 10000, market_data)
                
                if trade['success']:
                    # Simulate quick reversal
                    reverse_trade = await self._execute_single_trade(pair, 'sell', trade['amount'], market_data, enhanced_rate=profit_rate)
                    
                    execution.success = reverse_trade['success']
                    execution.profit = reverse_trade.get('profit', 0)
                    execution.trades = [trade, reverse_trade]
                    execution.total_cost = trade['cost'] + reverse_trade.get('cost', 0)
            else:
                # Standard execution
                trade = await self._execute_single_trade(pair, 'buy', 10000, market_data)
                
                execution.success = trade['success']
                execution.profit = trade.get('profit', 0) * profit_rate
                execution.trades = [trade]
                execution.total_cost = trade['cost']
            
            return execution
            
        except Exception as e:
            logger.error(f"Timezone arbitrage execution failed: {e}")
            execution.success = False
            execution.error_message = str(e)
            return execution
    
    async def _execute_volatility_arbitrage(self, opportunity: ArbitrageOpportunity, market_data: MarketData, execution: TradeExecution) -> TradeExecution:
        """Execute volatility arbitrage"""
        try:
            pair = opportunity.pairs[0]
            volatility = opportunity.volatility_score
            
            # Volatility-based profit calculation
            volatility_multiplier = 1 + volatility * 5
            target_profit = opportunity.calculations.profit_potential / 100 * volatility_multiplier
            
            # Execute volatility strategy
            # For demo: simulate volatility trading
            base_trade = await self._execute_single_trade(pair, 'buy', 5000, market_data)
            
            if base_trade['success']:
                # Calculate volatility-enhanced profit
                execution.success = True
                execution.profit = base_trade.get('profit', 0) * volatility_multiplier
                execution.trades = [base_trade]
                execution.total_cost = base_trade['cost']
                execution.market_impact = volatility * 0.01  # Higher volatility = higher market impact
            
            return execution
            
        except Exception as e:
            logger.error(f"Volatility arbitrage execution failed: {e}")
            execution.success = False
            execution.error_message = str(e)
            return execution
    
    async def _execute_single_trade(self, pair: str, action: str, amount: float, market_data: MarketData, enhanced_rate: float = 0) -> Dict[str, Any]:
        """Execute single trade"""
        try:
            if pair not in market_data.prices:
                return {
                    'success': False,
                    'error': f'Pair {pair} not available',
                    'pair': pair,
                    'action': action,
                    'amount': amount
                }
            
            price = market_data.prices[pair]
            
            # Calculate execution rate with slippage
            if action == 'buy':
                execution_rate = price.ask
            else:
                execution_rate = price.bid
            
            # Apply enhanced rate if provided (for demo purposes)
            if enhanced_rate > 0:
                execution_rate *= (1 + enhanced_rate)
            
            # Simulate slippage
            slippage = self._calculate_slippage(amount, price, action)
            execution_rate *= (1 + slippage)
            
            # Simulate trade execution
            await asyncio.sleep(0.01)  # Simulate network latency
            
            trade_result = {
                'success': True,
                'pair': pair,
                'action': action,
                'amount': amount,
                'rate': execution_rate,
                'cost': amount * execution_rate,
                'slippage': slippage,
                'timestamp': datetime.now(timezone.utc)
            }
            
            # Calculate profit for demo purposes
            if hasattr(self, '_last_prices'):
                last_price = self._last_prices.get(pair, execution_rate)
                trade_result['profit'] = (execution_rate - last_price) * amount if action == 'buy' else (last_price - execution_rate) * amount
            
            # Update last prices
            if not hasattr(self, '_last_prices'):
                self._last_prices = {}
            self._last_prices[pair] = execution_rate
            
            return trade_result
            
        except Exception as e:
            logger.error(f"Single trade execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'pair': pair,
                'action': action,
                'amount': amount
            }
    
    def _calculate_slippage(self, amount: float, price, action: str) -> float:
        """Calculate slippage based on trade size and market conditions"""
        try:
            # Base slippage
            base_slippage = 0.0001  # 1 pip
            
            # Volume-based slippage
            volume_factor = amount / 100000  # Base volume $100k
            
            # Market conditions slippage
            spread_factor = price.effective_spread_pct / 100
            
            # Action-based slippage (buying often has higher slippage)
            action_factor = 1.2 if action == 'buy' else 1.0
            
            total_slippage = base_slippage * (1 + volume_factor) * (1 + spread_factor) * action_factor
            
            return min(0.01, total_slippage)  # Cap at 1%
            
        except Exception as e:
            logger.error(f"Slippage calculation failed: {e}")
            return 0.001
    
    async def _manage_position_risk(self, execution: TradeExecution, market_data: MarketData):
        """Post-execution risk management"""
        try:
            if execution.success:
                # Update active positions
                for trade in execution.trades:
                    pair = trade['pair']
                    action = trade['action']
                    amount = trade['amount']
                    
                    with self._lock:
                        if pair not in self.active_positions:
                            self.active_positions[pair] = {
                                'long': 0.0,
                                'short': 0.0,
                                'net_exposure': 0.0
                            }
                        
                        position = self.active_positions[pair]
                        if action == 'buy':
                            position['long'] += amount
                        else:
                            position['short'] += amount
                        
                        position['net_exposure'] = position['long'] - position['short']
                
                # Check for risk breaches
                await self._check_risk_limits()
            
        except Exception as e:
            logger.error(f"Position risk management failed: {e}")
    
    async def _check_risk_limits(self):
        """Check risk limits for active positions"""
        try:
            for pair, position in self.active_positions.items():
                # Check stop loss limits
                net_exposure = abs(position['net_exposure'])
                if net_exposure > self.position_limits['max_position_size']:
                    logger.warning(f"Position size limit exceeded for {pair}: {net_exposure}")
                
                # Check leverage limits
                total_exposure = position['long'] + position['short']
                if total_exposure > self.position_limits['max_position_size'] * self.position_limits['max_leverage']:
                    logger.warning(f"Leverage limit exceeded for {pair}")
            
        except Exception as e:
            logger.error(f"Risk limit check failed: {e}")
    
    def _update_execution_metrics(self, execution: TradeExecution):
        """Update execution metrics"""
        with self._lock:
            self.execution_metrics['total_trades'] += 1
            
            if execution.success:
                self.execution_metrics['successful_trades'] += 1
                self.execution_metrics['total_profit'] += execution.net_profit
            else:
                self.execution_metrics['failed_trades'] += 1
                if execution.net_profit < 0:
                    self.execution_metrics['total_loss'] += abs(execution.net_profit)
            
            # Update averages
            total_trades = self.execution_metrics['total_trades']
            self.execution_metrics['avg_execution_time'] = (
                (self.execution_metrics['avg_execution_time'] * (total_trades - 1) + execution.execution_time) / total_trades
            )
            
            if execution.slippage > 0:
                self.execution_metrics['slippage_avg'] = (
                    (self.execution_metrics['slippage_avg'] * (total_trades - 1) + execution.slippage) / total_trades
                )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        with self._lock:
            metrics = self.execution_metrics.copy()
            
            # Calculate derived metrics
            if metrics['total_trades'] > 0:
                metrics['success_rate'] = (metrics['successful_trades'] / metrics['total_trades']) * 100
                metrics['avg_profit_per_trade'] = metrics['total_profit'] / metrics['successful_trades'] if metrics['successful_trades'] > 0 else 0
                metrics['profit_loss_ratio'] = metrics['total_profit'] / max(metrics['total_loss'], 1)
            else:
                metrics['success_rate'] = 0
                metrics['avg_profit_per_trade'] = 0
                metrics['profit_loss_ratio'] = 0
            
            metrics['active_positions'] = len(self.active_positions)
            metrics['total_exposure'] = sum(pos['net_exposure'] for pos in self.active_positions.values())
            
            return metrics
    
    def close_positions(self, pair: Optional[str] = None):
        """Close positions (demo function)"""
        with self._lock:
            if pair:
                if pair in self.active_positions:
                    logger.info(f"Closing positions for {pair}")
                    del self.active_positions[pair]
            else:
                logger.info("Closing all positions")
                self.active_positions.clear()


class ArbitrageExecutor:
    """
    Main Arbitrage Executor
    Bosh ijrochi
    """
    
    def __init__(self, arbitrage_config):
        self.config = arbitrage_config
        self.trade_manager = TradeManager(arbitrage_config)
        self.execution_queue = asyncio.Queue()
        self.running = False
        self.executor_task = None
        
        # Execution settings
        self.max_concurrent_trades = 5
        self.execution_timeout = 30.0
        
        logger.info("Arbitrage Executor initialized")
    
    async def start_executor(self):
        """Start executor service"""
        self.running = True
        self.executor_task = asyncio.create_task(self._execution_loop())
        logger.info("Arbitrage Executor started")
    
    async def stop_executor(self):
        """Stop executor service"""
        self.running = False
        if self.executor_task:
            self.executor_task.cancel()
        
        # Close all positions
        self.trade_manager.close_positions()
        logger.info("Arbitrage Executor stopped")
    
    async def execute_arbitrage(self, opportunity: ArbitrageOpportunity) -> TradeExecution:
        """Execute arbitrage opportunity"""
        try:
            # Create execution task
            execution_task = asyncio.create_task(
                self._execute_with_timeout(opportunity)
            )
            
            # Wait for execution
            execution = await execution_task
            
            return execution
            
        except asyncio.TimeoutError:
            logger.error(f"Arbitrage execution timeout for opportunity {opportunity.id}")
            return TradeExecution(
                opportunity_id=opportunity.id,
                success=False,
                error_message="Execution timeout"
            )
        except Exception as e:
            logger.error(f"Arbitrage execution error: {e}")
            return TradeExecution(
                opportunity_id=opportunity.id,
                success=False,
                error_message=str(e)
            )
    
    async def _execute_with_timeout(self, opportunity: ArbitrageOpportunity) -> TradeExecution:
        """Execute with timeout"""
        return await asyncio.wait_for(
            self.trade_manager.execute_arbitrage(opportunity, MarketData()),
            timeout=self.execution_timeout
        )
    
    async def _execution_loop(self):
        """Main execution loop"""
        while self.running:
            try:
                # Check for pending executions (in real implementation)
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Execution loop error: {e}")
                await asyncio.sleep(1)
    
    def get_status(self) -> Dict[str, Any]:
        """Get executor status"""
        return {
            'running': self.running,
            'trade_manager_metrics': self.trade_manager.get_performance_metrics(),
            'active_positions': len(self.trade_manager.active_positions),
            'max_concurrent_trades': self.max_concurrent_trades,
            'execution_timeout': self.execution_timeout
        }


class RiskLimits:
    """Risk limit management"""
    
    def __init__(self):
        self.position_limits = {
            'max_single_position': 500000,  # $500k
            'max_total_exposure': 2000000,  # $2M
            'max_correlation_exposure': 1000000  # $1M
        }
        
        self.drawdown_limits = {
            'max_daily_drawdown': 50000,  # $50k
            'max_weekly_drawdown': 100000,  # $100k
            'stop_loss_percentage': 0.02  # 2%
        }
        
        self.current_drawdown = 0.0
        self.daily_pnl = 0.0
    
    def check_position_limits(self, proposed_position: float) -> bool:
        """Check position size limits"""
        return proposed_position <= self.position_limits['max_single_position']
    
    def check_total_exposure(self, total_exposure: float) -> bool:
        """Check total exposure limits"""
        return total_exposure <= self.position_limits['max_total_exposure']
    
    def check_drawdown_limits(self, current_pnl: float) -> bool:
        """Check drawdown limits"""
        if current_pnl < 0:
            self.current_drawdown += abs(current_pnl)
        
        daily_loss = self.daily_pnl if self.daily_pnl < 0 else 0
        return abs(daily_loss) <= self.drawdown_limits['max_daily_drawdown']
    
    def update_daily_pnl(self, pnl: float):
        """Update daily P&L"""
        self.daily_pnl += pnl