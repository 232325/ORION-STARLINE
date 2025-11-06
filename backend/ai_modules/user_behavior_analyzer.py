"""
User Behavior Analyzer
======================

AI-powered behavioral analysis system for investment decision making.
Analyzes user behavior patterns, biases, and decision-making styles.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json
import logging
from collections import defaultdict, Counter
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import warnings
warnings.filterwarnings('ignore')

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BehavioralPattern:
    """Behavioral pattern analysis result"""
    pattern_name: str
    intensity: float  # 0-100 scale
    description: str
    impact_on_decisions: str
    confidence_level: float

@dataclass
class BiasAnalysis:
    """Bias analysis result"""
    bias_name: str
    strength: float  # 0-100 scale
    evidence: List[str]
    severity: str  # low, medium, high
    mitigation_strategies: List[str]

@dataclass
class RiskResponsePattern:
    """Risk response pattern analysis"""
    tolerance_for_losses: float  # 0-100
    time_to_recover: int  # days
    panic_threshold: float  # % loss before panic
    risk_increase_behavior: str
    decision_speed_under_stress: str

@dataclass
class InvestmentBehaviorProfile:
    """Complete behavioral analysis profile"""
    user_id: str
    behavioral_patterns: List[BehavioralPattern]
    bias_analysis: List[BiasAnalysis]
    risk_response: RiskResponsePattern
    decision_making_style: str
    emotional_reactions: Dict[str, float]
    learning_pattern: str
    overconfidence_score: float
    loss_aversion_score: float
    herd_instinct_score: float
    recency_bias_score: float
    anchoring_score: float
    mental_accounting_score: float
    last_updated: datetime
    confidence_level: float

class UserBehaviorAnalyzer:
    """AI-powered user behavior analysis system"""
    
    def __init__(self):
        """Initialize the behavior analyzer"""
        # Behavioral analysis parameters
        self.analysis_window_days = 90
        self.min_trades_for_analysis = 10
        self.benchmark_volatility = 15.0  # S&P 500 average volatility
        
        # Bias detection thresholds
        self.bias_thresholds = {
            'overconfidence': {'low': 30, 'medium': 60, 'high': 80},
            'loss_aversion': {'low': 40, 'medium': 65, 'high': 85},
            'herd_instinct': {'low': 35, 'medium': 60, 'high': 80},
            'recency_bias': {'low': 25, 'medium': 50, 'high': 75},
            'anchoring': {'low': 30, 'medium': 55, 'high': 75},
            'mental_accounting': {'low': 35, 'medium': 60, 'high': 80}
        }
        
        # Initialize ML models
        self.clustering_model = KMeans(n_clusters=5, random_state=42)
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        
        self.is_models_trained = False
    
    def analyze_trading_behavior(self, trading_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze trading behavior patterns from historical data
        
        Args:
            trading_history: List of trade records
            
        Returns:
            Trading behavior analysis
        """
        try:
            if not trading_history or len(trading_history) < self.min_trades_for_analysis:
                logger.warning("Insufficient trading data for analysis")
                return self._get_default_analysis()
            
            df = pd.DataFrame(trading_history)
            analysis = {}
            
            # Trade frequency analysis
            analysis['trade_frequency'] = self._analyze_trade_frequency(df)
            
            # Position sizing behavior
            analysis['position_sizing'] = self._analyze_position_sizing(df)
            
            # Risk management behavior
            analysis['risk_management'] = self._analyze_risk_management(df)
            
            # Performance patterns
            analysis['performance_patterns'] = self._analyze_performance_patterns(df)
            
            # Market timing behavior
            analysis['market_timing'] = self._analyze_market_timing(df)
            
            # Emotional trading patterns
            analysis['emotional_patterns'] = self._analyze_emotional_patterns(df)
            
            # Win/loss ratio analysis
            analysis['win_loss_analysis'] = self._analyze_win_loss_patterns(df)
            
            logger.info("Trading behavior analysis completed")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing trading behavior: {e}")
            return self._get_default_analysis()
    
    def _analyze_trade_frequency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trading frequency patterns"""
        try:
            df['trade_date'] = pd.to_datetime(df.get('timestamp', df.get('date', datetime.now())))
            df = df.sort_values('trade_date')
            
            # Calculate trading intervals
            df['days_between'] = df['trade_date'].diff().dt.days
            
            # Trading frequency metrics
            avg_interval = df['days_between'].mean()
            std_interval = df['days_between'].std()
            
            # Identify patterns
            patterns = []
            if avg_interval <= 1:
                patterns.append("day_trading")
            elif avg_interval <= 7:
                patterns.append("frequent_trading")
            elif avg_interval <= 30:
                patterns.append("moderate_trading")
            else:
                patterns.append("infrequent_trading")
            
            return {
                'average_interval_days': avg_interval,
                'frequency_pattern': patterns[0],
                'consistency_score': max(0, 100 - (std_interval * 10)),
                'trading_consistency': 'high' if std_interval < 5 else 'medium' if std_interval < 15 else 'low'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trade frequency: {e}")
            return {'frequency_pattern': 'unknown', 'consistency_score': 50}
    
    def _analyze_position_sizing(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze position sizing behavior"""
        try:
            # Calculate position sizes as percentage of portfolio
            df['position_size'] = df.get('position_size_pct', 0)
            df['portfolio_value'] = df.get('portfolio_value', 100000)
            
            # Position sizing statistics
            avg_position = df['position_size'].mean()
            max_position = df['position_size'].max()
            position_std = df['position_size'].std()
            
            # Risk assessment
            risk_score = 0
            if avg_position > 20:
                risk_score += 40
            if max_position > 30:
                risk_score += 30
            if position_std > 10:
                risk_score += 30
            
            # Behavior classification
            if avg_position <= 5:
                behavior = "very_conservative"
            elif avg_position <= 10:
                behavior = "conservative"
            elif avg_position <= 20:
                behavior = "moderate"
            elif avg_position <= 30:
                behavior = "aggressive"
            else:
                behavior = "very_aggressive"
            
            return {
                'average_position_size': avg_position,
                'max_position_size': max_position,
                'position_variability': position_std,
                'sizing_behavior': behavior,
                'risk_score': min(100, risk_score),
                'diversification_score': max(0, 100 - position_std)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing position sizing: {e}")
            return {'sizing_behavior': 'moderate', 'risk_score': 50}
    
    def _analyze_risk_management(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze risk management behavior"""
        try:
            # Stop-loss usage
            stop_loss_usage = df.get('has_stop_loss', False).sum() / len(df) if 'has_stop_loss' in df else 0
            
            # Profit taking behavior
            df['profit'] = df.get('profit_loss', 0)
            profit_taking = (df['profit'] > 0).sum() / len(df)
            
            # Risk-reward analysis
            profits = df[df['profit'] > 0]['profit']
            losses = df[df['profit'] < 0]['profit']
            
            avg_profit = profits.mean() if len(profits) > 0 else 0
            avg_loss = losses.mean() if len(losses) > 0 else 0
            
            risk_reward_ratio = abs(avg_profit / avg_loss) if avg_loss != 0 else 1
            
            # Risk management score
            risk_mgmt_score = 0
            if stop_loss_usage > 0.7:
                risk_mgmt_score += 30
            if profit_taking > 0.6:
                risk_mgmt_score += 25
            if risk_reward_ratio >= 1.5:
                risk_mgmt_score += 25
            if (df['profit'] < -10).sum() / len(df) < 0.1:  # Less than 10% large losses
                risk_mgmt_score += 20
            
            return {
                'stop_loss_usage': stop_loss_usage,
                'profit_taking_rate': profit_taking,
                'risk_reward_ratio': risk_reward_ratio,
                'risk_management_score': min(100, risk_mgmt_score),
                'discipline_level': 'high' if risk_mgmt_score >= 80 else 'medium' if risk_mgmt_score >= 50 else 'low'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing risk management: {e}")
            return {'risk_management_score': 50, 'discipline_level': 'medium'}
    
    def _analyze_performance_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance patterns"""
        try:
            profits = df.get('profit_loss', pd.Series([0])).values
            
            # Performance metrics
            total_return = np.sum(profits)
            win_rate = (np.array(profits) > 0).mean()
            avg_win = np.mean(profits[profits > 0]) if len(profits[profits > 0]) > 0 else 0
            avg_loss = np.mean(profits[profits < 0]) if len(profits[profits < 0]) > 0 else 0
            
            # Performance consistency
            profit_std = np.std(profits)
            consistency_score = max(0, 100 - (profit_std / np.mean(np.abs(profits)) * 100)) if np.mean(np.abs(profits)) > 0 else 50
            
            # Streak analysis
            streaks = self._analyze_win_streaks(profits)
            
            return {
                'total_return': total_return,
                'win_rate': win_rate,
                'average_win': avg_win,
                'average_loss': avg_loss,
                'profit_factor': abs(avg_win / avg_loss) if avg_loss != 0 else 1,
                'consistency_score': consistency_score,
                'largest_win_streak': streaks['largest_win'],
                'largest_loss_streak': streaks['largest_loss'],
                'performance_stability': 'stable' if consistency_score >= 70 else 'moderate' if consistency_score >= 40 else 'volatile'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing performance patterns: {e}")
            return {'win_rate': 0.5, 'consistency_score': 50}
    
    def _analyze_win_streaks(self, profits: np.ndarray) -> Dict[str, int]:
        """Analyze win and loss streaks"""
        try:
            wins = profits > 0
            win_streaks = []
            loss_streaks = []
            
            current_streak = 0
            current_type = wins[0]
            
            for is_win in wins:
                if is_win == current_type:
                    current_streak += 1
                else:
                    if current_type:
                        win_streaks.append(current_streak)
                    else:
                        loss_streaks.append(current_streak)
                    current_streak = 1
                    current_type = is_win
            
            # Add final streak
            if current_type:
                win_streaks.append(current_streak)
            else:
                loss_streaks.append(current_streak)
            
            return {
                'largest_win': max(win_streaks) if win_streaks else 0,
                'largest_loss': max(loss_streaks) if loss_streaks else 0,
                'average_win_streak': np.mean(win_streaks) if win_streaks else 0,
                'average_loss_streak': np.mean(loss_streaks) if loss_streaks else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing win streaks: {e}")
            return {'largest_win': 0, 'largest_loss': 0}
    
    def _analyze_market_timing(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market timing behavior"""
        try:
            # This would require market data to compare against
            # For now, analyze based on trade distribution and patterns
            
            df['trade_date'] = pd.to_datetime(df.get('timestamp', df.get('date', datetime.now())))
            df['day_of_week'] = df['trade_date'].dt.dayofweek
            df['hour_of_day'] = df['trade_date'].dt.hour
            
            # Trading time patterns
            weekday_trades = (df['day_of_week'] < 5).sum()
            weekend_trades = (df['day_of_week'] >= 5).sum()
            
            # Morning vs afternoon trading
            morning_trades = (df['hour_of_day'] < 12).sum()
            afternoon_trades = (df['hour_of_day'] >= 12).sum()
            
            # Volatility-based timing (if volatility data available)
            volatility_data = df.get('market_volatility', pd.Series([self.benchmark_volatility] * len(df)))
            high_vol_trades = (volatility_data > self.benchmark_volatility * 1.5).sum()
            
            timing_score = 0
            if morning_trades > afternoon_trades:
                timing_score += 30  # Morning trades often better
            if weekday_trades > weekend_trades * 2:
                timing_score += 20
            if high_vol_trades / len(df) < 0.3:
                timing_score += 30  # Avoiding high volatility periods
            if len(df['day_of_week'].unique()) >= 4:
                timing_score += 20  # Diversified timing
            
            return {
                'weekday_trade_ratio': weekday_trades / len(df),
                'morning_trade_ratio': morning_trades / len(df),
                'high_volatility_avoidance': 1 - (high_vol_trades / len(df)),
                'timing_score': min(100, timing_score),
                'timing_discipline': 'high' if timing_score >= 70 else 'medium' if timing_score >= 40 else 'low'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market timing: {e}")
            return {'timing_score': 50, 'timing_discipline': 'medium'}
    
    def _analyze_emotional_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze emotional trading patterns"""
        try:
            # Emotional trading indicators
            rapid_trades = self._detect_rapid_trading(df)
            large_positions = self._detect_emotional_position_sizing(df)
            after_loss_behavior = self._analyze_post_loss_behavior(df)
            
            # Emotional score calculation
            emotional_score = 0
            if rapid_trades['is_rapid']:
                emotional_score += 40
            if large_positions['has_emotional_sizes']:
                emotional_score += 30
            if after_loss_behavior['increased_risk']:
                emotional_score += 30
            
            emotional_state = {
                'emotional_trading_score': min(100, emotional_score),
                'impulsiveness_level': 'high' if emotional_score >= 70 else 'medium' if emotional_score >= 40 else 'low',
                'rapid_trading_frequency': rapid_trades['frequency'],
                'emotional_sizing_incidents': large_positions['incident_count']
            }
            
            return emotional_state
            
        except Exception as e:
            logger.error(f"Error analyzing emotional patterns: {e}")
            return {'emotional_trading_score': 50, 'impulsiveness_level': 'medium'}
    
    def _detect_rapid_trading(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect rapid trading patterns indicating emotional decisions"""
        try:
            df['trade_date'] = pd.to_datetime(df.get('timestamp', df.get('date', datetime.now())))
            df = df.sort_values('trade_date')
            df['time_between'] = df['trade_date'].diff().dt.total_seconds() / 3600  # hours
            
            # Rapid trading: trades within 1 hour
            rapid_trades = (df['time_between'] < 1).sum()
            rapid_frequency = rapid_trades / len(df) if len(df) > 0 else 0
            
            return {
                'is_rapid': rapid_frequency > 0.2,  # More than 20% rapid trades
                'frequency': rapid_frequency,
                'count': rapid_trades
            }
            
        except Exception as e:
            logger.error(f"Error detecting rapid trading: {e}")
            return {'is_rapid': False, 'frequency': 0}
    
    def _detect_emotional_position_sizing(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect emotional position sizing (too large positions)"""
        try:
            if 'position_size_pct' not in df:
                return {'has_emotional_sizes': False, 'incident_count': 0}
            
            # Define emotional sizing threshold (user typically uses 10%, suddenly uses 25%+)
            position_sizes = df['position_size_pct'].values
            mean_size = np.mean(position_sizes)
            emotional_threshold = mean_size * 2  # 2x average
            
            emotional_sizing = (position_sizes > emotional_threshold).sum()
            
            return {
                'has_emotional_sizes': emotional_sizing > 0,
                'incident_count': emotional_sizing,
                'emotional_threshold': emotional_threshold,
                'max_emotional_size': np.max(position_sizes)
            }
            
        except Exception as e:
            logger.error(f"Error detecting emotional sizing: {e}")
            return {'has_emotional_sizes': False, 'incident_count': 0}
    
    def _analyze_post_loss_behavior(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze behavior patterns after losses"""
        try:
            if 'profit_loss' not in df:
                return {'increased_risk': False, 'behavior_score': 50}
            
            df['is_loss'] = df['profit_loss'] < 0
            df['next_position_size'] = df.get('position_size_pct', pd.Series([10] * len(df))).shift(-1)
            
            # Find trades after losses
            loss_indices = df[df['is_loss']].index
            post_loss_increases = 0
            
            for idx in loss_indices:
                if idx + 1 < len(df):
                    current_size = df.loc[idx, 'position_size_pct'] if 'position_size_pct' in df.columns else 10
                    next_size = df.loc[idx + 1, 'next_position_size']
                    if next_size > current_size * 1.5:  # 50% increase in position size
                        post_loss_increases += 1
            
            increased_risk = post_loss_increases > len(loss_indices) * 0.3 if len(loss_indices) > 0 else False
            
            return {
                'increased_risk': increased_risk,
                'post_loss_increases': post_loss_increases,
                'total_loss_trades': len(loss_indices),
                'behavior_score': min(100, (post_loss_increases / max(len(loss_indices), 1)) * 100)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing post-loss behavior: {e}")
            return {'increased_risk': False, 'behavior_score': 50}
    
    def _analyze_win_loss_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze win/loss patterns and their relationships"""
        try:
            profits = df.get('profit_loss', pd.Series([0])).values
            is_wins = profits > 0
            
            # Win rate analysis
            win_rate = is_wins.mean()
            
            # Pattern analysis
            patterns = {
                'consecutive_wins': 0,
                'consecutive_losses': 0,
                'mixed_patterns': 0
            }
            
            current_streak = 0
            current_type = is_wins[0] if len(is_wins) > 0 else True
            
            for is_win in is_wins:
                if is_win == current_type:
                    current_streak += 1
                else:
                    if current_streak >= 3:
                        if current_type:
                            patterns['consecutive_wins'] += 1
                        else:
                            patterns['consecutive_losses'] += 1
                    else:
                        patterns['mixed_patterns'] += 1
                    current_streak = 1
                    current_type = is_win
            
            return {
                'win_rate': win_rate,
                'win_loss_consistency': patterns,
                'pattern_diversity': len(set(is_wins)) > 1,  # Has both wins and losses
                'streak_behavior': 'streak_prone' if max(patterns.values()) > 2 else 'mixed'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing win/loss patterns: {e}")
            return {'win_rate': 0.5, 'streak_behavior': 'mixed'}
    
    def detect_behavioral_biases(self, trading_data: List[Dict[str, Any]]) -> Dict[str, BiasAnalysis]:
        """
        Detect behavioral biases from trading data
        
        Args:
            trading_data: Historical trading data
            
        Returns:
            Dictionary of detected biases
        """
        try:
            biases = {}
            df = pd.DataFrame(trading_data)
            
            # Overconfidence Bias
            biases['overconfidence'] = self._detect_overconfidence_bias(df)
            
            # Loss Aversion
            biases['loss_aversion'] = self._detect_loss_aversion_bias(df)
            
            # Recency Bias
            biases['recency_bias'] = self._detect_recency_bias(df)
            
            # Anchoring Bias
            biases['anchoring'] = self._detect_anchoring_bias(df)
            
            # Mental Accounting
            biases['mental_accounting'] = self._detect_mental_accounting_bias(df)
            
            # Herding Behavior
            biases['herding'] = self._detect_herding_bias(df)
            
            # Confirmation Bias
            biases['confirmation'] = self._detect_confirmation_bias(df)
            
            logger.info(f"Detected {len(biases)} behavioral biases")
            return biases
            
        except Exception as e:
            logger.error(f"Error detecting behavioral biases: {e}")
            return self._get_default_biases()
    
    def _detect_overconfidence_bias(self, df: pd.DataFrame) -> BiasAnalysis:
        """Detect overconfidence bias"""
        try:
            # Indicators of overconfidence
            trade_frequency = len(df) / 30  # trades per month
            position_sizes = df.get('position_size_pct', pd.Series([10] * len(df)))
            avg_position = position_sizes.mean()
            win_rate = (df.get('profit_loss', pd.Series([0])) > 0).mean()
            
            # Overconfidence score
            overconfidence_score = 0
            evidence = []
            
            if trade_frequency > 10:  # More than 10 trades per month
                overconfidence_score += 30
                evidence.append("Yuqori savdo chastotasi")
            
            if avg_position > 20:  # Large average positions
                overconfidence_score += 25
                evidence.append("Katta pozitsiyalar")
            
            if win_rate < 0.4 and trade_frequency > 5:  # High frequency but low win rate
                overconfidence_score += 35
                evidence.append("Yuqori chastota, past g'alaba foizi")
            
            # Classify severity
            if overconfidence_score >= self.bias_thresholds['overconfidence']['high']:
                severity = 'high'
            elif overconfidence_score >= self.bias_thresholds['overconfidence']['medium']:
                severity = 'medium'
            else:
                severity = 'low'
            
            return BiasAnalysis(
                bias_name="o'ziga ishonch ortiqchaligi",
                strength=min(100, overconfidence_score),
                evidence=evidence,
                severity=severity,
                mitigation_strategies=[
                    "Pozitsiyalar hajmini kamaytirish",
                    "Savdo chastotasini cheklash",
                    "Kichik qadamlar bilan test qilish",
                    "Moliyaviy maslahat olish"
                ]
            )
            
        except Exception as e:
            logger.error(f"Error detecting overconfidence bias: {e}")
            return self._default_bias("o'ziga ishonch ortiqchaligi")
    
    def _detect_loss_aversion_bias(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect loss aversion bias"""
        try:
            profits = df.get('profit_loss', pd.Series([0])).values
            is_wins = profits > 0
            
            # Loss aversion indicators
            wins = profits[is_wins]
            losses = profits[~is_wins]
            
            avg_win = np.mean(wins) if len(wins) > 0 else 0
            avg_loss = np.mean(losses) if len(losses) > 0 else 0
            loss_count = len(losses)
            
            # Loss aversion score (fear of losses greater than joy of gains)
            loss_aversion_score = 0
            evidence = []
            
            if len(losses) > 0 and len(wins) > 0:
                ratio = abs(avg_loss / avg_win) if avg_win != 0 else 1
                if ratio > 2.0:  # Losses hurt more than wins help
                    loss_aversion_score += 40
                    evidence.append(f"Yo'qotishlar daromaddan {ratio:.1f} marta ko'p ta'sir qiladi")
            
            # Quick profit taking vs holding losses
            if loss_count > 0:
                small_losses = (np.abs(losses) < np.abs(avg_loss) * 0.5).sum()
                if small_losses / loss_count > 0.7:
                    loss_aversion_score += 30
                    evidence.append("Kichik yo'qotishlarni tez yopish")
            
            if loss_aversion_score >= self.bias_thresholds['loss_aversion']['high']:
                severity = 'high'
            elif loss_aversion_score >= self.bias_thresholds['loss_aversion']['medium']:
                severity = 'medium'
            else:
                severity = 'low'
            
            return BiasAnalysis(
                bias_name="yo'qotishlardan qochish",
                strength=min(100, loss_aversion_score),
                evidence=evidence,
                severity=severity,
                mitigation_strategies=[
                    "Stop-loss va take-profit darajasini aniqlash",
                    "Risk-reward nisbatini hisoblash",
                    "Emotsional qarorlar uchun vaqt berish",
                    "Pozitsiyalar hajmini reja asosida belgilash"
                ]
            )
            
        except Exception as e:
            logger.error(f"Error detecting loss aversion bias: {e}")
            return self._default_bias("yo'qotishlardan qochish")
    
    def _detect_recency_bias(self, df: pd.DataFrame) -> BiasAnalysis:
        """Detect recency bias (overweighting recent events)"""
        try:
            df['trade_date'] = pd.to_datetime(df.get('timestamp', df.get('date', datetime.now())))
            df = df.sort_values('trade_date')
            
            # Recency indicators
            recent_trades = df.tail(int(len(df) * 0.3))  # Last 30% of trades
            recent_performance = recent_trades.get('profit_loss', pd.Series([0])).mean()
            overall_performance = df.get('profit_loss', pd.Series([0])).mean()
            
            recency_score = 0
            evidence = []
            
            # Recent performance significantly different from overall
            if recent_performance > 0 and abs(recent_performance - overall_performance) > overall_performance * 0.5:
                recency_score += 35
                evidence.append("So'nggi natijalar umumiy natijalardan farq qiladi")
            
            # Chasing recent winners
            if recent_performance > overall_performance * 1.5:
                recency_score += 40
                evidence.append("So'nggi muvaffaqiyatli savdolar ortida quvish")
            
            if recency_score >= self.bias_thresholds['recency_bias']['high']:
                severity = 'high'
            elif recency_score >= self.bias_thresholds['recency_bias']['medium']:
                severity = 'medium'
            else:
                severity = 'low'
            
            return BiasAnalysis(
                bias_name="yaqinlik xatosi",
                strength=min(100, recency_score),
                evidence=evidence,
                severity=severity,
                mitigation_strategies=[
                    "Uzoq muddatli ma'lumotlarni tahlil qilish",
                    "So'nggi muvaffaqiyatlarni qadrlash",
                    "Tizimli yondashuvni saqlash",
                    "Emotsional qarorlar uchun kutish"
                ]
            )
            
        except Exception as e:
            logger.error(f"Error detecting recency bias: {e}")
            return self._default_bias("yaqinlik xatosi")
    
    def _detect_anchoring_bias(self, df: pd.DataFrame) -> BiasAnalysis:
        """Detect anchoring bias"""
        try:
            # This is complex and would need specific market data
            # For now, use position sizing patterns as proxy
            position_sizes = df.get('position_size_pct', pd.Series([10] * len(df)))
            
            anchor_score = 0
            evidence = []
            
            # Consistent position sizing (anchoring to a preferred size)
            size_variance = position_sizes.std()
            if size_variance < 5:  # Very consistent sizing
                anchor_score += 30
                evidence.append("Pozitsiya hajmi juda barqaror")
            
            # Refusing to adjust after significant changes
            if len(df) > 20:
                recent_avg = position_sizes.tail(10).mean()
                early_avg = position_sizes.head(10).mean()
                if abs(recent_avg - early_avg) < early_avg * 0.2:
                    anchor_score += 25
                    evidence.append("Pozitsiya hajmi vaqt o'tishi bilan o'zgarmaydi")
            
            if anchor_score >= self.bias_thresholds['anchoring']['high']:
                severity = 'high'
            elif anchor_score >= self.bias_thresholds['anchoring']['medium']:
                severity = 'medium'
            else:
                severity = 'low'
            
            return BiasAnalysis(
                bias_name="ilgaklash xatosi",
                strength=min(100, anchor_score),
                evidence=evidence,
                severity=severity,
                mitigation_strategies=[
                    "Pozitsiya hajmini elastik belgilash",
                    "Sharoitlarga qarab o'zgartirish",
                    "Mantiqiy sabablarni yozib olish",
                    "Boshqa savdogarlarning strategiyalarini o'rganish"
                ]
            )
            
        except Exception as e:
            logger.error(f"Error detecting anchoring bias: {e}")
            return self._default_bias("ilgaklash xatosi")
    
    def _detect_mental_accounting_bias(self, df: pd.DataFrame) -> BiasAnalysis:
        """Detect mental accounting bias"""
        try:
            # Mental accounting: treating money differently based on source/goal
            # This would require more detailed account/goal data
            # For now, use trading patterns across different asset types
            
            mental_score = 0
            evidence = []
            
            # Inconsistent risk tolerance across different assets
            if 'asset_type' in df.columns:
                asset_risks = df.groupby('asset_type').agg({
                    'position_size_pct': 'mean',
                    'profit_loss': 'mean'
                }).reset_index()
                
                if len(asset_risks) > 1:
                    risk_variance = asset_risks['position_size_pct'].std()
                    if risk_variance > 10:
                        mental_score += 35
                        evidence.append("Turli aktivlar uchun xavf tolerancei farqli")
            
            if mental_score >= self.bias_thresholds['mental_accounting']['high']:
                severity = 'high'
            elif mental_score >= self.bias_thresholds['mental_accounting']['medium']:
                severity = 'medium'
            else:
                severity = 'low'
            
            return BiasAnalysis(
                bias_name="hisob-kitob mentaliteti",
                strength=min(100, mental_score),
                evidence=evidence,
                severity=severity,
                mitigation_strategies=[
                    "Barcha mablag'larni bir xil ko'rish",
                    "Umumiy risk strategiyasi ishlab chiqish",
                    "Mantiqiy qarorlar qabul qilish",
                    "Hisob-kitob tizimini qayta ko'rib chiqish"
                ]
            )
            
        except Exception as e:
            logger.error(f"Error detecting mental accounting bias: {e}")
            return self._default_bias("hisob-kitob mentaliteti")
    
    def _detect_herding_bias(self, df: pd.DataFrame) -> BiasAnalysis:
        """Detect herding bias (following the crowd)"""
        try:
            # Herding: copying popular trades or following market sentiment
            # This would require sentiment data and market data
            # For now, use timing patterns
            
            herding_score = 0
            evidence = []
            
            # Trading during high volume periods (following crowd)
            if 'market_volume' in df.columns:
                high_volume_trades = (df['market_volume'] > df['market_volume'].quantile(0.8)).sum()
                herding_ratio = high_volume_trades / len(df)
                
                if herding_ratio > 0.6:
                    herding_score += 40
                    evidence.append("Yuqori hajmli davrlarda ko'p savdo qilish")
            
            # Inconsistent independent research
            if len(df) > 20:
                research_mentions = df.get('has_research', pd.Series([False] * len(df))).sum()
                research_ratio = research_mentions / len(df)
                
                if research_ratio < 0.3:
                    herding_score += 30
                    evidence.append("Tadqiqot yetarli emas")
            
            if herding_score >= self.bias_thresholds['herd_instinct']['high']:
                severity = 'high'
            elif herding_score >= self.bias_thresholds['herd_instinct']['medium']:
                severity = 'medium'
            else:
                severity = 'low'
            
            return BiasAnalysis(
                bias_name="ola quvish instinkti",
                strength=min(100, herding_score),
                evidence=evidence,
                severity=severity,
                mitigation_strategies=[
                    "Mustaqil tadqiqot o'tkazish",
                    "Ommabop fikrga qarshi turish",
                    "Shaxsiy strategiya ishlab chiqish",
                    "Keng turli manbalardan ma'lumot olish"
                ]
            )
            
        except Exception as e:
            logger.error(f"Error detecting herding bias: {e}")
            return self._default_bias("ola quvish instinkti")
    
    def _detect_confirmation_bias(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect confirmation bias (seeking confirming evidence)"""
        try:
            # Confirmation: ignoring contradictory evidence
            # This would require detailed decision rationale data
            
            confirmation_score = 0
            evidence = []
            
            # High confidence in losing trades (ignoring warning signs)
            losing_trades = df[df['profit_loss'] < 0]
            if len(losing_trades) > 0:
                high_confidence_losers = (losing_trades.get('confidence_level', pd.Series([0.5] * len(losing_trades))) > 0.7).sum()
                if high_confidence_losers / len(losing_trades) > 0.4:
                    confirmation_score += 35
                    evidence.append("Yuqori ishonch bilan yo'qotish")
            
            if confirmation_score >= 60:
                severity = 'high'
            elif confirmation_score >= 40:
                severity = 'medium'
            else:
                severity = 'low'
            
            return BiasAnalysis(
                bias_name="tasdiqlash xatosi",
                strength=min(100, confirmation_score),
                evidence=evidence,
                severity=severity,
                mitigation_strategies=[
                    "Qarama-qarshi dalillarni qidirish",
                    "Ob'ektiv ma'lumotlarga e'tibor qaratish",
                    "O'z fikrlarini sinab ko'rish",
                    "Boshqa nuqtai nazarlarni eshitish"
                ]
            )
            
        except Exception as e:
            logger.error(f"Error detecting confirmation bias: {e}")
            return self._default_bias("tasdiqlash xatosi")
    
    def _default_bias(self, name: str) -> BiasAnalysis:
        """Create default bias analysis"""
        return BiasAnalysis(
            bias_name=name,
            strength=30,
            evidence=["Ma'lumot yetarli emas"],
            severity='low',
            mitigation_strategies=["Qo'shimcha ma'lumot to'plash"]
        )
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """Get default analysis for insufficient data"""
        return {
            'trade_frequency': {'frequency_pattern': 'unknown', 'consistency_score': 50},
            'position_sizing': {'sizing_behavior': 'moderate', 'risk_score': 50},
            'risk_management': {'risk_management_score': 50, 'discipline_level': 'medium'},
            'performance_patterns': {'win_rate': 0.5, 'consistency_score': 50},
            'market_timing': {'timing_score': 50, 'timing_discipline': 'medium'},
            'emotional_patterns': {'emotional_trading_score': 50, 'impulsiveness_level': 'medium'},
            'win_loss_analysis': {'win_rate': 0.5, 'streak_behavior': 'mixed'}
        }
    
    def _get_default_biases(self) -> Dict[str, BiasAnalysis]:
        """Get default bias analyses"""
        return {
            'overconfidence': self._default_bias("o'ziga ishonch ortiqchaligi"),
            'loss_aversion': self._default_bias("yo'qotishlardan qochish"),
            'recency_bias': self._default_bias("yaqinlik xatosi"),
            'anchoring': self._default_bias("ilgaklash xatosi"),
            'mental_accounting': self._default_bias("hisob-kitob mentaliteti"),
            'herding': self._default_bias("ola quvish instinkti"),
            'confirmation': self._default_bias("tasdiqlash xatosi")
        }
    
    def analyze_risk_response(self, trading_history: List[Dict[str, Any]]) -> RiskResponsePattern:
        """
        Analyze how user responds to risk and losses
        
        Args:
            trading_history: Historical trading data
            
        Returns:
            RiskResponsePattern analysis
        """
        try:
            if not trading_history:
                return self._default_risk_response()
            
            df = pd.DataFrame(trading_history)
            
            # Loss tolerance analysis
            losses = df[df['profit_loss'] < 0]['profit_loss'].values
            tolerance_score = self._calculate_loss_tolerance(losses)
            
            # Recovery time analysis
            recovery_time = self._analyze_recovery_time(df)
            
            # Panic threshold
            panic_threshold = self._calculate_panic_threshold(df)
            
            # Risk behavior under stress
            stress_behavior = self._analyze_stress_behavior(df)
            
            return RiskResponsePattern(
                tolerance_for_losses=tolerance_score,
                time_to_recover=recovery_time,
                panic_threshold=panic_threshold,
                risk_increase_behavior=stress_behavior['risk_increase'],
                decision_speed_under_stress=stress_behavior['decision_speed']
            )
            
        except Exception as e:
            logger.error(f"Error analyzing risk response: {e}")
            return self._default_risk_response()
    
    def _calculate_loss_tolerance(self, losses: np.ndarray) -> float:
        """Calculate tolerance for losses"""
        if len(losses) == 0:
            return 50.0
        
        avg_loss = np.mean(np.abs(losses))
        max_loss = np.max(np.abs(losses))
        
        # Score based on ability to handle large losses
        tolerance_score = 100 - (max_loss / 100 * 10)  # Lower score for larger losses
        return max(0, min(100, tolerance_score))
    
    def _analyze_recovery_time(self, df: pd.DataFrame) -> int:
        """Analyze time to recover from losses"""
        try:
            df['trade_date'] = pd.to_datetime(df.get('timestamp', df.get('date', datetime.now())))
            df = df.sort_values('trade_date')
            df['cumulative_pnl'] = df.get('profit_loss', pd.Series([0])).cumsum()
            
            # Find drawdown periods and recovery
            peak = 0
            recovery_times = []
            
            for i, pnl in enumerate(df['cumulative_pnl']):
                if pnl > peak:
                    peak = pnl
                else:
                    # Find recovery
                    for j in range(i + 1, len(df)):
                        if df['cumulative_pnl'].iloc[j] >= peak:
                            recovery_time = (df['trade_date'].iloc[j] - df['trade_date'].iloc[i]).days
                            recovery_times.append(recovery_time)
                            break
            
            return int(np.mean(recovery_times)) if recovery_times else 30  # Default 30 days
            
        except Exception as e:
            logger.error(f"Error analyzing recovery time: {e}")
            return 30
    
    def _calculate_panic_threshold(self, df: pd.DataFrame) -> float:
        """Calculate panic threshold (maximum loss before panic selling)"""
        try:
            # Look for sudden large position changes or selling sprees after losses
            df['trade_date'] = pd.to_datetime(df.get('timestamp', df.get('date', datetime.now())))
            df = df.sort_values('trade_date')
            
            # Find consecutive sell orders after significant losses
            df['is_loss'] = df.get('profit_loss', pd.Series([0])) < 0
            df['consecutive_sells'] = 0
            
            current_sells = 0
            for is_loss in df['is_loss']:
                if is_loss:
                    current_sells += 1
                else:
                    if current_sells >= 3:  # 3+ consecutive losses
                        break
                    current_sells = 0
            
            # Estimate panic threshold based on loss patterns
            losses = df[df['is_loss']]['profit_loss'].values
            if len(losses) > 0:
                panic_threshold = np.percentile(np.abs(losses), 90)  # 90th percentile loss
            else:
                panic_threshold = 5.0  # Default 5%
            
            return float(panic_threshold)
            
        except Exception as e:
            logger.error(f"Error calculating panic threshold: {e}")
            return 5.0
    
    def _analyze_stress_behavior(self, df: pd.DataFrame) -> Dict[str, str]:
        """Analyze behavior under stress"""
        try:
            # Stress indicators: increased trade frequency, larger positions, poor decisions
            stress_indicators = 0
            
            # Rapid trading after losses
            df['trade_date'] = pd.to_datetime(df.get('timestamp', df.get('date', datetime.now())))
            df = df.sort_values('trade_date')
            df['time_between'] = df['trade_date'].diff().dt.total_seconds() / 3600  # hours
            
            rapid_after_loss = 0
            for i in range(len(df) - 1):
                if df.iloc[i]['profit_loss'] < 0 and df.iloc[i + 1]['time_between'] < 2:
                    rapid_after_loss += 1
            
            if rapid_after_loss > 2:
                stress_indicators += 1
            
            # Increased position sizes after losses
            position_increases = 0
            for i in range(len(df) - 1):
                if (df.iloc[i]['profit_loss'] < 0 and 
                    'position_size_pct' in df.columns and
                    i + 1 < len(df)):
                    current_size = df.iloc[i]['position_size_pct']
                    next_size = df.iloc[i + 1]['position_size_pct']
                    if next_size > current_size * 1.5:
                        position_increases += 1
            
            if position_increases > 1:
                stress_indicators += 1
            
            # Classify stress behavior
            if stress_indicators >= 2:
                risk_increase = "aggressive"
                decision_speed = "very_fast"
            elif stress_indicators == 1:
                risk_increase = "moderate"
                decision_speed = "fast"
            else:
                risk_increase = "controlled"
                decision_speed = "normal"
            
            return {
                'risk_increase': risk_increase,
                'decision_speed': decision_speed
            }
            
        except Exception as e:
            logger.error(f"Error analyzing stress behavior: {e}")
            return {'risk_increase': 'controlled', 'decision_speed': 'normal'}
    
    def _default_risk_response(self) -> RiskResponsePattern:
        """Create default risk response pattern"""
        return RiskResponsePattern(
            tolerance_for_losses=50.0,
            time_to_recover=30,
            panic_threshold=5.0,
            risk_increase_behavior="moderate",
            decision_speed_under_stress="normal"
        )
    
    def create_behavioral_profile(
        self,
        user_id: str,
        trading_history: List[Dict[str, Any]],
        questionnaire_data: Optional[Dict[str, Any]] = None
    ) -> InvestmentBehaviorProfile:
        """
        Create complete behavioral analysis profile
        
        Args:
            user_id: User identifier
            trading_history: Historical trading data
            questionnaire_data: Optional questionnaire responses
            
        Returns:
            Complete InvestmentBehaviorProfile
        """
        try:
            # Analyze trading behavior
            trading_analysis = self.analyze_trading_behavior(trading_history)
            
            # Detect behavioral biases
            bias_analysis = self.detect_behavioral_biases(trading_history)
            
            # Analyze risk response
            risk_response = self.analyze_risk_response(trading_history)
            
            # Extract behavioral patterns
            patterns = self._extract_behavioral_patterns(trading_analysis)
            
            # Determine decision making style
            decision_style = self._determine_decision_style(trading_analysis, risk_response)
            
            # Calculate emotional reactions
            emotional_reactions = self._calculate_emotional_reactions(trading_analysis, risk_response)
            
            # Determine learning pattern
            learning_pattern = self._determine_learning_pattern(trading_history)
            
            # Calculate bias scores
            bias_scores = self._calculate_bias_scores(bias_analysis)
            
            # Create profile
            profile = InvestmentBehaviorProfile(
                user_id=user_id,
                behavioral_patterns=patterns,
                bias_analysis=list(bias_analysis.values()),
                risk_response=risk_response,
                decision_making_style=decision_style,
                emotional_reactions=emotional_reactions,
                learning_pattern=learning_pattern,
                overconfidence_score=bias_scores['overconfidence'],
                loss_aversion_score=bias_scores['loss_aversion'],
                herd_instinct_score=bias_scores['herding'],
                recency_bias_score=bias_scores['recency'],
                anchoring_score=bias_scores['anchoring'],
                mental_accounting_score=bias_scores['mental'],
                last_updated=datetime.now(),
                confidence_level=0.85
            )
            
            logger.info(f"Created behavioral profile for user {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Error creating behavioral profile: {e}")
            return self._create_default_profile(user_id)
    
    def _extract_behavioral_patterns(self, trading_analysis: Dict[str, Any]) -> List[BehavioralPattern]:
        """Extract behavioral patterns from analysis"""
        patterns = []
        
        try:
            # Trade frequency pattern
            frequency_pattern = trading_analysis.get('trade_frequency', {})
            patterns.append(BehavioralPattern(
                pattern_name="Savdo chastotasi",
                intensity=100 - frequency_pattern.get('consistency_score', 50),
                description=frequency_pattern.get('frequency_pattern', 'noma\'lum'),
                impact_on_decisions="Yuqori chastota tez qaror qabul qilishga olib keladi",
                confidence_level=0.8
            ))
            
            # Risk management pattern
            risk_mgmt = trading_analysis.get('risk_management', {})
            patterns.append(BehavioralPattern(
                pattern_name="Xavf boshqaruv",
                intensity=100 - risk_mgmt.get('risk_management_score', 50),
                description=risk_mgmt.get('discipline_level', 'o\'rtacha'),
                impact_on_decisions="Disiplinsizlik katta yo'qotishlarga olib kelishi mumkin",
                confidence_level=0.9
            ))
            
            # Emotional trading pattern
            emotional = trading_analysis.get('emotional_patterns', {})
            patterns.append(BehavioralPattern(
                pattern_name="Emotsional savdo",
                intensity=emotional.get('emotional_trading_score', 50),
                description=emotional.get('impulsiveness_level', 'o\'rtacha'),
                impact_on_decisions="Impulsiv qarorlar moliyaviy yo'qotishlarga olib keladi",
                confidence_level=0.85
            ))
            
        except Exception as e:
            logger.error(f"Error extracting behavioral patterns: {e}")
            patterns = [BehavioralPattern(
                pattern_name="Noma'lum",
                intensity=50,
                description="Ma'lumot yetarli emas",
                impact_on_decisions="Aniqlanish qiyin",
                confidence_level=0.3
            )]
        
        return patterns
    
    def _determine_decision_style(
        self, 
        trading_analysis: Dict[str, Any], 
        risk_response: RiskResponsePattern
    ) -> str:
        """Determine user's decision making style"""
        try:
            # Analyze decision characteristics
            risk_mgmt = trading_analysis.get('risk_management', {}).get('risk_management_score', 50)
            emotional = trading_analysis.get('emotional_patterns', {}).get('emotional_trading_score', 50)
            timing = trading_analysis.get('market_timing', {}).get('timing_score', 50)
            
            # Decision style factors
            discipline_score = risk_mgmt
            impulsiveness_score = emotional
            systematic_score = timing
            
            # Classify decision style
            if discipline_score >= 80 and systematic_score >= 70:
                return "tizimli_va_diskresiyalashtirilgan"
            elif impulsiveness_score >= 70:
                return "impulsiv_va_tezhayotgan"
            elif systematic_score >= 60:
                return "tizimli_va_rejali"
            elif risk_response.risk_increase_behavior == "aggressive":
                return "yuqori_xavf_oluvchi"
            else:
                return "muvozanatlashgan"
                
        except Exception as e:
            logger.error(f"Error determining decision style: {e}")
            return "muvozanatlashgan"
    
    def _calculate_emotional_reactions(
        self, 
        trading_analysis: Dict[str, Any], 
        risk_response: RiskResponsePattern
    ) -> Dict[str, float]:
        """Calculate emotional reaction patterns"""
        reactions = {
            'stress_tolerance': 100 - risk_response.time_to_recover,
            'patience_level': 100 - (trading_analysis.get('emotional_patterns', {}).get('emotional_trading_score', 50)),
            'frustration_tolerance': 100 - risk_response.panic_threshold * 10,
            'excitement_control': trading_analysis.get('risk_management', {}).get('risk_management_score', 50),
            'fear_response': 100 - risk_response.tolerance_for_losses
        }
        
        # Normalize to 0-100 scale
        for key in reactions:
            reactions[key] = max(0, min(100, reactions[key]))
        
        return reactions
    
    def _determine_learning_pattern(self, trading_history: List[Dict[str, Any]]) -> str:
        """Determine user's learning pattern"""
        try:
            if not trading_history:
                return "no_learning_data"
            
            df = pd.DataFrame(trading_history)
            
            # Analyze if user improves over time
            df['trade_date'] = pd.to_datetime(df.get('timestamp', df.get('date', datetime.now())))
            df = df.sort_values('trade_date')
            
            # Split into early and late periods
            midpoint = len(df) // 2
            early_period = df.head(midpoint)
            late_period = df.tail(len(df) - midpoint)
            
            early_performance = early_period.get('profit_loss', pd.Series([0])).mean()
            late_performance = late_period.get('profit_loss', pd.Series([0])).mean()
            
            # Analyze position sizing changes
            early_positioning = early_period.get('position_size_pct', pd.Series([10] * len(early_period))).mean()
            late_positioning = late_period.get('position_size_pct', pd.Series([10] * len(late_period))).mean()
            
            # Determine learning pattern
            performance_improvement = late_performance - early_performance
            risk_management_improvement = abs(late_positioning - early_positioning) < early_positioning * 0.2
            
            if performance_improvement > early_performance * 0.2:
                return "tezhayotgan_va_o'rganuvchi"
            elif risk_management_improvement:
                return "tizimli_o'rganuvchi"
            elif abs(performance_improvement) < early_performance * 0.1:
                return "barqaror_lekin_asta_sekin_ilgarilash"
            else:
                return "qiyinchilik_bilan_o'rganuvchi"
                
        except Exception as e:
            logger.error(f"Error determining learning pattern: {e}")
            return "noma'lum"
    
    def _calculate_bias_scores(self, bias_analysis: Dict[str, BiasAnalysis]) -> Dict[str, float]:
        """Calculate individual bias scores"""
        return {
            'overconfidence': bias_analysis.get('overconfidence', self._default_bias("overconfidence")).strength,
            'loss_aversion': bias_analysis.get('loss_aversion', self._default_bias("loss_aversion")).strength,
            'herding': bias_analysis.get('herding', self._default_bias("herding")).strength,
            'recency': bias_analysis.get('recency_bias', self._default_bias("recency")).strength,
            'anchoring': bias_analysis.get('anchoring', self._default_bias("anchoring")).strength,
            'mental': bias_analysis.get('mental_accounting', self._default_bias("mental")).strength
        }
    
    def _create_default_profile(self, user_id: str) -> InvestmentBehaviorProfile:
        """Create default behavioral profile"""
        return InvestmentBehaviorProfile(
            user_id=user_id,
            behavioral_patterns=[
                BehavioralPattern(
                    pattern_name="Standart",
                    intensity=50,
                    description="Ma'lumot yetarli emas",
                    impact_on_decisions="Aniqlanish qiyin",
                    confidence_level=0.3
                )
            ],
            bias_analysis=[
                self._default_bias("umumiy"),
                self._default_bias("kuzatish")
            ],
            risk_response=self._default_risk_response(),
            decision_making_style="muvozanatlashgan",
            emotional_reactions={'stress_tolerance': 50, 'patience_level': 50},
            learning_pattern="noma'lum",
            overconfidence_score=50,
            loss_aversion_score=50,
            herd_instinct_score=50,
            recency_bias_score=50,
            anchoring_score=50,
            mental_accounting_score=50,
            last_updated=datetime.now(),
            confidence_level=0.3
        )
    
    def update_behavioral_profile(
        self, 
        existing_profile: InvestmentBehaviorProfile, 
        new_trading_data: List[Dict[str, Any]]
    ) -> InvestmentBehaviorProfile:
        """
        Update existing behavioral profile with new data
        
        Args:
            existing_profile: Current behavioral profile
            new_trading_data: New trading data to analyze
            
        Returns:
            Updated InvestmentBehaviorProfile
        """
        try:
            # Re-analyze with new data
            combined_data = new_trading_data  # In practice, would combine with existing data
            
            # Update behavioral analysis
            updated_analysis = self.analyze_trading_behavior(combined_data)
            updated_biases = self.detect_behavioral_biases(combined_data)
            updated_risk_response = self.analyze_risk_response(combined_data)
            
            # Update components
            existing_profile.behavioral_patterns = self._extract_behavioral_patterns(updated_analysis)
            existing_profile.bias_analysis = list(updated_biases.values())
            existing_profile.risk_response = updated_risk_response
            existing_profile.decision_making_style = self._determine_decision_style(updated_analysis, updated_risk_response)
            existing_profile.emotional_reactions = self._calculate_emotional_reactions(updated_analysis, updated_risk_response)
            existing_profile.learning_pattern = self._determine_learning_pattern(combined_data)
            
            # Update bias scores
            bias_scores = self._calculate_bias_scores(updated_biases)
            existing_profile.overconfidence_score = bias_scores['overconfidence']
            existing_profile.loss_aversion_score = bias_scores['loss_aversion']
            existing_profile.herd_instinct_score = bias_scores['herding']
            existing_profile.recency_bias_score = bias_scores['recency']
            existing_profile.anchoring_score = bias_scores['anchoring']
            existing_profile.mental_accounting_score = bias_scores['mental']
            
            # Update confidence level
            existing_profile.confidence_level = min(0.95, existing_profile.confidence_level + 0.1)
            existing_profile.last_updated = datetime.now()
            
            logger.info(f"Updated behavioral profile for user {existing_profile.user_id}")
            return existing_profile
            
        except Exception as e:
            logger.error(f"Error updating behavioral profile: {e}")
            return existing_profile

# Example usage and testing
if __name__ == "__main__":
    # Initialize behavior analyzer
    analyzer = UserBehaviorAnalyzer()
    
    # Sample trading history
    sample_trades = [
        {
            'timestamp': '2024-01-01',
            'profit_loss': 100,
            'position_size_pct': 10,
            'asset_type': 'stock'
        },
        {
            'timestamp': '2024-01-05',
            'profit_loss': -50,
            'position_size_pct': 15,
            'asset_type': 'stock'
        },
        {
            'timestamp': '2024-01-10',
            'profit_loss': 200,
            'position_size_pct': 20,
            'asset_type': 'etf'
        }
        # Add more sample data as needed
    ]
    
    # Analyze trading behavior
    behavior_analysis = analyzer.analyze_trading_behavior(sample_trades)
    print("Trading Behavior Analysis:")
    for key, value in behavior_analysis.items():
        print(f"{key}: {value}")
    
    # Detect behavioral biases
    biases = analyzer.detect_behavioral_biases(sample_trades)
    print("\nBehavioral Biases:")
    for bias_name, bias in biases.items():
        print(f"{bias_name}: {bias.strength} - {bias.severity}")
    
    # Create comprehensive profile
    profile = analyzer.create_behavioral_profile("user_123", sample_trades)
    print(f"\nBehavioral Profile for {profile.user_id}:")
    print(f"Decision Style: {profile.decision_making_style}")
    print(f"Overconfidence: {profile.overconfidence_score}")
    print(f"Learning Pattern: {profile.learning_pattern}")
    print(f"Confidence Level: {profile.confidence_level}")