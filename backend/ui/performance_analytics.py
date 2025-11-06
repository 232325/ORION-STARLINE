"""
Performance Analytics Module
Portfolio natijalarini tahlil qilish uchun keng qamrovli analitika moduli

Bu modul quyidagi asosiy funksiyalarni o'z ichiga oladi:
- calculate_performance_metrics: Asosiy ko'rsatkichlarni hisoblash
- analyze_drawdown: Drawdown tahlili
- get_equity_curve_data: Equity curve ma'lumotlarini olish
- calculate_sharpe_ratio: Sharpe ratio ni hisoblash
- calculate_max_drawdown: Maksimal drawdown ni hisoblash
- compare_performance: Portfellar o'rtasida taqqoslash
- get_risk_metrics: Risk ko'rsatkichlarini olish
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
import warnings
warnings.filterwarnings('ignore')


class PerformanceAnalytics:
    """
    Portfolio natijalarini tahlil qilish uchun asosiy klass
    
    Portfolio analitikasi, risk boshqaruvi va performance o'lchash
    uchun to'liq funksional imkoniyatlarni ta'minlaydi.
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Performance analytics klasini ishga tushirish
        
        Args:
            risk_free_rate: Yillik risk mukofoti (default: 2%)
        """
        self.risk_free_rate = risk_free_rate
    
    def calculate_performance_metrics(self, returns: pd.Series, 
                                    benchmark_returns: Optional[pd.Series] = None,
                                    initial_capital: float = 100000) -> Dict[str, float]:
        """
        Asosiy performance ko'rsatkichlarini hisoblash
        
        Args:
            returns: Portfolio daromadlari
            benchmark_returns: Benchmark daromadlari (ixtiyoriy)
            initial_capital: Boshlang'ich kapital
            
        Returns:
            Dict[str, float]: To'liq ko'rsatkichlar lug'ati
        """
        if returns.empty:
            return self._get_empty_metrics()
            
        # Asosiy ko'rsatkichlar
        total_return = (1 + returns).prod() - 1
        
        # Yilliklashtirilgan ko'rsatkichlar
        trading_days = len(returns)
        annualized_return = (1 + returns.mean()) ** 252 - 1
        volatility = returns.std() * np.sqrt(252)
        
        # Risk mukofoti ko'rsatkichlari
        excess_returns = returns - self.risk_free_rate / 252
        sharpe_ratio = self.calculate_sharpe_ratio(returns)
        
        # Drawdown tahlili
        cumulative_returns = (1 + returns).cumprod()
        max_drawdown = self.calculate_max_drawdown(returns)
        
        # Trading statistikasi
        win_rate = (returns > 0).sum() / len(returns)
        profit_factor = self._calculate_profit_factor(returns)
        
        # Qo'shimcha ko'rsatkichlar
        avg_return = returns.mean()
        return_std = returns.std()
        
        # Sortino ratio (downside deviation asosida)
        downside_returns = returns[returns < 0]
        downside_deviation = downside_returns.std() if len(downside_returns) > 0 else 0.001
        sortino_ratio = (annualized_return - self.risk_free_rate) / (downside_deviation * np.sqrt(252))
        
        # Calmar ratio (annual return / max drawdown)
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Omega ratio
        threshold = self.risk_free_rate / 252
        gains = sum(max(r - threshold, 0) for r in returns)
        losses = sum(max(threshold - r, 0) for r in returns)
        omega_ratio = gains / losses if losses > 0 else 0
        
        # Maksimum marosimlar
        best_day = returns.max()
        worst_day = returns.min()
        
        # Value at Risk (VaR)
        var_95 = np.percentile(returns, 5)
        var_99 = np.percentile(returns, 1)
        
        # Conditional VaR (CVaR)
        cvar_95 = returns[returns <= var_95].mean()
        cvar_99 = returns[returns <= var_99].mean()
        
        metrics = {
            # Asosiy daromad ko'rsatkichlari
            'total_return': total_return,
            'annualized_return': annualized_return,
            'daily_avg_return': avg_return,
            'volatility': volatility,
            
            # Risk mukofoti ko'rsatkichlari
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'omega_ratio': omega_ratio,
            
            # Drawdown ko'rsatkichlari
            'max_drawdown': max_drawdown,
            'current_drawdown': (cumulative_returns.iloc[-1] - cumulative_returns.expanding().max().iloc[-1]) / cumulative_returns.expanding().max().iloc[-1],
            
            # Trading statistikasi
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_trades': len(returns),
            'avg_return': avg_return,
            'return_std': return_std,
            
            # Maksimal marosimlar
            'best_day': best_day,
            'worst_day': worst_day,
            
            # Risk ko'rsatkichlari
            'var_95': var_95,
            'var_99': var_99,
            'cvar_95': cvar_95,
            'cvar_99': cvar_99,
            'downside_deviation': downside_deviation,
            
            # Kapitalsal ko'rsatkichlar
            'initial_capital': initial_capital,
            'final_value': initial_capital * cumulative_returns.iloc[-1],
            'total_profit': initial_capital * cumulative_returns.iloc[-1] - initial_capital
        }
        
        # Benchmark bilan taqqoslash
        if benchmark_returns is not None and not benchmark_returns.empty:
            beta, alpha = self._calculate_beta_alpha(returns, benchmark_returns)
            tracking_error = (returns - benchmark_returns).std() * np.sqrt(252)
            information_ratio = (returns.mean() - benchmark_returns.mean()) * np.sqrt(252) / tracking_error if tracking_error > 0 else 0
            
            metrics.update({
                'beta': beta,
                'alpha': alpha,
                'tracking_error': tracking_error,
                'information_ratio': information_ratio,
                'benchmark_return': (1 + benchmark_returns).prod() - 1
            })
        
        return metrics
    
    def analyze_drawdown(self, returns: pd.Series, 
                        period: str = 'daily') -> Dict[str, any]:
        """
        Drawdown tahlilini bajarish
        
        Args:
            returns: Portfolio daromadlari
            period: Vaqt oralig'i ('daily', 'weekly', 'monthly')
            
        Returns:
            Dict: To'liq drawdown tahlili natijalari
        """
        if returns.empty:
            return {'error': 'Bo\'sh ma\'lumot'}
            
        # Drawdown hisoblash
        cumulative_returns = (1 + returns).cumprod()
        peak = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - peak) / peak
        
        # Asosiy drawdown ko'rsatkichlari
        max_drawdown = drawdown.min()
        max_drawdown_date = drawdown.idxmin()
        
        # Joriy drawdown
        current_drawdown = drawdown.iloc[-1]
        
        # Drawdown davomiyligi tahlili
        underwater = drawdown < 0
        drawdown_periods = []
        in_drawdown = False
        start_date = None
        
        for date, is_underwater in underwater.items():
            if is_underwater and not in_drawdown:
                start_date = date
                in_drawdown = True
            elif not is_underwater and in_drawdown:
                end_date = date
                duration_days = (end_date - start_date).days
                period_peak = peak.loc[start_date:end_date].max()
                period_min = cumulative_returns.loc[start_date:end_date].min()
                period_drawdown = (period_min - period_peak) / period_peak
                
                drawdown_periods.append({
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'duration_days': duration_days,
                    'max_drawdown': period_drawdown
                })
                in_drawdown = False
                
        # Agar hali ham drawdown holatida
        if in_drawdown and start_date:
            current_date = returns.index[-1]
            duration_days = (current_date - start_date).days
            period_peak = peak.loc[start_date:].max()
            period_min = cumulative_returns.loc[start_date:].min()
            period_drawdown = (period_min - period_peak) / period_peak
            
            drawdown_periods.append({
                'start_date': start_date.isoformat(),
                'end_date': current_date.isoformat(),
                'duration_days': duration_days,
                'max_drawdown': period_drawdown
            })
        
        # O'rtacha ko'rsatkichlar
        avg_drawdown = drawdown[drawdown < 0].mean() if len(drawdown[drawdown < 0]) > 0 else 0
        avg_recovery_time = self._calculate_avg_recovery_time(returns, drawdown)
        
        # Maksimal drawdown davomiyligi
        max_dd_duration = 0
        if drawdown_periods:
            max_dd_duration = max(period['duration_days'] for period in drawdown_periods)
        
        return {
            'max_drawdown': max_drawdown,
            'max_drawdown_date': max_drawdown_date.isoformat(),
            'max_drawdown_duration_days': max_dd_duration,
            'current_drawdown': current_drawdown,
            'avg_drawdown': avg_drawdown,
            'avg_recovery_time_days': avg_recovery_time,
            'drawdown_periods_count': len(drawdown_periods),
            'drawdown_periods': drawdown_periods,
            'drawdown_series': drawdown.to_dict(),
            'recovery_factor': self._calculate_recovery_factor(returns, max_drawdown)
        }
    
    def get_equity_curve_data(self, returns: pd.Series, 
                            initial_capital: float = 100000) -> pd.DataFrame:
        """
        Equity curve ma'lumotlarini tayyorlash
        
        Args:
            returns: Portfolio daromadlari
            initial_capital: Boshlang'ich kapital
            
        Returns:
            pd.DataFrame: To'liq equity curve ma'lumotlari
        """
        if returns.empty:
            return pd.DataFrame()
            
        # Asosiy equity curve
        cumulative_returns = (1 + returns).cumprod()
        equity_curve = initial_capital * cumulative_returns
        
        # Peak va drawdown hisoblash
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        
        # Qo'shimcha ma'lumotlar
        df = pd.DataFrame({
            'date': returns.index,
            'returns': returns,
            'cumulative_returns': cumulative_returns,
            'equity': equity_curve,
            'peak': peak,
            'drawdown': drawdown,
            'daily_pnl': returns * equity_curve.shift(1).fillna(initial_capital),
            'cumulative_pnl': equity_curve - initial_capital,
            'drawdown_duration': self._calculate_drawdown_duration(returns)
        })
        
        # Percentile hisoblash
        df['equity_percentile'] = df['equity'].rank(pct=True)
        df['rolling_volatility'] = df['returns'].rolling(30).std() * np.sqrt(252)
        df['rolling_sharpe'] = (df['returns'].rolling(30).mean() * 252) / (df['returns'].rolling(30).std() * np.sqrt(252))
        
        return df
    
    def calculate_sharpe_ratio(self, returns: pd.Series, 
                             risk_free_rate: Optional[float] = None) -> float:
        """
        Sharpe ratio ni hisoblash
        
        Args:
            returns: Portfolio daromadlari
            risk_free_rate: Yillik risk mukofoti (default: instansdagi qiymat)
            
        Returns:
            float: Sharpe ratio
        """
        if returns.empty or returns.std() == 0:
            return 0.0
            
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
            
        # Kunlik risk mukofoti
        daily_risk_free = risk_free_rate / 252
        
        # Excess returns
        excess_returns = returns - daily_risk_free
        
        # Sharpe ratio
        return excess_returns.mean() * np.sqrt(252) / excess_returns.std()
    
    def calculate_max_drawdown(self, returns: Union[pd.Series, pd.DataFrame]) -> float:
        """
        Maksimal drawdown ni hisoblash
        
        Args:
            returns: Daromadlar qatori yoki DataFrame
            
        Returns:
            float: Maksimal drawdown (manfiy qiymat)
        """
        if isinstance(returns, pd.DataFrame):
            # Agar bir nechta aktiv bo'lsa, umumiy daromadni hisoblaymiz
            if returns.empty.empty:
                return 0.0
            cumulative_returns = (1 + returns).mean(axis=1).cumprod()
        else:
            if returns.empty:
                return 0.0
            cumulative_returns = (1 + returns).cumprod()
            
        # Peak va drawdown hisoblash
        peak = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - peak) / peak
        
        return drawdown.min()
    
    def compare_performance(self, returns_list: List[pd.Series], 
                          labels: List[str],
                          benchmark_returns: Optional[pd.Series] = None) -> pd.DataFrame:
        """
        Bir nechta portfelni performance bo'yicha taqqoslash
        
        Args:
            returns_list: Portfel daromadlari ro'yxati
            labels: Portfel nomlari
            benchmark_returns: Benchmark daromadlari (ixtiyoriy)
            
        Returns:
            pd.DataFrame: Taqqoslash natijalari
        """
        if len(returns_list) != len(labels):
            raise ValueError("returns_list va labels uzunliklari bir xil bo'lishi kerak")
            
        comparison_data = []
        
        for returns, label in zip(returns_list, labels):
            if not returns.empty:
                # Asosiy ko'rsatkichlar
                metrics = self.calculate_performance_metrics(returns, benchmark_returns)
                
                # Risk ko'rsatkichlari
                risk_metrics = self.get_risk_metrics(returns)
                
                # Barcha ko'rsatkichlarni birlashtirish
                all_metrics = {**metrics, **risk_metrics}
                all_metrics['portfolio'] = label
                
                comparison_data.append(all_metrics)
        
        if not comparison_data:
            return pd.DataFrame()
        
        return pd.DataFrame(comparison_data)
    
    def get_risk_metrics(self, returns: pd.Series) -> Dict[str, float]:
        """
        Risk ko'rsatkichlarini hisoblash
        
        Args:
            returns: Portfolio daromadlari
            
        Returns:
            Dict[str, float]: To'liq risk ko'rsatkichlari
        """
        if returns.empty:
            return self._get_empty_risk_metrics()
            
        # Volatility ko'rsatkichlari
        daily_vol = returns.std()
        annualized_vol = daily_vol * np.sqrt(252)
        
        # Value at Risk (VaR)
        var_95 = np.percentile(returns, 5)
        var_99 = np.percentile(returns, 1)
        
        # Conditional VaR (CVaR)
        cvar_95 = returns[returns <= var_95].mean() if len(returns[returns <= var_95]) > 0 else 0
        cvar_99 = returns[returns <= var_99].mean() if len(returns[returns <= var_99]) > 0 else 0
        
        # Downside deviation
        downside_returns = returns[returns < 0]
        downside_deviation = downside_returns.std() if len(downside_returns) > 0 else 0
        
        # Sortino ratio
        sortino_ratio = (returns.mean() * 252 - self.risk_free_rate) / (downside_deviation * np.sqrt(252)) if downside_deviation > 0 else 0
        
        # Maksimal kunlik zarar
        max_single_day_loss = returns.min()
        
        # Bernoulli probability
        prob_loss = (returns < 0).mean()
        prob_large_loss = (returns < var_95).mean()
        
        # Skewness va Kurtosis
        skewness = returns.skew()
        kurtosis = returns.kurtosis()
        
        # Jarayon buzilishi (jarayon koeffitsenti)
        tail_ratio = abs(np.percentile(returns, 95)) / abs(np.percentile(returns, 5))
        
        # Custom risk ko'rsatkichlari
        #Ulcer Index (drawdown asosida)
        cumulative_returns = (1 + returns).cumprod()
        peak = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - peak) / peak
        ulcer_index = np.sqrt((drawdown ** 2).mean())
        
        # Pain Index
        pain_index = abs(drawdown[drawdown < 0]).mean()
        
        # Kelly criterion asosida optimal position size
        win_rate = (returns > 0).mean()
        avg_win = returns[returns > 0].mean() if len(returns[returns > 0]) > 0 else 0
        avg_loss = abs(returns[returns < 0].mean()) if len(returns[returns < 0]) > 0 else 0
        
        if avg_loss > 0:
            win_loss_ratio = avg_win / avg_loss
            kelly_fraction = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
            kelly_fraction = max(0, min(kelly_fraction, 0.25))  # 0-25% oralig'ida cheklash
        else:
            kelly_fraction = 0
        
        return {
            # Asosiy volatility ko'rsatkichlari
            'daily_volatility': daily_vol,
            'annualized_volatility': annualized_vol,
            
            # VaR ko'rsatkichlari
            'var_95': var_95,
            'var_99': var_99,
            'cvar_95': cvar_95,
            'cvar_99': cvar_99,
            
            # Risk mukofoti ko'rsatkichlari
            'downside_deviation': downside_deviation,
            'sortino_ratio': sortino_ratio,
            'tail_ratio': tail_ratio,
            
            # Maksimal zararlar
            'max_single_day_loss': max_single_day_loss,
            'max_consecutive_losses': self._calculate_max_consecutive_losses(returns),
            
            # Ehtimollik ko'rsatkichlari
            'probability_of_loss': prob_loss,
            'probability_of_large_loss': prob_large_loss,
            
            # Statistik ko'rsatkichlari
            'skewness': skewness,
            'kurtosis': kurtosis,
            
            # Qo'shimcha risk ko'rsatkichlari
            'ulcer_index': ulcer_index,
            'pain_index': pain_index,
            'kelly_fraction': kelly_fraction,
            
            # Boshqa ko'rsatkichlar
            'correlation_with_market': self._simulate_market_correlation(returns),
            'beta_risk': self._calculate_beta_risk(returns)
        }
    
    def calculate_var(self, returns: pd.Series, confidence_level: float = 0.95,
                     method: str = 'historical') -> float:
        """
        Value at Risk (VaR) hisoblash
        
        Args:
            returns: Portfolio daromadlari
            confidence_level: Ishonchlilik darajasi
            method: Hisoblash usuli ('historical', 'parametric', 'monte_carlo')
            
        Returns:
            float: VaR qiymati
        """
        if returns.empty:
            return 0.0
            
        alpha = 1 - confidence_level
        
        if method == 'historical':
            # Tarixiy metod
            return np.percentile(returns, alpha * 100)
            
        elif method == 'parametric':
            # Parametrik metod (Normal distribution)
            z_score = stats.norm.ppf(alpha)
            return returns.mean() + z_score * returns.std()
            
        elif method == 'monte_carlo':
            # Monte Carlo simulyatsiya
            np.random.seed(42)
            simulated_returns = np.random.normal(returns.mean(), returns.std(), 10000)
            return np.percentile(simulated_returns, alpha * 100)
            
        else:
            raise ValueError("Noto'g'ri method. 'historical', 'parametric' yoki 'monte_carlo' tanlang")
    
    def analyze_monthly_performance(self, returns: pd.Series) -> pd.DataFrame:
        """
        Oylik performance tahlili
        
        Args:
            returns: Portfolio daromadlari
            
        Returns:
            pd.DataFrame: Oylik natijalar
        """
        if returns.empty:
            return pd.DataFrame()
            
        # Oylik daromadlarni hisoblash
        monthly_returns = returns.resample('M').apply(lambda x: (1 + x).prod() - 1)
        
        # Oylik ma'lumotlar
        analysis = pd.DataFrame({
            'month': monthly_returns.index,
            'returns': monthly_returns.values,
            'cumulative_returns': (1 + monthly_returns).cumprod(),
            'year': monthly_returns.index.year,
            'month_name': monthly_returns.index.strftime('%B'),
            'is_positive': monthly_returns.values > 0
        })
        
        # Oylik rolling ko'rsatkichlar
        analysis['rolling_3m'] = analysis['returns'].rolling(3).mean()
        analysis['rolling_6m'] = analysis['returns'].rolling(6).mean()
        analysis['rolling_12m'] = analysis['returns'].rolling(12).mean()
        
        # Yillik hisobot
        yearly_summary = analysis.groupby('year').agg({
            'returns': ['sum', 'mean', 'std', 'min', 'max'],
            'is_positive': 'sum',
            'month': 'count'
        }).round(4)
        
        # Best/Worst oylar
        best_month = analysis.loc[analysis['returns'].idxmax()]
        worst_month = analysis.loc[analysis['returns'].idxmin()]
        
        analysis['best_month_flag'] = analysis.index == analysis['returns'].idxmax()
        analysis['worst_month_flag'] = analysis.index == analysis['returns'].idxmin()
        
        return analysis
    
    def risk_return_profile(self, returns: pd.Series) -> Dict[str, float]:
        """
        Risk-return profili tahlili
        
        Args:
            returns: Portfolio daromadlari
            
        Returns:
            Dict[str, float]: Risk-return ko'rsatkichlari
        """
        if returns.empty:
            return {}
            
        # Asosiy ko'rsatkichlar
        annual_return = (1 + returns.mean()) ** 252 - 1
        annual_volatility = returns.std() * np.sqrt(252)
        
        # Risk mukofoti ko'rsatkichlari
        risk_adjusted_return = annual_return / annual_volatility if annual_volatility > 0 else 0
        
        # Calmar ratio (annual return / max drawdown)
        max_dd = abs(self.calculate_max_drawdown(returns))
        calmar_ratio = annual_return / max_dd if max_dd > 0 else 0
        
        # Sterling ratio (3-yillik return / avg drawdown)
        if len(returns) >= 252 * 3:
            three_year_return = (1 + returns.iloc[-252*3:].mean()) ** 252 - 1
            avg_drawdown = abs(self.analyze_drawdown(returns.iloc[-252*3:])['avg_drawdown'])
            sterling_ratio = three_year_return / avg_drawdown if avg_drawdown > 0 else 0
        else:
            sterling_ratio = 0
        
        # Optimal portfolio ko'rsatkichlari
        # (bu yerda real portfolio optimization algoritmi ishlatiladi)
        optimal_sharpe = self.calculate_sharpe_ratio(returns)
        
        # Efficiency ratio
        total_positive = sum(r for r in returns if r > 0)
        total_negative = abs(sum(r for r in returns if r < 0))
        efficiency_ratio = total_positive / (total_positive + total_negative) if (total_positive + total_negative) > 0 else 0
        
        return {
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'risk_adjusted_return': risk_adjusted_return,
            'calmar_ratio': calmar_ratio,
            'sterling_ratio': sterling_ratio,
            'optimal_sharpe_ratio': optimal_sharpe,
            'efficiency_ratio': efficiency_ratio,
            'return_to_risk_ratio': annual_return / annual_volatility if annual_volatility > 0 else 0,
            'volatility_adj_return': annual_return / (annual_volatility ** 2) if annual_volatility > 0 else 0
        }
    
    # Yordamchi funksiyalar
    def _calculate_profit_factor(self, returns: pd.Series) -> float:
        """Profit factor hisoblash"""
        profits = returns[returns > 0].sum()
        losses = abs(returns[returns < 0].sum())
        return profits / losses if losses > 0 else float('inf') if profits > 0 else 0
    
    def _calculate_avg_recovery_time(self, returns: pd.Series, drawdown: pd.Series) -> float:
        """O'rtacha recovery vaqti hisoblash"""
        recovery_times = []
        underwater = drawdown < 0
        in_drawdown = False
        dd_start = None
        
        for i, (date, is_underwater) in enumerate(underwater.items()):
            if is_underwater and not in_drawdown:
                dd_start = i
                in_drawdown = True
            elif not is_underwater and in_drawdown:
                recovery_time = i - dd_start
                recovery_times.append(recovery_time)
                in_drawdown = False
        
        return np.mean(recovery_times) if recovery_times else 0
    
    def _calculate_recovery_factor(self, returns: pd.Series, max_drawdown: float) -> float:
        """Recovery factor hisoblash"""
        total_profit = (1 + returns).prod() - 1
        return total_profit / abs(max_drawdown) if max_drawdown != 0 else 0
    
    def _calculate_drawdown_duration(self, returns: pd.Series) -> pd.Series:
        """Drawdown davomiyligi hisoblash"""
        cumulative_returns = (1 + returns).cumprod()
        peak = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - peak) / peak
        
        duration = 0
        durations = []
        
        for dd in drawdown:
            if dd < 0:
                duration += 1
            else:
                if duration > 0:
                    durations.append(duration)
                duration = 0
        
        if duration > 0:
            durations.append(duration)
        
        # Har bir nuqta uchun joriy drawdown davomiyligi
        current_duration = 0
        result_durations = []
        
        for dd in drawdown:
            if dd < 0:
                current_duration += 1
            else:
                current_duration = 0
            result_durations.append(current_duration)
        
        return pd.Series(result_durations, index=drawdown.index)
    
    def _calculate_max_consecutive_losses(self, returns: pd.Series) -> int:
        """Maksimal ketma-ket zararlar sonini hisoblash"""
        max_consecutive = 0
        current_consecutive = 0
        
        for ret in returns:
            if ret < 0:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    def _calculate_beta_risk(self, returns: pd.Series) -> float:
        """Beta risk hisoblash (simulyatsiya)"""
        # Bu yerda real bozor indeksini ishlatish kerak
        np.random.seed(42)
        market_returns = np.random.normal(0.0005, 0.015, len(returns))
        
        if len(returns) > 1:
            return np.cov(returns, market_returns)[0, 1] / np.var(market_returns)
        return 1.0
    
    def _simulate_market_correlation(self, returns: pd.Series) -> float:
        """Bozor korrelatsiyasini simulyatsiya qilish"""
        np.random.seed(42)
        market_returns = np.random.normal(0.0005, 0.015, len(returns))
        
        if len(returns) > 1:
            return np.corrcoef(returns, market_returns)[0, 1]
        return 0.0
    
    def _calculate_beta_alpha(self, returns: pd.Series, 
                            benchmark_returns: pd.Series) -> Tuple[float, float]:
        """Beta va Alpha koeffitsentlarini hisoblash"""
        if returns.empty or benchmark_returns.empty:
            return 0.0, 0.0
            
        # Time alignment
        aligned_data = pd.concat([returns, benchmark_returns], axis=1).dropna()
        if aligned_data.empty:
            return 0.0, 0.0
            
        portfolio_aligned = aligned_data.iloc[:, 0]
        benchmark_aligned = aligned_data.iloc[:, 1]
        
        # Beta hisoblash
        covariance = np.cov(portfolio_aligned, benchmark_aligned)[0, 1]
        benchmark_variance = benchmark_aligned.var()
        beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
        
        # Alpha hisoblash (annualized)
        portfolio_mean = portfolio_aligned.mean()
        benchmark_mean = benchmark_aligned.mean()
        alpha = (portfolio_mean - beta * benchmark_mean) * 252
        
        return beta, alpha
    
    def _get_empty_metrics(self) -> Dict[str, float]:
        """Bo'sh ma'lumotlar uchun default ko'rsatkichlar"""
        return {
            'total_return': 0.0, 'annualized_return': 0.0, 'volatility': 0.0,
            'sharpe_ratio': 0.0, 'max_drawdown': 0.0, 'win_rate': 0.0,
            'profit_factor': 0.0, 'total_trades': 0, 'avg_return': 0.0,
            'return_std': 0.0, 'best_day': 0.0, 'worst_day': 0.0,
            'var_95': 0.0, 'var_99': 0.0, 'cvar_95': 0.0, 'cvar_99': 0.0
        }
    
    def _get_empty_risk_metrics(self) -> Dict[str, float]:
        """Bo'sh risk ko'rsatkichlari"""
        return {
            'daily_volatility': 0.0, 'annualized_volatility': 0.0,
            'var_95': 0.0, 'var_99': 0.0, 'cvar_95': 0.0, 'cvar_99': 0.0,
            'downside_deviation': 0.0, 'sortino_ratio': 0.0,
            'max_single_day_loss': 0.0, 'probability_of_loss': 0.0,
            'skewness': 0.0, 'kurtosis': 0.0, 'correlation_with_market': 0.0,
            'ulcer_index': 0.0, 'pain_index': 0.0, 'kelly_fraction': 0.0
        }


# Yordamchi funksiyalar
def generate_sample_data(days: int = 252, 
                        start_date: str = '2023-01-01') -> pd.Series:
    """
    Test ma'lumotlarini yaratish uchun yordamchi funksiya
    
    Args:
        days: Kun soni (default: 252 = 1 yil)
        start_date: Boshlang'ich sana
        
    Returns:
        pd.Series: Sample daromadlar
    """
    np.random.seed(42)
    dates = pd.date_range(start=start_date, periods=days, freq='D')
    
    # Realistic return simulation with trends
    returns = []
    cumulative_trend = 1.0
    
    for i in range(days):
        # Trend component
        trend = 0.0001 * np.sin(i / 50) + 0.0002 * np.cos(i / 30)
        
        # Random component
        random_component = np.random.normal(0, 0.015)
        
        # Combine
        daily_return = trend + random_component
        returns.append(daily_return)
        
        cumulative_trend *= (1 + daily_return)
    
    return pd.Series(returns, index=dates)


def calculate_portfolio_metrics(weights: np.ndarray, 
                              returns_df: pd.DataFrame,
                              risk_free_rate: float = 0.02) -> Dict[str, float]:
    """
    Portfolio metrikalarini hisoblash
    
    Args:
        weights: Portfolio vaznlari
        returns_df: Aktivlar daromadlari
        risk_free_rate: Risk mukofoti
        
    Returns:
        Dict[str, float]: Portfolio ko'rsatkichlari
    """
    # Portfolio daromadlari
    portfolio_returns = (returns_df * weights).sum(axis=1)
    
    # Analytics instance yaratish
    analytics = PerformanceAnalytics(risk_free_rate)
    
    # Ko'rsatkichlarni hisoblash
    metrics = analytics.calculate_performance_metrics(portfolio_returns)
    risk_metrics = analytics.get_risk_metrics(portfolio_returns)
    risk_return = analytics.risk_return_profile(portfolio_returns)
    
    # Barcha natijalarni birlashtirish
    return {**metrics, **risk_metrics, **risk_return}


# Test funksiyasi
def test_performance_analytics():
    """Performance analytics test funksiyasi"""
    print("=== Performance Analytics Test ===")
    
    # Analytics instance yaratish
    analytics = PerformanceAnalytics(risk_free_rate=0.02)
    
    # Sample data
    sample_returns = generate_sample_data(252)
    print(f"Sample returns: {len(sample_returns)} kun")
    
    # Test 1: Asosiy ko'rsatkichlar
    print("\n1. Asosiy performance ko'rsatkichlari:")
    metrics = analytics.calculate_performance_metrics(sample_returns)
    for key, value in list(metrics.items())[:10]:
        print(f"   {key}: {value:.4f}")
    
    # Test 2: Risk ko'rsatkichlari
    print("\n2. Risk ko'rsatkichlari:")
    risk_metrics = analytics.get_risk_metrics(sample_returns)
    for key, value in list(risk_metrics.items())[:8]:
        print(f"   {key}: {value:.4f}")
    
    # Test 3: Drawdown tahlili
    print("\n3. Drawdown tahlili:")
    drawdown_analysis = analytics.analyze_drawdown(sample_returns)
    print(f"   Maksimal drawdown: {drawdown_analysis['max_drawdown']:.4f}")
    print(f"   O'rtacha recovery vaqti: {drawdown_analysis['avg_recovery_time_days']:.1f} kun")
    
    # Test 4: Sharpe ratio
    print("\n4. Sharpe ratio test:")
    sharpe = analytics.calculate_sharpe_ratio(sample_returns)
    print(f"   Sharpe ratio: {sharpe:.4f}")
    
    # Test 5: Maksimal drawdown
    print("\n5. Max drawdown test:")
    max_dd = analytics.calculate_max_drawdown(sample_returns)
    print(f"   Max drawdown: {max_dd:.4f}")
    
    # Test 6: Portfolio taqqoslash
    print("\n6. Portfolio taqqoslash test:")
    returns_list = [sample_returns, sample_returns * 1.2]  # Ikkinchi portfolio 20% yuqori
    labels = ['Portfolio A', 'Portfolio B']
    comparison = analytics.compare_performance(returns_list, labels)
    print(f"   Taqqoslangan portfolio soni: {len(comparison)}")
    
    print("\nTest muvaffaqiyatli tugallandi!")


if __name__ == "__main__":
    test_performance_analytics()