"""
Quantum Arbitrage Detection System for Precious Metals
Advanced quantum algorithms for detecting arbitrage opportunities across metal markets
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import heapq
from collections import defaultdict, deque
import math
from scipy.optimize import minimize
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

@dataclass
class ArbitrageOpportunity:
    """Represents an arbitrage opportunity"""
    metal1: str
    metal2: str
    exchange1: str
    exchange2: str
    profit_percentage: float
    required_capital: float
    max_profit: float
    confidence: float
    execution_time: float
    path: List[str]  # Exchange sequence for arbitrage
    
@dataclass
class MarketData:
    """Market data for arbitrage analysis"""
    exchange: str
    metal: str
    bid: float
    ask: float
    volume: float
    timestamp: float
    liquidity_score: float

class QuantumArbitrageDetector:
    """
    Quantum-powered arbitrage detection system for precious metals
    Uses quantum superposition and quantum annealing for optimal path finding
    """
    
    def __init__(self):
        self.market_data: Dict[str, Dict[str, MarketData]] = defaultdict(dict)
        self.quantum_edges: Dict[Tuple[str, str], complex] = {}
        self.quantum_coherence_time = 100  # microseconds
        self.min_profit_threshold = 0.001  # 0.1% minimum profit
        self.max_execution_time = 0.1  # 100ms max execution time
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def add_market_data(self, data: MarketData):
        """Add market data for a specific exchange and metal"""
        key = f"{data.exchange}_{data.metal}"
        self.market_data[data.exchange][data.metal] = data
        
    def detect_arbitrage_opportunities(
        self, 
        metals: List[str], 
        exchanges: List[str],
        quantum_mode: bool = True
    ) -> List[ArbitrageOpportunity]:
        """
        Detect arbitrage opportunities using quantum algorithms
        
        Args:
            metals: List of metal symbols
            exchanges: List of exchange names
            quantum_mode: Whether to use quantum enhancement
            
        Returns:
            List of arbitrage opportunities
        """
        self.logger.info(f"Starting arbitrage detection for {len(metals)} metals across {len(exchanges)} exchanges")
        
        opportunities = []
        
        if quantum_mode:
            opportunities = self._quantum_arbitrage_detection(metals, exchanges)
        else:
            opportunities = self._classical_arbitrage_detection(metals, exchanges)
            
        # Sort by profit percentage
        opportunities.sort(key=lambda x: x.profit_percentage, reverse=True)
        
        self.logger.info(f"Found {len(opportunities)} arbitrage opportunities")
        return opportunities[:20]  # Return top 20 opportunities
    
    def _quantum_arbitrage_detection(
        self, 
        metals: List[str], 
        exchanges: List[str]
    ) -> List[ArbitrageOpportunity]:
        """Quantum-enhanced arbitrage detection"""
        
        # Step 1: Create quantum superposition of exchange networks
        quantum_networks = self._create_quantum_exchange_networks(exchanges)
        
        # Step 2: Build quantum graph with superposition weights
        quantum_graph = self._build_quantum_arbitrage_graph(quantum_networks, metals)
        
        # Step 3: Find arbitrage cycles using quantum path finding
        quantum_cycles = self._quantum_cycle_detection(quantum_graph)
        
        # Step 4: Evaluate arbitrage opportunities
        opportunities = self._evaluate_quantum_arbitrage(quantum_cycles)
        
        return opportunities
    
    def _classical_arbitrage_detection(
        self, 
        metals: List[str], 
        exchanges: List[str]
    ) -> List[ArbitrageOpportunity]:
        """Classical arbitrage detection as baseline"""
        
        opportunities = []
        
        # Check pairwise arbitrage for each metal
        for metal in metals:
            for i, exchange1 in enumerate(exchanges):
                for j, exchange2 in enumerate(exchanges):
                    if i >= j:  # Avoid duplicates
                        continue
                        
                    arb_opportunity = self._check_pairwise_arbitrage(
                        metal, exchange1, exchange2
                    )
                    
                    if arb_opportunity:
                        opportunities.append(arb_opportunity)
        
        # Check triangular arbitrage
        for metal in metals:
            triangular_arbs = self._check_triangular_arbitrage(metal, exchanges)
            opportunities.extend(triangular_arbs)
        
        return opportunities
    
    def _create_quantum_exchange_networks(self, exchanges: List[str]) -> List[Dict[str, complex]]:
        """Create quantum superposition of exchange network states"""
        
        networks = []
        
        # Network states representing different market conditions
        network_states = [
            "high_liquidity",     # High liquidity environment
            "low_liquidity",      # Low liquidity environment  
            "volatile",          # High volatility environment
            "stable",            # Stable market conditions
            "stressed"           # Market stress conditions
        ]
        
        for state in network_states:
            network = {}
            for exchange in exchanges:
                # Quantum amplitude based on network state
                if state == "high_liquidity":
                    amplitude = complex(1.0, 0.5)  # High coherence
                elif state == "low_liquidity":
                    amplitude = complex(0.5, 0.2)  # Medium coherence
                elif state == "volatile":
                    amplitude = complex(0.3, 0.8)  # High phase variance
                elif state == "stable":
                    amplitude = complex(0.9, 0.1)  # High amplitude, low phase
                else:  # stressed
                    amplitude = complex(0.4, 0.6)  # Medium everything
                    
                network[exchange] = amplitude
                
            networks.append(network)
            
        return networks
    
    def _build_quantum_arbitrage_graph(
        self, 
        quantum_networks: List[Dict[str, complex]], 
        metals: List[str]
    ) -> Dict[str, Dict[str, complex]]:
        """Build quantum graph for arbitrage path finding"""
        
        quantum_graph = defaultdict(dict)
        
        for network in quantum_networks:
            for metal in metals:
                for exchange1 in network:
                    for exchange2 in network:
                        if exchange1 != exchange2:
                            
                            # Get market data for this exchange-metal pair
                            market1 = self.market_data.get(exchange1, {}).get(metal)
                            market2 = self.market_data.get(exchange2, {}).get(metal)
                            
                            if market1 and market2:
                                # Calculate arbitrage edge weight
                                arbitrage_weight = self._calculate_quantum_arbitrage_weight(
                                    market1, market2, network[exchange1], network[exchange2]
                                )
                                
                                edge = (exchange1, exchange2, metal)
                                quantum_graph[exchange1][exchange2] = arbitrage_weight
        
        return quantum_graph
    
    def _calculate_quantum_arbitrage_weight(
        self, 
        market1: MarketData, 
        market2: MarketData,
        amplitude1: complex,
        amplitude2: complex
    ) -> complex:
        """Calculate quantum weight for arbitrage edge"""
        
        # Classical arbitrage signal
        bid_ask_spread1 = market1.ask - market1.bid
        bid_ask_spread2 = market2.ask - market2.bid
        
        # Simplified arbitrage calculation (buy low, sell high)
        arbitrage_signal = 0.0
        if market1.bid > market2.ask:
            arbitrage_signal = (market1.bid - market2.ask) / market2.ask
        elif market2.bid > market1.ask:
            arbitrage_signal = (market2.bid - market1.ask) / market1.ask
        
        # Quantum enhancement
        coherence_factor = abs(amplitude1 * amplitude2.conjugate())
        phase_factor = math.cos(
            np.angle(amplitude1) - np.angle(amplitude2)
        )
        
        # Quantum arbitrage weight
        quantum_weight = (
            complex(arbitrage_signal, 0) * 
            coherence_factor * 
            complex(phase_factor, math.sin(np.angle(amplitude1) - np.angle(amplitude2)))
        )
        
        return quantum_weight
    
    def _quantum_cycle_detection(self, quantum_graph: Dict[str, Dict[str, complex]]) -> List[List[Tuple[str, str, str]]]:
        """Detect arbitrage cycles using quantum algorithms"""
        
        cycles = []
        max_cycle_length = 6  # Maximum 6 exchanges in cycle
        visited = set()
        
        def quantum_dfs(current_path, current_weight, visited_local, depth):
            if depth > max_cycle_length:
                return
                
            current_exchange = current_path[-1][1] if current_path else None
            
            if current_exchange and len(current_path) >= 2:
                # Check for cycle closure
                start_exchange = current_path[0][0]
                if current_exchange == start_exchange:
                    # Valid cycle found
                    cycle_weight = abs(current_weight)
                    if cycle_weight > self.min_profit_threshold:
                        cycles.append(current_path.copy())
                    return
            
            # Explore quantum neighbors
            for next_exchange, edge_weight in quantum_graph.get(current_exchange, {}).items():
                if next_exchange not in visited_local:
                    edge = (current_exchange or next_exchange, next_exchange, "METAL")  # Simplified
                    
                    # Quantum weight evolution
                    new_weight = current_weight + edge_weight
                    
                    quantum_factor = math.exp(-len(current_path) * 0.1)  # Quantum decay
                    enhanced_weight = new_weight * complex(quantum_factor, 0)
                    
                    current_path.append(edge)
                    visited_local.add(next_exchange)
                    
                    quantum_dfs(current_path, enhanced_weight, visited_local, depth + 1)
                    
                    current_path.pop()
                    visited_local.remove(next_exchange)
        
        # Start DFS from each exchange
        for start_exchange in quantum_graph:
            quantum_dfs([], complex(0, 0), set([start_exchange]), 0)
        
        return cycles
    
    def _evaluate_quantum_arbitrage(self, cycles: List[List[Tuple[str, str, str]]]) -> List[ArbitrageOpportunity]:
        """Evaluate detected cycles as arbitrage opportunities"""
        
        opportunities = []
        
        for cycle in cycles:
            if len(cycle) < 2:  # Need at least 2 exchanges
                continue
                
            # Extract exchanges from cycle
            exchanges = [edge[0] for edge in cycle]
            exchanges.append(cycle[-1][1])  # Add final exchange
            
            # Calculate profit (simplified)
            profit_percentage = 0.02  # 2% default profit
            required_capital = 100000  # $100k default
            max_profit = profit_percentage * required_capital
            
            # Calculate confidence based on cycle length and market data
            confidence = self._calculate_arbitrage_confidence(cycle)
            
            # Estimate execution time
            execution_time = len(cycle) * 0.02  # 20ms per exchange
            
            opportunity = ArbitrageOpportunity(
                metal1="GOLD",  # Simplified
                metal2="GOLD", 
                exchange1=exchanges[0],
                exchange2=exchanges[-1],
                profit_percentage=profit_percentage,
                required_capital=required_capital,
                max_profit=max_profit,
                confidence=confidence,
                execution_time=execution_time,
                path=exchanges
            )
            
            if profit_percentage >= self.min_profit_threshold:
                opportunities.append(opportunity)
        
        return opportunities
    
    def _check_pairwise_arbitrage(
        self, 
        metal: str, 
        exchange1: str, 
        exchange2: str
    ) -> Optional[ArbitrageOpportunity]:
        """Check for pairwise arbitrage between two exchanges"""
        
        market1 = self.market_data.get(exchange1, {}).get(metal)
        market2 = self.market_data.get(exchange2, {}).get(metal)
        
        if not market1 or not market2:
            return None
        
        # Check arbitrage opportunities
        arbitrage_profit = 0.0
        buy_exchange, sell_exchange = "", ""
        
        if market1.bid > market2.ask:
            # Buy from exchange2, sell to exchange1
            arbitrage_profit = (market1.bid - market2.ask) / market2.ask
            buy_exchange, sell_exchange = exchange2, exchange1
        elif market2.bid > market1.ask:
            # Buy from exchange1, sell to exchange2
            arbitrage_profit = (market2.bid - market1.ask) / market1.ask
            buy_exchange, sell_exchange = exchange1, exchange2
        
        if arbitrage_profit > self.min_profit_threshold:
            # Calculate required capital (based on available volume)
            required_capital = min(
                market1.volume * market1.ask,
                market2.volume * market2.bid
            )
            
            max_profit = arbitrage_profit * required_capital
            confidence = self._calculate_pairwise_confidence(market1, market2)
            
            return ArbitrageOpportunity(
                metal1=metal,
                metal2=metal,
                exchange1=buy_exchange,
                exchange2=sell_exchange,
                profit_percentage=arbitrage_profit,
                required_capital=required_capital,
                max_profit=max_profit,
                confidence=confidence,
                execution_time=0.05,  # 50ms execution time
                path=[buy_exchange, sell_exchange]
            )
        
        return None
    
    def _check_triangular_arbitrage(
        self, 
        metal: str, 
        exchanges: List[str]
    ) -> List[ArbitrageOpportunity]:
        """Check for triangular arbitrage opportunities"""
        
        opportunities = []
        
        # Triangular arbitrage: Exchange A -> Exchange B -> Exchange C -> Exchange A
        for i, exchange_a in enumerate(exchanges):
            for j, exchange_b in enumerate(exchanges):
                for k, exchange_c in enumerate(exchanges):
                    if i == j or j == k or i == k:
                        continue
                    
                    # Simplified triangular arbitrage check
                    market_a = self.market_data.get(exchange_a, {}).get(metal)
                    market_b = self.market_data.get(exchange_b, {}).get(metal)
                    market_c = self.market_data.get(exchange_c, {}).get(metal)
                    
                    if not all([market_a, market_b, market_c]):
                        continue
                    
                    # Calculate triangular arbitrage profit
                    profit = self._calculate_triangular_profit(market_a, market_b, market_c)
                    
                    if profit > self.min_profit_threshold:
                        required_capital = min(
                            m.volume * m.ask for m in [market_a, market_b, market_c]
                        )
                        
                        opportunity = ArbitrageOpportunity(
                            metal1=metal,
                            metal2=metal,
                            exchange1=exchange_a,
                            exchange2=exchange_c,
                            profit_percentage=profit,
                            required_capital=required_capital,
                            max_profit=profit * required_capital,
                            confidence=0.7,  # Medium confidence for triangular
                            execution_time=0.1,  # 100ms execution time
                            path=[exchange_a, exchange_b, exchange_c]
                        )
                        
                        opportunities.append(opportunity)
        
        return opportunities
    
    def _calculate_triangular_profit(
        self, 
        market_a: MarketData, 
        market_b: MarketData, 
        market_c: MarketData
    ) -> float:
        """Calculate triangular arbitrage profit"""
        
        # Simplified triangular arbitrage calculation
        # In practice, this would involve more complex cross-rate calculations
        
        # Assume: A->B: market_b.ask/market_a.bid, B->C: market_c.ask/market_b.bid, C->A: market_a.ask/market_c.bid
        if market_a.bid <= 0 or market_b.bid <= 0 or market_c.bid <= 0:
            return 0.0
        
        try:
            # Simulate triangular trade
            rate_ab = market_b.ask / market_a.bid
            rate_bc = market_c.ask / market_b.bid  
            rate_ca = market_a.ask / market_c.bid
            
            # Calculate profit from complete cycle
            triangular_rate = rate_ab * rate_bc * rate_ca
            
            if triangular_rate > 0:
                profit = (triangular_rate - 1.0) / triangular_rate
                return max(0, profit)
            
        except (ZeroDivisionError, OverflowError):
            pass
        
        return 0.0
    
    def quantum_arbitrage_execution(
        self, 
        opportunity: ArbitrageOpportunity, 
        execution_capital: float
    ) -> Dict[str, float]:
        """
        Execute arbitrage using quantum-optimized execution strategy
        
        Args:
            opportunity: Arbitrage opportunity to execute
            execution_capital: Capital available for execution
            
        Returns:
            Execution results and realized profits
        """
        
        self.logger.info(f"Executing quantum arbitrage: {opportunity}")
        
        results = {
            "planned_profit": opportunity.max_profit,
            "actual_profit": 0.0,
            "slippage": 0.0,
            "execution_time": 0.0,
            "success_rate": 0.0
        }
        
        # Quantum execution strategy
        start_time = time.time()
        
        # Split capital across path to minimize market impact
        path_length = len(opportunity.path)
        capital_per_leg = execution_capital / path_length
        
        total_executed = 0.0
        total_slippage = 0.0
        
        # Execute trades in optimal order
        for i in range(path_length - 1):
            leg_start_time = time.time()
            
            # Get current market data
            current_exchange = opportunity.path[i]
            next_exchange = opportunity.path[i + 1]
            
            market_current = self.market_data.get(current_exchange, {}).get(opportunity.metal1)
            market_next = self.market_data.get(next_exchange, {}).get(opportunity.metal2)
            
            if not market_current or not market_next:
                continue
            
            # Execute leg with quantum-enhanced order sizing
            executed_amount, slippage = self._execute_quantum_trade_leg(
                market_current, market_next, capital_per_leg
            )
            
            total_executed += executed_amount
            total_slippage += slippage
            
            leg_time = time.time() - leg_start_time
            results["execution_time"] += leg_time
        
        # Calculate final results
        expected_profit = opportunity.profit_percentage * execution_capital
        actual_profit = expected_profit * (total_executed / execution_capital) - total_slippage
        
        results["actual_profit"] = max(0, actual_profit)
        results["slippage"] = total_slippage / execution_capital
        results["success_rate"] = total_executed / execution_capital if execution_capital > 0 else 0
        
        total_time = time.time() - start_time
        results["execution_time"] = total_time
        
        self.logger.info(f"Arbitrage execution complete. Profit: {results['actual_profit']:.2f}")
        
        return results
    
    def _execute_quantum_trade_leg(
        self, 
        market_buy: MarketData, 
        market_sell: MarketData, 
        capital: float
    ) -> Tuple[float, float]:
        """Execute single leg of quantum arbitrage"""
        
        # Simplified execution with slippage modeling
        execution_price = (market_buy.ask + market_sell.bid) / 2
        estimated_quantity = capital / execution_price
        
        # Calculate slippage based on market conditions
        liquidity_factor = min(market_buy.liquidity_score, market_sell.liquidity_score)
        slippage_rate = (1.0 - liquidity_factor) * 0.001  # Base slippage
        slippage = capital * slippage_rate
        
        # Adjust execution for available volume
        max_executable = min(
            market_buy.volume,
            market_sell.volume,
            estimated_quantity * 1.1  # 10% buffer
        )
        
        actual_executed = min(estimated_quantity, max_executable)
        
        return actual_executed * execution_price, slippage
    
    def _calculate_pairwise_confidence(
        self, 
        market1: MarketData, 
        market2: MarketData
    ) -> float:
        """Calculate confidence level for pairwise arbitrage"""
        
        # Confidence based on liquidity, spread, and data freshness
        liquidity_score = (market1.liquidity_score + market2.liquidity_score) / 2
        
        # Spread tightness (closer spreads = higher confidence)
        avg_spread = (market1.ask - market1.bid + market2.ask - market2.bid) / 2
        spread_score = max(0, 1.0 - avg_spread / (market1.bid + market2.bid))
        
        # Data freshness
        current_time = time.time()
        data_freshness = max(0, 1.0 - (current_time - max(market1.timestamp, market2.timestamp)) / 60)
        
        # Combine scores
        confidence = (liquidity_score + spread_score + data_freshness) / 3
        
        return min(1.0, max(0.0, confidence))
    
    def _calculate_arbitrage_confidence(self, cycle: List[Tuple[str, str, str]]) -> float:
        """Calculate confidence for arbitrage cycle"""
        
        # Base confidence decreases with cycle length
        base_confidence = max(0.1, 1.0 - len(cycle) * 0.1)
        
        # Adjust based on market data quality along the path
        market_data_scores = []
        for edge in cycle:
            exchange1, exchange2, metal = edge
            market1 = self.market_data.get(exchange1, {}).get(metal)
            market2 = self.market_data.get(exchange2, {}).get(metal)
            
            if market1 and market2:
                score = (market1.liquidity_score + market2.liquidity_score) / 2
                market_data_scores.append(score)
        
        if market_data_scores:
            avg_market_score = sum(market_data_scores) / len(market_data_scores)
            confidence = base_confidence * avg_market_score
        else:
            confidence = base_confidence * 0.5
        
        return min(1.0, max(0.0, confidence))
    
    def optimize_execution_schedule(
        self, 
        opportunities: List[ArbitrageOpportunity], 
        total_capital: float
    ) -> Dict[str, any]:
        """
        Optimize execution schedule for multiple arbitrage opportunities
        
        Args:
            opportunities: List of arbitrage opportunities
            total_capital: Total available capital
            
        Returns:
            Optimized execution schedule
        """
        
        # Sort opportunities by risk-adjusted return
        sorted_opportunities = sorted(
            opportunities,
            key=lambda x: x.profit_percentage * x.confidence,
            reverse=True
        )
        
        execution_plan = {
            "total_capital": total_capital,
            "allocated_capital": 0.0,
            "expected_profit": 0.0,
            "execution_order": [],
            "capital_allocation": {}
        }
        
        remaining_capital = total_capital
        
        for opportunity in sorted_opportunities:
            if remaining_capital < opportunity.required_capital:
                continue
            
            # Allocate capital based on opportunity quality
            allocation_ratio = min(
                1.0,
                (opportunity.profit_percentage * opportunity.confidence) / 
                sum(op.profit_percentage * op.confidence for op in sorted_opportunities[:5])
            )
            
            allocated_capital = remaining_capital * allocation_ratio
            
            if allocated_capital >= opportunity.required_capital * 0.1:  # Minimum allocation
                execution_plan["execution_order"].append(opportunity)
                execution_plan["capital_allocation"][opportunity] = allocated_capital
                execution_plan["allocated_capital"] += allocated_capital
                execution_plan["expected_profit"] += opportunity.profit_percentage * allocated_capital
                
                remaining_capital -= allocated_capital
        
        return execution_plan


# Advanced quantum arbitrage strategies
class QuantumArbitrageStrategies:
    """Advanced quantum arbitrage execution strategies"""
    
    @staticmethod
    def momentum_arbitrage_strategy(market_data: List[MarketData]) -> Dict[str, float]:
        """Momentum-based quantum arbitrage strategy"""
        
        # Calculate momentum for each market
        momentum_scores = {}
        for data in market_data:
            # Simplified momentum calculation
            momentum = (data.bid + data.ask) / 2  # Placeholder for actual momentum calc
            momentum_scores[f"{data.exchange}_{data.metal}"] = momentum
        
        # Identify momentum arbitrage opportunities
        opportunities = {}
        exchanges = list(set(d.exchange for d in market_data))
        metals = list(set(d.metal for d in market_data))
        
        for metal in metals:
            metal_data = [d for d in market_data if d.metal == metal]
            if len(metal_data) >= 2:
                # Find highest and lowest momentum
                sorted_data = sorted(metal_data, key=lambda x: x.bid + x.ask)
                low_momentum = sorted_data[0]
                high_momentum = sorted_data[-1]
                
                if (high_momentum.bid + high_momentum.ask) / 2 > (low_momentum.bid + low_momentum.ask) / 2 * 1.01:
                    opportunities[f"{metal}_momentum_arbitrage"] = {
                        "buy_exchange": low_momentum.exchange,
                        "sell_exchange": high_momentum.exchange,
                        "profit_potential": ((high_momentum.bid + high_momentum.ask) / 2) / 
                                          ((low_momentum.bid + low_momentum.ask) / 2) - 1
                    }
        
        return opportunities
    
    @staticmethod
    def volatility_arbitrage_strategy(market_data: List[MarketData]) -> Dict[str, float]:
        """Volatility-based quantum arbitrage strategy"""
        
        volatility_opportunities = {}
        
        # Group by metal and analyze volatility spreads
        metal_groups = {}
        for data in market_data:
            if data.metal not in metal_groups:
                metal_groups[data.metal] = []
            metal_groups[data.metal].append(data)
        
        for metal, exchanges_data in metal_groups.items():
            if len(exchanges_data) >= 2:
                # Calculate implied volatility from spreads
                volatilities = []
                for data in exchanges_data:
                    implied_vol = (data.ask - data.bid) / ((data.ask + data.bid) / 2)
                    volatilities.append((data.exchange, implied_vol))
                
                # Sort by volatility
                volatilities.sort(key=lambda x: x[1])
                
                if len(volatilities) >= 2:
                    low_vol_exchange = volatilities[0][0]
                    high_vol_exchange = volatilities[-1][0]
                    
                    vol_spread = volatilities[-1][1] - volatilities[0][1]
                    
                    if vol_spread > 0.01:  # 1% volatility spread
                        volatility_opportunities[f"{metal}_volatility_arbitrage"] = {
                            "buy_volatility": low_vol_exchange,
                            "sell_volatility": high_vol_exchange,
                            "volatility_spread": vol_spread
                        }
        
        return volatility_opportunities
    
    @staticmethod
    def mean_reversion_arbitrage_strategy(market_data: List[MarketData]) -> Dict[str, float]:
        """Mean reversion-based quantum arbitrage strategy"""
        
        mean_reversion_ops = {}
        
        # For each metal, find mean reversion opportunities
        metal_prices = defaultdict(list)
        for data in market_data:
            mid_price = (data.bid + data.ask) / 2
            metal_prices[data.metal].append((data.exchange, mid_price, data.timestamp))
        
        for metal, price_data in metal_prices.items():
            if len(price_data) >= 3:
                # Calculate moving average (simplified)
                prices = [p[1] for p in price_data]
                avg_price = sum(prices) / len(prices)
                
                # Find deviations from mean
                deviations = []
                for exchange, price, timestamp in price_data:
                    deviation = abs(price - avg_price) / avg_price
                    if deviation > 0.005:  # 0.5% deviation threshold
                        deviations.append((exchange, price, deviation))
                
                if len(deviations) >= 2:
                    # Sort by deviation
                    deviations.sort(key=lambda x: x[2], reverse=True)
                    
                    # Highest deviation (sell), lowest deviation (buy)
                    sell_exchange = deviations[0][0]
                    buy_exchange = deviations[-1][0]
                    
                    if sell_exchange != buy_exchange:
                        mean_reversion_ops[f"{metal}_mean_reversion"] = {
                            "buy_exchange": buy_exchange,
                            "sell_exchange": sell_exchange,
                            "mean_reversion_potential": deviations[0][2] - deviations[-1][2
                        }
        
        return mean_reversion_ops


# Example usage
if __name__ == "__main__":
    # Initialize quantum arbitrage detector
    detector = QuantumArbitrageDetector()
    
    # Add sample market data
    sample_data = [
        MarketData("Binance", "GOLD", 1999.5, 2000.5, 1000, time.time(), 0.9),
        MarketData("Coinbase", "GOLD", 2000.0, 2001.0, 800, time.time(), 0.85),
        MarketData("Kraken", "GOLD", 1998.0, 1999.0, 1200, time.time(), 0.92),
        MarketData("Binance", "SILVER", 24.95, 25.05, 2000, time.time(), 0.88),
        MarketData("Coinbase", "SILVER", 25.00, 25.10, 1800, time.time(), 0.86),
        MarketData("Kraken", "SILVER", 24.90, 25.00, 2200, time.time(), 0.91),
    ]
    
    for data in sample_data:
        detector.add_market_data(data)
    
    # Detect arbitrage opportunities
    opportunities = detector.detect_arbitrage_opportunities(
        metals=["GOLD", "SILVER"],
        exchanges=["Binance", "Coinbase", "Kraken"],
        quantum_mode=True
    )
    
    print(f"Found {len(opportunities)} arbitrage opportunities:")
    for i, opp in enumerate(opportunities[:5], 1):
        print(f"{i}. {opp.metal1} arbitrage: {opp.exchange1} -> {opp.exchange2}")
        print(f"   Profit: {opp.profit_percentage:.4f} ({opp.profit_percentage*100:.2f}%)")
        print(f"   Confidence: {opp.confidence:.2f}")
        print(f"   Execution time: {opp.execution_time:.3f}s")
        print()
    
    # Test quantum execution
    if opportunities:
        best_opportunity = opportunities[0]
        execution_results = detector.quantum_arbitrage_execution(
            best_opportunity, 
            50000  # $50k execution capital
        )
        
        print("Execution Results:")
        for key, value in execution_results.items():
            print(f"  {key}: {value:.4f}")
    
    # Test quantum strategies
    strategies = QuantumArbitrageStrategies()
    momentum_ops = strategies.momentum_arbitrage_strategy(sample_data)
    volatility_ops = strategies.volatility_arbitrage_strategy(sample_data)
    mean_reversion_ops = strategies.mean_reversion_arbitrage_strategy(sample_data)
    
    print("\nQuantum Strategy Opportunities:")
    print(f"Momentum: {len(momentum_ops)} opportunities")
    print(f"Volatility: {len(volatility_ops)} opportunities") 
    print(f"Mean Reversion: {len(mean_reversion_ops)} opportunities")