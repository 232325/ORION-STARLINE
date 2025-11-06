"""
Market Regime Detection Module
Advanced market regime detection using multiple approaches
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from sklearn.mixture import GaussianMixture
from sklearn.cluster import KMeans
from scipy import stats
from scipy.optimize import minimize_scalar
import warnings

warnings.filterwarnings('ignore')

class RegimeDetector:
    """
    Asosiy market regime detection class
    Trending, Ranging, High Volatility, Low Volatility, Crisis rejimlarini aniqlaydi
    """
    
    def __init__(self, lookback_window: int = 252, transition_threshold: float = 0.7):
        """
        Args:
            lookback_window: Regime aniqlash uchun tarixiy ma'lumotlar soni
            transition_threshold: Rejim o'tish uchun ishonchlilik chegarasi
        """
        self.lookback_window = lookback_window
        self.transition_threshold = transition_threshold
        self.regime_history = []
        self.current_regime = "Unknown"
        
    def detect_trending_market(self, prices: pd.Series, window: int = 20) -> pd.Series:
        """
        Trending market detection
        
        Args:
            prices: Narx ma'lumotlari
            window: Trend tahlil uchun davomiylik
            
        Returns:
            Boolean series: True agar trend market bo'lsa
        """
        returns = prices.pct_change().dropna()
        
        # Linear trend slope
        def linear_trend(x, y):
            slope, intercept, r_value, _, _ = stats.linregress(x, y)
            return slope, r_value**2
            
        trend_signals = []
        
        for i in range(window, len(returns)):
            y_window = returns.iloc[i-window:i]
            x_window = np.arange(len(y_window))
            
            slope, r_squared = linear_trend(x_window, y_window)
            
            # Significant trend indicator
            strong_trend = abs(slope) > np.std(y_window) * 2 and r_squared > 0.6
            
            trend_signals.append(strong_trend)
            
        return pd.Series(trend_signals, index=returns.iloc[window:].index)
        
    def detect_ranging_market(self, prices: pd.Series, window: int = 20) -> pd.Series:
        """
        Ranging market detection
        
        Args:
            prices: Narx ma'lumotlari
            window: Range tahlil uchun davomiylik
            
        Returns:
            Boolean series: True agar ranging market bo'lsa
        """
        returns = prices.pct_change().dropna()
        
        ranging_signals = []
        
        for i in range(window, len(returns)):
            price_window = prices.iloc[i-window:i]
            returns_window = returns.iloc[i-window:i]
            
            # Calculate price range
            price_range = (price_window.max() - price_window.min()) / price_window.mean()
            # Calculate mean reversion tendency
            mean_reversion = abs(returns_window.mean()) < np.std(returns_window) * 0.5
            
            # Ranging market: low range + mean reversion
            ranging = price_range < 0.05 and mean_reversion
            
            ranging_signals.append(ranging)
            
        return pd.Series(ranging_signals, index=returns.iloc[window:].index)
        
    def detect_volatility_regime(self, returns: pd.Series, window: int = 20) -> pd.Series:
        """
        Volatility regime detection (High/Low)
        
        Args:
            returns: Return ma'lumotlari
            window: Volatility hisoblash davomiyligi
            
        Returns:
            Series: 'High', 'Low', yoki 'Normal' volatility rejimi
        """
        rolling_vol = returns.rolling(window=window).std()
        
        # Volatility percentiles
        vol_75 = rolling_vol.quantile(0.75)
        vol_25 = rolling_vol.quantile(0.25)
        
        volatility_regimes = []
        
        for vol in rolling_vol:
            if pd.isna(vol):
                volatility_regimes.append('Unknown')
            elif vol >= vol_75:
                volatility_regimes.append('High')
            elif vol <= vol_25:
                volatility_regimes.append('Low')
            else:
                volatility_regimes.append('Normal')
                
        return pd.Series(volatility_regimes, index=rolling_vol.index)
        
    def detect_crisis_regime(self, returns: pd.Series, window: int = 60) -> pd.Series:
        """
        Crisis regime identification
        
        Args:
            returns: Return ma'lumotlari
            window: Crisis detection davomiylik
            
        Returns:
            Boolean series: True agar crisis period bo'lsa
        """
        if len(returns) < window:
            return pd.Series([False] * len(returns), index=returns.index)
            
        cumulative_returns = (1 + returns).cumprod()
        drawdown = (cumulative_returns / cumulative_returns.cummax()) - 1
        
        crisis_signals = []
        
        for i in range(window, len(returns)):
            # Severe drawdown
            recent_drawdown = drawdown.iloc[i-window:i].min()
            
            # Extreme volatility
            recent_vol = returns.iloc[i-window:i].std()
            long_term_vol = returns.iloc[i-window*2:i-window].std() if i >= window*2 else recent_vol
            
            vol_spike = recent_vol > long_term_vol * 2
            
            # Negative momentum
            recent_momentum = returns.iloc[i-window:i].sum()
            
            # Crisis conditions
            crisis = (recent_drawdown < -0.15 or vol_spike) and recent_momentum < -0.1
            
            crisis_signals.append(crisis)
            
        return pd.Series(crisis_signals, index=returns.iloc[window:].index)
        
    def detect_all_regimes(self, prices: pd.Series) -> Dict[str, pd.Series]:
        """
        Barcha rejimlarni aniqlash
        
        Args:
            prices: Narx ma'lumotlari
            
        Returns:
            Dict: Barcha rejim signals
        """
        returns = prices.pct_change().dropna()
        
        regimes = {
            'trending': self.detect_trending_market(prices),
            'ranging': self.detect_ranging_market(prices),
            'volatility_regime': self.detect_volatility_regime(returns),
            'crisis': self.detect_crisis_regime(returns)
        }
        
        return regimes
        
    def get_current_regime(self, prices: pd.Series) -> str:
        """
        Joriy market rejimini aniqlash
        
        Args:
            prices: Narx ma'lumotlari
            
        Returns:
            str: Joriy rejim nomi
        """
        if len(prices) < 60:
            return "Insufficient Data"
            
        returns = prices.pct_change().dropna()
        
        # Get recent signals
        recent_trending = self.detect_trending_market(prices).iloc[-1] if len(prices) > 20 else False
        recent_ranging = self.detect_ranging_market(prices).iloc[-1] if len(prices) > 20 else False
        recent_vol_regime = self.detect_volatility_regime(returns).iloc[-1] if len(returns) > 20 else 'Unknown'
        recent_crisis = self.detect_crisis_regime(returns).iloc[-1] if len(returns) > 60 else False
        
        # Determine dominant regime
        if recent_crisis:
            return "Crisis"
        elif recent_vol_regime == 'High':
            return "High Volatility"
        elif recent_vol_regime == 'Low':
            return "Low Volatility"
        elif recent_trending:
            return "Trending"
        elif recent_ranging:
            return "Ranging"
        else:
            return "Mixed/Neutral"
            
    def analyze_regime_transitions(self, regime_series: pd.Series) -> Dict:
        """
        Rejim o'tishlarini tahlil qilish
        
        Args:
            regime_series: Rejim time series
            
        Returns:
            Dict: Transition statistics
        """
        if len(regime_series) < 2:
            return {}
            
        # Transition matrix calculation
        regimes = regime_series.unique()
        n_regimes = len(regimes)
        transition_matrix = np.zeros((n_regimes, n_regimes))
        
        regime_to_idx = {regime: i for i, regime in enumerate(regimes)}
        
        for i in range(len(regime_series) - 1):
            current_regime = regime_series.iloc[i]
            next_regime = regime_series.iloc[i + 1]
            
            current_idx = regime_to_idx[current_regime]
            next_idx = regime_to_idx[next_regime]
            
            transition_matrix[current_idx, next_idx] += 1
            
        # Normalize to probabilities
        for i in range(n_regimes):
            row_sum = transition_matrix[i, :].sum()
            if row_sum > 0:
                transition_matrix[i, :] /= row_sum
                
        # Calculate regime persistence
        persistence = np.diag(transition_matrix)
        
        return {
            'regimes': regimes,
            'transition_matrix': pd.DataFrame(
                transition_matrix, 
                index=regimes, 
                columns=regimes
            ),
            'persistence': dict(zip(regimes, persistence)),
            'most_persistent_regime': regimes[np.argmax(persistence)]
        }


class HiddenMarkovRegimeDetector:
    """
    Hidden Markov Model bilan Regime Detection
    """
    
    def __init__(self, n_regimes: int = 3, max_iter: int = 100):
        """
        Args:
            n_regimes: Rejimlar soni
            max_iter: Maksimum iteratsiya soni
        """
        self.n_regimes = n_regimes
        self.max_iter = max_iter
        self.model = None
        self.fitted = False
        
    def prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """
        HMM uchun xususiyatlarni tayyorlash
        
        Args:
            data: Price va return ma'lumotlari
            
        Returns:
            np.ndarray: HMM xususiyatlari
        """
        features = []
        
        # Return features
        returns = data['price'].pct_change().dropna()
        features.append(returns.values.reshape(-1, 1))
        
        # Volatility features
        if len(returns) > 20:
            rolling_vol = returns.rolling(20).std()
            features.append(rolling_vol.dropna().values.reshape(-1, 1))
            
        # Momentum features
        if len(returns) > 10:
            momentum = returns.rolling(10).sum()
            features.append(momentum.dropna().values.reshape(-1, 1))
            
        return np.hstack(features)
        
    def fit(self, data: pd.DataFrame):
        """
        HMM model fit qilish
        
        Args:
            data: Price ma'lumotlari
        """
        features = self.prepare_features(data)
        
        if len(features) == 0:
            raise ValueError("Insufficient data for HMM fitting")
            
        self.model = GaussianMixture(
            n_components=self.n_regimes,
            covariance_type='full',
            max_iter=self.max_iter
        )
        
        self.model.fit(features)
        self.fitted = True
        
    def predict_regimes(self, data: pd.DataFrame) -> pd.Series:
        """
        Rejimlarni bashorat qilish
        
        Args:
            data: Price ma'lumotlari
            
        Returns:
            pd.Series: Bashorat qilingan rejimlar
        """
        if not self.fitted:
            raise ValueError("Model must be fitted first")
            
        features = self.prepare_features(data)
        regime_probs = self.model.predict_proba(features)
        predicted_regimes = self.model.predict(features)
        
        # Map regime numbers to names
        regime_names = {
            0: "Regime_1",
            1: "Regime_2", 
            2: "Regime_3",
            3: "Regime_4",
            4: "Regime_5"
        }
        
        regime_labels = [regime_names.get(r, f"Regime_{r+1}") for r in predicted_regimes]
        
        return pd.Series(regime_labels, index=data.index[-len(regime_labels):])
        
    def get_regime_probabilities(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Rejim ehtimolliklarini olish
        
        Args:
            data: Price ma'lumotlari
            
        Returns:
            pd.DataFrame: Rejim ehtimolliklari
        """
        if not self.fitted:
            raise ValueError("Model must be fitted first")
            
        features = self.prepare_features(data)
        regime_probs = self.model.predict_proba(features)
        
        prob_df = pd.DataFrame(
            regime_probs,
            index=data.index[-len(regime_probs):],
            columns=[f"Regime_{i+1}_Prob" for i in range(self.n_regimes)]
        )
        
        return prob_df


class RegimeAnalyzer:
    """
    Regime tahlil va statistika
    """
    
    def __init__(self):
        self.regime_stats = {}
        
    def analyze_regime_characteristics(self, prices: pd.Series, regimes: Dict[str, pd.Series]) -> Dict:
        """
        Rejim xususiyatlarini tahlil qilish
        
        Args:
            prices: Narx ma'lumotlari
            regimes: Rejim signals
            
        Returns:
            Dict: Rejim statistikalari
        """
        returns = prices.pct_change().dropna()
        stats_by_regime = {}
        
        for regime_name, regime_signals in regimes.items():
            if len(regime_signals) == 0:
                continue
                
            # Align returns with regime signals
            common_index = returns.index.intersection(regime_signals.index)
            if len(common_index) == 0:
                continue
                
            regime_returns = returns[common_index]
            signal_series = regime_signals[common_index]
            
            # Calculate statistics for each regime state
            unique_states = signal_series.unique()
            regime_stats = {}
            
            for state in unique_states:
                if pd.isna(state):
                    continue
                    
                mask = signal_series == state
                state_returns = regime_returns[mask]
                
                if len(state_returns) > 0:
                    regime_stats[str(state)] = {
                        'count': mask.sum(),
                        'avg_return': state_returns.mean(),
                        'volatility': state_returns.std(),
                        'sharpe_ratio': state_returns.mean() / state_returns.std() if state_returns.std() > 0 else 0,
                        'max_drawdown': self._calculate_max_drawdown((1 + state_returns).cumprod()),
                        'win_rate': (state_returns > 0).mean()
                    }
            
            stats_by_regime[regime_name] = regime_stats
            
        return stats_by_regime
        
    def _calculate_max_drawdown(self, cumulative_returns: pd.Series) -> float:
        """Maximum drawdown hisoblash"""
        peak = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - peak) / peak
        return drawdown.min()
        
    def regime_performance_attribution(self, portfolio_returns: pd.Series, regimes: Dict[str, pd.Series]) -> pd.DataFrame:
        """
        Portfolio performance attribution by regime
        
        Args:
            portfolio_returns: Portfolio returnlari
            regimes: Rejim signals
            
        Returns:
            pd.DataFrame: Regime-based performance attribution
        """
        attribution_results = {}
        
        for regime_name, regime_signals in regimes.items():
            # Find overlapping periods
            common_index = portfolio_returns.index.intersection(regime_signals.index)
            
            if len(common_index) == 0:
                continue
                
            portfolio_common = portfolio_returns[common_index]
            signal_common = regime_signals[common_index]
            
            attribution_by_state = {}
            
            for state in signal_common.unique():
                if pd.isna(state):
                    continue
                    
                mask = signal_common == state
                state_returns = portfolio_common[mask]
                
                if len(state_returns) > 0:
                    attribution_by_state[str(state)] = {
                        'periods': mask.sum(),
                        'avg_return': state_returns.mean(),
                        'total_return': state_returns.sum(),
                        'volatility': state_returns.std(),
                        'contribution_to_total': state_returns.sum() / portfolio_returns.sum() if portfolio_returns.sum() != 0 else 0
                    }
            
            attribution_results[regime_name] = attribution_by_state
            
        return pd.DataFrame(attribution_results).T


if __name__ == "__main__":
    # Test
    import matplotlib.pyplot as plt
    
    # Sample data generation
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=1000, freq='D')
    
    # Create sample price data with regime changes
    returns = np.random.normal(0.001, 0.02, 1000)
    returns[200:400] = np.random.normal(0.003, 0.03, 200)  # High volatility period
    returns[600:800] = np.random.normal(0, 0.01, 200)     # Low volatility period
    
    prices = pd.Series(100 * (1 + returns).cumprod(), index=dates)
    
    # Test regime detection
    detector = RegimeDetector()
    regimes = detector.detect_all_regimes(prices)
    
    current_regime = detector.get_current_regime(prices)
    
    print(f"Current regime: {current_regime}")
    print(f"Regime detection completed for {len(prices)} data points")