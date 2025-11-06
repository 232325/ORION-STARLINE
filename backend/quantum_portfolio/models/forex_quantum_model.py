"""
Forex Quantum Model
===================

Foreign Exchange markets uchun quantum portfolio model.
Bu modul valyuta juftliklari uchun quantum portfolio optimizatsiyasini amalga oshiradi.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
import logging
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

class ForexQuantumModel:
    """
    Forex Quantum Model - Valyuta juftliklari uchun quantum portfolio modeli
    """
    
    def __init__(self, 
                 currency_pairs: List[str],
                 quantum_coherence_time: float = 100.0,
                 base_currency: str = 'USD'):
        """
        Initialize forex quantum model
        
        Args:
            currency_pairs: Currency pair nomlari (e.g., ['EURUSD', 'GBPUSD'])
            quantum_coherence_time: Quantum coherence time
            base_currency: Base currency for calculations
        """
        self.currency_pairs = currency_pairs
        self.n_pairs = len(currency_pairs)
        self.base_currency = base_currency
        
        # Currency quantum properties
        self.currency_states = {}
        self.pair_entanglement = {}
        self.central_bank_quantum_effects = {}
        
        # Market regime detection
        self.trending_regime = {}
        self.ranging_regime = {}
        
        # Carry trade opportunities
        self.carry_opportunities = {}
        
        self.quantum_coherence_time = quantum_coherence_time
        self.logger = logging.getLogger(__name__)
        
        self._initialize_quantum_currency_states()
    
    def _initialize_quantum_currency_states(self):
        """Currency quantum states initialization"""
        # Major currencies with their quantum characteristics
        currency_characteristics = {
            'USD': {'volatility': 0.8, 'liquidity': 1.0, 'safe_haven': 0.9},
            'EUR': {'volatility': 0.7, 'liquidity': 0.9, 'safe_haven': 0.6},
            'GBP': {'volatility': 1.0, 'liquidity': 0.8, 'safe_haven': 0.5},
            'JPY': {'volatility': 0.6, 'liquidity': 0.9, 'safe_haven': 0.95},
            'CHF': {'volatility': 0.5, 'liquidity': 0.7, 'safe_haven': 0.98},
            'CAD': {'volatility': 0.9, 'liquidity': 0.6, 'safe_haven': 0.4},
            'AUD': {'volatility': 1.1, 'liquidity': 0.7, 'safe_haven': 0.3},
            'NZD': {'volatility': 1.2, 'liquidity': 0.5, 'safe_haven': 0.2}
        }
        
        # Initialize quantum states for currencies
        for pair in self.currency_pairs:
            base_currency = pair[:3]
            quote_currency = pair[3:]
            
            # Base currency state
            base_chars = currency_characteristics.get(base_currency, 
                                                    {'volatility': 0.8, 'liquidity': 0.7, 'safe_haven': 0.5})
            
            # Quote currency state
            quote_chars = currency_characteristics.get(quote_currency,
                                                     {'volatility': 0.8, 'liquidity': 0.7, 'safe_haven': 0.5})
            
            # Create pair quantum state
            pair_state = self._create_pair_quantum_state(base_chars, quote_chars)
            self.currency_states[pair] = pair_state
            
            # Calculate pair entanglement
            self._calculate_pair_entanglement(pair, base_chars, quote_chars)
    
    def _create_pair_quantum_state(self, base_chars: Dict, quote_chars: Dict) -> np.ndarray:
        """Create quantum state for currency pair"""
        # State parameters based on currency characteristics
        volatility_factor = (base_chars['volatility'] + quote_chars['volatility']) / 2
        liquidity_factor = (base_chars['liquidity'] + quote_chars['liquidity']) / 2
        safe_haven_balance = base_chars['safe_haven'] - quote_chars['safe_haven']
        
        # Create superposition state
        alpha_magnitude = np.sqrt((liquidity_factor + 0.5) / 1.5)
        beta_magnitude = np.sqrt((volatility_factor + 0.5) / 1.5)
        
        # Normalize
        norm = np.sqrt(alpha_magnitude**2 + beta_magnitude**2)
        alpha_magnitude /= norm
        beta_magnitude /= norm
        
        # Add phase based on safe haven balance
        phase = np.arctan2(safe_haven_balance, 1.0) / 2
        
        # Create complex quantum state
        alpha = alpha_magnitude * np.exp(1j * phase)
        beta = beta_magnitude * np.exp(-1j * phase)
        
        return np.array([alpha, beta], dtype=complex)
    
    def _calculate_pair_entanglement(self, pair: str, base_chars: Dict, quote_chars: Dict):
        """Calculate entanglement between currency pairs"""
        self.pair_entanglement[pair] = {}
        
        for other_pair in self.currency_pairs:
            if pair != other_pair:
                # Common currency entanglement
                pair_base = pair[:3]
                pair_quote = pair[3:]
                other_base = other_pair[:3]
                other_quote = other_pair[3:]
                
                common_currencies = {pair_base, pair_quote} & {other_base, other_quote}
                
                if common_currencies:
                    # Higher entanglement for shared currencies
                    entanglement_strength = 0.8 if len(common_currencies) == 1 else 0.5
                else:
                    # Lower entanglement for different currencies
                    entanglement_strength = 0.1
                
                self.pair_entanglement[pair][other_pair] = entanglement_strength
    
    def load_data(self, 
                  exchange_rate_data: pd.DataFrame,
                  interest_rates: Optional[Dict] = None):
        """
        Forex data yuklash
        
        Args:
            exchange_rate_data: Exchange rate ma'lumotlari
            interest_rates: Interest rate ma'lumotlari (optional)
        """
        # Validate available pairs
        available_pairs = [pair for pair in self.currency_pairs if pair in exchange_rate_data.columns]
        
        if not available_pairs:
            raise ValueError("Hech qanday currency pair ma'lumoti topilmadi")
        
        self.returns_data = exchange_rate_data[available_pairs].pct_change().dropna()
        
        # Load interest rates if available
        if interest_rates:
            self.interest_rates = interest_rates
            self._calculate_carry_opportunities()
        
        # Detect market regimes
        self._detect_market_regimes()
        
        self.logger.info(f"Forex data yuklandi: {len(available_pairs)} currency pair")
    
    def _calculate_carry_opportunities(self):
        """Carry trade opportunities hisoblash"""
        if not hasattr(self, 'interest_rates'):
            return
        
        self.carry_opportunities = {}
        
        for pair in self.currency_pairs:
            base_curr = pair[:3]
            quote_curr = pair[3:]
            
            if base_curr in self.interest_rates and quote_curr in self.interest_rates:
                base_rate = self.interest_rates[base_curr]
                quote_rate = self.interest_rates[quote_curr]
                
                # Carry return (interest rate differential)
                carry_return = base_rate - quote_rate
                
                # Quantum carry enhancement
                pair_state = self.currency_states[pair]
                quantum_enhancement = np.real(pair_state[0] * np.conj(pair_state[1]))
                enhanced_carry = carry_return * (1 + quantum_enhancement * 0.1)
                
                self.carry_opportunities[pair] = {
                    'carry_return': carry_return,
                    'enhanced_carry': enhanced_carry,
                    'quantum_enhancement': quantum_enhancement,
                    'base_rate': base_rate,
                    'quote_rate': quote_rate
                }
    
    def _detect_market_regimes(self):
        """Market regime detection (trending vs ranging)"""
        self.trending_regime = {}
        self.ranging_regime = {}
        
        for pair in self.returns_data.columns:
            returns = self.returns_data[pair].dropna()
            
            if len(returns) < 20:  # Not enough data
                continue
            
            # Calculate trend strength using rolling standard deviation
            rolling_std = returns.rolling(window=20).std()
            current_std = rolling_std.iloc[-1] if not rolling_std.empty else returns.std()
            avg_std = returns.std()
            
            # Regime detection based on volatility
            volatility_ratio = current_std / avg_std
            
            if volatility_ratio < 0.8:  # Low volatility = ranging market
                self.ranging_regime[pair] = True
                self.trending_regime[pair] = False
            elif volatility_ratio > 1.2:  # High volatility = trending market
                self.trending_regime[pair] = True
                self.ranging_regime[pair] = False
            else:  # Mixed regime
                self.trending_regime[pair] = False
                self.ranging_regime[pair] = False
    
    def quantum_correlation_matrix(self) -> np.ndarray:
        """
        Quantum correlation matrix for currency pairs
        """
        if not hasattr(self, 'returns_data'):
            raise ValueError("Returns ma'lumotlari yuklanmagan")
        
        # Classical correlation
        classical_corr = self.returns_data.corr().values
        
        # Quantum corrections
        n_pairs = len(self.returns_data.columns)
        quantum_corr = classical_corr.copy()
        
        for i in range(n_pairs):
            for j in range(i + 1, n_pairs):
                pair_i = self.returns_data.columns[i]
                pair_j = self.returns_data.columns[j]
                
                # Entanglement-based correlation adjustment
                if pair_i in self.pair_entanglement and pair_j in self.pair_entanglement[pair_i]:
                    entanglement = self.pair_entanglement[pair_i][pair_j]
                    quantum_corr[i, j] = classical_corr[i, j] * (1 + entanglement * 0.1)
                    quantum_corr[j, i] = classical_corr[i, j] * (1 + entanglement * 0.1)
                
                # Safe haven effects
                pair_i_state = self.currency_states[pair_i]
                pair_j_state = self.currency_states[pair_j]
                
                safe_haven_correlation = np.real(np.vdot(pair_i_state, pair_j_state))
                if abs(safe_haven_correlation) > 0.5:  # Strong quantum correlation
                    quantum_corr[i, j] *= 0.9  # Reduce correlation due to safe haven effects
                    quantum_corr[j, i] *= 0.9
        
        return quantum_corr
    
    def calculate_quantum_spot_forward_relationship(self, 
                                                   pair: str,
                                                   forward_points: Optional[pd.Series] = None) -> Dict:
        """
        Quantum spot-forward relationship analysis
        
        Args:
            pair: Currency pair
            forward_points: Forward points (optional)
            
        Returns:
            Spot-forward relationship analysis
        """
        if pair not in self.returns_data.columns:
            raise ValueError(f"Currency pair {pair} topilmadi")
        
        # Current spot rate
        current_spot = self.returns_data[pair].iloc[-1] if not self.returns_data.empty else 0
        
        # Quantum state of the pair
        pair_state = self.currency_states[pair]
        
        # Quantum uncertainty principle for spot-forward
        quantum_uncertainty = np.abs(pair_state[0] * np.conj(pair_state[1]))
        
        # Forward rate estimation (simplified)
        if hasattr(self, 'interest_rates'):
            base_curr = pair[:3]
            quote_curr = pair[3:]
            
            if base_curr in self.interest_rates and quote_curr in self.interest_rates:
                base_rate = self.interest_rates[base_curr]
                quote_rate = self.interest_rates[quote_curr]
                rate_differential = base_rate - quote_rate
                
                # Quantum forward rate
                quantum_forward_adj = rate_differential * (1 + quantum_uncertainty * 0.05)
                estimated_forward = current_spot * (1 + quantum_forward_adj)
                
                return {
                    'pair': pair,
                    'current_spot': current_spot,
                    'rate_differential': rate_differential,
                    'estimated_forward': estimated_forward,
                    'quantum_uncertainty': quantum_uncertainty,
                    'quantum_adjustment': quantum_forward_adj
                }
        
        return {
            'pair': pair,
            'current_spot': current_spot,
            'quantum_uncertainty': quantum_uncertainty,
            'note': 'Forward calculation requires interest rates'
        }
    
    def quantum_risk_parity_portfolio(self, 
                                    regime_filtering: bool = True,
                                    carry_weight: float = 0.3) -> Dict:
        """
        Quantum risk parity portfolio construction
        
        Args:
            regime_filtering: Use regime detection for allocation
            carry_weight: Weight for carry trade component
            
        Returns:
            Risk parity portfolio allocation
        """
        if not hasattr(self, 'returns_data'):
            raise ValueError("Returns ma'lumotlari yuklanmagan")
        
        # Calculate quantum volatilities
        pair_volatilities = {}
        quantum_volatilities = {}
        
        for pair in self.returns_data.columns:
            classical_vol = self.returns_data[pair].std()
            pair_state = self.currency_states[pair]
            
            # Quantum volatility enhancement
            quantum_enhancement = np.abs(pair_state[0]) ** 2
            quantum_vol = classical_vol * (1 + quantum_enhancement * 0.1)
            
            pair_volatilities[pair] = classical_vol
            quantum_volatilities[pair] = quantum_vol
        
        # Apply regime filtering
        if regime_filtering:
            for pair in list(quantum_volatilities.keys()):
                if self.trending_regime.get(pair, False):
                    # Reduce volatility in trending markets (momentum effect)
                    quantum_volatilities[pair] *= 0.8
                elif self.ranging_regime.get(pair, False):
                    # Increase volatility in ranging markets (mean reversion effect)
                    quantum_volatilities[pair] *= 1.2
        
        # Risk parity weights
        total_vol = sum(1/vol for vol in quantum_volatilities.values())
        
        risk_parity_weights = {}
        for pair, vol in quantum_volatilities.items():
            risk_parity_weights[pair] = (1/vol) / total_vol
        
        # Apply carry trade adjustment
        if hasattr(self, 'carry_opportunities'):
            for pair, carry_data in self.carry_opportunities.items():
                if pair in risk_parity_weights:
                    carry_factor = abs(carry_data['enhanced_carry'])
                    risk_parity_weights[pair] *= (1 + carry_weight * carry_factor)
        
        # Normalize weights
        total_weight = sum(risk_parity_weights.values())
        risk_parity_weights = {pair: weight/total_weight 
                             for pair, weight in risk_parity_weights.items()}
        
        # Calculate portfolio metrics
        portfolio_vol = np.sqrt(sum(weight**2 * vol**2 for pair, vol in pair_volatilities.items() 
                                  for weight in [risk_parity_weights[pair]]))
        
        # Expected portfolio return
        if hasattr(self, 'carry_opportunities'):
            expected_carry = sum(risk_parity_weights[pair] * carry_data['enhanced_carry'] 
                               for pair, carry_data in self.carry_opportunities.items() 
                               if pair in risk_parity_weights)
        else:
            expected_carry = 0
        
        # Quantum portfolio coherence
        quantum_coherence = self._portfolio_quantum_coherence(risk_parity_weights)
        
        return {
            'weights': risk_parity_weights,
            'portfolio_volatility': portfolio_vol,
            'expected_carry_return': expected_carry,
            'quantum_coherence': quantum_coherence,
            'regime_filtering_applied': regime_filtering,
            'carry_weight_used': carry_weight,
            'risk_contributions': {pair: weight * vol for pair, vol in pair_volatilities.items() 
                                 for weight in [risk_parity_weights[pair]]}
        }
    
    def _portfolio_quantum_coherence(self, weights: Dict[str, float]) -> float:
        """Portfolio quantum coherence calculation"""
        coherence = 0.0
        
        for pair, weight in weights.items():
            if pair in self.currency_states:
                pair_state = self.currency_states[pair]
                off_diagonal = np.abs(pair_state[0] * np.conj(pair_state[1]))
                coherence += weight * off_diagonal
        
        return coherence
    
    def quantum_volatility_forecasting(self, 
                                     pair: str,
                                     forecast_horizon: int = 30,
                                     method: str = 'quantum_garch') -> Dict:
        """
        Quantum volatility forecasting
        
        Args:
            pair: Currency pair
            forecast_horizon: Forecast horizon in days
            method: Forecasting method ('quantum_garch', 'quantum_ar', 'quantum_sv')
            
        Returns:
            Volatility forecast
        """
        if pair not in self.returns_data.columns:
            raise ValueError(f"Currency pair {pair} topilmadi")
        
        returns = self.returns_data[pair].dropna()
        
        if method == 'quantum_garch':
            return self._quantum_garch_forecast(returns, forecast_horizon)
        elif method == 'quantum_ar':
            return self._quantum_ar_forecast(returns, forecast_horizon)
        elif method == 'quantum_sv':
            return self._quantum_stochastic_volatility_forecast(returns, forecast_horizon)
        else:
            raise ValueError(f"Qo'llab-quvvatlanmaydigan method: {method}")
    
    def _quantum_garch_forecast(self, returns: pd.Series, horizon: int) -> Dict:
        """Quantum GARCH volatility forecast"""
        # Simplified GARCH(1,1) with quantum enhancement
        alpha = 0.1  # GARCH alpha
        beta = 0.85  # GARCH beta
        omega = returns.var() * (1 - alpha - beta)  # Long-run variance
        
        # Current variance
        current_var = returns.var()
        
        # Quantum enhancement
        pair_state = self.currency_states[returns.name]
        quantum_factor = np.abs(pair_state[0]) ** 2
        omega_quantum = omega * (1 + quantum_factor * 0.05)
        
        # Forecast variance
        forecast_vars = []
        current_variance = current_var
        
        for t in range(horizon):
            next_variance = omega_quantum + alpha * current_variance + beta * current_variance
            forecast_vars.append(next_variance)
            current_variance = next_variance
        
        # Convert to volatility
        forecast_vols = [np.sqrt(var) for var in forecast_vars]
        
        return {
            'method': 'quantum_garch',
            'forecast_volatility': forecast_vols,
            'quantum_enhancement': quantum_factor,
            'current_volatility': np.sqrt(current_var),
            'forecast_horizon': horizon
        }
    
    def _quantum_ar_forecast(self, returns: pd.Series, horizon: int) -> Dict:
        """Quantum AR volatility forecast"""
        # AR(1) model for returns with quantum enhancement
        ar_coef = np.corrcoef(returns.iloc[1:].values, returns.iloc[:-1].values)[0, 1]
        
        # Quantum adjustment
        pair_state = self.currency_states[returns.name]
        quantum_factor = np.real(pair_state[0] * np.conj(pair_state[1]))
        ar_coef_quantum = ar_coef * (1 + quantum_factor * 0.1)
        
        # Forecast returns
        last_return = returns.iloc[-1]
        forecast_returns = []
        
        for t in range(horizon):
            next_return = ar_coef_quantum * last_return
            forecast_returns.append(next_return)
            last_return = next_return
        
        # Calculate volatility from forecast returns
        forecast_vol = np.std(forecast_returns) if len(forecast_returns) > 1 else returns.std()
        
        return {
            'method': 'quantum_ar',
            'forecast_returns': forecast_returns,
            'forecast_volatility': [forecast_vol] * horizon,
            'quantum_enhancement': quantum_factor,
            'ar_coefficient': ar_coef_quantum
        }
    
    def _quantum_stochastic_volatility_forecast(self, returns: pd.Series, horizon: int) -> Dict:
        """Quantum stochastic volatility forecast"""
        # Simplified stochastic volatility with quantum enhancement
        returns_squared = returns ** 2
        log_returns_squared = np.log(returns_squared + 1e-8)
        
        # Estimate parameters
        mean_log_var = np.mean(log_returns_squared)
        var_log_var = np.var(log_returns_squared)
        
        # Quantum enhancement
        pair_state = self.currency_states[returns.name]
        quantum_factor = np.abs(pair_state[1]) ** 2  # Using |1⟩ state for volatility
        
        # Forecast log variance
        forecast_log_vars = []
        current_log_var = mean_log_var
        
        for t in range(horizon):
            # Random walk with quantum enhancement
            noise = np.random.normal(0, np.sqrt(var_log_var) * (1 + quantum_factor * 0.1))
            next_log_var = current_log_var + noise
            forecast_log_vars.append(next_log_var)
            current_log_var = next_log_var
        
        # Convert to volatility
        forecast_vols = [np.sqrt(np.exp(log_var)) for log_var in forecast_log_vars]
        
        return {
            'method': 'quantum_stochastic_volatility',
            'forecast_volatility': forecast_vols,
            'quantum_enhancement': quantum_factor,
            'mean_log_variance': mean_log_var
        }
    
    def central_bank_quantum_intervention_analysis(self, 
                                                 central_bank: str,
                                                 intervention_history: Optional[pd.DataFrame] = None) -> Dict:
        """
        Central bank quantum intervention analysis
        
        Args:
            central_bank: Central bank name ('FED', 'ECB', 'BOJ', etc.)
            intervention_history: Intervention history data (optional)
            
        Returns:
            Central bank intervention analysis
        """
        # Central bank quantum characteristics
        cb_characteristics = {
            'FED': {'hawkish_bias': 0.3, 'dovish_bias': 0.7, 'intervention_strength': 0.8},
            'ECB': {'hawkish_bias': 0.4, 'dovish_bias': 0.6, 'intervention_strength': 0.7},
            'BOJ': {'hawkish_bias': 0.2, 'dovish_bias': 0.8, 'intervention_strength': 0.9},
            'BOE': {'hawkish_bias': 0.5, 'dovish_bias': 0.5, 'intervention_strength': 0.6},
            'SNB': {'hawkish_bias': 0.1, 'dovish_bias': 0.9, 'intervention_strength': 0.95}
        }
        
        cb_chars = cb_characteristics.get(central_bank, cb_characteristics['FED'])
        
        # Quantum intervention effect
        quantum_intervention = (cb_chars['hawkish_bias'] - cb_chars['dovish_bias']) * cb_chars['intervention_strength']
        
        # Currency impact analysis
        currency_impact = {}
        
        for pair in self.currency_pairs:
            base_curr = pair[:3]
            quote_curr = pair[3:]
            
            # Determine if central bank affects this pair
            if central_bank == 'FED' and base_curr == 'USD':
                impact = quantum_intervention
            elif central_bank == 'ECB' and (base_curr == 'EUR' or quote_curr == 'EUR'):
                impact = quantum_intervention * 0.8
            elif central_bank == 'BOJ' and (base_curr == 'JPY' or quote_curr == 'JPY'):
                impact = quantum_intervention * 1.1
            else:
                impact = 0
            
            currency_impact[pair] = {
                'quantum_impact': impact,
                'intervention_strength': cb_chars['intervention_strength'],
                'hawkish_bias': cb_chars['hawkish_bias'],
                'dovish_bias': cb_chars['dovish_bias']
            }
        
        return {
            'central_bank': central_bank,
            'characteristics': cb_chars,
            'overall_quantum_intervention': quantum_intervention,
            'currency_impacts': currency_impact
        }
    
    def visualize_quantum_forex_analysis(self, save_path: Optional[str] = None) -> None:
        """Quantum forex analysis visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Quantum Forex Analysis Dashboard', fontsize=16)
        
        # 1. Quantum correlation heatmap
        if hasattr(self, 'returns_data') and not self.returns_data.empty:
            quantum_corr = self.quantum_correlation_matrix()
            
            im1 = axes[0, 0].imshow(quantum_corr, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
            axes[0, 0].set_title('Quantum Correlation Matrix')
            axes[0, 0].set_xticks(range(len(self.returns_data.columns)))
            axes[0, 0].set_yticks(range(len(self.returns_data.columns)))
            axes[0, 0].set_xticklabels(self.returns_data.columns, rotation=45)
            axes[0, 0].set_yticklabels(self.returns_data.columns)
            plt.colorbar(im1, ax=axes[0, 0])
        
        # 2. Carry trade opportunities
        if hasattr(self, 'carry_opportunities') and self.carry_opportunities:
            pairs = list(self.carry_opportunities.keys())
            carry_returns = [self.carry_opportunities[pair]['enhanced_carry'] for pair in pairs]
            
            bars = axes[0, 1].bar(pairs, carry_returns, 
                                color=['green' if x > 0 else 'red' for x in carry_returns])
            axes[0, 1].set_title('Enhanced Carry Trade Returns')
            axes[0, 1].tick_params(axis='x', rotation=45)
            axes[0, 1].set_ylabel('Carry Return')
            axes[0, 1].axhline(y=0, color='black', linestyle='--', alpha=0.5)
        
        # 3. Quantum states visualization
        if self.currency_states:
            first_pair = list(self.currency_states.keys())[0]
            quantum_state = self.currency_states[first_pair]
            
            x = [0, 1]
            y = [np.abs(quantum_state[0])**2, np.abs(quantum_state[1])**2]
            
            axes[1, 0].bar(x, y, color=['blue', 'red'], alpha=0.7)
            axes[1, 0].set_title(f'Quantum State Probabilities - {first_pair}')
            axes[1, 0].set_xlabel('Quantum State |0⟩, |1⟩')
            axes[1, 0].set_ylabel('Probability')
        
        # 4. Market regime distribution
        if hasattr(self, 'trending_regime') and hasattr(self, 'ranging_regime'):
            trending_pairs = [pair for pair, trending in self.trending_regime.items() if trending]
            ranging_pairs = [pair for pair, ranging in self.ranging_regime.items() if ranging]
            neutral_pairs = [pair for pair in self.currency_pairs 
                           if not self.trending_regime.get(pair, False) and not self.ranging_regime.get(pair, False)]
            
            regime_data = {
                'Trending': len(trending_pairs),
                'Ranging': len(ranging_pairs),
                'Neutral': len(neutral_pairs)
            }
            
            axes[1, 1].pie(regime_data.values(), labels=regime_data.keys(), autopct='%1.1f%%')
            axes[1, 1].set_title('Market Regime Distribution')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Quantum forex analysis visualization saqlandi: {save_path}")
        else:
            plt.show()
    
    def save_model_state(self, filepath: str):
        """Model state saqlash"""
        model_state = {
            'currency_pairs': self.currency_pairs,
            'base_currency': self.base_currency,
            'quantum_coherence_time': self.quantum_coherence_time,
            'currency_states': {
                pair: state.tolist() for pair, state in self.currency_states.items()
            },
            'pair_entanglement': self.pair_entanglement,
            'trending_regime': self.trending_regime,
            'ranging_regime': self.ranging_regime
        }
        
        import json
        with open(filepath, 'w') as f:
            json.dump(model_state, f, indent=2, default=str)
        
        self.logger.info(f"Forex model state saqlandi: {filepath}")
    
    def load_model_state(self, filepath: str):
        """Model state yuklash"""
        import json
        with open(filepath, 'r') as f:
            model_state = json.load(f)
        
        self.currency_pairs = model_state['currency_pairs']
        self.base_currency = model_state['base_currency']
        self.quantum_coherence_time = model_state['quantum_coherence_time']
        
        # Restore quantum states
        self.currency_states = {
            pair: np.array(state, dtype=complex) for pair, state in model_state['currency_states'].items()
        }
        
        # Restore other states
        self.pair_entanglement = model_state['pair_entanglement']
        self.trending_regime = model_state['trending_regime']
        self.ranging_regime = model_state['ranging_regime']
        
        self.logger.info(f"Forex model state yuklandi: {filepath}")