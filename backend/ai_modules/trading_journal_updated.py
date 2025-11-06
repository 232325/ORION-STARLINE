"""
AI Trading Journal - Asosiy journal funksiyalari
Professional trading journal with AI-powered analysis and insights
"""

import json
import sqlite3
import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import pandas as pd
from pathlib import Path
import logging
import os

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradeType(Enum):
    """Trade turlari"""
    BUY = "buy"
    SELL = "sell"

class EmotionalState(Enum):
    """Emotsional holatlar"""
    CONFIDENT = "confident"
    NERVOUS = "nervous"
    FEARFUL = "fearful"
    GREEDY = "greedy"
    CALM = "calm"
    FRUSTRATED = "frustrated"
    EXCITED = "excited"
    ANXIOUS = "anxious"

class MarketCondition(Enum):
    """Bozor sharoitlari"""
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"
    LOW_VOLATILITY = "low_volatility"
    NEWS_EVENT = "news_event"

@dataclass
class TradeEntry:
    """Trade ma'lumotlari"""
    id: str
    symbol: str
    trade_type: TradeType
    entry_price: float
    exit_price: float
    quantity: float
    entry_time: datetime.datetime
    exit_time: datetime.datetime
    pnl: float
    pnl_percentage: float
    strategy: str
    emotional_state: EmotionalState
    market_condition: MarketCondition
    rationale: str
    lessons_learned: str
    follow_up_actions: str
    strategy_notes: str
    confidence_level: int  # 1-10
    risk_reward_ratio: float
    stop_loss: float
    take_profit: float
    created_at: datetime.datetime
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class PerformanceMetrics:
    """Performance metrikalari"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    average_win: float
    average_loss: float
    largest_win: float
    largest_loss: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float
    total_return: float

class TradingJournal:
    """AI Trading Journal tizimi"""
    
    def __init__(self, db_path: str = "trading_journal.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Database ni boshlash"""
        # Database fayli mavjudligini tekshirish va o'chirish
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Trades jadvalini yaratish
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                trade_type TEXT NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL NOT NULL,
                quantity REAL NOT NULL,
                entry_time TEXT NOT NULL,
                exit_time TEXT NOT NULL,
                pnl REAL NOT NULL,
                pnl_percentage REAL NOT NULL,
                strategy TEXT NOT NULL,
                emotional_state TEXT NOT NULL,
                market_condition TEXT NOT NULL,
                rationale TEXT NOT NULL,
                lessons_learned TEXT NOT NULL,
                follow_up_actions TEXT NOT NULL,
                strategy_notes TEXT NOT NULL,
                confidence_level INTEGER NOT NULL,
                risk_reward_ratio REAL NOT NULL,
                stop_loss REAL NOT NULL,
                take_profit REAL NOT NULL,
                created_at TEXT NOT NULL,
                tags TEXT
            )
        ''')
        
        # Performance metrics jadvalini yaratish
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                total_trades INTEGER NOT NULL,
                winning_trades INTEGER NOT NULL,
                losing_trades INTEGER NOT NULL,
                win_rate REAL NOT NULL,
                total_pnl REAL NOT NULL,
                average_win REAL NOT NULL,
                average_loss REAL NOT NULL,
                largest_win REAL NOT NULL,
                largest_loss REAL NOT NULL,
                profit_factor REAL NOT NULL,
                sharpe_ratio REAL NOT NULL,
                max_drawdown REAL NOT NULL,
                total_return REAL NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        
        # AI analysis results jadvalini yaratish
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT NOT NULL,
                quality_score REAL NOT NULL,
                mistake_flags TEXT NOT NULL,
                bias_detection TEXT NOT NULL,
                optimization_suggestions TEXT NOT NULL,
                risk_analysis TEXT NOT NULL,
                timing_analysis TEXT NOT NULL,
                portfolio_impact REAL NOT NULL,
                ai_insights TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (trade_id) REFERENCES trades (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Trading journal database initialized")
    
    def add_trade(self, trade: TradeEntry) -> bool:
        """Trade qo'shish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO trades (
                    id, symbol, trade_type, entry_price, exit_price, quantity,
                    entry_time, exit_time, pnl, pnl_percentage, strategy,
                    emotional_state, market_condition, rationale, lessons_learned,
                    follow_up_actions, strategy_notes, confidence_level,
                    risk_reward_ratio, stop_loss, take_profit, created_at, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade.id, trade.symbol, trade.trade_type.value,
                trade.entry_price, trade.exit_price, trade.quantity,
                trade.entry_time.isoformat(), trade.exit_time.isoformat(),
                trade.pnl, trade.pnl_percentage, trade.strategy,
                trade.emotional_state.value, trade.market_condition.value,
                trade.rationale, trade.lessons_learned, trade.follow_up_actions,
                trade.strategy_notes, trade.confidence_level, trade.risk_reward_ratio,
                trade.stop_loss, trade.take_profit, trade.created_at.isoformat(),
                json.dumps(trade.tags)
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Trade added successfully: {trade.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding trade: {e}")
            return False
    
    def get_trade(self, trade_id: str) -> Optional[TradeEntry]:
        """Trade olish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM trades WHERE id = ?', (trade_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self._row_to_trade_entry(row)
            return None
            
        except Exception as e:
            logger.error(f"Error getting trade: {e}")
            return None
    
    def get_all_trades(self) -> List[TradeEntry]:
        """Barcha tradelarni olish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM trades ORDER BY entry_time DESC')
            rows = cursor.fetchall()
            conn.close()
            
            return [self._row_to_trade_entry(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting trades: {e}")
            return []
    
    def get_trades_by_symbol(self, symbol: str) -> List[TradeEntry]:
        """Symbol bo'yicha tradelarni filtrlash"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM trades WHERE symbol = ? ORDER BY entry_time DESC', (symbol,))
            rows = cursor.fetchall()
            conn.close()
            
            return [self._row_to_trade_entry(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting trades by symbol: {e}")
            return []
    
    def get_trades_by_date_range(self, start_date: datetime.datetime, 
                                end_date: datetime.datetime) -> List[TradeEntry]:
        """Sana oralig'idagi tradelarni olish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM trades 
                WHERE entry_time >= ? AND entry_time <= ? 
                ORDER BY entry_time DESC
            ''', (start_date.isoformat(), end_date.isoformat()))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [self._row_to_trade_entry(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting trades by date range: {e}")
            return []
    
    def calculate_performance_metrics(self, trades: List[TradeEntry] = None) -> PerformanceMetrics:
        """Performance metrikalarni hisoblash"""
        if trades is None:
            trades = self.get_all_trades()
        
        if not trades:
            return PerformanceMetrics(0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        
        # Basic metrics
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.pnl > 0])
        losing_trades = len([t for t in trades if t.pnl < 0])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        # P&L metrics
        total_pnl = sum(t.pnl for t in trades)
        winning_pnls = [t.pnl for t in trades if t.pnl > 0]
        losing_pnls = [t.pnl for t in trades if t.pnl < 0]
        
        average_win = np.mean(winning_pnls) if winning_pnls else 0.0
        average_loss = np.mean(losing_pnls) if losing_pnls else 0.0
        largest_win = max(winning_pnls) if winning_pnls else 0.0
        largest_loss = min(losing_pnls) if losing_pnls else 0.0
        
        # Profit factor
        gross_profit = sum(winning_pnls) if winning_pnls else 0.0
        gross_loss = abs(sum(losing_pnls)) if losing_pnls else 0.0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Sharpe ratio (simplified)
        if len(trades) > 1:
            returns = [t.pnl_percentage for t in trades]
            sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0.0
        else:
            sharpe_ratio = 0.0
        
        # Max drawdown
        cumulative_pnl = 0
        peak = 0
        max_drawdown = 0
        
        for trade in sorted(trades, key=lambda x: x.entry_time):
            cumulative_pnl += trade.pnl
            if cumulative_pnl > peak:
                peak = cumulative_pnl
            drawdown = peak - cumulative_pnl
            max_drawdown = max(max_drawdown, drawdown)
        
        # Total return (percentage)
        if trades:
            total_return = (total_pnl / abs(sum(t.entry_price * t.quantity for t in trades))) * 100
        else:
            total_return = 0.0
        
        return PerformanceMetrics(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_pnl=total_pnl,
            average_win=average_win,
            average_loss=average_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            total_return=total_return
        )
    
    def save_performance_metrics(self, metrics: PerformanceMetrics) -> bool:
        """Performance metrikalarni saqlash"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_metrics (
                    date, total_trades, winning_trades, losing_trades, win_rate,
                    total_pnl, average_win, average_loss, largest_win, largest_loss,
                    profit_factor, sharpe_ratio, max_drawdown, total_return, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.datetime.now().date().isoformat(),
                metrics.total_trades, metrics.winning_trades, metrics.losing_trades,
                metrics.win_rate, metrics.total_pnl, metrics.average_win, metrics.average_loss,
                metrics.largest_win, metrics.largest_loss, metrics.profit_factor,
                metrics.sharpe_ratio, metrics.max_drawdown, metrics.total_return,
                datetime.datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error saving performance metrics: {e}")
            return False
    
    def get_performance_trends(self, days: int = 30) -> Dict[str, Any]:
        """Performance trendlarini olish"""
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        
        trades = self.get_trades_by_date_range(start_date, end_date)
        
        if not trades:
            return {"error": "No trades found in the specified period"}
        
        # Daily performance
        daily_performance = {}
        for trade in trades:
            date = trade.entry_time.date().isoformat()
            if date not in daily_performance:
                daily_performance[date] = {"pnl": 0, "trades": 0}
            daily_performance[date]["pnl"] += trade.pnl
            daily_performance[date]["trades"] += 1
        
        # Weekly performance
        weekly_performance = {}
        for trade in trades:
            week = trade.entry_time.isocalendar()[1]
            year = trade.entry_time.year
            week_key = f"{year}-W{week:02d}"
            if week_key not in weekly_performance:
                weekly_performance[week_key] = {"pnl": 0, "trades": 0}
            weekly_performance[week_key]["pnl"] += trade.pnl
            weekly_performance[week_key]["trades"] += 1
        
        # Symbol performance
        symbol_performance = {}
        for trade in trades:
            if trade.symbol not in symbol_performance:
                symbol_performance[trade.symbol] = {"pnl": 0, "trades": 0}
            symbol_performance[trade.symbol]["pnl"] += trade.pnl
            symbol_performance[trade.symbol]["trades"] += 1
        
        # Strategy performance
        strategy_performance = {}
        for trade in trades:
            if trade.strategy not in strategy_performance:
                strategy_performance[trade.strategy] = {"pnl": 0, "trades": 0}
            strategy_performance[trade.strategy]["pnl"] += trade.pnl
            strategy_performance[trade.strategy]["trades"] += 1
        
        return {
            "period_days": days,
            "total_trades": len(trades),
            "daily_performance": daily_performance,
            "weekly_performance": weekly_performance,
            "symbol_performance": symbol_performance,
            "strategy_performance": strategy_performance,
            "total_pnl": sum(t.pnl for t in trades)
        }
    
    def export_trades_to_csv(self, file_path: str, trades: List[TradeEntry] = None) -> bool:
        """Tradelarni CSV ga eksport qilish"""
        if trades is None:
            trades = self.get_all_trades()
        
        if not trades:
            return False
        
        try:
            data = []
            for trade in trades:
                data.append({
                    "ID": trade.id,
                    "Symbol": trade.symbol,
                    "Type": trade.trade_type.value,
                    "Entry_Price": trade.entry_price,
                    "Exit_Price": trade.exit_price,
                    "Quantity": trade.quantity,
                    "Entry_Time": trade.entry_time.isoformat(),
                    "Exit_Time": trade.exit_time.isoformat(),
                    "P&L": trade.pnl,
                    "P&L_%": trade.pnl_percentage,
                    "Strategy": trade.strategy,
                    "Emotional_State": trade.emotional_state.value,
                    "Market_Condition": trade.market_condition.value,
                    "Confidence_Level": trade.confidence_level,
                    "Risk_Reward_Ratio": trade.risk_reward_ratio
                })
            
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)
            logger.info(f"Trades exported to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting trades: {e}")
            return False
    
    def _row_to_trade_entry(self, row) -> TradeEntry:
        """Database row ni TradeEntry ga aylantirish"""
        return TradeEntry(
            id=row[0],
            symbol=row[1],
            trade_type=TradeType(row[2]),
            entry_price=row[3],
            exit_price=row[4],
            quantity=row[5],
            entry_time=datetime.datetime.fromisoformat(row[6]),
            exit_time=datetime.datetime.fromisoformat(row[7]),
            pnl=row[8],
            pnl_percentage=row[9],
            strategy=row[10],
            emotional_state=EmotionalState(row[11]),
            market_condition=MarketCondition(row[12]),
            rationale=row[13],
            lessons_learned=row[14],
            follow_up_actions=row[15],
            strategy_notes=row[16],
            confidence_level=row[17],
            risk_reward_ratio=row[18],
            stop_loss=row[19],
            take_profit=row[20],
            created_at=datetime.datetime.fromisoformat(row[21]),
            tags=json.loads(row[22]) if row[22] else []
        )
    
    def get_recent_trades(self, limit: int = 10) -> List[TradeEntry]:
        """So'nggi tradelarni olish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM trades ORDER BY entry_time DESC LIMIT ?', (limit,))
            rows = cursor.fetchall()
            conn.close()
            
            return [self._row_to_trade_entry(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting recent trades: {e}")
            return []