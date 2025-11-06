"""
Arbitrage Bot - CEX/DEX Cross-Exchange Arbitrage Detection & Execution
============================================================================

Bu modul turli birjalar (CEX va DEX) orasidagi narx farqlarini aniqlaydi va 
arbitraj imkoniyatlarini avtomatik ravishda bajaradi.

Asosiy xususiyatlar:
- Real-time narx monitoring
- Multi-exchange support (Binance, Coinbase, Uniswap, PancakeSwap)
- Triangle arbitrage detection
- Gas fee optimization (DEX uchun)
- Slippage calculation
- Profit threshold filtering
"""

import asyncio
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from decimal import Decimal
import logging
from datetime import datetime
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ArbitrageOpportunity:
    """Arbitraj imkoniyati ma'lumotlari"""
    exchange_from: str
    exchange_to: str
    symbol: str
    price_from: float
    price_to: float
    profit_percentage: float
    volume_available: float
    timestamp: datetime
    execution_cost: float  # Gas fees, trading fees
    net_profit: float


@dataclass
class ExchangeConfig:
    """Birja konfiguratsiyasi"""
    name: str
    api_key: str
    api_secret: str
    is_dex: bool
    trading_fee: float  # Percentage
    withdrawal_fee: float


class ArbitrageBot:
    """
    Cross-exchange arbitrage bot
    
    Attributes:
        exchanges: Monitoring qilinadigan birjalar ro'yxati
        min_profit_threshold: Minimal foyda chegarasi (%)
        max_slippage: Maksimal slippage (%)
        check_interval: Narxlarni tekshirish intervali (soniya)
    """
    
    def __init__(
        self,
        exchanges: List[ExchangeConfig],
        min_profit_threshold: float = 0.5,
        max_slippage: float = 0.3,
        check_interval: int = 1
    ):
        self.exchanges = exchanges
        self.min_profit_threshold = min_profit_threshold
        self.max_slippage = max_slippage
        self.check_interval = check_interval
        self.running = False
        
        # Price cache
        self.price_cache: Dict[str, Dict[str, float]] = {}
        
        # Arbitrage history
        self.opportunities_found: List[ArbitrageOpportunity] = []
        self.executed_trades: List[Dict] = []
        
        logger.info(f"ArbitrageBot initialized with {len(exchanges)} exchanges")
        
    async def fetch_price(self, exchange: str, symbol: str) -> Optional[float]:
        """
        Birjadan narxni olish (async)
        
        Args:
            exchange: Birja nomi
            symbol: Trading juftligi (masalan, 'BTC/USDT')
            
        Returns:
            Joriy narx yoki None
        """
        # Real implementation: API call to exchange
        # Bu yerda mock data ishlatamiz
        try:
            # Simulate API latency
            await asyncio.sleep(0.1)
            
            # Mock price with random fluctuation
            base_prices = {
                'BTC/USDT': 45000,
                'ETH/USDT': 3000,
                'BNB/USDT': 350,
                'SOL/USDT': 110
            }
            
            if symbol in base_prices:
                # Add random variation for different exchanges
                base = base_prices[symbol]
                variation = np.random.uniform(-0.5, 0.5)  # ±0.5%
                price = base * (1 + variation / 100)
                
                return round(price, 2)
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching price from {exchange} for {symbol}: {e}")
            return None
    
    async def fetch_all_prices(self, symbols: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Barcha birjalardan narxlarni parallel ravishda olish
        
        Args:
            symbols: Trading juftliklari ro'yxati
            
        Returns:
            {exchange: {symbol: price}} strukturasida ma'lumotlar
        """
        tasks = []
        for exchange in self.exchanges:
            for symbol in symbols:
                tasks.append(self.fetch_price(exchange.name, symbol))
        
        results = await asyncio.gather(*tasks)
        
        # Organize results
        prices = {}
        idx = 0
        for exchange in self.exchanges:
            prices[exchange.name] = {}
            for symbol in symbols:
                if results[idx] is not None:
                    prices[exchange.name][symbol] = results[idx]
                idx += 1
        
        self.price_cache = prices
        return prices
    
    def calculate_arbitrage_profit(
        self,
        price_buy: float,
        price_sell: float,
        amount: float,
        exchange_from: ExchangeConfig,
        exchange_to: ExchangeConfig
    ) -> Tuple[float, float]:
        """
        Arbitraj foydani hisoblash
        
        Args:
            price_buy: Sotib olish narxi
            price_sell: Sotish narxi
            amount: Trading hajmi
            exchange_from: Sotib olish birjasi
            exchange_to: Sotish birjasi
            
        Returns:
            (foyda_foizi, sof_foyda)
        """
        # Buy cost
        buy_cost = amount * price_buy
        buy_fee = buy_cost * (exchange_from.trading_fee / 100)
        total_buy_cost = buy_cost + buy_fee
        
        # Sell revenue
        sell_revenue = amount * price_sell
        sell_fee = sell_revenue * (exchange_to.trading_fee / 100)
        total_sell_revenue = sell_revenue - sell_fee
        
        # Withdrawal/transfer cost
        transfer_cost = exchange_from.withdrawal_fee
        
        # Calculate profit
        net_profit = total_sell_revenue - total_buy_cost - transfer_cost
        profit_percentage = (net_profit / total_buy_cost) * 100
        
        return profit_percentage, net_profit
    
    def detect_simple_arbitrage(
        self,
        symbol: str,
        prices: Dict[str, Dict[str, float]]
    ) -> List[ArbitrageOpportunity]:
        """
        Oddiy arbitraj imkoniyatlarini aniqlash (A -> B)
        
        Args:
            symbol: Trading juftligi
            prices: Narxlar ma'lumoti
            
        Returns:
            Arbitraj imkoniyatlari ro'yxati
        """
        opportunities = []
        
        # Compare all exchange pairs
        exchanges_with_price = [
            (ex, prices[ex.name].get(symbol)) 
            for ex in self.exchanges 
            if ex.name in prices and symbol in prices[ex.name]
        ]
        
        for i, (ex_from, price_from) in enumerate(exchanges_with_price):
            for ex_to, price_to in exchanges_with_price[i+1:]:
                if price_from is None or price_to is None:
                    continue
                
                # Check both directions
                for buy_ex, buy_price, sell_ex, sell_price in [
                    (ex_from, price_from, ex_to, price_to),
                    (ex_to, price_to, ex_from, price_from)
                ]:
                    if sell_price > buy_price:
                        # Potential arbitrage
                        test_amount = 1.0  # Test with 1 unit
                        profit_pct, net_profit = self.calculate_arbitrage_profit(
                            buy_price, sell_price, test_amount, buy_ex, sell_ex
                        )
                        
                        if profit_pct >= self.min_profit_threshold:
                            opportunity = ArbitrageOpportunity(
                                exchange_from=buy_ex.name,
                                exchange_to=sell_ex.name,
                                symbol=symbol,
                                price_from=buy_price,
                                price_to=sell_price,
                                profit_percentage=profit_pct,
                                volume_available=test_amount,
                                timestamp=datetime.now(),
                                execution_cost=buy_ex.trading_fee + sell_ex.trading_fee,
                                net_profit=net_profit
                            )
                            opportunities.append(opportunity)
        
        return opportunities
    
    def detect_triangle_arbitrage(
        self,
        base_currency: str = 'USDT'
    ) -> List[ArbitrageOpportunity]:
        """
        Triangle arbitrage detection (A -> B -> C -> A)
        
        Args:
            base_currency: Bazaviy valyuta
            
        Returns:
            Triangle arbitrage imkoniyatlari
        """
        opportunities = []
        
        # Triangle paths: USDT -> BTC -> ETH -> USDT
        triangles = [
            ('BTC/USDT', 'ETH/BTC', 'ETH/USDT'),
            ('BNB/USDT', 'BTC/BNB', 'BTC/USDT'),
            ('SOL/USDT', 'ETH/SOL', 'ETH/USDT'),
        ]
        
        for exchange in self.exchanges:
            ex_prices = self.price_cache.get(exchange.name, {})
            
            for path in triangles:
                # Check if all pairs exist
                if all(pair in ex_prices for pair in path):
                    p1, p2, p3 = [ex_prices[pair] for pair in path]
                    
                    # Calculate triangle return
                    # Start with 100 USDT
                    amount = 100
                    
                    # Step 1: USDT -> BTC
                    btc_amount = amount / p1
                    
                    # Step 2: BTC -> ETH
                    eth_amount = btc_amount / p2
                    
                    # Step 3: ETH -> USDT
                    final_usdt = eth_amount * p3
                    
                    # Calculate profit
                    profit = final_usdt - amount
                    profit_pct = (profit / amount) * 100
                    
                    # Account for fees (3 trades)
                    total_fees = 3 * exchange.trading_fee
                    net_profit_pct = profit_pct - total_fees
                    
                    if net_profit_pct >= self.min_profit_threshold:
                        opportunity = ArbitrageOpportunity(
                            exchange_from=exchange.name,
                            exchange_to=exchange.name,
                            symbol=f"Triangle: {' -> '.join(path)}",
                            price_from=amount,
                            price_to=final_usdt,
                            profit_percentage=net_profit_pct,
                            volume_available=amount,
                            timestamp=datetime.now(),
                            execution_cost=total_fees,
                            net_profit=profit
                        )
                        opportunities.append(opportunity)
        
        return opportunities
    
    async def execute_arbitrage(
        self,
        opportunity: ArbitrageOpportunity
    ) -> Dict:
        """
        Arbitraj imkoniyatini bajarish
        
        Args:
            opportunity: Bajarilishi kerak bo'lgan arbitraj
            
        Returns:
            Execution natijasi
        """
        logger.info(f"Executing arbitrage: {opportunity.symbol}")
        logger.info(f"  Buy at {opportunity.exchange_from}: {opportunity.price_from}")
        logger.info(f"  Sell at {opportunity.exchange_to}: {opportunity.price_to}")
        logger.info(f"  Expected profit: {opportunity.profit_percentage:.2f}%")
        
        try:
            # Step 1: Buy on exchange_from
            buy_order = await self._place_order(
                exchange=opportunity.exchange_from,
                symbol=opportunity.symbol,
                side='buy',
                amount=opportunity.volume_available,
                price=opportunity.price_from
            )
            
            if not buy_order['success']:
                return {'success': False, 'error': 'Buy order failed'}
            
            # Step 2: Transfer (if different exchanges)
            if opportunity.exchange_from != opportunity.exchange_to:
                transfer = await self._transfer_funds(
                    from_exchange=opportunity.exchange_from,
                    to_exchange=opportunity.exchange_to,
                    amount=opportunity.volume_available
                )
                
                if not transfer['success']:
                    return {'success': False, 'error': 'Transfer failed'}
            
            # Step 3: Sell on exchange_to
            sell_order = await self._place_order(
                exchange=opportunity.exchange_to,
                symbol=opportunity.symbol,
                side='sell',
                amount=opportunity.volume_available,
                price=opportunity.price_to
            )
            
            if not sell_order['success']:
                return {'success': False, 'error': 'Sell order failed'}
            
            # Calculate actual profit
            actual_profit = sell_order['revenue'] - buy_order['cost']
            
            result = {
                'success': True,
                'opportunity': opportunity,
                'buy_order': buy_order,
                'sell_order': sell_order,
                'actual_profit': actual_profit,
                'timestamp': datetime.now()
            }
            
            self.executed_trades.append(result)
            logger.info(f"✅ Arbitrage executed successfully! Profit: ${actual_profit:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Arbitrage execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _place_order(
        self,
        exchange: str,
        symbol: str,
        side: str,
        amount: float,
        price: float
    ) -> Dict:
        """Place order on exchange (mock)"""
        # Simulate order placement
        await asyncio.sleep(0.5)
        
        cost = amount * price
        fee = cost * 0.1 / 100  # 0.1% fee
        
        return {
            'success': True,
            'exchange': exchange,
            'symbol': symbol,
            'side': side,
            'amount': amount,
            'price': price,
            'cost': cost + fee if side == 'buy' else cost,
            'revenue': cost - fee if side == 'sell' else 0,
            'fee': fee
        }
    
    async def _transfer_funds(
        self,
        from_exchange: str,
        to_exchange: str,
        amount: float
    ) -> Dict:
        """Transfer funds between exchanges (mock)"""
        # Simulate transfer time
        await asyncio.sleep(2.0)
        
        return {
            'success': True,
            'from': from_exchange,
            'to': to_exchange,
            'amount': amount
        }
    
    async def monitor_loop(self, symbols: List[str]):
        """
        Asosiy monitoring loop
        
        Args:
            symbols: Monitoring qilinadigan juftliklar
        """
        self.running = True
        logger.info(f"🚀 Arbitrage bot started. Monitoring {len(symbols)} symbols...")
        
        while self.running:
            try:
                # Fetch prices
                prices = await self.fetch_all_prices(symbols)
                
                # Detect simple arbitrage
                all_opportunities = []
                for symbol in symbols:
                    opportunities = self.detect_simple_arbitrage(symbol, prices)
                    all_opportunities.extend(opportunities)
                
                # Detect triangle arbitrage
                triangle_opps = self.detect_triangle_arbitrage()
                all_opportunities.extend(triangle_opps)
                
                # Log opportunities
                if all_opportunities:
                    logger.info(f"🎯 Found {len(all_opportunities)} arbitrage opportunities!")
                    
                    # Sort by profit
                    all_opportunities.sort(key=lambda x: x.profit_percentage, reverse=True)
                    
                    # Show top 3
                    for i, opp in enumerate(all_opportunities[:3], 1):
                        logger.info(f"  #{i}: {opp.symbol}")
                        logger.info(f"      {opp.exchange_from} -> {opp.exchange_to}")
                        logger.info(f"      Profit: {opp.profit_percentage:.2f}%")
                    
                    # Store opportunities
                    self.opportunities_found.extend(all_opportunities)
                    
                    # Auto-execute best opportunity if profit > 1%
                    best = all_opportunities[0]
                    if best.profit_percentage > 1.0:
                        await self.execute_arbitrage(best)
                
                # Wait before next check
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        logger.info("🛑 Arbitrage bot stopped")
    
    def get_statistics(self) -> Dict:
        """Get bot statistics"""
        total_opportunities = len(self.opportunities_found)
        total_executed = len(self.executed_trades)
        
        if total_executed > 0:
            total_profit = sum(t['actual_profit'] for t in self.executed_trades)
            avg_profit = total_profit / total_executed
        else:
            total_profit = 0
            avg_profit = 0
        
        return {
            'total_opportunities_found': total_opportunities,
            'total_trades_executed': total_executed,
            'total_profit': total_profit,
            'average_profit_per_trade': avg_profit,
            'success_rate': (total_executed / total_opportunities * 100) if total_opportunities > 0 else 0
        }


# Example usage
async def main():
    """Test arbitrage bot"""
    # Configure exchanges
    exchanges = [
        ExchangeConfig(
            name='Binance',
            api_key='dummy_key',
            api_secret='dummy_secret',
            is_dex=False,
            trading_fee=0.1,  # 0.1%
            withdrawal_fee=0.0005
        ),
        ExchangeConfig(
            name='Coinbase',
            api_key='dummy_key',
            api_secret='dummy_secret',
            is_dex=False,
            trading_fee=0.15,
            withdrawal_fee=0.001
        ),
        ExchangeConfig(
            name='Uniswap',
            api_key='',
            api_secret='',
            is_dex=True,
            trading_fee=0.3,  # 0.3%
            withdrawal_fee=0.002  # Gas fee equivalent
        )
    ]
    
    # Initialize bot
    bot = ArbitrageBot(
        exchanges=exchanges,
        min_profit_threshold=0.5,  # 0.5% minimum profit
        check_interval=2  # Check every 2 seconds
    )
    
    # Symbols to monitor
    symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT']
    
    # Run for 30 seconds
    try:
        task = asyncio.create_task(bot.monitor_loop(symbols))
        await asyncio.sleep(30)
        bot.stop()
        await task
    except KeyboardInterrupt:
        bot.stop()
    
    # Show statistics
    stats = bot.get_statistics()
    print("\n" + "="*60)
    print("ARBITRAGE BOT STATISTICS")
    print("="*60)
    print(f"Total opportunities found: {stats['total_opportunities_found']}")
    print(f"Total trades executed: {stats['total_trades_executed']}")
    print(f"Total profit: ${stats['total_profit']:.2f}")
    print(f"Average profit per trade: ${stats['average_profit_per_trade']:.2f}")
    print(f"Success rate: {stats['success_rate']:.1f}%")
    print("="*60)


if __name__ == '__main__':
    asyncio.run(main())
