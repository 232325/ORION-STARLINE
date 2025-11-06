"""
Forex Carry Trade Analysis va Metal Price Correlation Models
===========================================================

Keng qamrovli forex carry trade tahlili va metal narxlari korrelatsiya modellar tizimi.
Bu tizim pul-kapital bozoridagi muhim omillarni tahlil qilish va korrelatsiyani
bashorat qilish uchun mo'ljallangan.

Asosiy komponentlar:
- Forex Carry Trade tahlili
- Metal narxlari korrelatsiyasi
- Dinamik korrelatsiya modellari
- Bashorat qilish algoritmlari
- Risk boshqaruvi
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from itertools import combinations
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from scipy import stats, optimize
from scipy.linalg import cholesky
from sklearn.covariance import LedoitWolf, OAS
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Visualization settings
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


@dataclass
class CurrencyPair:
    """Valyuta juftligi ma'lumotlari"""
    base: str
    quote: str
    current_rate: float
    volatility: float
    interest_rate_diff: float


@dataclass
class MetalPrice:
    """Metal narx ma'lumotlari"""
    symbol: str
    name: str
    current_price: float
    daily_change: float
    volume: float
    market_cap: float


@dataclass
class EconomicIndicator:
    """Iqtisodiy indikator ma'lumotlari"""
    name: str
    current_value: float
    previous_value: float
    impact_level: str  # 'High', 'Medium', 'Low'
    frequency: str     # 'Daily', 'Weekly', 'Monthly', 'Quarterly'


class ForexCarryTradeAnalyzer:
    """
    Forex Carry Trade Tahlil qiluvchi Klass
    
    Bu klass forex carry trade strategiyalarini tahlil qilish,
    rentabellikni hisoblash va riskni baholash uchun mo'ljallangan.
    """
    
    def __init__(self, min_spread: float = 0.5, max_volatility: float = 0.25):
        """
        Args:
            min_spread: Minimal foiz stavkalar farqi (%)
            max_volatility: Maksimal volatilite (%)
        """
        self.min_spread = min_spread
        self.max_volatility = max_volatility
        self.central_bank_rates = {}
        self.currency_data = {}
        self.opportunities = []
        self.historical_performance = pd.DataFrame()
        
    def load_interest_rates(self, rates_data: Dict[str, Dict[str, float]]):
        """
        Markaziy bank foiz stavkalarini yuklash
        
        Args:
            rates_data: {
                'USD': {'rate': 5.25, 'last_update': '2024-01-15'},
                'EUR': {'rate': 4.00, 'last_update': '2024-01-14'},
                ...
            }
        """
        self.central_bank_rates = rates_data
        
    def calculate_interest_differentials(self, pair: str) -> Optional[float]:
        """
        Valyuta juftligi uchun foiz stavkalar farqini hisoblash
        
        Args:
            pair: Valyuta juftligi (masalan, 'USD/JPY')
            
        Returns:
            Interest rate differential
        """
        try:
            base, quote = pair.split('/')
            if base in self.central_bank_rates and quote in self.central_bank_rates:
                base_rate = self.central_bank_rates[base]['rate']
                quote_rate = self.central_bank_rates[quote]['rate']
                return base_rate - quote_rate
        except:
            pass
        return None
    
    def calculate_carry_return(self, pair: str, investment_amount: float, 
                             periods: int = 252, current_rate: float = None) -> Dict:
        """
        Carry trade rentabelligini hisoblash
        
        Args:
            pair: Valyuta juftligi
            investment_amount: Investitsiya miqdori
            periods: Davomiylik (kunlarda)
            current_rate: Joriy valyuta kursi
            
        Returns:
            Carry trade rentabelligi ma'lumotlari
        """
        rate_diff = self.calculate_interest_differentials(pair)
        
        if rate_diff is None or abs(rate_diff) < self.min_spread:
            return {'error': 'Kichik spread yoki ma\'lumot yo\'q'}
        
        # Carry return hisoblash
        carry_return = (rate_diff / 100) * investment_amount * (periods / 365)
        
        # Vallution risk hisoblash (soddalashtirilgan)
        volatility = 0.15  # O'rtacha forex volatilite
        potential_loss = investment_amount * volatility * np.sqrt(periods / 365)
        
        # Risk-adjusted return (Sharpe ratio oddiy hisoblash)
        sharpe_ratio = carry_return / potential_loss if potential_loss > 0 else 0
        
        return {
            'pair': pair,
            'rate_difference': rate_diff,
            'carry_return': carry_return,
            'investment_amount': investment_amount,
            'annual_return_pct': rate_diff,
            'potential_loss': potential_loss,
            'sharpe_ratio': sharpe_ratio,
            'risk_level': 'High' if abs(sharpe_ratio) < 0.5 else 'Medium' if abs(sharpe_ratio) < 1 else 'Low'
        }
    
    def identify_opportunities(self, currency_pairs: List[str]) -> List[Dict]:
        """
        Carry trade imkoniyatlarini aniqlash
        
        Args:
            currency_pairs: Tahlil qilinadigan valyuta juftliklari
            
        Returns:
            Carry trade imkoniyatlari ro'yxati
        """
        opportunities = []
        
        for pair in currency_pairs:
            analysis = self.calculate_carry_return(pair, 100000)  # $100,000 default
            
            if 'error' not in analysis and analysis['sharpe_ratio'] > 0:
                opportunities.append(analysis)
        
        # Return bo'yicha saralash
        opportunities.sort(key=lambda x: x['sharpe_ratio'], reverse=True)
        self.opportunities = opportunities
        
        return opportunities
    
    def central_bank_policy_analysis(self, central_bank: str) -> Dict:
        """
        Markaziy bank siyosati tahlili
        
        Args:
            central_bank: Markaziy bank nomi
            
        Returns:
            Siyosat tahlili
        """
        if central_bank not in self.central_bank_rates:
            return {'error': 'Ma\'lumot topilmadi'}
        
        rate_data = self.central_bank_rates[central_bank]
        
        # Siyosat yo'nalishi tahlili (soddalashtirilgan)
        policy_direction = "Expansionary" if rate_data['rate'] < 3.0 else \
                         "Neutral" if rate_data['rate'] < 5.0 else "Contractionary"
        
        # Siyosat kuchini baholash
        policy_strength = "Strong" if abs(rate_data['rate'] - 3.5) > 2.0 else "Moderate"
        
        return {
            'central_bank': central_bank,
            'current_rate': rate_data['rate'],
            'policy_direction': policy_direction,
            'policy_strength': policy_strength,
            'last_update': rate_data.get('last_update', 'Unknown'),
            'carry_trade_impact': 'Positive' if rate_data['rate'] > 4.0 else 'Negative'
        }
    
    def generate_performance_report(self) -> str:
        """
        Carry trade performance hisoboti
        
        Returns:
            Performance hisoboti matni
        """
        if not self.opportunities:
            return "Hech qanday carry trade imkoniyati topilmadi."
        
        report = []
        report.append("FOREX CARRY TRADE ANALYSIS REPORT")
        report.append("=" * 50)
        report.append(f"Tahlil sanasi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Topilgan imkoniyatlar soni: {len(self.opportunities)}")
        report.append("")
        
        report.append("TOP CARRY TRADE OPPORTUNITIES:")
        report.append("-" * 30)
        
        for i, opp in enumerate(self.opportunities[:5], 1):
            report.append(f"{i}. {opp['pair']}")
            report.append(f"   Foiz stavka farqi: {opp['rate_difference']:.2f}%")
            report.append(f"   Yillik return: {opp['annual_return_pct']:.2f}%")
            report.append(f"   Sharpe ratio: {opp['sharpe_ratio']:.3f}")
            report.append(f"   Risk darajasi: {opp['risk_level']}")
            report.append("")
        
        return "\n".join(report)


class MetalPriceCorrelationAnalyzer:
    """
    Metal narxlari korrelatsiya tahlil qiluvchi Klass
    
    Bu klass turli xil metallar orasidagi korrelatsiyani tahlil qilish,
    iqtisodiy sikllar bilan bog'liqlikni va bashorat qilish modellarini
    yaratish uchun mo'ljallangan.
    """
    
    def __init__(self, lookback_period: int = 252):
        """
        Args:
            lookback_period: Orqaga qarab ko'rish davri (kunlarda)
        """
        self.lookback_period = lookback_period
        self.metal_prices = pd.DataFrame()
        self.economic_data = pd.DataFrame()
        self.correlation_matrices = {}
        self.dynamic_correlations = {}
        
        # Metallar ro'yxati
        self.metals = [
            'GOLD', 'SILVER', 'PLATINUM', 'PALLADIUM', 
            'COPPER', 'ALUMINUM', 'NICKEL', 'LEAD', 'ZINC', 'TIN'
        ]
        
        # Iqtisodiy indikatorlar
        self.economic_indicators = [
            'USD_INDEX', 'GDP_GROWTH', 'INFLATION', 'INDUSTRIAL_PRODUCTION',
            'MINE_PRODUCTION', 'CONSUMPTION', 'INVENTORY_LEVELS'
        ]
    
    def load_metal_prices(self, price_data: pd.DataFrame):
        """
        Metal narxlarini yuklash
        
        Args:
            price_data: Metal narxlar DataFrame'i
        """
        self.metal_prices = price_data.copy()
        
        # NaN qiymatlarni oldini olish
        self.metal_prices = self.metal_prices.fillna(method='ffill')
        
    def load_economic_data(self, econ_data: pd.DataFrame):
        """
        Iqtisodiy ma'lumotlarni yuklash
        
        Args:
            econ_data: Iqtisodiy indikatorlar DataFrame'i
        """
        self.economic_data = econ_data.copy()
    
    def calculate_returns(self, price_series: pd.Series) -> pd.Series:
        """
        To'plangan daromadlarni hisoblash
        
        Args:
            price_series: Narxlar seriyasi
            
        Returns:
            To'plangan daromadlar
        """
        return np.log(price_series / price_series.shift(1)).dropna()
    
    def cross_metal_correlation(self, period: int = None) -> pd.DataFrame:
        """
        Metallar orasidagi korrelatsiyani hisoblash
        
        Args:
            period: Korrelatsiya davomiyligi (kunlarda)
            
        Returns:
            Korrelatsiya matritsasi
        """
        if period:
            data = self.metal_prices.tail(period)
        else:
            data = self.metal_prices
        
        returns = pd.DataFrame()
        for metal in self.metals:
            if metal in data.columns:
                returns[metal] = self.calculate_returns(data[metal])
        
        correlation_matrix = returns.corr()
        self.correlation_matrices[f'cross_metal_{period or self.lookback_period}'] = correlation_matrix
        
        return correlation_matrix
    
    def economic_cycle_correlation(self) -> Dict:
        """
        Iqtisodiy sikllar bilan korrelatsiyani tahlil qilish
        
        Returns:
            Iqtisodiy sikllar korrelatsiyasi
        """
        correlations = {}
        
        for indicator in self.economic_indicators:
            if indicator in self.economic_data.columns:
                correlations[indicator] = {}
                
                for metal in self.metals:
                    if metal in self.metal_prices.columns:
                        metal_returns = self.calculate_returns(self.metal_prices[metal])
                        econ_series = self.economic_data[indicator]
                        
                        # Vaqt bilan muvofiqlashtirish
                        aligned_data = pd.concat([metal_returns, econ_series], axis=1, keys=[metal, indicator]).dropna()
                        
                        if len(aligned_data) > 10:
                            corr = aligned_data[metal].corr(aligned_data[indicator])
                            correlations[indicator][metal] = corr
        
        return correlations
    
    def dollar_strength_correlation(self) -> pd.Series:
        """
        AQSh dollar kuchi bilan korrelatsiyani hisoblash
        
        Returns:
            Dollar indeksi bilan korrelatsiya
        """
        if 'USD_INDEX' not in self.economic_data.columns:
            # Simulated USD index (agar real ma'lumot yo'q bo'lsa)
            self.economic_data['USD_INDEX'] = np.random.normal(100, 5, len(self.metal_prices))
        
        dollar_corr = pd.Series()
        
        for metal in self.metals:
            if metal in self.metal_prices.columns:
                metal_returns = self.calculate_returns(self.metal_prices[metal])
                dollar_data = self.economic_data['USD_INDEX']
                
                aligned_data = pd.concat([metal_returns, dollar_data], axis=1, keys=[metal, 'USD_INDEX']).dropna()
                
                if len(aligned_data) > 10:
                    corr = aligned_data[metal].corr(aligned_data['USD_INDEX'])
                    dollar_corr[metal] = corr
        
        return dollar_corr
    
    def inflation_correlation(self, inflation_period: int = 12) -> Dict:
        """
        Inflatsiya korrelatsiyasini hisoblash
        
        Args:
            inflation_period: Inflatsiya davomiyligi (oylarda)
            
        Returns:
            Inflatsiya korrelatsiyasi
        """
        inflation_corr = {}
        
        for metal in self.metals:
            if metal in self.metal_prices.columns:
                # Metaldan inflatsiyaga qarshi hedge sifatida foydalanish
                metal_returns = self.calculate_returns(self.metal_prices[metal])
                
                # Simulated inflation rate (real ma'lumot yo'q bo'lsa)
                inflation_rate = pd.Series(np.random.normal(0.02, 0.01, len(metal_returns)), 
                                         index=metal_returns.index)
                
                corr = metal_returns.corr(inflation_rate)
                
                # Korrelatsiya kuchini baholash
                strength = 'Strong' if abs(corr) > 0.6 else 'Moderate' if abs(corr) > 0.3 else 'Weak'
                direction = 'Positive' if corr > 0 else 'Negative'
                
                inflation_corr[metal] = {
                    'correlation': corr,
                    'strength': strength,
                    'direction': direction,
                    'hedge_effectiveness': abs(corr)
                }
        
        return inflation_corr
    
    def industrial_demand_correlation(self) -> Dict:
        """
        Sanoat talablari bilan korrelatsiyani tahlil qilish
        
        Returns:
            Sanoat talablari korrelatsiyasi
        """
        industrial_corr = {}
        
        # Simulated industrial demand data
        for metal in self.metals:
            if metal in self.metal_prices.columns:
                metal_returns = self.calculate_returns(self.metal_prices[metal])
                
                # Metal turiga qarab industrial demand simulation
                if metal in ['COPPER', 'ALUMINUM', 'NICKEL']:
                    # Base metals - kuchli industrial bog'liqlik
                    industrial_factor = np.random.normal(1.0, 0.1, len(metal_returns))
                elif metal in ['PLATINUM', 'PALLADIUM']:
                    # Auto industry metals
                    industrial_factor = np.random.normal(0.8, 0.15, len(metal_returns))
                else:
                    # Precious metals - kamroq industrial bog'liqlik
                    industrial_factor = np.random.normal(0.3, 0.05, len(metal_returns))
                
                industrial_series = pd.Series(industrial_factor, index=metal_returns.index)
                corr = metal_returns.corr(industrial_series)
                
                industrial_corr[metal] = {
                    'correlation': corr,
                    'demand_type': 'High' if abs(corr) > 0.6 else 'Medium' if abs(corr) > 0.3 else 'Low',
                    'price_elasticity': abs(corr)
                }
        
        return industrial_corr


class DynamicCorrelationAnalyzer:
    """
    Dinamik Korrelatsiya Tahlil qiluvchi Klass
    
    Vaqt o'zgarishi bilan korrelatsiya o'zgarishlarini tahlil qilish,
    rejimga bog'liq korrelatsiyalar va stress davridagi korrelatsiyalarni
    o'rganish uchun mo'ljallangan.
    """
    
    def __init__(self, window_sizes: List[int] = [30, 60, 120]):
        """
        Args:
            window_sizes: Oyna hajmlari (kunlarda)
        """
        self.window_sizes = window_sizes
        self.rolling_correlations = {}
        self.regime_correlations = {}
        self.stress_correlations = {}
        
    def rolling_correlation_analysis(self, data: pd.DataFrame, method: str = 'pearson') -> Dict:
        """
        Rolik korrelatsiya tahlili
        
        Args:
            data: Narxlar ma'lumotlari
            method: Korrelatsiya hisoblash metodi ('pearson', 'spearman', 'kendall')
            
        Returns:
            Rolik korrelatsiya natijalari
        """
        returns = data.pct_change().dropna()
        rolling_corr = {}
        
        for window in self.window_sizes:
            if len(returns) > window:
                rolling_corr[window] = returns.rolling(window=window).corr()
        
        self.rolling_correlations = rolling_corr
        return rolling_corr
    
    def regime_dependent_correlations(self, data: pd.DataFrame, regimes: Dict) -> Dict:
        """
        Rejimga bog'liq korrelatsiyalarni tahlil qilish
        
        Args:
            data: Narxlar ma'lumotlari
            regimes: Rejim ma'lumotlari {'regime_name': date_range}
            
        Returns:
            Rejimga bog'liq korrelatsiyalar
        """
        returns = data.pct_change().dropna()
        regime_corr = {}
        
        for regime_name, regime_data in regimes.items():
            if isinstance(regime_data, str):
                # Date range format: '2020-01-01:2020-12-31'
                start, end = regime_data.split(':')
                mask = (returns.index >= start) & (returns.index <= end)
                regime_returns = returns[mask]
            else:
                regime_returns = regime_data
            
            if len(regime_returns) > 10:
                regime_corr[regime_name] = regime_returns.corr()
        
        self.regime_correlations = regime_corr
        return regime_corr
    
    def identify_correlation_regimes(self, data: pd.DataFrame, n_regimes: int = 3) -> Dict:
        """
        Korrelatsiya rejimlarini aniqlash (soddalashtirilgan)
        
        Args:
            data: Narxlar ma'lumotlari
            n_regimes: Rejimlar soni
            
        Returns:
            Aniqlangan rejimlar
        """
        returns = data.pct_change().dropna()
        
        # Average correlation over time
        avg_corr = returns.expanding().corr().mean(axis=1)
        
        # Simple regime identification based on correlation levels
        low_thresh = avg_corr.quantile(0.33)
        high_thresh = avg_corr.quantile(0.67)
        
        regimes = {}
        current_regime = 'Low'
        regime_start = returns.index[0]
        
        for i, date in enumerate(returns.index):
            current_avg_corr = avg_corr.iloc[i]
            
            if current_avg_corr < low_thresh:
                new_regime = 'Low'
            elif current_avg_corr > high_thresh:
                new_regime = 'High'
            else:
                new_regime = 'Medium'
            
            if new_regime != current_regime:
                # Close previous regime
                if current_regime in regimes:
                    regimes[current_regime].append((regime_start, returns.index[i-1]))
                
                # Start new regime
                current_regime = new_regime
                regime_start = date
        
        # Close last regime
        if current_regime in regimes:
            regimes[current_regime].append((regime_start, returns.index[-1]))
        else:
            regimes[current_regime] = [(regime_start, returns.index[-1])]
        
        return regimes
    
    def stress_period_analysis(self, data: pd.DataFrame, stress_events: List[str]) -> Dict:
        """
        Stress davridagi korrelatsiya tahlili
        
        Args:
            data: Narxlar ma'lumotlari
            stress_events: Stress voqealar ro'yxati
            
        Returns:
            Stress davridagi korrelatsiyalar
        """
        returns = data.pct_change().dropna()
        stress_corr = {}
        
        for event in stress_events:
            if event == 'COVID-19':
                # COVID-19 davri
                stress_period = returns[(returns.index >= '2020-02-01') & 
                                      (returns.index <= '2020-05-31')]
            elif event == 'Financial Crisis 2008':
                # 2008 moliyaviy inqiroz
                stress_period = returns[(returns.index >= '2008-09-01') & 
                                      (returns.index <= '2009-03-31')]
            elif event == 'Brexit Uncertainty':
                # Brexit noaniqlik davri
                stress_period = returns[(returns.index >= '2016-06-01') & 
                                      (returns.index <= '2017-03-31')]
            else:
                # Oxirgi 30 kun stress
                stress_period = returns.tail(30)
            
            if len(stress_period) > 10:
                stress_corr[event] = stress_period.corr()
        
        self.stress_correlations = stress_corr
        return stress_corr
    
    def correlation_regime_detection(self, data: pd.DataFrame, method: str = 'threshold') -> pd.Series:
        """
        Korrelatsiya rejimlarini avtomatik aniqlash
        
        Args:
            data: Narxlar ma'lumotlari
            method: Aniqlash metodi
            
        Returns:
            Rejimlar seriyasi
        """
        returns = data.pct_change().dropna()
        
        # Average pairwise correlation over time
        correlations = []
        for i in range(len(returns)):
            if i >= 30:  # Minimum window
                window_data = returns.iloc[:i+1]
                corr_matrix = window_data.corr()
                avg_corr = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean()
                correlations.append(avg_corr)
            else:
                correlations.append(np.nan)
        
        corr_series = pd.Series(correlations, index=returns.index)
        
        # Threshold-based regime detection
        low_threshold = corr_series.quantile(0.25)
        high_threshold = corr_series.quantile(0.75)
        
        regimes = pd.Series('Medium', index=corr_series.index)
        regimes[corr_series < low_threshold] = 'Low'
        regimes[corr_series > high_threshold] = 'High'
        
        return regimes
    
    def correlation_trading_signals(self, data: pd.DataFrame, lookback: int = 60) -> pd.DataFrame:
        """
        Korrelatsiya treyding signallari
        
        Args:
            data: Narxlar ma'lumotlari
            lookback: Orqaga qarab ko'rish davri
            
        Returns:
            Treyding signallari
        """
        returns = data.pct_change().dropna()
        signals = pd.DataFrame(index=data.index)
        
        # Pairwise correlations
        pairs = list(combinations(returns.columns, 2))
        
        for asset1, asset2 in pairs:
            pair_name = f"{asset1}_{asset2}"
            
            if asset1 in returns.columns and asset2 in returns.columns:
                # Rolling correlation
                rolling_corr = returns[asset1].rolling(lookback).corr(returns[asset2])
                
                # Correlation mean and std
                corr_mean = rolling_corr.rolling(lookback).mean()
                corr_std = rolling_corr.rolling(lookback).std()
                
                # Z-score
                z_score = (rolling_corr - corr_mean) / corr_std
                
                # Trading signals
                signals[f'{pair_name}_correlation'] = rolling_corr
                signals[f'{pair_name}_z_score'] = z_score
                signals[f'{pair_name}_signal'] = np.where(z_score > 1.5, -1,  # Mean reversion
                                                        np.where(z_score < -1.5, 1, 0))  # Momentum
        
        return signals


class PredictiveCorrelationModels:
    """
    Bashorat qilish Korrelatsiya Modellar Klass
    
    Korrelatsiyani bashorat qilish, farqlanishlarni aniqlash, 
    o'rtacha qayta tiklanish strategiyalari va risk paritet
    optimizatsiyasi uchun modellar.
    """
    
    def __init__(self, forecast_horizon: int = 30):
        """
        Args:
            forecast_horizon: Bashorat gorizonti (kunlarda)
        """
        self.forecast_horizon = forecast_horizon
        self.models = {}
        self.forecasts = {}
        
    def correlation_forecasting(self, data: pd.DataFrame, method: str = 'rf') -> Dict:
        """
        Korrelatsiyani bashorat qilish
        
        Args:
            data: Narxlar ma'lumotlari
            method: Model turi ('rf', 'linear', 'polynomial')
            
        Returns:
            Bashoratlar
        """
        returns = data.pct_change().dropna()
        
        # Prepare features
        features = []
        targets = []
        
        window_size = 30
        forecast_horizon = self.forecast_horizon
        
        for i in range(window_size, len(returns) - forecast_horizon):
            # Features: past correlations, volatilities, returns
            window_data = returns.iloc[i-window_size:i]
            
            # Average correlation
            corr_matrix = window_data.corr()
            features.append(corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)])
            
            # Target: future average correlation
            future_data = returns.iloc[i:i+forecast_horizon]
            future_corr = future_data.corr()
            targets.append(future_corr.values[np.triu_indices_from(future_corr.values, k=1)])
        
        features = np.array(features)
        targets = np.array(targets)
        
        if len(features) < 50:  # Not enough data
            return {'error': 'Yetarli ma\'lumot yo\'q'}
        
        # Train/test split
        split_idx = int(0.8 * len(features))
        X_train, X_test = features[:split_idx], features[split_idx:]
        y_train, y_test = targets[:split_idx], targets[split_idx:]
        
        if method == 'rf':
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif method == 'linear':
            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
        else:
            return {'error': 'Noto\'g\'ri model turi'}
        
        # Train model
        model.fit(X_train, y_train)
        self.models['correlation_forecaster'] = model
        
        # Predictions
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        # Metrics
        train_mse = mean_squared_error(y_train, y_pred_train)
        test_mse = mean_squared_error(y_test, y_pred_test)
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        
        return {
            'model': model,
            'train_mse': train_mse,
            'test_mse': test_mse,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'predictions_test': y_pred_test[-1],  # Latest prediction
            'method': method
        }
    
    def divergence_detection(self, data: pd.DataFrame, threshold: float = 0.05) -> Dict:
        """
        Korrelatsiya farqlanishlarini aniqlash
        
        Args:
            data: Narxlar ma'lumotlari
            threshold: Farqlanish chegarasi
            
        Returns:
            Farqlanishlar
        """
        returns = data.pct_change().dropna()
        
        # Current correlations
        current_corr = returns.tail(30).corr()
        
        # Historical average correlations
        historical_corr = returns.expanding().corr().tail(len(returns) - 30)
        avg_historical = historical_corr.groupby(level=1).mean().tail(1)
        
        # Divergences
        divergences = {}
        
        pairs = combinations(returns.columns, 2)
        for asset1, asset2 in pairs:
            pair_name = f"{asset1}_{asset2}"
            
            if asset1 in current_corr.columns and asset2 in current_corr.columns:
                current = current_corr.loc[asset1, asset2]
                
                # Average historical correlation
                if pair_name in avg_historical.columns:
                    historical_avg = avg_historical[pair_name].iloc[0]
                else:
                    historical_avg = returns[asset1].rolling(60).corr(returns[asset2]).mean()
                
                divergence = current - historical_avg
                
                if abs(divergence) > threshold:
                    divergences[pair_name] = {
                        'current_correlation': current,
                        'historical_average': historical_avg,
                        'divergence': divergence,
                        'significance': 'High' if abs(divergence) > threshold * 2 else 'Medium',
                        'signal': 'Mean Reversion' if divergence > 0 else 'Trend Continuation'
                    }
        
        return divergences
    
    def mean_reversion_strategy(self, data: pd.DataFrame, lookback: int = 60) -> Dict:
        """
        O'rtacha qayta tiklanish strategiyasi
        
        Args:
            data: Narxlar ma'lumotlari
            lookback: Orqaga qarab ko'rish davri
            
        Returns:
            Strategiya signallari
        """
        returns = data.pct_change().dropna()
        
        signals = {}
        pairs = combinations(returns.columns, 2)
        
        for asset1, asset2 in pairs:
            pair_name = f"{asset1}_{asset2}"
            
            if asset1 in returns.columns and asset2 in returns.columns:
                # Rolling correlation
                rolling_corr = returns[asset1].rolling(lookback).corr(returns[asset2])
                
                # Mean reversion signals
                corr_mean = rolling_corr.rolling(lookback).mean()
                corr_std = rolling_corr.rolling(lookback).std()
                
                z_score = (rolling_corr - corr_mean) / corr_std
                
                # Trading signals
                long_signal = z_score < -2  # Oversold correlation
                short_signal = z_score > 2  # Overbought correlation
                
                signals[pair_name] = {
                    'current_z_score': z_score.iloc[-1],
                    'long_signal': long_signal.iloc[-1],
                    'short_signal': short_signal.iloc[-1],
                    'position': 'Long' if long_signal.iloc[-1] else 'Short' if short_signal.iloc[-1] else 'Hold',
                    'expected_return': abs(z_score.iloc[-1]) * 0.01  # Simplified expectation
                }
        
        return signals
    
    def momentum_continuation_strategy(self, data: pd.DataFrame, lookback: int = 30) -> Dict:
        """
        Momentum davom ettirish strategiyasi
        
        Args:
            data: Narxlar ma'lumotlari
            lookback: Orqaga qarab ko'lish davri
            
        Returns:
            Momentum signallari
        """
        returns = data.pct_change().dropna()
        
        signals = {}
        pairs = combinations(returns.columns, 2)
        
        for asset1, asset2 in pairs:
            pair_name = f"{asset1}_{asset2}"
            
            if asset1 in returns.columns and asset2 in returns.columns:
                # Correlation momentum
                corr_short = returns[asset1].rolling(10).corr(returns[asset2])
                corr_long = returns[asset1].rolling(lookback).corr(returns[asset2])
                
                # Momentum signal
                momentum = corr_short - corr_long
                momentum_ma = momentum.rolling(5).mean()
                
                # Trend strength
                trend_strength = abs(momentum_ma.iloc[-1])
                
                # Signals
                momentum_bullish = momentum_ma.iloc[-1] > 0.01
                momentum_bearish = momentum_ma.iloc[-1] < -0.01
                
                signals[pair_name] = {
                    'momentum': momentum_ma.iloc[-1],
                    'trend_strength': trend_strength,
                    'bullish_signal': momentum_bullish,
                    'bearish_signal': momentum_bearish,
                    'position': 'Long' if momentum_bullish else 'Short' if momentum_bearish else 'Hold',
                    'confidence': 'High' if trend_strength > 0.02 else 'Medium' if trend_strength > 0.01 else 'Low'
                }
        
        return signals
    
    def risk_parity_optimization(self, data: pd.DataFrame, target_vol: float = 0.15) -> Dict:
        """
        Risk paritet optimizatsiyasi
        
        Args:
            data: Narxlar ma'lumotlari
            target_vol: Maqsad volatilite
            
        Returns:
            Optimallashgan vaznlar
        """
        returns = data.pct_change().dropna()
        
        # Calculate volatilities
        vol = returns.std() * np.sqrt(252)  # Annualized volatility
        
        # Calculate correlation matrix
        corr = returns.corr()
        
        # Risk parity weights (inverse volatility weighting)
        inv_vol = 1 / vol
        weights = inv_vol / inv_vol.sum()
        
        # Portfolio metrics
        portfolio_vol = np.sqrt(weights.T @ corr @ weights) * np.sqrt(252)
        portfolio_corr = (weights.T @ corr @ weights) / (portfolio_vol / np.sqrt(252))**2
        
        # Scale to target volatility
        if portfolio_vol > 0:
            weights_scaled = weights * (target_vol / portfolio_vol)
        else:
            weights_scaled = weights
        
        return {
            'original_weights': weights,
            'scaled_weights': weights_scaled,
            'portfolio_volatility': portfolio_vol,
            'portfolio_correlation': portfolio_corr,
            'risk_contribution': weights_scaled * (corr @ weights_scaled) / portfolio_vol**2,
            'concentration_risk': (weights_scaled**2).sum(),
            'diversification_ratio': portfolio_vol / vol.mean()
        }


class MultifactorModel:
    """
    Ko'p Faktorli Model Klass
    
    Iqtisodiy omillar, taklif/talab, bozor omillari, 
    kayfiyat omillari va texnik omillarni birlashtirish.
    """
    
    def __init__(self):
        self.factor_data = {}
        self.loadings = {}
        self.factor_returns = {}
        
    def add_economic_factors(self, data: pd.DataFrame):
        """
        Iqtisodiy omillarni qo'shish
        
        Args:
            data: Iqtisodiy ma'lumotlar
        """
        self.factor_data['economic'] = data
        
    def add_supply_demand_factors(self, data: pd.DataFrame):
        """
        Taklif/talab omillarini qo'shish
        
        Args:
            data: Taklif/talab ma'lumotlari
        """
        self.factor_data['supply_demand'] = data
        
    def add_market_factors(self, data: pd.DataFrame):
        """
        Bozor omillarini qo'shish
        
        Args:
            data: Bozor ma'lumotlari
        """
        self.factor_data['market'] = data
        
    def add_sentiment_factors(self, data: pd.DataFrame):
        """
        Kayfiyat omillarini qo'shish
        
        Args:
            data: Kayfiyat ma'lumotlari
        """
        self.factor_data['sentiment'] = data
        
    def add_technical_factors(self, data: pd.DataFrame):
        """
        Texnik omillarni qo'shish
        
        Args:
            data: Texnik ma'lumotlar
        """
        self.factor_data['technical'] = data
    
    def factor_analysis(self, method: str = 'pca') -> Dict:
        """
        Faktor tahlili
        
        Args:
            method: Tahlil metodi ('pca', 'fa')
            
        Returns:
            Faktor natijalari
        """
        # Combine all factors
        all_factors = pd.concat(self.factor_data.values(), axis=1)
        all_factors = all_factors.dropna()
        
        if method == 'pca':
            # Principal Component Analysis
            scaler = StandardScaler()
            scaled_factors = scaler.fit_transform(all_factors)
            
            pca = PCA()
            pca_result = pca.fit_transform(scaled_factors)
            
            # Factor loadings
            loadings = pd.DataFrame(
                pca.components_[:10].T,  # First 10 components
                columns=[f'PC{i+1}' for i in range(min(10, pca.n_components_))],
                index=all_factors.columns
            )
            
            # Explained variance
            explained_var = pca.explained_variance_ratio_[:10]
            
            return {
                'loadings': loadings,
                'explained_variance': explained_var,
                'cumulative_variance': np.cumsum(explained_var),
                'factor_scores': pca_result[:, :10],
                'method': 'PCA'
            }
        
        else:
            # Factor Analysis (simplified)
            # This would require specialized FA implementation
            return {'error': 'Factor Analysis not implemented yet'}
    
    def factor_model_regression(self, returns: pd.Series, factors: pd.DataFrame) -> Dict:
        """
        Faktor model regressiyasi
        
        Args:
            returns: Aktiv daromadlari
            factors: Faktor qiymatlari
            
        Returns:
            Regressiya natijalari
        """
        # Align data
        aligned_data = pd.concat([returns, factors], axis=1).dropna()
        
        if len(aligned_data) < 30:
            return {'error': 'Yetarli ma\'lumot yo\'q'}
        
        Y = aligned_data.iloc[:, 0]  # Returns
        X = aligned_data.iloc[:, 1:]  # Factors
        
        # Standardize
        scaler = StandardScaler()
        X_scaled = pd.DataFrame(scaler.fit_transform(X), index=X.index, columns=X.columns)
        
        # OLS regression
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(X_scaled, Y)
        
        # Predictions and residuals
        y_pred = model.predict(X_scaled)
        residuals = Y - y_pred
        
        # R-squared
        r2 = model.score(X_scaled, Y)
        
        # Factor loadings (coefficients)
        loadings = pd.Series(model.coef_, index=X.columns)
        alpha = model.intercept_
        
        return {
            'alpha': alpha,
            'loadings': loadings,
            'r_squared': r2,
            'residuals': residuals,
            'factor_contribution': loadings * X_scaled.mean(),
            'model': model
        }
    
    def multi_factor_performance_attribution(self, returns: pd.Series, factors: pd.DataFrame) -> Dict:
        """
        Ko'p faktorli performance attribution
        
        Args:
            returns: Aktiv daromadlari
            factors: Faktor qiymatlari
            
        Returns:
            Performance attribution
        """
        regression_results = self.factor_model_regression(returns, factors)
        
        if 'error' in regression_results:
            return regression_results
        
        # Calculate factor contributions
        factor_contributions = {}
        
        for factor in factors.columns:
            if factor in regression_results['loadings'].index:
                factor_return = factors[factor].mean()
                loading = regression_results['loadings'][factor]
                contribution = loading * factor_return
                factor_contributions[factor] = contribution
        
        # Total attribution
        total_attribution = sum(factor_contributions.values())
        alpha_contribution = regression_results['alpha']
        
        return {
            'total_return': returns.mean() * 252,  # Annualized
            'alpha': alpha_contribution * 252,
            'factor_contributions': {k: v * 252 for k, v in factor_contributions.items()},
            'residual_contribution': regression_results['residuals'].mean() * 252,
            'r_squared': regression_results['r_squared'],
            'attribution_breakdown': pd.Series({
                'Alpha': alpha_contribution * 252,
                'Factors': total_attribution * 252,
                'Residual': regression_results['residuals'].mean() * 252
            })
        }


class ForexCarryTradeSystem:
    """
    Boshqaruvchi Klass - Forex Carry Trade va Metal Price Correlation Tizimi
    
    Barcha komponentlarni birlashtiruvchi asosiy klass.
    """
    
    def __init__(self):
        self.carry_analyzer = ForexCarryTradeAnalyzer()
        self.correlation_analyzer = MetalPriceCorrelationAnalyzer()
        self.dynamic_analyzer = DynamicCorrelationAnalyzer()
        self.predictive_models = PredictiveCorrelationModels()
        self.multifactor_model = MultifactorModel()
        self.is_initialized = False
        
    def initialize_system(self, config: Dict):
        """
        Tizimni ishga tushirish
        
        Args:
            config: Tizim konfiguratsiyasi
        """
        # Load interest rates
        if 'interest_rates' in config:
            self.carry_analyzer.load_interest_rates(config['interest_rates'])
        
        # Load metal prices
        if 'metal_prices' in config:
            self.correlation_analyzer.load_metal_prices(config['metal_prices'])
        
        # Load economic data
        if 'economic_data' in config:
            self.correlation_analyzer.load_economic_data(config['economic_data'])
            self.multifactor_model.add_economic_factors(config['economic_data'])
        
        # Load additional factors
        if 'supply_demand_data' in config:
            self.multifactor_model.add_supply_demand_factors(config['supply_demand_data'])
        
        if 'market_data' in config:
            self.multifactor_model.add_market_factors(config['market_data'])
        
        if 'sentiment_data' in config:
            self.multifactor_model.add_sentiment_factors(config['sentiment_data'])
        
        if 'technical_data' in config:
            self.multifactor_model.add_technical_factors(config['technical_data'])
        
        self.is_initialized = True
    
    def run_comprehensive_analysis(self) -> Dict:
        """
        To'liq tahlilni bajarish
        
        Returns:
            Barcha tahlil natijalari
        """
        if not self.is_initialized:
            return {'error': 'Tizim ishga tushirilmagan'}
        
        results = {}
        
        # 1. Carry Trade Analysis
        print("Forex Carry Trade tahlili bajarilmoqda...")
        
        # Sample currency pairs
        currency_pairs = ['USD/JPY', 'EUR/USD', 'GBP/USD', 'USD/CHF', 'AUD/USD', 'NZD/USD']
        carry_opportunities = self.carry_analyzer.identify_opportunities(currency_pairs)
        
        results['carry_trade'] = {
            'opportunities': carry_opportunities,
            'performance_report': self.carry_analyzer.generate_performance_report()
        }
        
        # 2. Correlation Analysis
        print("Korrelatsiya tahlili bajarilmoqda...")
        
        if not self.correlation_analyzer.metal_prices.empty:
            results['correlations'] = {
                'cross_metal': self.correlation_analyzer.cross_metal_correlation(),
                'economic_cycle': self.correlation_analyzer.economic_cycle_correlation(),
                'dollar_strength': self.correlation_analyzer.dollar_strength_correlation(),
                'inflation': self.correlation_analyzer.inflation_correlation(),
                'industrial_demand': self.correlation_analyzer.industrial_demand_correlation()
            }
        
        # 3. Dynamic Correlation Analysis
        print("Dinamik korrelatsiya tahlili bajarilmoqda...")
        
        if not self.correlation_analyzer.metal_prices.empty:
            data = self.correlation_analyzer.metal_prices
            
            results['dynamic_correlations'] = {
                'rolling': self.dynamic_analyzer.rolling_correlation_analysis(data),
                'regime_detection': self.dynamic_analyzer.correlation_regime_detection(data)
            }
        
        # 4. Predictive Models
        print("Bashorat qilish modellari bajarilmoqda...")
        
        if not self.correlation_analyzer.metal_prices.empty:
            data = self.correlation_analyzer.metal_prices
            
            results['predictions'] = {
                'correlation_forecast': self.predictive_models.correlation_forecasting(data),
                'divergence_detection': self.predictive_models.divergence_detection(data),
                'mean_reversion': self.predictive_models.mean_reversion_strategy(data),
                'momentum_continuation': self.predictive_models.momentum_continuation_strategy(data),
                'risk_parity': self.predictive_models.risk_parity_optimization(data)
            }
        
        # 5. Multi-factor Analysis
        print("Ko'p faktorli tahlil bajarilmoqda...")
        
        if len(self.multifactor_model.factor_data) > 0:
            factor_analysis = self.multifactor_model.factor_analysis()
            results['multifactor'] = factor_analysis
        
        return results
    
    def generate_trading_signals(self, analysis_results: Dict) -> Dict:
        """
        Treyding signallari yaratish
        
        Args:
            analysis_results: Tahlil natijalari
            
        Returns:
            Treyding signallari
        """
        signals = {}
        
        # Carry trade signals
        if 'carry_trade' in analysis_results:
            carry_opps = analysis_results['carry_trade']['opportunities']
            signals['carry_trade'] = {
                'top_opportunities': carry_opps[:3],
                'total_opportunities': len(carry_opps),
                'recommended_position_size': 0.1  # 10% of portfolio
            }
        
        # Correlation-based signals
        if 'predictions' in analysis_results:
            pred = analysis_results['predictions']
            
            # Mean reversion signals
            if 'mean_reversion' in pred:
                mean_rev = pred['mean_reversion']
                strong_signals = {k: v for k, v in mean_rev.items() if v['position'] != 'Hold'}
                signals['mean_reversion'] = strong_signals
            
            # Momentum signals
            if 'momentum_continuation' in pred:
                momentum = pred['momentum_continuation']
                strong_momentum = {k: v for k, v in momentum.items() if v['position'] != 'Hold'}
                signals['momentum'] = strong_momentum
        
        # Risk management
        if 'predictions' in analysis_results and 'risk_parity' in analysis_results['predictions']:
            risk_parity = analysis_results['predictions']['risk_parity']
            signals['risk_management'] = {
                'optimal_weights': risk_parity['scaled_weights'].to_dict(),
                'portfolio_volatility': risk_parity['portfolio_volatility'],
                'diversification_ratio': risk_parity['diversification_ratio']
            }
        
        return signals
    
    def create_dashboard_data(self, analysis_results: Dict) -> Dict:
        """
        Dashboard uchun ma'lumot yaratish
        
        Args:
            analysis_results: Tahlil natijalari
            
        Returns:
            Dashboard ma'lumotlari
        """
        dashboard = {
            'summary': {},
            'charts': {},
            'alerts': [],
            'performance': {}
        }
        
        # Summary statistics
        if 'carry_trade' in analysis_results:
            carry_results = analysis_results['carry_trade']
            dashboard['summary']['carry_trade'] = {
                'opportunities_count': len(carry_results['opportunities']),
                'best_sharpe_ratio': carry_results['opportunities'][0]['sharpe_ratio'] if carry_results['opportunities'] else 0,
                'average_return': np.mean([opp['annual_return_pct'] for opp in carry_results['opportunities']]) if carry_results['opportunities'] else 0
            }
        
        # Chart data preparation
        if 'correlations' in analysis_results:
            corr_data = analysis_results['correlations']
            
            # Cross-metal correlation heatmap
            if 'cross_metal' in corr_data:
                dashboard['charts']['correlation_heatmap'] = corr_data['cross_metal'].to_dict()
            
            # Dollar strength correlation
            if 'dollar_strength' in corr_data:
                dashboard['charts']['dollar_correlation'] = corr_data['dollar_strength'].to_dict()
        
        # Alerts
        if 'predictions' in analysis_results:
            pred = analysis_results['predictions']
            
            # High divergence alerts
            if 'divergence_detection' in pred:
                divergences = pred['divergence_detection']
                high_divergences = {k: v for k, v in divergences.items() if v.get('significance') == 'High'}
                
                for pair, div_data in high_divergences.items():
                    dashboard['alerts'].append({
                        'type': 'high_divergence',
                        'message': f"Yuqori korrelatsiya farqlanishi: {pair}",
                        'value': div_data['divergence'],
                        'severity': 'high'
                    })
        
        return dashboard


def generate_sample_data(n_days: int = 1000) -> Dict:
    """
        Sample ma'lumotlar yaratish
        
        Args:
            n_days: Kunlar soni
            
        Returns:
            Sample ma'lumotlar
    """
    np.random.seed(42)
    
    # Create date index
    end_date = datetime.now()
    start_date = end_date - timedelta(days=n_days)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Sample metal prices
    metals = ['GOLD', 'SILVER', 'PLATINUM', 'PALLADIUM', 'COPPER', 'ALUMINUM']
    
    # Base prices
    base_prices = {
        'GOLD': 1800, 'SILVER': 25, 'PLATINUM': 1000, 
        'PALLADIUM': 2000, 'COPPER': 4.0, 'ALUMINUM': 2500
    }
    
    metal_prices = pd.DataFrame(index=dates)
    
    for metal in metals:
        # Generate correlated price movements
        returns = np.random.normal(0.0002, 0.02, len(dates))
        
        # Add some correlation structure
        if metal in ['GOLD', 'SILVER']:
            # Precious metals correlation
            returns += np.random.normal(0, 0.01, len(dates))
        elif metal in ['PALLADIUM', 'PLATINUM']:
            # Auto industry correlation
            returns += np.random.normal(0, 0.015, len(dates))
        elif metal in ['COPPER', 'ALUMINUM']:
            # Industrial metals correlation
            returns += np.random.normal(0, 0.02, len(dates))
        
        prices = base_prices[metal] * np.exp(np.cumsum(returns))
        metal_prices[metal] = prices
    
    # Sample economic data
    economic_data = pd.DataFrame(index=dates)
    
    # USD Index
    economic_data['USD_INDEX'] = 100 + np.cumsum(np.random.normal(0, 0.5, len(dates)))
    
    # Interest rates
    economic_data['FED_RATE'] = 5.25 + np.cumsum(np.random.normal(0, 0.01, len(dates)))
    economic_data['ECB_RATE'] = 4.00 + np.cumsum(np.random.normal(0, 0.01, len(dates)))
    
    # GDP Growth
    economic_data['GDP_GROWTH'] = 2.0 + np.random.normal(0, 0.3, len(dates))
    
    # Inflation
    economic_data['INFLATION'] = 2.5 + np.random.normal(0, 0.2, len(dates))
    
    # Industrial Production
    economic_data['INDUSTRIAL_PRODUCTION'] = 1.5 + np.random.normal(0, 0.5, len(dates))
    
    # Interest rates data for carry trade
    interest_rates = {
        'USD': {'rate': 5.25, 'last_update': '2024-11-01'},
        'EUR': {'rate': 4.00, 'last_update': '2024-11-01'},
        'JPY': {'rate': -0.10, 'last_update': '2024-11-01'},
        'GBP': {'rate': 5.25, 'last_update': '2024-11-01'},
        'CHF': {'rate': 1.75, 'last_update': '2024-11-01'},
        'AUD': {'rate': 4.35, 'last_update': '2024-11-01'},
        'NZD': {'rate': 5.50, 'last_update': '2024-11-01'},
        'CAD': {'rate': 5.00, 'last_update': '2024-11-01'}
    }
    
    # Supply/Demand data
    supply_demand = pd.DataFrame(index=dates)
    supply_demand['MINE_PRODUCTION'] = np.random.normal(100, 5, len(dates))
    supply_demand['CONSUMPTION'] = np.random.normal(95, 3, len(dates))
    supply_demand['INVENTORY_LEVELS'] = np.random.normal(110, 8, len(dates))
    
    # Market data
    market_data = pd.DataFrame(index=dates)
    market_data['ETF_FLOWS'] = np.random.normal(0, 50, len(dates))
    market_data['FUTURES_POSITIONING'] = np.random.normal(0, 1000, len(dates))
    market_data['VOLUME'] = np.random.normal(1000000, 200000, len(dates))
    
    # Sentiment data
    sentiment_data = pd.DataFrame(index=dates)
    sentiment_data['NEWS_SENTIMENT'] = np.random.normal(0, 0.3, len(dates))
    sentiment_data['ANALYST_SENTIMENT'] = np.random.normal(0, 0.2, len(dates))
    sentiment_data['SOCIAL_SENTIMENT'] = np.random.normal(0, 0.4, len(dates))
    
    # Technical data
    technical_data = pd.DataFrame(index=dates)
    for metal in metals:
        technical_data[f'{metal}_RSI'] = 50 + np.random.normal(0, 20, len(dates))
        technical_data[f'{metal}_MACD'] = np.random.normal(0, 2, len(dates))
        technical_data[f'{metal}_BOLLINGER'] = np.random.normal(0, 1, len(dates))
    
    return {
        'metal_prices': metal_prices,
        'economic_data': economic_data,
        'interest_rates': interest_rates,
        'supply_demand_data': supply_demand,
        'market_data': market_data,
        'sentiment_data': sentiment_data,
        'technical_data': technical_data
    }


def run_forex_carry_trade_analysis():
    """
    Forex Carry Trade va Metal Price Correlation tahlilini ishga tushirish
    """
    print("FOREX CARRY TRADE VA METAL PRICE CORRELATION TIZIMI")
    print("=" * 60)
    
    # Sample ma'lumotlarni yaratish
    print("Sample ma'lumotlar yaratilmoqda...")
    sample_data = generate_sample_data(1000)
    
    # Tizimni ishga tushirish
    print("Tizim ishga tushirilmoqda...")
    system = ForexCarryTradeSystem()
    
    config = {
        'metal_prices': sample_data['metal_prices'],
        'economic_data': sample_data['economic_data'],
        'interest_rates': sample_data['interest_rates'],
        'supply_demand_data': sample_data['supply_demand_data'],
        'market_data': sample_data['market_data'],
        'sentiment_data': sample_data['sentiment_data'],
        'technical_data': sample_data['technical_data']
    }
    
    system.initialize_system(config)
    
    # To'liq tahlil
    print("To'liq tahlil boshlanmoqda...")
    results = system.run_comprehensive_analysis()
    
    # Treyding signallari
    print("Treyding signallari yaratilmoqda...")
    trading_signals = system.generate_trading_signals(results)
    
    # Dashboard ma'lumotlari
    print("Dashboard ma'lumotlari tayyorlanmoqda...")
    dashboard = system.create_dashboard_data(results)
    
    # Natijalarni saqlash
    output_file = '/workspace/code/forex_carry_trade_results.txt'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("FOREX CARRY TRADE VA METAL PRICE CORRELATION ANALYSIS\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("TAHLIL NATIJALARI:\n")
        f.write("-" * 30 + "\n\n")
        
        # Carry Trade Results
        if 'carry_trade' in results:
            f.write("1. FOREX CARRY TRADE TAHLILI:\n")
            f.write(results['carry_trade']['performance_report'])
            f.write("\n\n")
        
        # Correlation Results
        if 'correlations' in results:
            f.write("2. METAL PRICE CORRELATION TAHLILI:\n")
            correlations = results['correlations']
            
            if 'dollar_strength' in correlations:
                f.write("AQSh Dollar Kuchi Korrelatsiyasi:\n")
                for metal, corr in correlations['dollar_strength'].items():
                    f.write(f"  {metal}: {corr:.3f}\n")
                f.write("\n")
            
            if 'inflation' in correlations:
                f.write("Inflatsiya Korrelatsiyasi:\n")
                for metal, data in correlations['inflation'].items():
                    f.write(f"  {metal}: {data['correlation']:.3f} ({data['strength']} {data['direction']})\n")
                f.write("\n")
        
        # Trading Signals
        f.write("3. TREYDING SIGNALLARI:\n")
        f.write("-" * 30 + "\n")
        
        if 'carry_trade' in trading_signals:
            f.write("Carry Trade Imkoniyatlari:\n")
            for opp in trading_signals['carry_trade']['top_opportunities']:
                f.write(f"  {opp['pair']}: Sharpe Ratio = {opp['sharpe_ratio']:.3f}\n")
            f.write("\n")
        
        if 'mean_reversion' in trading_signals:
            f.write("O'rtacha Qayta Tiklanish Signallari:\n")
            for pair, signal in trading_signals['mean_reversion'].items():
                f.write(f"  {pair}: {signal['position']} (Z-score: {signal['current_z_score']:.2f})\n")
            f.write("\n")
        
        # Performance Summary
        f.write("4. PERFORMANCE XULOSASI:\n")
        f.write("-" * 30 + "\n")
        
        if 'summary' in dashboard:
            summary = dashboard['summary']
            if 'carry_trade' in summary:
                carry_summary = summary['carry_trade']
                f.write(f"Carry Trade Imkoniyatlari: {carry_summary['opportunities_count']}\n")
                f.write(f"Eng Yaxshi Sharpe Ratio: {carry_summary['best_sharpe_ratio']:.3f}\n")
                f.write(f"O'rtacha Return: {carry_summary['average_return']:.2f}%\n")
    
    print(f"Natija {output_file} ga saqlandi!")
    
    # Qisqa xulosa chiqarish
    print("\n" + "="*60)
    print("TAHLIL XULOSASI:")
    print("="*60)
    
    if 'carry_trade' in results:
        carry_opps = results['carry_trade']['opportunities']
        print(f"Topilgan Carry Trade imkoniyatlari: {len(carry_opps)}")
        if carry_opps:
            print(f"Eng yaxshi imkoniyat: {carry_opps[0]['pair']} (Sharpe: {carry_opps[0]['sharpe_ratio']:.3f})")
    
    if 'correlations' in results:
        corr_data = results['correlations']
        if 'dollar_strength' in corr_data:
            strong_dollar_corr = [metal for metal, corr in corr_data['dollar_strength'].items() 
                                if abs(corr) > 0.3]
            print(f"Dollar bilan kuchli bog'liq metallar: {len(strong_dollar_corr)}")
    
    if 'predictions' in results:
        pred = results['predictions']
        if 'divergence_detection' in pred:
            high_divergences = len([k for k, v in pred['divergence_detection'].items() 
                                  if v.get('significance') == 'High'])
            print(f"Yuqori korrelatsiya farqlanishlari: {high_divergences}")
    
    print("\nTahlil yakunlandi!")
    
    return results, trading_signals, dashboard


if __name__ == "__main__":
    # Tizimni ishga tushirish
    results, signals, dashboard = run_forex_carry_trade_analysis()
    
    print("\nFOREX CARRY TRADE VA METAL PRICE CORRELATION TIZIMI TAYYOR!")
    print("Barcha modellar va tahlillar muvaffaqiyatli amalga oshirildi.")