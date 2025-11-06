"""
Stocks Quantum Model
====================

Equities uchun quantum portfolio model implementation.
Bu modul aktsiyalar bo'yicha quantum portfolio optimizatsiyasini amalga oshiradi.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
import logging
from scipy import stats
import matplotlib.pyplot as plt

class StocksQuantumModel:
    """
    Stocks Quantum Model - Aktsiyalar uchun quantum portfolio modeli
    """
    
    def __init__(self, 
                 stocks: List[str],
                 quantum_coherence_time: float = 100.0,
                 sector_mapping: Optional[Dict[str, str]] = None):
        """
        Initialize stocks quantum model
        
        Args:
            stocks: Stock ticker'lar ro'yxati
            quantum_coherence_time: Quantum coherence time (microseconds)
            sector_mapping: Sector mapping for stocks (e.g., {'AAPL': 'Technology'})
        """
        self.stocks = stocks
        self.n_stocks = len(stocks)
        self.quantum_coherence_time = quantum_coherence_time
        
        # Sector information
        self.sector_mapping = sector_mapping or {}
        self.sectors = list(set(self.sector_mapping.values())) if self.sector_mapping else ['General']
        
        # Quantum states for stocks
        self.quantum_states = {}
        self.stock_volatility = {}
        self.stock_returns = {}
        
        # Sector quantum entanglement
        self.sector_entanglement = {}
        
        # Market quantum properties
        self.market_quantum_state = np.array([1/np.sqrt(2), 1/np.sqrt(2)], dtype=complex)
        
        self.logger = logging.getLogger(__name__)
        self._initialize_quantum_states()
    
    def _initialize_quantum_states(self):
        """Quantum states yaratish"""
        for stock in self.stocks:
            # Stock quantum state based on market characteristics
            stock_state = self._create_stock_quantum_state(stock)
            self.quantum_states[stock] = stock_state
            
            # Sector entanglement
            sector = self.sector_mapping.get(stock, 'General')
            if sector not in self.sector_entanglement:
                self.sector_entanglement[sector] = []
            self.sector_entanglement[sector].append(stock)
    
    def _create_stock_quantum_state(self, stock: str) -> np.ndarray:
        """
        Stock uchun quantum state yaratish
        """
        # Random seed based on stock name for consistency
        np.random.seed(hash(stock) % 2**32)
        
        # State parameters based on stock characteristics
        sector = self.sector_mapping.get(stock, 'General')
        
        # Sector-based quantum state parameters
        sector_params = {
            'Technology': {'alpha': 0.9, 'beta': 0.1, 'phase': np.pi/6},
            'Financial': {'alpha': 0.7, 'beta': 0.3, 'phase': np.pi/4},
            'Healthcare': {'alpha': 0.8, 'beta': 0.2, 'phase': np.pi/8},
            'Energy': {'alpha': 0.6, 'beta': 0.4, 'phase': np.pi/3},
            'Consumer': {'alpha': 0.75, 'beta': 0.25, 'phase': np.pi/12},
            'General': {'alpha': 0.8, 'beta': 0.2, 'phase': np.pi/6}
        }
        
        params = sector_params.get(sector, sector_params['General'])
        
        # Create quantum state
        alpha = params['alpha'] + 0.1 * np.random.random()
        beta = np.sqrt(1 - alpha**2)
        
        quantum_state = np.array([alpha, beta], dtype=complex)
        
        # Apply phase
        phase = params['phase']
        quantum_state *= np.exp(1j * phase)
        
        return quantum_state
    
    def load_data(self, 
                  price_data: pd.DataFrame,
                  fundamental_data: Optional[Dict] = None):
        """
        Stock data yuklash
        
        Args:
            price_data: Stock narxlari DataFrame
            fundamental_data: Fundamental ma'lumotlar (optional)
        """
        # Price data validation
        available_stocks = [stock for stock in self.stocks if stock in price_data.columns]
        
        if not available_stocks:
            raise ValueError("Hech qanday stock ma'lumoti topilmadi")
        
        self.stock_returns = price_data[available_stocks].pct_change().dropna()
        
        # Calculate quantum-enhanced volatility
        self.stock_volatility = {}
        for stock in available_stocks:
            classical_vol = self.stock_returns[stock].std()
            
            # Quantum enhancement
            quantum_state = self.quantum_states[stock]
            quantum_enhancement = np.abs(quantum_state[0] * np.conj(quantum_state[1]))
            enhanced_vol = classical_vol * (1 + quantum_enhancement * 0.1)
            
            self.stock_volatility[stock] = enhanced_vol
        
        self.logger.info(f"Stock data yuklandi: {len(available_stocks)} stock")
    
    def calculate_quantum_correlation(self, 
                                    returns_data: Optional[pd.DataFrame] = None) -> np.ndarray:
        """
        Quantum correlation matrix hisoblash
        """
        if returns_data is None:
            returns_data = self.stock_returns
        
        if returns_data.empty:
            raise ValueError("Returns ma'lumotlari mavjud emas")
        
        # Classical correlation matrix
        classical_corr = returns_data.corr().values
        
        # Quantum corrections
        n_stocks = len(returns_data.columns)
        quantum_corr = classical_corr.copy()
        
        for i in range(n_stocks):
            for j in range(i + 1, n_stocks):
                stock_i = returns_data.columns[i]
                stock_j = returns_data.columns[j]
                
                # Sector entanglement factor
                sector_i = self.sector_mapping.get(stock_i, 'General')
                sector_j = self.sector_mapping.get(stock_j, 'General')
                
                # Same sector gets quantum entanglement
                if sector_i == sector_j:
                    entanglement_factor = 0.1
                    quantum_corr[i, j] = classical_corr[i, j] * (1 + entanglement_factor)
                    quantum_corr[j, i] = classical_corr[i, j] * (1 + entanglement_factor)
                else:
                    # Different sectors - quantum decoherence
                    decoherence_factor = -0.05
                    quantum_corr[i, j] = classical_corr[i, j] * (1 + decoherence_factor)
                    quantum_corr[j, i] = classical_corr[i, j] * (1 + decoherence_factor)
        
        return quantum_corr
    
    def quantum_factor_model(self, 
                           returns_data: Optional[pd.DataFrame] = None,
                           n_factors: int = 3) -> Dict:
        """
        Quantum factor model estimation
        
        Args:
            returns_data: Returns ma'lumotlari
            n_factors: Factor soni
            
        Returns:
            Factor model results
        """
        if returns_data is None:
            returns_data = self.stock_returns
        
        # Classical factor analysis
        from sklearn.decomposition import PCA
        
        pca = PCA(n_components=n_factors)
        factors = pca.fit_transform(returns_data.fillna(0))
        
        # Factor loadings
        loadings = pca.components_.T
        
        # Quantum factor enhancement
        quantum_factors = []
        quantum_loadings = np.zeros_like(loadings)
        
        for i, stock in enumerate(returns_data.columns):
            quantum_state = self.quantum_states[stock]
            
            for j in range(n_factors):
                # Quantum enhancement of factor loading
                enhancement_factor = np.real(quantum_state[0] * np.conj(quantum_state[1]))
                quantum_loadings[i, j] = loadings[i, j] * (1 + enhancement_factor * 0.1)
        
        # Factor returns
        factor_returns = pd.DataFrame(factors, 
                                    columns=[f'Factor_{i+1}' for i in range(n_factors)],
                                    index=returns_data.index)
        
        # Specific returns (quantum enhanced)
        specific_returns = returns_data - np.dot(factors, loadings.T)
        
        # Quantum specific volatility
        quantum_specific_vol = {}
        for stock in returns_data.columns:
            stock_idx = list(returns_data.columns).index(stock)
            classical_vol = specific_returns[stock].std()
            quantum_state = self.quantum_states[stock]
            quantum_enhancement = np.abs(quantum_state[0]) ** 2
            quantum_specific_vol[stock] = classical_vol * (1 + quantum_enhancement * 0.05)
        
        return {
            'factors': factor_returns,
            'loadings': loadings,
            'quantum_loadings': quantum_loadings,
            'specific_returns': specific_returns,
            'quantum_specific_volatility': quantum_specific_vol,
            'explained_variance_ratio': pca.explained_variance_ratio_,
            'total_variance_explained': np.sum(pca.explained_variance_ratio_)
        }
    
    def quantum_beta_calculation(self, 
                               stock: str,
                               market_returns: Optional[pd.Series] = None,
                               returns_data: Optional[pd.DataFrame] = None) -> Dict:
        """
        Quantum beta hisoblash
        """
        if returns_data is None:
            returns_data = self.stock_returns
        
        if stock not in returns_data.columns:
            raise ValueError(f"Stock {stock} topilmadi")
        
        # Market returns
        if market_returns is None:
            market_returns = returns_data.mean(axis=1)
        
        # Align data
        aligned_data = pd.concat([returns_data[stock], market_returns], axis=1).dropna()
        stock_returns = aligned_data.iloc[:, 0]
        market_returns_aligned = aligned_data.iloc[:, 1]
        
        # Classical beta
        covariance = np.cov(stock_returns, market_returns_aligned)[0, 1]
        market_variance = np.var(market_returns_aligned)
        classical_beta = covariance / market_variance
        
        # Quantum beta enhancement
        quantum_state = self.quantum_states[stock]
        quantum_enhancement = np.real(quantum_state[0] * np.conj(quantum_state[1]))
        
        # Sector adjustment
        sector = self.sector_mapping.get(stock, 'General')
        sector_beta_adjustments = {
            'Technology': 1.2,
            'Financial': 0.8,
            'Healthcare': 0.9,
            'Energy': 1.1,
            'Consumer': 1.0,
            'General': 1.0
        }
        sector_adjustment = sector_beta_adjustments.get(sector, 1.0)
        
        quantum_beta = classical_beta * (1 + quantum_enhancement * 0.15) * sector_adjustment
        
        # Alpha calculation
        stock_mean = stock_returns.mean()
        market_mean = market_returns_aligned.mean()
        risk_free_rate = 0.02 / 252  # Daily risk-free rate
        
        quantum_alpha = stock_mean - risk_free_rate - quantum_beta * (market_mean - risk_free_rate)
        
        # R-squared
        correlation = np.corrcoef(stock_returns, market_returns_aligned)[0, 1]
        r_squared = correlation ** 2
        
        return {
            'stock': stock,
            'sector': sector,
            'classical_beta': classical_beta,
            'quantum_beta': quantum_beta,
            'quantum_alpha': quantum_alpha,
            'quantum_enhancement_factor': quantum_enhancement,
            'sector_adjustment': sector_adjustment,
            'correlation': correlation,
            'r_squared': r_squared
        }
    
    def sector_quantum_analysis(self) -> Dict:
        """
        Sectors o'rtasidagi quantum analysis
        """
        sector_analysis = {}
        
        for sector in self.sectors:
            sector_stocks = [stock for stock in self.stocks 
                           if self.sector_mapping.get(stock, 'General') == sector]
            
            if len(sector_stocks) < 2:
                continue
            
            # Sector quantum state
            sector_state = self._calculate_sector_quantum_state(sector_stocks)
            
            # Sector correlations
            sector_returns = self.stock_returns[sector_stocks]
            sector_corr = sector_returns.corr()
            
            # Sector entanglement matrix
            entanglement_matrix = self._calculate_sector_entanglement(sector_stocks)
            
            # Sector risk metrics
            sector_volatility = np.sqrt(np.diag(sector_returns.cov()))
            sector_diversification = 1 / np.sum(sector_volatility ** 2) if len(sector_volatility) > 0 else 0
            
            sector_analysis[sector] = {
                'stocks': sector_stocks,
                'quantum_state': sector_state,
                'correlation_matrix': sector_corr,
                'entanglement_matrix': entanglement_matrix,
                'volatilities': sector_volatility.tolist(),
                'diversification_ratio': sector_diversification,
                'sector_size': len(sector_stocks)
            }
        
        return sector_analysis
    
    def _calculate_sector_quantum_state(self, sector_stocks: List[str]) -> np.ndarray:
        """Sector quantum state hisoblash"""
        if not sector_stocks:
            return np.array([1, 0], dtype=complex)
        
        # Combine quantum states of all stocks in sector
        combined_state = np.zeros(2, dtype=complex)
        
        for stock in sector_stocks:
            if stock in self.quantum_states:
                quantum_state = self.quantum_states[stock]
                # Weighted combination
                stock_weight = 1.0 / len(sector_stocks)
                combined_state += stock_weight * quantum_state
        
        # Normalize
        norm = np.linalg.norm(combined_state)
        if norm > 0:
            combined_state /= norm
        
        return combined_state
    
    def _calculate_sector_entanglement(self, sector_stocks: List[str]) -> np.ndarray:
        """Sector entanglement matrix hisoblash"""
        n_stocks = len(sector_stocks)
        entanglement = np.zeros((n_stocks, n_stocks))
        
        for i in range(n_stocks):
            for j in range(n_stocks):
                if i != j:
                    stock_i, stock_j = sector_stocks[i], sector_stocks[j]
                    
                    if stock_i in self.quantum_states and stock_j in self.quantum_states:
                        state_i = self.quantum_states[stock_i]
                        state_j = self.quantum_states[stock_j]
                        
                        # Quantum entanglement measure
                        entanglement[i, j] = np.abs(np.vdot(state_i, state_j)) ** 2
        
        return entanglement
    
    def quantum_portfolio_optimization(self, 
                                     target_return: Optional[float] = None,
                                     risk_aversion: float = 1.0,
                                     sector_constraints: Optional[Dict] = None) -> Dict:
        """
        Quantum portfolio optimization for stocks
        """
        from scipy.optimize import minimize
        
        # Data preparation
        available_stocks = list(self.stock_returns.columns)
        n_stocks = len(available_stocks)
        
        # Expected returns (quantum enhanced)
        expected_returns = self.stock_returns.mean().values
        quantum_returns = np.zeros_like(expected_returns)
        
        for i, stock in enumerate(available_stocks):
            quantum_state = self.quantum_states[stock]
            enhancement = np.real(quantum_state[0] * np.conj(quantum_state[1]))
            quantum_returns[i] = expected_returns[i] * (1 + enhancement * 0.1)
        
        # Quantum covariance matrix
        quantum_corr = self.calculate_quantum_correlation()
        
        # Volatilities
        volatilities = np.array([self.stock_volatility[stock] for stock in available_stocks])
        quantum_cov = np.outer(volatilities, volatilities) * quantum_corr
        
        # Objective function
        def objective(weights):
            portfolio_return = np.sum(weights * quantum_returns)
            portfolio_variance = np.dot(weights, np.dot(quantum_cov, weights))
            utility = portfolio_return - 0.5 * risk_aversion * portfolio_variance
            
            # Quantum enhancements
            quantum_coherence = self._portfolio_quantum_coherence(weights, available_stocks)
            quantum_entropy = self._portfolio_quantum_entropy(weights)
            
            return -(utility + quantum_coherence * 0.1 + quantum_entropy * 0.05)
        
        # Constraints
        constraints = []
        
        # Budget constraint
        constraints.append({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0})
        
        # Return constraint
        if target_return is not None:
            constraints.append({
                'type': 'eq',
                'fun': lambda w: np.sum(w * quantum_returns) - target_return
            })
        
        # Sector constraints
        if sector_constraints:
            for sector, max_weight in sector_constraints.items():
                sector_stocks = [i for i, stock in enumerate(available_stocks)
                               if self.sector_mapping.get(stock, 'General') == sector]
                if sector_stocks:
                    constraints.append({
                        'type': 'ineq',
                        'fun': lambda w, stocks=sector_stocks, max_w=max_weight: max_w - np.sum(w[stocks])
                    })
        
        # Bounds
        bounds = [(0, 0.4) for _ in range(n_stocks)]  # Max 40% per stock
        
        # Initial guess
        x0 = np.ones(n_stocks) / n_stocks
        
        # Optimization
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if result.success:
            weights = result.x
            allocation = {stock: weight for stock, weight in zip(available_stocks, weights) 
                         if weight > 0.001}
            
            portfolio_return = np.sum(weights * quantum_returns)
            portfolio_volatility = np.sqrt(np.dot(weights, np.dot(quantum_cov, weights)))
            
            return {
                'allocation': allocation,
                'weights': weights,
                'expected_return': portfolio_return,
                'volatility': portfolio_volatility,
                'sharpe_ratio': portfolio_return / portfolio_volatility,
                'quantum_coherence': self._portfolio_quantum_coherence(weights, available_stocks),
                'quantum_entropy': self._portfolio_quantum_entropy(weights),
                'optimization_status': 'success'
            }
        else:
            return {'optimization_status': 'failed', 'message': result.message}
    
    def _portfolio_quantum_coherence(self, weights: np.ndarray, stocks: List[str]) -> float:
        """Portfolio quantum coherence hisoblash"""
        coherence = 0.0
        
        for i, weight in enumerate(weights):
            if weight > 0 and i < len(stocks):
                stock = stocks[i]
                quantum_state = self.quantum_states[stock]
                off_diagonal = np.abs(quantum_state[0] * np.conj(quantum_state[1]))
                coherence += weight * off_diagonal
        
        return coherence
    
    def _portfolio_quantum_entropy(self, weights: np.ndarray) -> float:
        """Portfolio quantum entropy hisoblash"""
        positive_weights = weights[weights > 0]
        if len(positive_weights) == 0:
            return 0
        
        normalized_weights = positive_weights / np.sum(positive_weights)
        entropy = -np.sum(normalized_weights * np.log2(normalized_weights + 1e-8))
        
        return entropy
    
    def visualize_sector_analysis(self, save_path: Optional[str] = None) -> None:
        """Sector analysis visualization"""
        sector_analysis = self.sector_quantum_analysis()
        
        if not sector_analysis:
            self.logger.warning("Sector analysis ma'lumotlari mavjud emas")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Stocks Quantum Sector Analysis', fontsize=16)
        
        # Sector sizes
        sector_sizes = [analysis['sector_size'] for analysis in sector_analysis.values()]
        sector_names = list(sector_analysis.keys())
        
        axes[0, 0].pie(sector_sizes, labels=sector_names, autopct='%1.1f%%')
        axes[0, 0].set_title('Sector Distribution')
        
        # Sector diversification
        diversifications = [analysis['diversification_ratio'] for analysis in sector_analysis.values()]
        
        axes[0, 1].bar(sector_names, diversifications)
        axes[0, 1].set_title('Sector Diversification Ratios')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Quantum states visualization (first sector)
        if sector_analysis:
            first_sector = list(sector_analysis.keys())[0]
            quantum_state = sector_analysis[first_sector]['quantum_state']
            
            x = [0, 1]
            y = [np.abs(quantum_state[0])**2, np.abs(quantum_state[1])**2]
            
            axes[1, 0].bar(x, y, color=['blue', 'red'], alpha=0.7)
            axes[1, 0].set_title(f'Quantum State Probabilities - {first_sector}')
            axes[1, 0].set_xlabel('Quantum State |0⟩, |1⟩')
            axes[1, 0].set_ylabel('Probability')
            
            # Entanglement heatmap (if available)
            entanglement_matrix = list(sector_analysis.values())[0]['entanglement_matrix']
            if entanglement_matrix.size > 0:
                im = axes[1, 1].imshow(entanglement_matrix, cmap='coolwarm', aspect='auto')
                axes[1, 1].set_title('Sector Entanglement Matrix')
                plt.colorbar(im, ax=axes[1, 1])
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Sector analysis visualization saqlandi: {save_path}")
        else:
            plt.show()
    
    def save_model_state(self, filepath: str):
        """Model state saqlash"""
        model_state = {
            'stocks': self.stocks,
            'sector_mapping': self.sector_mapping,
            'sectors': self.sectors,
            'quantum_coherence_time': self.quantum_coherence_time,
            'quantum_states': {
                stock: state.tolist() for stock, state in self.quantum_states.items()
            },
            'stock_volatility': self.stock_volatility
        }
        
        import json
        with open(filepath, 'w') as f:
            json.dump(model_state, f, indent=2)
        
        self.logger.info(f"Model state saqlandi: {filepath}")
    
    def load_model_state(self, filepath: str):
        """Model state yuklash"""
        import json
        with open(filepath, 'r') as f:
            model_state = json.load(f)
        
        self.stocks = model_state['stocks']
        self.sector_mapping = model_state['sector_mapping']
        self.sectors = model_state['sectors']
        self.quantum_coherence_time = model_state['quantum_coherence_time']
        
        # Restore quantum states
        self.quantum_states = {
            stock: np.array(state) for stock, state in model_state['quantum_states'].items()
        }
        
        # Restore volatilities
        self.stock_volatility = model_state['stock_volatility']
        
        self.logger.info(f"Model state yuklandi: {filepath}")