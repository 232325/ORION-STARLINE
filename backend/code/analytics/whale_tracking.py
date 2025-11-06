"""
Whale Tracking System
On-chain analytics, large transaction detection, whale movement monitoring
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import aiohttp
from decimal import Decimal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WhaleTransaction:
    """Whale transaction ma'lumotlari"""
    tx_hash: str
    blockchain: str
    from_address: str
    to_address: str
    token: str
    amount: Decimal
    usd_value: Decimal
    timestamp: datetime
    tx_type: str  # 'transfer', 'swap', 'deposit', 'withdrawal'
    exchange: Optional[str] = None
    is_whale: bool = False
    whale_score: float = 0.0


@dataclass
class WhaleWallet:
    """Whale wallet profili"""
    address: str
    blockchain: str
    total_balance_usd: Decimal
    tokens: Dict[str, Decimal]
    transaction_count: int
    first_seen: datetime
    last_activity: datetime
    whale_rank: str  # 'mega', 'large', 'medium'
    labels: List[str]  # ['exchange', 'dex', 'institutional', etc]


class WhaleTracker:
    """Whale tracking va monitoring tizimi"""
    
    def __init__(
        self,
        whale_threshold_usd: Decimal = Decimal('100000'),
        mega_whale_threshold: Decimal = Decimal('1000000'),
        min_balance_tracking: Decimal = Decimal('50000')
    ):
        self.whale_threshold = whale_threshold_usd
        self.mega_whale_threshold = mega_whale_threshold
        self.min_balance_tracking = min_balance_tracking
        
        self.tracked_whales: Dict[str, WhaleWallet] = {}
        self.recent_transactions: List[WhaleTransaction] = []
        self.alert_subscribers: List[callable] = []
        
        # Blockchain explorers API endpoints
        self.explorers = {
            'ethereum': 'https://api.etherscan.io/api',
            'bsc': 'https://api.bscscan.com/api',
            'polygon': 'https://api.polygonscan.com/api',
            'avalanche': 'https://api.snowtrace.io/api',
            'arbitrum': 'https://api.arbiscan.io/api'
        }
        
        # Exchange addresses (known whale addresses)
        self.exchange_addresses = {
            'binance': ['0x...', '0x...'],  # Placeholder
            'coinbase': ['0x...'],
            'kraken': ['0x...'],
            'okx': ['0x...'],
        }
        
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """Tracker'ni boshlash"""
        self.session = aiohttp.ClientSession()
        logger.info("Whale Tracker initialized")
    
    async def cleanup(self):
        """Resurslarni tozalash"""
        if self.session:
            await self.session.close()
    
    async def track_blockchain(
        self,
        blockchain: str,
        tokens: Optional[List[str]] = None
    ) -> List[WhaleTransaction]:
        """Blockchain'dagi whale transactionlarni kuzatish"""
        try:
            if blockchain not in self.explorers:
                raise ValueError(f"Unsupported blockchain: {blockchain}")
            
            # Get latest blocks
            latest_block = await self._get_latest_block(blockchain)
            
            # Scan recent transactions
            whale_txs = []
            for block_num in range(latest_block - 10, latest_block + 1):
                block_txs = await self._scan_block(blockchain, block_num, tokens)
                whale_txs.extend(block_txs)
            
            # Analyze and classify
            for tx in whale_txs:
                await self._analyze_transaction(tx)
            
            self.recent_transactions.extend(whale_txs)
            
            # Trigger alerts
            await self._trigger_alerts(whale_txs)
            
            logger.info(f"Found {len(whale_txs)} whale transactions on {blockchain}")
            return whale_txs
            
        except Exception as e:
            logger.error(f"Error tracking blockchain {blockchain}: {e}")
            return []
    
    async def _get_latest_block(self, blockchain: str) -> int:
        """Eng oxirgi block raqamini olish"""
        try:
            # Simulate API call
            await asyncio.sleep(0.1)
            return 18500000  # Placeholder
            
        except Exception as e:
            logger.error(f"Error getting latest block: {e}")
            return 0
    
    async def _scan_block(
        self,
        blockchain: str,
        block_num: int,
        tokens: Optional[List[str]] = None
    ) -> List[WhaleTransaction]:
        """Blockdagi transactionlarni scan qilish"""
        try:
            whale_txs = []
            
            # Simulate block scanning
            await asyncio.sleep(0.1)
            
            # In real implementation, call blockchain API
            # Parse transactions, filter by value threshold
            
            return whale_txs
            
        except Exception as e:
            logger.error(f"Error scanning block {block_num}: {e}")
            return []
    
    async def _analyze_transaction(self, tx: WhaleTransaction):
        """Transaction tahlili va whale score hisoblash"""
        try:
            # Calculate whale score based on:
            # 1. Transaction value
            # 2. Wallet history
            # 3. Address labels
            # 4. Transaction pattern
            
            score = 0.0
            
            # Value score (0-40 points)
            if tx.usd_value >= self.mega_whale_threshold:
                score += 40
            elif tx.usd_value >= self.whale_threshold:
                score += 20 + (float(tx.usd_value) / float(self.mega_whale_threshold)) * 20
            
            # Wallet history score (0-30 points)
            from_wallet = await self._get_wallet_info(tx.from_address, tx.blockchain)
            if from_wallet:
                if from_wallet.total_balance_usd >= self.mega_whale_threshold:
                    score += 30
                elif from_wallet.total_balance_usd >= self.whale_threshold:
                    score += 15
            
            # Label score (0-30 points)
            if from_wallet and 'institutional' in from_wallet.labels:
                score += 30
            elif from_wallet and 'exchange' in from_wallet.labels:
                score += 20
            
            tx.whale_score = score
            tx.is_whale = score >= 50
            
        except Exception as e:
            logger.error(f"Error analyzing transaction: {e}")
    
    async def _get_wallet_info(
        self,
        address: str,
        blockchain: str
    ) -> Optional[WhaleWallet]:
        """Wallet ma'lumotlarini olish"""
        try:
            # Check cache
            cache_key = f"{blockchain}:{address}"
            if cache_key in self.tracked_whales:
                return self.tracked_whales[cache_key]
            
            # Fetch wallet data
            await asyncio.sleep(0.1)  # Simulate API call
            
            # In real implementation:
            # - Get wallet balance
            # - Get transaction history
            # - Identify labels
            
            wallet = WhaleWallet(
                address=address,
                blockchain=blockchain,
                total_balance_usd=Decimal('0'),
                tokens={},
                transaction_count=0,
                first_seen=datetime.now(),
                last_activity=datetime.now(),
                whale_rank='medium',
                labels=[]
            )
            
            # Cache wallet
            self.tracked_whales[cache_key] = wallet
            
            return wallet
            
        except Exception as e:
            logger.error(f"Error getting wallet info: {e}")
            return None
    
    async def track_whale_wallet(
        self,
        address: str,
        blockchain: str
    ) -> Optional[WhaleWallet]:
        """Muayyan whale wallet'ni kuzatish"""
        try:
            wallet = await self._get_wallet_info(address, blockchain)
            
            if not wallet:
                return None
            
            # Get recent transactions
            recent_txs = await self._get_wallet_transactions(address, blockchain)
            
            # Update wallet info
            wallet.last_activity = datetime.now()
            wallet.transaction_count = len(recent_txs)
            
            # Classify whale rank
            if wallet.total_balance_usd >= self.mega_whale_threshold:
                wallet.whale_rank = 'mega'
            elif wallet.total_balance_usd >= self.whale_threshold:
                wallet.whale_rank = 'large'
            else:
                wallet.whale_rank = 'medium'
            
            logger.info(f"Tracking whale {address[:10]}... on {blockchain}")
            return wallet
            
        except Exception as e:
            logger.error(f"Error tracking whale wallet: {e}")
            return None
    
    async def _get_wallet_transactions(
        self,
        address: str,
        blockchain: str,
        limit: int = 100
    ) -> List[WhaleTransaction]:
        """Wallet transactionlarini olish"""
        try:
            await asyncio.sleep(0.1)  # Simulate API call
            
            # In real implementation:
            # - Call blockchain API
            # - Parse transaction history
            # - Filter by relevance
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting wallet transactions: {e}")
            return []
    
    async def detect_whale_movements(
        self,
        exchanges: List[str],
        time_window_hours: int = 24
    ) -> Dict[str, List[WhaleTransaction]]:
        """Exchange'larga/dan whale movementlarni aniqlash"""
        try:
            movements = {
                'inflow': [],
                'outflow': []
            }
            
            since = datetime.now() - timedelta(hours=time_window_hours)
            
            for tx in self.recent_transactions:
                if tx.timestamp < since:
                    continue
                
                # Check if transaction involves exchange
                to_exchange = self._is_exchange_address(tx.to_address, exchanges)
                from_exchange = self._is_exchange_address(tx.from_address, exchanges)
                
                if to_exchange and tx.usd_value >= self.whale_threshold:
                    tx.exchange = to_exchange
                    movements['inflow'].append(tx)
                
                elif from_exchange and tx.usd_value >= self.whale_threshold:
                    tx.exchange = from_exchange
                    movements['outflow'].append(tx)
            
            logger.info(
                f"Detected {len(movements['inflow'])} inflows, "
                f"{len(movements['outflow'])} outflows"
            )
            
            return movements
            
        except Exception as e:
            logger.error(f"Error detecting whale movements: {e}")
            return {'inflow': [], 'outflow': []}
    
    def _is_exchange_address(
        self,
        address: str,
        exchanges: List[str]
    ) -> Optional[str]:
        """Address exchange'ga tegishli ekanligini tekshirish"""
        for exchange, addresses in self.exchange_addresses.items():
            if exchange not in exchanges:
                continue
            if address.lower() in [a.lower() for a in addresses]:
                return exchange
        return None
    
    async def get_top_whales(
        self,
        blockchain: str,
        token: str,
        limit: int = 100
    ) -> List[WhaleWallet]:
        """Eng yirik whale'larni olish"""
        try:
            # Filter and sort whales
            whales = [
                w for w in self.tracked_whales.values()
                if w.blockchain == blockchain and token in w.tokens
            ]
            
            whales.sort(
                key=lambda x: x.tokens.get(token, Decimal('0')),
                reverse=True
            )
            
            return whales[:limit]
            
        except Exception as e:
            logger.error(f"Error getting top whales: {e}")
            return []
    
    async def analyze_whale_behavior(
        self,
        address: str,
        blockchain: str,
        days: int = 30
    ) -> Dict:
        """Whale xatti-harakatini tahlil qilish"""
        try:
            wallet = await self._get_wallet_info(address, blockchain)
            if not wallet:
                return {}
            
            since = datetime.now() - timedelta(days=days)
            txs = await self._get_wallet_transactions(address, blockchain, limit=1000)
            
            # Filter by time
            recent_txs = [tx for tx in txs if tx.timestamp >= since]
            
            # Analyze patterns
            analysis = {
                'total_transactions': len(recent_txs),
                'total_volume_usd': sum(tx.usd_value for tx in recent_txs),
                'avg_transaction_usd': 0,
                'buy_sell_ratio': 0,
                'most_traded_tokens': {},
                'trading_hours': {},  # Hour of day distribution
                'trading_days': {},   # Day of week distribution
                'exchange_interactions': {}
            }
            
            if recent_txs:
                analysis['avg_transaction_usd'] = (
                    analysis['total_volume_usd'] / len(recent_txs)
                )
            
            # Calculate buy/sell ratio
            buys = sum(1 for tx in recent_txs if tx.tx_type == 'buy')
            sells = sum(1 for tx in recent_txs if tx.tx_type == 'sell')
            if sells > 0:
                analysis['buy_sell_ratio'] = buys / sells
            
            # Token distribution
            for tx in recent_txs:
                token = tx.token
                if token not in analysis['most_traded_tokens']:
                    analysis['most_traded_tokens'][token] = Decimal('0')
                analysis['most_traded_tokens'][token] += tx.amount
            
            # Time patterns
            for tx in recent_txs:
                hour = tx.timestamp.hour
                day = tx.timestamp.strftime('%A')
                
                analysis['trading_hours'][hour] = \
                    analysis['trading_hours'].get(hour, 0) + 1
                analysis['trading_days'][day] = \
                    analysis['trading_days'].get(day, 0) + 1
            
            logger.info(f"Analyzed whale behavior for {address[:10]}...")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing whale behavior: {e}")
            return {}
    
    def subscribe_to_alerts(self, callback: callable):
        """Alert subscription qo'shish"""
        self.alert_subscribers.append(callback)
        logger.info("Added alert subscriber")
    
    async def _trigger_alerts(self, transactions: List[WhaleTransaction]):
        """Alert'larni yuborish"""
        try:
            for tx in transactions:
                if not tx.is_whale:
                    continue
                
                alert_data = {
                    'type': 'whale_transaction',
                    'transaction': tx,
                    'timestamp': datetime.now(),
                    'severity': 'high' if tx.whale_score >= 80 else 'medium'
                }
                
                # Call all subscribers
                for callback in self.alert_subscribers:
                    try:
                        await callback(alert_data)
                    except Exception as e:
                        logger.error(f"Error in alert callback: {e}")
            
        except Exception as e:
            logger.error(f"Error triggering alerts: {e}")
    
    async def get_whale_statistics(self) -> Dict:
        """Whale statistikasini olish"""
        try:
            stats = {
                'total_tracked_whales': len(self.tracked_whales),
                'mega_whales': 0,
                'large_whales': 0,
                'medium_whales': 0,
                'total_usd_tracked': Decimal('0'),
                'recent_transactions_24h': 0,
                'top_blockchains': {},
                'top_tokens': {}
            }
            
            # Count whale categories
            for wallet in self.tracked_whales.values():
                if wallet.whale_rank == 'mega':
                    stats['mega_whales'] += 1
                elif wallet.whale_rank == 'large':
                    stats['large_whales'] += 1
                else:
                    stats['medium_whales'] += 1
                
                stats['total_usd_tracked'] += wallet.total_balance_usd
                
                # Blockchain distribution
                blockchain = wallet.blockchain
                stats['top_blockchains'][blockchain] = \
                    stats['top_blockchains'].get(blockchain, 0) + 1
            
            # Recent transactions
            since_24h = datetime.now() - timedelta(hours=24)
            stats['recent_transactions_24h'] = sum(
                1 for tx in self.recent_transactions
                if tx.timestamp >= since_24h
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting whale statistics: {e}")
            return {}


async def main():
    """Test function"""
    tracker = WhaleTracker(
        whale_threshold_usd=Decimal('100000'),
        mega_whale_threshold=Decimal('1000000')
    )
    
    await tracker.initialize()
    
    try:
        # Track Ethereum blockchain
        whale_txs = await tracker.track_blockchain('ethereum', tokens=['ETH', 'USDT'])
        print(f"Found {len(whale_txs)} whale transactions")
        
        # Detect exchange movements
        movements = await tracker.detect_whale_movements(['binance', 'coinbase'])
        print(f"Inflows: {len(movements['inflow'])}, Outflows: {len(movements['outflow'])}")
        
        # Get statistics
        stats = await tracker.get_whale_statistics()
        print(f"Tracking {stats['total_tracked_whales']} whales")
        print(f"Total USD tracked: ${stats['total_usd_tracked']:,.2f}")
        
    finally:
        await tracker.cleanup()


if __name__ == '__main__':
    asyncio.run(main())
