"""
Data Aggregator

Turli manbalardan ma'lumotlarni to'plash va birlashtirish
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

class DataAggregator:
    """
    Ma'lumotlarni to'plash va qayta ishlash
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Data source configurations
        self.data_sources = {
            "market_data": self._fetch_market_data,
            "portfolio_data": self._fetch_portfolio_data,
            "performance_data": self._fetch_performance_data,
            "news_data": self._fetch_news_data
        }
        
        self._is_running = False
        self._data_cache = {}
        self._last_update = {}
    
    async def _fetch_market_data(self) -> Dict[str, Any]:
        """Market data ni olish"""
        # Real implementation da API calls
        return {
            "timestamp": datetime.now(),
            "symbols": ["EURUSD", "GBPUSD", "USDJPY"],
            "prices": {"EURUSD": 1.0945, "GBPUSD": 1.2750, "USDJPY": 149.85},
            "volumes": {"EURUSD": 1000, "GBPUSD": 800, "USDJPY": 600},
            "volatility": {"EURUSD": 0.012, "GBPUSD": 0.015, "USDJPY": 0.008},
            "trends": {"EURUSD": "bullish", "GBPUSD": "bearish", "USDJPY": "neutral"}
        }
    
    async def _fetch_portfolio_data(self) -> Dict[str, Any]:
        """Portfolio data ni olish"""
        return {
            "timestamp": datetime.now(),
            "total_value": 100000.0,
            "positions": [
                {"symbol": "EURUSD", "size": 50000, "pnl": 250.50, "pnl_percent": 0.005},
                {"symbol": "GBPUSD", "size": 30000, "pnl": -120.75, "pnl_percent": -0.004},
                {"symbol": "USDJPY", "size": 20000, "pnl": 85.25, "pnl_percent": 0.004}
            ],
            "cash": 50000.0,
            "leverage": 1.2,
            "risk_metrics": {
                "var_1d": 0.025,
                "max_drawdown": 0.03,
                "sharpe_ratio": 1.5
            }
        }
    
    async def _fetch_performance_data(self) -> Dict[str, Any]:
        """Performance data ni olish"""
        return {
            "timestamp": datetime.now(),
            "daily_returns": 0.0025,
            "weekly_returns": 0.015,
            "monthly_returns": 0.045,
            "ytd_returns": 0.125,
            "win_rate": 0.68,
            "avg_win": 0.012,
            "avg_loss": -0.008,
            "profit_factor": 1.5,
            "maximum_drawdown": 0.032,
            "current_drawdown": 0.008,
            "volatility": 0.15,
            "sharpe_ratio": 1.35
        }
    
    async def _fetch_news_data(self) -> Dict[str, Any]:
        """News data ni olish"""
        return {
            "timestamp": datetime.now(),
            "sentiment_score": 0.65,
            "economic_events": [
                {
                    "event": "FOMC Meeting",
                    "impact": "high",
                    "timestamp": datetime.now() + timedelta(hours=2)
                }
            ],
            "market_sentiment": {
                "bullish": 0.45,
                "bearish": 0.35,
                "neutral": 0.20
            },
            "trending_topics": ["inflation", "interest_rates", "employment"]
        }
    
    async def aggregate_data(self, data_types: List[str]) -> Dict[str, Any]:
        """
        Bir nechta data type larni birlashtirish
        """
        aggregated_data = {
            "timestamp": datetime.now(),
            "data": {}
        }
        
        tasks = []
        for data_type in data_types:
            if data_type in self.data_sources:
                tasks.append(self._get_cached_data(data_type))
            else:
                self.logger.warning(f"Noma'lum data type: {data_type}")
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            data_type = data_types[i]
            if isinstance(result, Exception):
                self.logger.error(f"Data fetch error for {data_type}: {str(result)}")
                aggregated_data["data"][data_type] = {"error": str(result)}
            else:
                aggregated_data["data"][data_type] = result
        
        return aggregated_data
    
    async def _get_cached_data(self, data_type: str) -> Any:
        """Cached data ni olish yoki fetch qilish"""
        cache_key = f"{data_type}_cache"
        cache_duration = self.config.get(f"cache.{data_type}_duration", 60)  # seconds
        
        # Cache check
        if cache_key in self._data_cache and cache_key in self._last_update:
            last_update = self._last_update[cache_key]
            if datetime.now() - last_update < timedelta(seconds=cache_duration):
                return self._data_cache[cache_key]
        
        # Fetch fresh data
        try:
            fresh_data = await self.data_sources[data_type]()
            
            # Cache update
            self._data_cache[cache_key] = fresh_data
            self._last_update[cache_key] = datetime.now()
            
            return fresh_data
            
        except Exception as e:
            self.logger.error(f"Data fetch error for {data_type}: {str(e)}")
            # Return cached data if available
            return self._data_cache.get(cache_key, {"error": str(e)})
    
    def get_latest_data(self, data_type: str) -> Optional[Dict[str, Any]]:
        """Latest cached data ni olish"""
        cache_key = f"{data_type}_cache"
        return self._data_cache.get(cache_key)
    
    def clear_cache(self, data_type: Optional[str] = None):
        """Cache ni tozalash"""
        if data_type:
            cache_key = f"{data_type}_cache"
            self._data_cache.pop(cache_key, None)
            self._last_update.pop(cache_key, None)
        else:
            self._data_cache.clear()
            self._last_update.clear()
    
    async def get_real_time_data(self) -> Dict[str, Any]:
        """Real-time data olish"""
        return await self.aggregate_data(["market_data", "portfolio_data", "performance_data"])
    
    async def get_comprehensive_data(self) -> Dict[str, Any]:
        """Comprehensive data olish"""
        all_types = list(self.data_sources.keys())
        return await self.aggregate_data(all_types)