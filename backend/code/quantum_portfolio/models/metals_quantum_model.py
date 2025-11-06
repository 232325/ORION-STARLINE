"""
Metals Quantum Model
====================

Precious metals uchun quantum portfolio model.
Bu modul qimmatbaho metallar bo'yicha quantum portfolio optimizatsiyasini amalga oshiradi.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
import logging
import matplotlib.pyplot as plt
from datetime import datetime

class MetalsQuantumModel:
    """
    Metals Quantum Model - Qimmatbaho metallar uchun quantum portfolio modeli
    """
    
    def __init__(self, 
                 metals: List[str],
                 quantum_coherence_time: float = 100.0,
                 storage_costs: Optional[Dict[str, float]] = None):
        """
        Initialize metals quantum model
        
        Args:
            metals: Metal nomlari (e.g., ['GOLD', 'SILVER', 'PLATINUM', 'PALLADIUM'])
            quantum_coherence_time: Quantum coherence time
            storage_costs: Annual storage costs as percentage
        """
        self.metals = metals
        self.n_metals = len(metals)
        self.storage_costs = storage_costs or {}
        
        # Metal quantum states and characteristics
        self.metal_quantum_states = {}
        self.metal_characteristics = {}
        self.seasonal_patterns = {}
        self.supply_demand_factors = {}
        
        # Market microstructure
        self.liquidity_profiles = {}
        self.volatility_regimes = {}
        
        self.quantum_coherence_time = quantum_coherence_time
        self.logger = logging.getLogger(__name__)
        
        self._initialize_metal_quantum_properties()
    
    def _initialize_metal_quantum_properties(self):
        """Metal quantum properties initialization"""
        # Metal characteristics
        metal_specs = {
            'GOLD': {
                'volatility': 0.15,
                'liquidity': 1.0,
                'safe_haven': 0.95,
                'industrial_demand': 0.2,
                'jewelry_demand': 0.7,
                'central_bank_demand': 0.8,
                'seasonal_strength': [12, 1, 9],  # Strong months
                'quantum_resistance': 0.9  # Resistance to quantum decoherence
            },
            'SILVER': {
                'volatility': 0.25,
                'liquidity': 0.8,
                'safe_haven': 0.7,
                'industrial_demand': 0.6,
                'jewelry_demand': 0.4,
                'central_bank_demand': 0.3,
                'seasonal_strength': [12, 1, 7, 8],
                'quantum_resistance': 0.7
            },
            'PLATINUM': {
                'volatility': 0.35,
                'liquidity': 0.5,
                'safe_haven': 0.4,
                'industrial_demand': 0.8,
                'jewelry_demand': 0.1,
                'central_bank_demand': 0.2,
                'seasonal_strength': [3, 4, 11],
                'quantum_resistance': 0.6
            },
            'PALLADIUM': {
                'volatility': 0.45,
                'liquidity': 0.3,
                'safe_haven': 0.3,
                'industrial_demand': 0.9,
                'jewelry_demand': 0.05,
                'central_bank_demand': 0.1,
                'seasonal_strength': [5, 6, 9],
                'quantum_resistance': 0.5
            },
            'COPPER': {
                'volatility': 0.30,
                'liquidity': 0.7,
                'safe_haven': 0.1,
                'industrial_demand': 0.95,
                'jewelry_demand': 0.0,
                'central_bank_demand': 0.0,
                'seasonal_strength': [2, 3, 10],
                'quantum_resistance': 0.4
            }
        }
        
        for metal in self.metals:
            if metal in metal_specs:
                self.metal_characteristics[metal] = metal_specs[metal]
            else:
                # Default characteristics
                self.metal_characteristics[metal] = {
                    'volatility': 0.25,
                    'liquidity': 0.6,
                    'safe_haven': 0.5,
                    'industrial_demand': 0.5,
                    'jewelry_demand': 0.3,
                    'central_bank_demand': 0.4,
                    'seasonal_strength': [1, 12],
                    'quantum_resistance': 0.5
                }
            
            # Create quantum state for metal
            self.metal_quantum_states[metal] = self._create_metal_quantum_state(metal)
            
            # Initialize liquidity profile
            self.liquidity_profiles[metal] = self._initialize_liquidity_profile(metal)
            
            # Supply-demand factors
            self.supply_demand_factors[metal] = self._calculate_supply_demand_factors(metal)
    
    def _create_metal_quantum_state(self, metal: str) -> np.ndarray:
        """Create quantum state for metal"""
        chars = self.metal_characteristics[metal]
        
        # Quantum state based on metal characteristics
        safe_haven_strength = chars['safe_haven']
        industrial_demand = chars['industrial_demand']
        liquidity = chars['liquidity']
        
        # Create superposition: safe_haven state |0⟩ vs industrial state |1⟩
        alpha_magnitude = np.sqrt(safe_haven_strength)
        beta_magnitude = np.sqrt(industrial_demand)
        
        # Normalize
        norm = np.sqrt(alpha_magnitude**2 + beta_magnitude**2)
        alpha_magnitude /= norm
        beta_magnitude /= norm
        
        # Add phase based on liquidity and quantum resistance
        phase = np.arctan2(liquidity - 0.5, chars['quantum_resistance']) / 3
        
        alpha = alpha_magnitude * np.exp(1j * phase)
        beta = beta_magnitude * np.exp(-1j * phase)
        
        return np.array([alpha, beta], dtype=complex)
    
    def _initialize_liquidity_profile(self, metal: str) -> Dict:
        """Initialize liquidity profile for metal"""
        liquidity = self.metal_characteristics[metal]['liquidity']
        
        return {
            'market_hours_volatility': liquidity * 0.8,
            'after_hours_volatility': liquidity * 1.2,
            'liquidity_premium': (1 - liquidity) * 0.05,
            'bid_ask_spread_proxy': (1 - liquidity) * 0.02
        }
    
    def _calculate_supply_demand_factors(self, metal: str) -> Dict:
        """Calculate supply-demand factors"""
        chars = self.metal_characteristics[metal]
        
        # Mining production factors
        production_difficulty = 1 - chars['liquidity']  # Less liquid = harder to produce
        
        # Demand factors
        total_demand = (chars['industrial_demand'] + 
                       chars['jewelry_demand'] + 
                       chars['central_bank_demand'])
        
        # Supply-demand imbalance
        supply_factor = 1 - production_difficulty
        demand_factor = total_demand
        
        # Quantum enhancement
        quantum_state = self.metal_quantum_states[metal]
        quantum_enhancement = np.real(quantum_state[0] * np.conj(quantum_state[1]))
        
        return {
            'supply_factor': supply_factor,
            'demand_factor': demand_factor,
            'imbalance': demand_factor - supply_factor,
            'quantum_enhancement': quantum_enhancement,
            'production_difficulty': production_difficulty,
            'total_demand': total_demand
        }
    
    def load_data(self, 
                  price_data: pd.DataFrame,
                  inventory_data: Optional[pd.DataFrame] = None,
                  mining_production: Optional[pd.DataFrame] = None):
        """
        Metals data yuklash
        
        Args:
            price_data: Metal narxlari DataFrame
            inventory_data: Inventory ma'lumotlari (optional)
            mining_production: Mining production ma'lumotlari (optional)
        """
        # Validate available metals
        available_metals = [metal for metal in self.metals if metal in price_data.columns]
        
        if not available_metals:
            raise ValueError("Hech qanday metal ma'lumoti topilmadi")
        
        self.price_data = price_data[available_metals]
        self.returns_data = price_data[available_metals].pct_change().dropna()
        
        # Load additional data if available
        if inventory_data is not None:
            self.inventory_data = inventory_data[available_metals] if available_metals else None
        
        if mining_production is not None:
            self.production_data = mining_production[available_metals] if available_metals else None
        
        # Analyze volatility regimes
        self._analyze_volatility_regimes()
        
        # Update seasonal patterns
        self._update_seasonal_patterns()
        
        self.logger.info(f"Metals data yuklandi: {len(available_metals)} metals")
    
    def _analyze_volatility_regimes(self):
        """Volatility regime analysis"""
        for metal in self.returns_data.columns:
            returns = self.returns_data[metal].dropna()
            
            if len(returns) < 50:
                continue
            
            # Calculate rolling volatility
            rolling_vol = returns.rolling(window=20).std()
            
            # Define volatility thresholds
            vol_25 = np.percentile(rolling_vol.dropna(), 25)
            vol_75 = np.percentile(rolling_vol.dropna(), 75)
            
            # Classify regimes
            current_vol = rolling_vol.iloc[-1] if not rolling_vol.empty else returns.std()
            
            if current_vol < vol_25:
                regime = 'low_volatility'
            elif current_vol > vol_75:
                regime = 'high_volatility'
            else:
                regime = 'normal_volatility'
            
            self.volatility_regimes[metal] = {
                'current_regime': regime,
                'current_volatility': current_vol,
                'volatility_percentiles': {'25th': vol_25, '75th': vol_75}
            }
    
    def _update_seasonal_patterns(self):
        """Update seasonal patterns analysis"""
        for metal in self.price_data.columns:
            prices = self.price_data[metal].dropna()
            
            if len(prices) < 365:  # Need at least one year of data
                continue
            
            # Calculate monthly returns
            monthly_data = prices.resample('M').last()
            monthly_returns = monthly_data.pct_change().dropna()
            
            # Seasonal strength by month
            seasonal_returns = {}
            for month in range(1, 13):
                month_returns = []
                for year in monthly_returns.index.year:
                    try:
                        month_return = monthly_returns[
                            (monthly_returns.index.year == year) & 
                            (monthly_returns.index.month == month)
                        ]
                        if not month_return.empty:
                            month_returns.append(month_return.iloc[0])
                    except:
                        continue
                
                if month_returns:
                    seasonal_returns[month] = {
                        'mean_return': np.mean(month_returns),
                        'volatility': np.std(month_returns),
                        'frequency': len(month_returns)
                    }
            
            self.seasonal_patterns[metal] = seasonal_returns
    
    def quantum_metals_correlation(self) -> np.ndarray:
        """
        Quantum correlation matrix for metals
        """
        if not hasattr(self, 'returns_data'):
            raise ValueError("Returns ma'lumotlari yuklanmagan")
        
        # Classical correlation
        classical_corr = self.returns_data.corr().values
        
        # Quantum corrections
        n_metals = len(self.returns_data.columns)
        quantum_corr = classical_corr.copy()
        
        for i in range(n_metals):
            for j in range(i + 1, n_metals):
                metal_i = self.returns_data.columns[i]
                metal_j = self.returns_data.columns[j]
                
                # Safe haven correlation enhancement
                safe_haven_i = self.metal_characteristics[metal_i]['safe_haven']
                safe_haven_j = self.metal_characteristics[metal_j]['safe_haven']
                
                if safe_haven_i > 0.7 and safe_haven_j > 0.7:
                    # Both are strong safe havens - quantum correlation
                    quantum_state_i = self.metal_quantum_states[metal_i]
                    quantum_state_j = self.metal_quantum_states[metal_j]
                    
                    quantum_correlation = np.real(np.vdot(quantum_state_i, quantum_state_j))
                    quantum_corr[i, j] = classical_corr[i, j] * (1 + abs(quantum_correlation) * 0.15)
                    quantum_corr[j, i] = classical_corr[i, j] * (1 + abs(quantum_correlation) * 0.15)
                
                # Industrial correlation (negative correlation with safe havens)
                industrial_i = self.metal_characteristics[metal_i]['industrial_demand']
                industrial_j = self.metal_characteristics[metal_j]['industrial_demand']
                
                if industrial_i > 0.7 and industrial_j > 0.7:
                    # Both are industrial metals - quantum decoherence
                    quantum_corr[i, j] *= 0.95
                    quantum_corr[j, i] *= 0.95
        
        return quantum_corr
    
    def quantum_safe_haven_analysis(self, 
                                   market_stress_indicator: float = 0.5,
                                   time_horizon: int = 30) -> Dict:
        """
        Quantum safe haven analysis
        
        Args:
            market_stress_indicator: Market stress level (0-1)
            time_horizon: Analysis horizon in days
            
        Returns:
            Safe haven analysis results
        """
        safe_haven_results = {}
        
        for metal in self.metals:
            if metal not in self.metal_characteristics:
                continue
            
            chars = self.metal_characteristics[metal]
            quantum_state = self.metal_quantum_states[metal]
            
            # Safe haven strength
            safe_haven_strength = chars['safe_haven']
            
            # Quantum safe haven enhancement
            quantum_enhancement = np.abs(quantum_state[0]) ** 2  # |0⟩ state strength
            
            # Stress response calculation
            stress_response = safe_haven_strength * (1 + quantum_enhancement * 0.2)
            
            # Safe haven correlation with other assets
            if hasattr(self, 'returns_data') and metal in self.returns_data.columns:
                metal_returns = self.returns_data[metal]
                
                # Simplified market correlation
                market_proxy = metal_returns.rolling(window=10).mean()
                correlation = metal_returns.corr(market_proxy)
                
                # In stress, correlation with market should decrease (flight to quality)
                stress_correlation = correlation * (1 - market_stress_indicator * 0.5)
            else:
                stress_correlation = -0.1  # Default assumption
            
            safe_haven_results[metal] = {
                'safe_haven_strength': safe_haven_strength,
                'quantum_enhancement': quantum_enhancement,
                'stress_response': stress_response,
                'market_correlation': stress_correlation,
                'safe_haven_score': (stress_response + (1 - abs(stress_correlation))) / 2
            }
        
        # Rank metals by safe haven quality
        ranked_metals = sorted(safe_haven_results.items(), 
                             key=lambda x: x[1]['safe_haven_score'], 
                             reverse=True)
        
        return {
            'safe_haven_analysis': safe_haven_results,
            'ranked_metals': ranked_metals,
            'market_stress_level': market_stress_indicator,
            'analysis_horizon': time_horizon
        }
    
    def quantum_portfolio_construction(self, 
                                      objective: str = 'safe_haven',
                                      target_volatility: float = 0.15,
                                      max_allocation: float = 0.4) -> Dict:
        """
        Quantum metals portfolio construction
        
        Args:
            objective: Portfolio objective ('safe_haven', 'momentum', 'diversification')
            target_volatility: Target portfolio volatility
            max_allocation: Maximum allocation per metal
            
        Returns:
            Portfolio allocation
        """
        if not hasattr(self, 'returns_data'):
            raise ValueError("Returns ma'lumotlari yuklanmagan")
        
        # Calculate metal characteristics
        metal_scores = {}
        
        for metal in self.returns_data.columns:
            if metal not in self.metal_characteristics:
                continue
            
            chars = self.metal_characteristics[metal]
            quantum_state = self.metal_quantum_states[metal]
            returns = self.returns_data[metal]
            
            # Base scores
            vol_score = 1 / (1 + returns.std())  # Lower volatility = higher score
            liquidity_score = chars['liquidity']
            quantum_score = np.abs(quantum_state[0] * np.conj(quantum_state[1]))
            
            # Objective-specific scoring
            if objective == 'safe_haven':
                score = (chars['safe_haven'] * 0.4 + 
                        vol_score * 0.3 + 
                        liquidity_score * 0.2 + 
                        quantum_score * 0.1)
            elif objective == 'momentum':
                momentum = (returns.iloc[-5:].mean() - returns.iloc[-20:-5].mean()) if len(returns) >= 20 else 0
                score = momentum + vol_score * 0.5 + quantum_score * 0.1
            else:  # diversification
                score = (liquidity_score * 0.4 + 
                        vol_score * 0.3 + 
                        (1 - chars['safe_haven']) * 0.2 + 
                        quantum_score * 0.1)
            
            metal_scores[metal] = score
        
        # Normalize scores
        total_score = sum(metal_scores.values())
        if total_score > 0:
            weights = {metal: score/total_score for metal, score in metal_scores.items()}
        else:
            weights = {metal: 1/len(metal_scores) for metal in metal_scores.keys()}
        
        # Apply volatility scaling
        portfolio_vol = np.sqrt(sum(weights[metal]**2 * returns.var() 
                                  for metal, returns in self.returns_data.items() 
                                  if metal in weights))
        
        if portfolio_vol > 0 and target_volatility > 0:
            vol_adjustment = target_volatility / portfolio_vol
            weights = {metal: weight * vol_adjustation for metal, weight in weights.items()}
        
        # Apply maximum allocation constraint
        for metal in weights:
            weights[metal] = min(weights[metal], max_allocation)
        
        # Renormalize
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {metal: weight/total_weight for metal, weight in weights.items()}
        
        # Calculate portfolio metrics
        portfolio_return = sum(weights[metal] * self.returns_data[metal].mean() 
                             for metal in weights if metal in self.returns_data.columns)
        
        portfolio_volatility = np.sqrt(sum(weights[metal]**2 * self.returns_data[metal].var() 
                                         for metal in weights if metal in self.returns_data.columns))
        
        # Quantum portfolio characteristics
        quantum_coherence = sum(weights[metal] * np.abs(self.metal_quantum_states[metal][0] * np.conj(self.metal_quantum_states[metal][1])) 
                              for metal in weights if metal in self.metal_quantum_states)
        
        # Safe haven score
        safe_haven_score = sum(weights[metal] * self.metal_characteristics[metal]['safe_haven'] 
                             for metal in weights if metal in self.metal_characteristics)
        
        return {
            'weights': weights,
            'portfolio_return': portfolio_return,
            'portfolio_volatility': portfolio_volatility,
            'sharpe_ratio': portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0,
            'quantum_coherence': quantum_coherence,
            'safe_haven_score': safe_haven_score,
            'objective': objective,
            'target_volatility': target_volatility,
            'metal_characteristics': {
                metal: self.metal_characteristics[metal] for metal in weights.keys() 
                if metal in self.metal_characteristics
            }
        }
    
    def quantum_backwardation_contango_analysis(self, 
                                              futures_data: Optional[pd.DataFrame] = None) -> Dict:
        """
        Quantum backwardation/contango analysis
        
        Args:
            futures_data: Futures prices data (optional)
            
        Returns:
            Backwardation/contango analysis
        """
        if futures_data is None:
            # Create synthetic futures data based on spot prices
            if not hasattr(self, 'price_data'):
                raise ValueError("Spot price ma'lumotlari yuklanmagan")
            
            futures_data = self.price_data.copy()
            for metal in futures_data.columns:
                # Add cost of carry
                chars = self.metal_characteristics.get(metal, {})
                storage_cost = self.storage_costs.get(metal, 0.02)  # 2% default
                financing_cost = 0.02  # 2% default financing
                total_cost = storage_cost + financing_cost
                
                # Synthetic futures prices (1 month forward)
                futures_data[metal] = self.price_data[metal] * (1 + total_cost/12)
        
        analysis_results = {}
        
        for metal in futures_data.columns:
            if metal in self.price_data.columns:
                # Calculate basis
                spot_price = self.price_data[metal].iloc[-1]
                futures_price = futures_data[metal].iloc[-1]
                
                basis = futures_price - spot_price
                basis_percentage = basis / spot_price
                
                # Determine market structure
                if basis_percentage > 0.01:  # > 1% premium
                    market_structure = 'contango'
                elif basis_percentage < -0.01:  # < -1% discount
                    market_structure = 'backwardation'
                else:
                    market_structure = 'flat'
                
                # Quantum enhancement of basis
                quantum_state = self.metal_quantum_states.get(metal, np.array([1, 0]))
                quantum_enhancement = np.real(quantum_state[0] * np.conj(quantum_state[1]))
                
                # Expected roll return
                expected_roll_return = -basis_percentage  # Negative basis gives positive roll return
                enhanced_roll_return = expected_roll_return * (1 + quantum_enhancement * 0.1)
                
                analysis_results[metal] = {
                    'spot_price': spot_price,
                    'futures_price': futures_price,
                    'basis': basis,
                    'basis_percentage': basis_percentage,
                    'market_structure': market_structure,
                    'quantum_enhancement': quantum_enhancement,
                    'expected_roll_return': expected_roll_return,
                    'enhanced_roll_return': enhanced_roll_return
                }
        
        return {
            'basis_analysis': analysis_results,
            'market_structure_summary': {
                'contango_metals': [metal for metal, data in analysis_results.items() 
                                  if data['market_structure'] == 'contango'],
                'backwardation_metals': [metal for metal, data in analysis_results.items() 
                                       if data['market_structure'] == 'backwardation'],
                'flat_metals': [metal for metal, data in analysis_results.items() 
                              if data['market_structure'] == 'flat']
            }
        }
    
    def quantum_metals_rotation_strategy(self, 
                                       rotation_frequency: str = 'monthly',
                                       momentum_lookback: int = 60) -> Dict:
        """
        Quantum metals rotation strategy
        
        Args:
            rotation_frequency: 'weekly', 'monthly', 'quarterly'
            momentum_lookback: Days for momentum calculation
            
        Returns:
            Rotation strategy results
        """
        if not hasattr(self, 'returns_data'):
            raise ValueError("Returns ma'lumotlari yuklanmagan")
        
        # Calculate momentum scores
        momentum_scores = {}
        
        for metal in self.returns_data.columns:
            returns = self.returns_data[metal]
            
            if len(returns) < momentum_lookback:
                momentum_scores[metal] = 0
                continue
            
            # Price momentum
            current_price = returns.iloc[-1]
            past_price = returns.iloc[-momentum_lookback]
            momentum = (current_price - past_price) / abs(past_price)
            
            # Volatility-adjusted momentum
            volatility = returns.rolling(window=momentum_lookback).std().iloc[-1]
            adj_momentum = momentum / volatility if volatility > 0 else momentum
            
            # Quantum momentum enhancement
            quantum_state = self.metal_quantum_states.get(metal, np.array([1, 0]))
            quantum_enhancement = np.abs(quantum_state[0] * np.conj(quantum_state[1]))
            
            # Seasonal adjustment
            seasonal_factor = 1.0
            if metal in self.seasonal_patterns:
                current_month = pd.Timestamp.now().month
                if current_month in self.seasonal_patterns[metal]:
                    seasonal_factor = 1 + self.seasonal_patterns[metal][current_month]['mean_return']
            
            final_momentum = adj_momentum * (1 + quantum_enhancement * 0.15) * seasonal_factor
            momentum_scores[metal] = final_momentum
        
        # Select top metals
        sorted_metals = sorted(momentum_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Equal weight allocation to top performers
        n_top = min(2, len(sorted_metals))  # Top 2 metals
        top_metals = [metal for metal, score in sorted_metals[:n_top]]
        
        if n_top > 0:
            allocation = {metal: 1.0/n_top for metal in top_metals}
        else:
            allocation = {}
        
        # Calculate strategy metrics
        if allocation:
            strategy_return = sum(allocation[metal] * self.returns_data[metal].iloc[-1] 
                                for metal in allocation if metal in self.returns_data.columns)
            
            strategy_volatility = np.sqrt(sum(allocation[metal]**2 * self.returns_data[metal].var() 
                                            for metal in allocation if metal in self.returns_data.columns))
        else:
            strategy_return = 0
            strategy_volatility = 0
        
        return {
            'allocation': allocation,
            'momentum_scores': momentum_scores,
            'strategy_return': strategy_return,
            'strategy_volatility': strategy_volatility,
            'strategy_sharpe': strategy_return / strategy_volatility if strategy_volatility > 0 else 0,
            'top_metals': top_metals,
            'rotation_frequency': rotation_frequency,
            'momentum_lookback': momentum_lookback
        }
    
    def visualize_quantum_metals_analysis(self, save_path: Optional[str] = None) -> None:
        """Quantum metals analysis visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Quantum Metals Analysis Dashboard', fontsize=16)
        
        # 1. Safe haven strength radar chart
        if self.metal_characteristics:
            metals = list(self.metal_characteristics.keys())
            safe_haven_scores = [self.metal_characteristics[metal]['safe_haven'] for metal in metals]
            liquidity_scores = [self.metal_characteristics[metal]['liquidity'] for metal in metals]
            
            axes[0, 0].scatter(safe_haven_scores, liquidity_scores, s=100, alpha=0.7)
            
            for i, metal in enumerate(metals):
                axes[0, 0].annotate(metal, (safe_haven_scores[i], liquidity_scores[i]), 
                                  xytext=(5, 5), textcoords='offset points')
            
            axes[0, 0].set_xlabel('Safe Haven Strength')
            axes[0, 0].set_ylabel('Liquidity Score')
            axes[0, 0].set_title('Safe Haven vs Liquidity')
            axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Quantum states visualization
        if self.metal_quantum_states:
            first_metal = list(self.metal_quantum_states.keys())[0]
            quantum_state = self.metal_quantum_states[first_metal]
            
            x = [0, 1]
            y = [np.abs(quantum_state[0])**2, np.abs(quantum_state[1])**2]
            
            axes[0, 1].bar(x, y, color=['gold', 'silver'], alpha=0.7)
            axes[0, 1].set_title(f'Quantum State - {first_metal}')
            axes[0, 1].set_xlabel('Quantum State |0⟩ (Safe Haven), |1⟩ (Industrial)')
            axes[0, 1].set_ylabel('Probability')
        
        # 3. Correlation heatmap
        if hasattr(self, 'returns_data') and not self.returns_data.empty:
            quantum_corr = self.quantum_metals_correlation()
            
            im = axes[1, 0].imshow(quantum_corr, cmap='RdYlBu_r', aspect='auto', vmin=-1, vmax=1)
            axes[1, 0].set_title('Quantum Correlation Matrix')
            axes[1, 0].set_xticks(range(len(self.returns_data.columns)))
            axes[1, 0].set_yticks(range(len(self.returns_data.columns)))
            axes[1, 0].set_xticklabels(self.returns_data.columns, rotation=45)
            axes[1, 0].set_yticklabels(self.returns_data.columns)
            plt.colorbar(im, ax=axes[1, 0])
        
        # 4. Volatility regimes
        if self.volatility_regimes:
            metals = list(self.volatility_regimes.keys())
            regimes = [self.volatility_regimes[metal]['current_regime'] for metal in metals]
            
            regime_colors = {'low_volatility': 'green', 'normal_volatility': 'blue', 'high_volatility': 'red'}
            colors = [regime_colors.get(regime, 'gray') for regime in regimes]
            
            axes[1, 1].bar(metals, range(len(metals)), color=colors, alpha=0.7)
            axes[1, 1].set_title('Current Volatility Regimes')
            axes[1, 1].set_ylabel('Regime Level')
            axes[1, 1].tick_params(axis='x', rotation=45)
            
            # Create legend
            from matplotlib.patches import Patch
            legend_elements = [Patch(facecolor=color, label=regime) 
                             for regime, color in regime_colors.items()]
            axes[1, 1].legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Quantum metals analysis visualization saqlandi: {save_path}")
        else:
            plt.show()
    
    def save_model_state(self, filepath: str):
        """Model state saqlash"""
        model_state = {
            'metals': self.metals,
            'storage_costs': self.storage_costs,
            'quantum_coherence_time': self.quantum_coherence_time,
            'metal_quantum_states': {
                metal: state.tolist() for metal, state in self.metal_quantum_states.items()
            },
            'metal_characteristics': self.metal_characteristics,
            'liquidity_profiles': self.liquidity_profiles,
            'supply_demand_factors': self.supply_demand_factors,
            'volatility_regimes': self.volatility_regimes,
            'seasonal_patterns': self.seasonal_patterns
        }
        
        import json
        with open(filepath, 'w') as f:
            json.dump(model_state, f, indent=2, default=str)
        
        self.logger.info(f"Metals model state saqlandi: {filepath}")
    
    def load_model_state(self, filepath: str):
        """Model state yuklash"""
        import json
        with open(filepath, 'r') as f:
            model_state = json.load(f)
        
        self.metals = model_state['metals']
        self.storage_costs = model_state['storage_costs']
        self.quantum_coherence_time = model_state['quantum_coherence_time']
        
        # Restore quantum states
        self.metal_quantum_states = {
            metal: np.array(state, dtype=complex) for metal, state in model_state['metal_quantum_states'].items()
        }
        
        # Restore other attributes
        self.metal_characteristics = model_state['metal_characteristics']
        self.liquidity_profiles = model_state['liquidity_profiles']
        self.supply_demand_factors = model_state['supply_demand_factors']
        self.volatility_regimes = model_state['volatility_regimes']
        self.seasonal_patterns = model_state['seasonal_patterns']
        
        self.logger.info(f"Metals model state yuklandi: {filepath}")