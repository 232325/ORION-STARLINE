"""
Trade Journal Backend
=====================

Comprehensive trade journaling system.
Trade history, notes, tags, filtering, analytics.

Features:
- Trade logging with notes
- Tags and categories
- Advanced filtering
- Search functionality
- Trade review system
- Pattern recognition
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import json


class TradeSetup(Enum):
    """Trade setup enum"""
    BREAKOUT = "breakout"
    PULLBACK = "pullback"
    REVERSAL = "reversal"
    TREND_FOLLOWING = "trend_following"
    RANGE_TRADING = "range_trading"
    SCALPING = "scalping"
    SWING = "swing"
    OTHER = "other"


class TradeOutcome(Enum):
    """Trade outcome enum"""
    BIG_WIN = "big_win"
    SMALL_WIN = "small_win"
    BREAKEVEN = "breakeven"
    SMALL_LOSS = "small_loss"
    BIG_LOSS = "big_loss"


class EmotionalState(Enum):
    """Emotional state enum"""
    CONFIDENT = "confident"
    FEARFUL = "fearful"
    GREEDY = "greedy"
    CALM = "calm"
    ANXIOUS = "anxious"
    EXCITED = "excited"
    FRUSTRATED = "frustrated"


@dataclass
class JournalEntry:
    """Trade journal entry"""
    entry_id: str
    trade_id: str
    
    # Trade details
    symbol: str
    side: str
    entry_date: datetime
    exit_date: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    size: float
    
    # PnL
    pnl: Optional[float]
    pnl_percent: Optional[float]
    
    # Setup and strategy
    setup: TradeSetup
    strategy_name: str
    timeframe: str
    
    # Notes and analysis
    entry_reason: str
    exit_reason: Optional[str]
    notes: str
    lessons_learned: Optional[str]
    
    # Tags
    tags: List[str]
    
    # Emotional tracking
    emotional_state_entry: EmotionalState
    emotional_state_exit: Optional[EmotionalState]
    
    # Outcome classification
    outcome: Optional[TradeOutcome]
    
    # Mistakes and improvements
    mistakes: List[str]
    what_went_well: List[str]
    what_to_improve: List[str]
    
    # Screenshots and charts
    screenshots: List[str] = field(default_factory=list)
    
    # Review
    reviewed: bool = False
    review_date: Optional[datetime] = None
    review_notes: Optional[str] = None
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'entry_id': self.entry_id,
            'trade_id': self.trade_id,
            'symbol': self.symbol,
            'side': self.side,
            'entry_date': self.entry_date.isoformat(),
            'exit_date': self.exit_date.isoformat() if self.exit_date else None,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'size': self.size,
            'pnl': self.pnl,
            'pnl_percent': self.pnl_percent,
            'setup': self.setup.value,
            'strategy_name': self.strategy_name,
            'timeframe': self.timeframe,
            'entry_reason': self.entry_reason,
            'exit_reason': self.exit_reason,
            'notes': self.notes,
            'lessons_learned': self.lessons_learned,
            'tags': self.tags,
            'emotional_state_entry': self.emotional_state_entry.value,
            'emotional_state_exit': self.emotional_state_exit.value if self.emotional_state_exit else None,
            'outcome': self.outcome.value if self.outcome else None,
            'mistakes': self.mistakes,
            'what_went_well': self.what_went_well,
            'what_to_improve': self.what_to_improve,
            'screenshots': self.screenshots,
            'reviewed': self.reviewed,
            'review_date': self.review_date.isoformat() if self.review_date else None,
            'review_notes': self.review_notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class JournalStats:
    """Journal statistics"""
    total_entries: int
    total_trades: int
    reviewed_trades: int
    unreviewed_trades: int
    
    # By setup
    setup_distribution: Dict[str, int]
    
    # By outcome
    outcome_distribution: Dict[str, int]
    
    # By emotional state
    emotional_distribution: Dict[str, int]
    
    # Common tags
    top_tags: List[Tuple[str, int]]
    
    # Patterns
    most_common_mistakes: List[Tuple[str, int]]
    best_performing_setups: List[Tuple[str, float]]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'total_entries': self.total_entries,
            'total_trades': self.total_trades,
            'reviewed_trades': self.reviewed_trades,
            'unreviewed_trades': self.unreviewed_trades,
            'setup_distribution': self.setup_distribution,
            'outcome_distribution': self.outcome_distribution,
            'emotional_distribution': self.emotional_distribution,
            'top_tags': self.top_tags,
            'most_common_mistakes': self.most_common_mistakes,
            'best_performing_setups': self.best_performing_setups
        }


class TradeJournal:
    """
    Trade Journal System
    
    Comprehensive trade journaling with notes, tags,
    filtering, and analytics.
    """
    
    def __init__(self):
        self.entries: Dict[str, JournalEntry] = {}
        
        # Generate sample entries
        self._generate_sample_entries()
    
    def _generate_sample_entries(self):
        """Generate sample journal entries"""
        import numpy as np
        
        setups = list(TradeSetup)
        emotions = list(EmotionalState)
        
        for i in range(50):
            entry_date = datetime.now() - timedelta(days=np.random.randint(1, 365))
            exit_date = entry_date + timedelta(hours=np.random.randint(1, 72))
            
            entry_price = np.random.uniform(40000, 60000)
            exit_price = entry_price * (1 + np.random.normal(0, 0.05))
            
            pnl = (exit_price - entry_price) * 0.1
            pnl_percent = (exit_price - entry_price) / entry_price
            
            # Determine outcome
            if pnl_percent > 0.05:
                outcome = TradeOutcome.BIG_WIN
            elif pnl_percent > 0:
                outcome = TradeOutcome.SMALL_WIN
            elif pnl_percent > -0.02:
                outcome = TradeOutcome.BREAKEVEN
            elif pnl_percent > -0.05:
                outcome = TradeOutcome.SMALL_LOSS
            else:
                outcome = TradeOutcome.BIG_LOSS
            
            entry_id = f"je_{i+1}"
            
            entry = JournalEntry(
                entry_id=entry_id,
                trade_id=f"trade_{i+1}",
                symbol=np.random.choice(['BTC/USDT', 'ETH/USDT', 'SOL/USDT']),
                side=np.random.choice(['long', 'short']),
                entry_date=entry_date,
                exit_date=exit_date,
                entry_price=entry_price,
                exit_price=exit_price,
                size=0.1,
                pnl=pnl,
                pnl_percent=pnl_percent,
                setup=np.random.choice(setups),
                strategy_name=np.random.choice(['Momentum', 'Mean Reversion', 'Breakout']),
                timeframe=np.random.choice(['5m', '15m', '1h', '4h']),
                entry_reason="Strong technical setup with volume confirmation",
                exit_reason="Target hit" if pnl > 0 else "Stop loss triggered",
                notes="Market conditions were favorable. Followed the plan.",
                lessons_learned="Need to be more patient with entry timing" if pnl < 0 else None,
                tags=list(np.random.choice(['scalp', 'swing', 'high-confidence', 'low-risk'], size=2, replace=False)),
                emotional_state_entry=np.random.choice(emotions),
                emotional_state_exit=np.random.choice(emotions),
                outcome=outcome,
                mistakes=['Entered too early'] if pnl < 0 else [],
                what_went_well=['Good risk management', 'Patient execution'] if pnl > 0 else [],
                what_to_improve=['Wait for better confirmation'] if pnl < 0 else [],
                reviewed=np.random.random() > 0.3,
                review_date=exit_date + timedelta(days=1) if np.random.random() > 0.3 else None,
                created_at=entry_date,
                updated_at=exit_date
            )
            
            self.entries[entry_id] = entry
    
    async def create_entry(self, entry: JournalEntry) -> JournalEntry:
        """
        Create new journal entry
        
        Args:
            entry: Journal entry
            
        Returns:
            Created entry
        """
        entry.created_at = datetime.now()
        entry.updated_at = datetime.now()
        
        self.entries[entry.entry_id] = entry
        
        return entry
    
    async def update_entry(
        self,
        entry_id: str,
        updates: Dict[str, Any]
    ) -> Optional[JournalEntry]:
        """
        Update journal entry
        
        Args:
            entry_id: Entry ID
            updates: Fields to update
            
        Returns:
            Updated entry
        """
        if entry_id not in self.entries:
            return None
        
        entry = self.entries[entry_id]
        
        for key, value in updates.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        
        entry.updated_at = datetime.now()
        
        return entry
    
    async def delete_entry(self, entry_id: str) -> bool:
        """Delete journal entry"""
        if entry_id in self.entries:
            del self.entries[entry_id]
            return True
        return False
    
    async def get_entry(self, entry_id: str) -> Optional[JournalEntry]:
        """Get journal entry by ID"""
        return self.entries.get(entry_id)
    
    async def search_entries(
        self,
        query: Optional[str] = None,
        symbol: Optional[str] = None,
        setup: Optional[TradeSetup] = None,
        outcome: Optional[TradeOutcome] = None,
        tags: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        reviewed: Optional[bool] = None,
        min_pnl: Optional[float] = None,
        max_pnl: Optional[float] = None,
        sort_by: str = "entry_date",
        sort_order: str = "desc",
        limit: Optional[int] = None
    ) -> List[JournalEntry]:
        """
        Search journal entries with filters
        
        Args:
            query: Text search query
            symbol: Filter by symbol
            setup: Filter by setup type
            outcome: Filter by outcome
            tags: Filter by tags
            start_date: Filter by start date
            end_date: Filter by end date
            reviewed: Filter by review status
            min_pnl: Minimum PnL filter
            max_pnl: Maximum PnL filter
            sort_by: Sort field
            sort_order: Sort order (asc/desc)
            limit: Result limit
            
        Returns:
            List of matching entries
        """
        entries = list(self.entries.values())
        
        # Apply filters
        if query:
            query_lower = query.lower()
            entries = [
                e for e in entries
                if (query_lower in e.notes.lower() or
                    query_lower in e.entry_reason.lower() or
                    (e.exit_reason and query_lower in e.exit_reason.lower()))
            ]
        
        if symbol:
            entries = [e for e in entries if e.symbol == symbol]
        
        if setup:
            entries = [e for e in entries if e.setup == setup]
        
        if outcome:
            entries = [e for e in entries if e.outcome == outcome]
        
        if tags:
            entries = [
                e for e in entries
                if any(tag in e.tags for tag in tags)
            ]
        
        if start_date:
            entries = [e for e in entries if e.entry_date >= start_date]
        
        if end_date:
            entries = [e for e in entries if e.entry_date <= end_date]
        
        if reviewed is not None:
            entries = [e for e in entries if e.reviewed == reviewed]
        
        if min_pnl is not None:
            entries = [e for e in entries if e.pnl and e.pnl >= min_pnl]
        
        if max_pnl is not None:
            entries = [e for e in entries if e.pnl and e.pnl <= max_pnl]
        
        # Sort
        reverse = (sort_order == "desc")
        
        if sort_by == "entry_date":
            entries.sort(key=lambda e: e.entry_date, reverse=reverse)
        elif sort_by == "pnl":
            entries.sort(key=lambda e: e.pnl or 0, reverse=reverse)
        elif sort_by == "pnl_percent":
            entries.sort(key=lambda e: e.pnl_percent or 0, reverse=reverse)
        
        # Limit
        if limit:
            entries = entries[:limit]
        
        return entries
    
    async def mark_as_reviewed(
        self,
        entry_id: str,
        review_notes: Optional[str] = None
    ) -> Optional[JournalEntry]:
        """
        Mark entry as reviewed
        
        Args:
            entry_id: Entry ID
            review_notes: Review notes
            
        Returns:
            Updated entry
        """
        if entry_id not in self.entries:
            return None
        
        entry = self.entries[entry_id]
        entry.reviewed = True
        entry.review_date = datetime.now()
        entry.review_notes = review_notes
        entry.updated_at = datetime.now()
        
        return entry
    
    async def get_statistics(self) -> JournalStats:
        """
        Get journal statistics
        
        Returns:
            JournalStats
        """
        entries = list(self.entries.values())
        
        # Setup distribution
        setup_dist = {}
        for entry in entries:
            setup = entry.setup.value
            setup_dist[setup] = setup_dist.get(setup, 0) + 1
        
        # Outcome distribution
        outcome_dist = {}
        for entry in entries:
            if entry.outcome:
                outcome = entry.outcome.value
                outcome_dist[outcome] = outcome_dist.get(outcome, 0) + 1
        
        # Emotional distribution
        emotional_dist = {}
        for entry in entries:
            emotion = entry.emotional_state_entry.value
            emotional_dist[emotion] = emotional_dist.get(emotion, 0) + 1
        
        # Top tags
        tag_counts = {}
        for entry in entries:
            for tag in entry.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Common mistakes
        mistake_counts = {}
        for entry in entries:
            for mistake in entry.mistakes:
                mistake_counts[mistake] = mistake_counts.get(mistake, 0) + 1
        
        most_common_mistakes = sorted(
            mistake_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Best performing setups
        setup_pnl = {}
        setup_count = {}
        
        for entry in entries:
            if entry.pnl:
                setup = entry.setup.value
                setup_pnl[setup] = setup_pnl.get(setup, 0) + entry.pnl
                setup_count[setup] = setup_count.get(setup, 0) + 1
        
        setup_avg = {
            setup: setup_pnl[setup] / setup_count[setup]
            for setup in setup_pnl
        }
        
        best_performing_setups = sorted(
            setup_avg.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return JournalStats(
            total_entries=len(entries),
            total_trades=len(entries),
            reviewed_trades=sum(1 for e in entries if e.reviewed),
            unreviewed_trades=sum(1 for e in entries if not e.reviewed),
            setup_distribution=setup_dist,
            outcome_distribution=outcome_dist,
            emotional_distribution=emotional_dist,
            top_tags=top_tags,
            most_common_mistakes=most_common_mistakes,
            best_performing_setups=best_performing_setups
        )
    
    async def get_insights(self) -> Dict[str, Any]:
        """
        Get trading insights from journal
        
        Returns:
            Trading insights
        """
        entries = list(self.entries.values())
        
        # Win rate by setup
        setup_wins = {}
        setup_total = {}
        
        for entry in entries:
            if entry.outcome:
                setup = entry.setup.value
                setup_total[setup] = setup_total.get(setup, 0) + 1
                
                if entry.outcome in [TradeOutcome.BIG_WIN, TradeOutcome.SMALL_WIN]:
                    setup_wins[setup] = setup_wins.get(setup, 0) + 1
        
        win_rate_by_setup = {
            setup: setup_wins.get(setup, 0) / setup_total[setup]
            for setup in setup_total
        }
        
        # Emotional impact on performance
        emotion_pnl = {}
        emotion_count = {}
        
        for entry in entries:
            if entry.pnl:
                emotion = entry.emotional_state_entry.value
                emotion_pnl[emotion] = emotion_pnl.get(emotion, 0) + entry.pnl
                emotion_count[emotion] = emotion_count.get(emotion, 0) + 1
        
        emotion_avg_pnl = {
            emotion: emotion_pnl[emotion] / emotion_count[emotion]
            for emotion in emotion_pnl
        }
        
        # Best trading times
        hour_pnl = {}
        hour_count = {}
        
        for entry in entries:
            if entry.pnl:
                hour = entry.entry_date.hour
                hour_pnl[hour] = hour_pnl.get(hour, 0) + entry.pnl
                hour_count[hour] = hour_count.get(hour, 0) + 1
        
        best_hours = sorted(
            [
                (hour, hour_pnl[hour] / hour_count[hour])
                for hour in hour_pnl
            ],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'win_rate_by_setup': win_rate_by_setup,
            'emotion_impact': emotion_avg_pnl,
            'best_trading_hours': best_hours,
            'total_reviewed': sum(1 for e in entries if e.reviewed),
            'total_unreviewed': sum(1 for e in entries if not e.reviewed)
        }
    
    async def export_to_csv(self) -> str:
        """
        Export journal to CSV format
        
        Returns:
            CSV data as string
        """
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Entry ID', 'Trade ID', 'Symbol', 'Side', 'Entry Date',
            'Exit Date', 'Entry Price', 'Exit Price', 'Size', 'PnL',
            'PnL %', 'Setup', 'Strategy', 'Timeframe', 'Entry Reason',
            'Exit Reason', 'Outcome', 'Reviewed'
        ])
        
        # Data
        for entry in self.entries.values():
            writer.writerow([
                entry.entry_id,
                entry.trade_id,
                entry.symbol,
                entry.side,
                entry.entry_date.isoformat(),
                entry.exit_date.isoformat() if entry.exit_date else '',
                entry.entry_price,
                entry.exit_price or '',
                entry.size,
                entry.pnl or '',
                entry.pnl_percent or '',
                entry.setup.value,
                entry.strategy_name,
                entry.timeframe,
                entry.entry_reason,
                entry.exit_reason or '',
                entry.outcome.value if entry.outcome else '',
                entry.reviewed
            ])
        
        return output.getvalue()

    async def export_entries(
        self,
        filename: Optional[str] = None,
        format_type: str = "csv",
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Export trade entries to file
        
        Args:
            filename: Output filename (optional)
            format_type: Export format (csv, json)
            filters: Filters to apply before export
            
        Returns:
            Exported data or filepath
        """
        if filters:
            entries = await self.search_entries(**filters)
        else:
            entries = list(self.entries.values())
        
        if format_type.lower() == "csv":
            # CSV export
            if not filename:
                filename = f"trade_journal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            import csv
            
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow([
                    'Entry ID', 'Symbol', 'Side', 'Entry Date', 'Exit Date',
                    'Entry Price', 'Exit Price', 'Size', 'PnL', 'PnL %',
                    'Setup', 'Strategy', 'Timeframe', 'Outcome', 'Reviewed',
                    'Tags', 'Notes'
                ])
                
                # Data
                for entry in entries:
                    writer.writerow([
                        entry.entry_id,
                        entry.symbol,
                        entry.side,
                        entry.entry_date.strftime('%Y-%m-%d %H:%M'),
                        entry.exit_date.strftime('%Y-%m-%d %H:%M') if entry.exit_date else '',
                        entry.entry_price,
                        entry.exit_price or '',
                        entry.size,
                        entry.pnl or 0,
                        f"{entry.pnl_percent:.2%}" if entry.pnl_percent else '',
                        entry.setup.value,
                        entry.strategy_name,
                        entry.timeframe,
                        entry.outcome.value if entry.outcome else '',
                        'Yes' if entry.reviewed else 'No',
                        ', '.join(entry.tags),
                        entry.notes[:100] + '...' if len(entry.notes) > 100 else entry.notes
                    ])
            
            return filename
        
        elif format_type.lower() == "json":
            # JSON export
            if not filename:
                filename = f"trade_journal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            import json
            
            with open(filename, 'w') as f:
                json.dump([entry.to_dict() for entry in entries], f, indent=2)
            
            return filename
        
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    async def generate_report(
        self,
        format_type: str = "text",
        include_charts: bool = False,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> str:
        """
        Generate comprehensive trade journal report
        
        Args:
            format_type: Report format (text, html, markdown)
            include_charts: Whether to include chart data
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Generated report
        """
        stats = await self.get_statistics()
        insights = await self.get_insights()
        
        # Apply date filters
        filters = {}
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date
        
        recent_entries = await self.search_entries(limit=10, **filters)
        
        if format_type.lower() == "html":
            report = f"""
            <html>
            <head>
                <title>Trade Journal Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                    .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                    .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #f9f9f9; border-radius: 3px; }}
                    table {{ width: 100%; border-collapse: collapse; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Trade Journal Hisoboti</h1>
                    <p>Yaratilgan sana: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="section">
                    <h2>Asosiy Statistikalar</h2>
                    <div class="metric">Jami savdolar: {stats.total_entries}</div>
                    <div class="metric">Ko'rilgan: {stats.reviewed_trades}</div>
                    <div class="metric">Ko'rilmagan: {stats.unreviewed_trades}</div>
                </div>
                
                <div class="section">
                    <h2>Setup Taqsimoti</h2>
                    <table>
                        <tr><th>Setup</th><th>Soni</th></tr>
                        {''.join([f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in stats.setup_distribution.items()])}
                    </table>
                </div>
                
                <div class="section">
                    <h2>Natija Taqsimoti</h2>
                    <table>
                        <tr><th>Natija</th><th>Soni</th></tr>
                        {''.join([f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in stats.outcome_distribution.items()])}
                    </table>
                </div>
                
                <div class="section">
                    <h2>So'nggi Savdolar</h2>
                    <table>
                        <tr><th>Symbol</th><th>Setup</th><th>Natija</th><th>PnL</th></tr>
                        {''.join([f'<tr><td>{e.symbol}</td><td>{e.setup.value}</td><td>{e.outcome.value if e.outcome else ""}</td><td>{e.pnl:.2f}</td></tr>' for e in recent_entries[:10]])}
                    </table>
                </div>
            </body>
            </html>
            """
            return report
        
        elif format_type.lower() == "markdown":
            report = f"""# Trade Journal Hisoboti

**Yaratilgan sana:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Asosiy Statistikalar

- **Jami savdolar:** {stats.total_entries}
- **Ko'rilgan:** {stats.reviewed_trades}
- **Ko'rilmagan:** {stats.unreviewed_trades}

## Setup Taqsimoti

| Setup | Soni |
|-------|------|
{chr(10).join([f"| {k} | {v} |" for k, v in stats.setup_distribution.items()])}

## Natija Taqsimoti

| Natija | Soni |
|--------|------|
{chr(10).join([f"| {k} | {v} |" for k, v in stats.outcome_distribution.items()])}

## Eng Yaxshi Setup'lar

| Setup | O'rtacha PnL |
|-------|-------------|
{chr(10).join([f"| {k} | {v:.2f} |" for k, v in stats.best_performing_setups])}

## Eng Ko'p Uchragan Xatolar

| Xato | Soni |
|------|------|
{chr(10).join([f"| {k} | {v} |" for k, v in stats.most_common_mistakes])}

## So'nggi 10 ta Savdo

| Symbol | Setup | Natija | PnL |
|--------|-------|--------|-----|
{chr(10).join([f"| {e.symbol} | {e.setup.value} | {e.outcome.value if e.outcome else ''} | {e.pnl:.2f} |" for e in recent_entries[:10]])}

## Tahlil

Bu davrdagi asosiy kuzatishlar:

1. **Eng muvaffaqiyatli setup:** {stats.best_performing_setups[0][0] if stats.best_performing_setups else 'Ma\'lumot yo\'q'}
2. **Eng ko'p uchragan xato:** {stats.most_common_mistakes[0][0] if stats.most_common_mistakes else 'Ma\'lumot yo\'q'}
3. **Sharhlangan savdolar foizi:** {(stats.reviewed_trades / stats.total_entries * 100) if stats.total_entries > 0 else 0:.1f}%
"""
            return report
        
        else:  # text format
            report = f"""
=== TRADE JOURNAL HISOBOTI ===
Yaratilgan sana: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

--- ASOSIY STATISTIKALAR ---
Jami savdolar: {stats.total_entries}
Ko'rilgan savdolar: {stats.reviewed_trades}
Ko'rilmagan savdolar: {stats.unreviewed_trades}
Sharhlangan foiz: {(stats.reviewed_trades / stats.total_entries * 100) if stats.total_entries > 0 else 0:.1f}%

--- SETUP TAQSIMOTI ---
"""
            
            for setup, count in stats.setup_distribution.items():
                report += f"{setup}: {count} ta\n"
            
            report += "\n--- NATIJA TAQSIMOTI ---\n"
            for outcome, count in stats.outcome_distribution.items():
                report += f"{outcome}: {count} ta\n"
            
            report += "\n--- ENG YAXSHI SETUP'LAR ---\n"
            for setup, avg_pnl in stats.best_performing_setups:
                report += f"{setup}: {avg_pnl:.2f} o'rtacha PnL\n"
            
            report += "\n--- ENG KO'P UCHRAGAN XATOLAR ---\n"
            for mistake, count in stats.most_common_mistakes:
                report += f"{mistake}: {count} marta\n"
            
            report += "\n--- SO'NNGI SAVDOLAR ---\n"
            for entry in recent_entries[:10]:
                report += f"{entry.symbol} | {entry.setup.value} | {entry.outcome.value if entry.outcome else 'N/A'} | PnL: {entry.pnl:.2f}\n"
            
            report += "\n=== HISOBOT TUGADI ==="
            return report

    async def add_entry(self, entry: JournalEntry) -> str:
        """
        Add new trade entry (alias for create_entry)
        
        Args:
            entry: Journal entry to add
            
        Returns:
            Entry ID
        """
        created_entry = await self.create_entry(entry)
        return created_entry.entry_id


# Global instance
trade_journal = TradeJournal()


async def test_trade_journal():
    """Test trade journal"""
    journal = TradeJournal()
    
    # Search entries
    entries = await journal.search_entries(
        outcome=TradeOutcome.BIG_WIN,
        limit=5
    )
    
    print(f"Big wins: {len(entries)}")
    for entry in entries:
        print(f"  {entry.symbol}: {entry.pnl_percent:.2%}")
    
    # Get statistics
    stats = await journal.get_statistics()
    print(f"\nJournal Statistics:")
    print(f"  Total entries: {stats.total_entries}")
    print(f"  Reviewed: {stats.reviewed_trades}")
    print(f"  Top tags: {stats.top_tags[:3]}")
    
    # Get insights
    insights = await journal.get_insights()
    print(f"\nInsights:")
    print(f"  Win rate by setup: {insights['win_rate_by_setup']}")


if __name__ == "__main__":
    asyncio.run(test_trade_journal())
