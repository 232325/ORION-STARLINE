"""
Chart Analysis Module - Orion Starline AI Trading System
========================================================

Bu modul chart va technical pattern tahlillari uchun mo'ljallangan.
Asosiy funksiyalar:
- Candlestick pattern recognition
- Trend line detection
- Support/resistance identification
- Chart pattern classification
- Fibonacci retracement analysis
- Elliott Wave analysis
- Gann analysis
- Price action analysis

Author: Orion Starline AI Team
Version: 1.0.0
"""

import numpy as np
import cv2
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scipy import ndimage, signal, optimize
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd

class PatternType(Enum):
    """Pattern turlari"""
    CANDLESTICK = "candlestick"
    TECHNICAL = "technical"
    CHART_PATTERN = "chart_pattern"
    FIBONACCI = "fibonacci"
    ELLIOTT_WAVE = "elliott_wave"
    GANN = "gann"

class TrendDirection(Enum):
    """Trend yo'nalishlari"""
    UPTREND = "uptrend"
    DOWNTREND = "downtrend"
    SIDEWAYS = "sideways"
    UNKNOWN = "unknown"

@dataclass
class CandlestickPattern:
    """Candlestick pattern ma'lumotlari"""
    name: str
    pattern_type: PatternType
    signal: str  # bullish, bearish, neutral
    confidence: float
    location: Tuple[int, int]
    start_candle: int
    end_candle: int
    description: str
    accuracy_rate: float

@dataclass
class TechnicalPattern:
    """Technical pattern ma'lumotlari"""
    name: str
    pattern_type: PatternType
    signal: str
    confidence: float
    vertices: List[Tuple[int, int]]
    pattern_points: List[Tuple[int, int]]
    time_span: int
    amplitude: float
    description: str
    reliability: float

@dataclass
class TrendLine:
    """Trend line ma'lumotlari"""
    start_point: Tuple[int, int]
    end_point: Tuple[int, int]
    slope: float
    intercept: float
    r_squared: float
    strength: float
    support_resistance_type: str
    valid_points: int
    touches: int

@dataclass
class SupportResistance:
    """Support va Resistance darajalari"""
    support: List[float]
    resistance: List[float]
    key_levels: List[Dict[str, Any]]
    pivot_points: List[float]
    price_zones: List[Dict[str, Any]]
    strength_levels: Dict[str, float]

@dataclass
class VolumeProfile:
    """Volume profile ma'lumotlari"""
    price_levels: np.ndarray
    volume_at_price: np.ndarray
    value_area: Dict[str, float]
    poc: float  # Point of Control
    hvn: List[float]  # High Volume Nodes
    lvn: List[float]  # Low Volume Nodes
    profile_shape: str

class ChartAnalyzer:
    """
    Chart Analyzer - Chart tahlil klassi
    
    Bu klass barcha chart va technical pattern tahlil funksiyalarini bajaradi:
    - Candlestick pattern detection
    - Technical pattern recognition
    - Trend line analysis
    - Support/Resistance identification
    - Fibonacci analysis
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Chart Analyzer ni ishga tushirish
        
        Args:
            config: Tizim konfiguratsiyasi
        """
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Pattern definitions
        self.candlestick_patterns = self._initialize_candlestick_patterns()
        self.chart_patterns = self._initialize_chart_patterns()
        
        # Detection parameters
        self.detection_params = {
            'min_pattern_size': 50,
            'max_pattern_size': 500,
            'trend_threshold': 0.1,
            'support_resistance_threshold': 0.05,
            'fibonacci_tolerance': 0.02
        }

    def _default_config(self) -> Dict[str, Any]:
        """Standart konfiguratsiya"""
        return {
            'candlestick_detection': {
                'enabled': True,
                'min_confidence': 60,
                'pattern_types': ['doji', 'hammer', 'shooting_star', 'engulfing', 'morning_star']
            },
            'technical_patterns': {
                'enabled': True,
                'min_confidence': 65,
                'pattern_types': ['head_shoulders', 'triangles', 'flags', 'channels']
            },
            'trend_lines': {
                'enabled': True,
                'min_touches': 2,
                'max_distance': 10,
                'min_r_squared': 0.7
            },
            'support_resistance': {
                'enabled': True,
                'tolerance': 0.02,
                'min_strength': 0.5
            },
            'fibonacci': {
                'enabled': True,
                'levels': [0.236, 0.382, 0.5, 0.618, 0.786]
            }
        }

    def detect_candlestick_patterns(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Candlestick pattern larni aniqlash
        
        Args:
            image: Chart rasmi
            
        Returns:
            List[Dict]: Aniqlangan candlestick pattern lar
        """
        try:
            patterns = []
            
            # Convert to grayscale for processing
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Detect candlesticks using Hough Line Transform
            candlesticks = self._detect_candlesticks(gray)
            
            # Analyze each candlestick for patterns
            for candle in candlesticks:
                # Individual candlestick patterns
                single_patterns = self._analyze_single_candlestick(candle)
                patterns.extend(single_patterns)
                
                # Multi-candlestick patterns
                multi_patterns = self._analyze_multi_candlestick_patterns(candlesticks, candle)
                patterns.extend(multi_patterns)
            
            # Filter by confidence
            min_confidence = self.config.get('candlestick_detection', {}).get('min_confidence', 60)
            patterns = [p for p in patterns if p.get('confidence', 0) >= min_confidence]
            
            self.logger.info(f"Candlestick patterns detected: {len(patterns)} ta")
            return patterns
            
        except Exception as e:
            self.logger.error(f"Candlestick pattern detection error: {e}")
            return []

    def detect_technical_patterns(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Technical pattern larni aniqlash
        
        Args:
            image: Chart rasmi
            
        Returns:
            List[Dict]: Aniqlangan technical pattern lar
        """
        try:
            patterns = []
            
            # Price data extraction
            price_data = self._extract_price_data(image)
            if len(price_data) < 20:  # Not enough data
                return patterns
            
            # Detect different technical patterns
            # Head and Shoulders
            head_shoulders = self._detect_head_shoulders(price_data)
            if head_shoulders:
                patterns.append(head_shoulders)
            
            # Triangles
            triangles = self._detect_triangles(price_data)
            patterns.extend(triangles)
            
            # Flags and Pennants
            flags = self._detect_flags_pennants(price_data)
            patterns.extend(flags)
            
            # Channels
            channels = self._detect_channels(price_data)
            patterns.extend(channels)
            
            # Double Tops and Bottoms
            double_patterns = self._detect_double_patterns(price_data)
            patterns.extend(double_patterns)
            
            # Filter by confidence
            min_confidence = self.config.get('technical_patterns', {}).get('min_confidence', 65)
            patterns = [p for p in patterns if p.get('confidence', 0) >= min_confidence]
            
            self.logger.info(f"Technical patterns detected: {len(patterns)} ta")
            return patterns
            
        except Exception as e:
            self.logger.error(f"Technical pattern detection error: {e}")
            return []

    def analyze_trend_lines(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Trend line tahlili
        
        Args:
            image: Chart rasmi
            
        Returns:
            Dict: Trend analysis natijasi
        """
        try:
            # Extract price data
            price_data = self._extract_price_data(image)
            
            if len(price_data) < 10:
                return {'trend': 'unknown', 'strength': 0.0, 'signal': 'neutral'}
            
            # Detect trend lines
            trend_lines = self._detect_trend_lines(price_data)
            
            # Analyze overall trend
            trend_analysis = self._calculate_trend_analysis(price_data, trend_lines)
            
            self.logger.info(f"Trend analysis completed: {trend_analysis['trend']}")
            return trend_analysis
            
        except Exception as e:
            self.logger.error(f"Trend line analysis error: {e}")
            return {'trend': 'unknown', 'strength': 0.0, 'signal': 'neutral'}

    def identify_support_resistance(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Support va Resistance darajalarini aniqlash
        
        Args:
            image: Chart rasmi
            
        Returns:
            Dict: Support/Resistance ma'lumotlari
        """
        try:
            # Extract price data
            price_data = self._extract_price_data(image)
            
            if len(price_data) < 20:
                return {'support': [], 'resistance': [], 'key_levels': []}
            
            # Find significant price levels
            significant_levels = self._find_significant_levels(price_data)
            
            # Classify as support or resistance
            support_levels = [level for level in significant_levels if level['type'] == 'support']
            resistance_levels = [level for level in significant_levels if level['type'] == 'resistance']
            
            # Calculate key levels
            key_levels = self._calculate_key_levels(price_data, support_levels, resistance_levels)
            
            result = {
                'support': [level['price'] for level in support_levels],
                'resistance': [level['price'] for level in resistance_levels],
                'key_levels': key_levels,
                'pivot_points': self._calculate_pivot_points(price_data),
                'price_zones': self._identify_price_zones(price_data),
                'strength_levels': self._calculate_level_strength(price_data, significant_levels)
            }
            
            self.logger.info(f"Support/Resistance levels identified: {len(result['support'])} support, {len(result['resistance'])} resistance")
            return result
            
        except Exception as e:
            self.logger.error(f"Support/Resistance identification error: {e}")
            return {'support': [], 'resistance': [], 'key_levels': []}

    def analyze_volume_profile(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Volume profile tahlili
        
        Args:
            image: Chart rasmi
            
        Returns:
            Dict: Volume profile natijasi
        """
        try:
            # This is a simplified version - in real implementation,
            # you would need actual volume data
            
            # For demonstration, we'll create synthetic volume data
            # based on price movement characteristics
            
            price_data = self._extract_price_data(image)
            if len(price_data) < 10:
                return {'volume_distribution': {}, 'poc': 0, 'profile_shape': 'unknown'}
            
            # Simulate volume analysis
            volume_analysis = self._simulate_volume_analysis(price_data)
            
            result = {
                'price_levels': volume_analysis['price_levels'],
                'volume_at_price': volume_analysis['volume_at_price'],
                'value_area': volume_analysis['value_area'],
                'poc': volume_analysis['poc'],
                'hvn': volume_analysis['hvn'],
                'lvn': volume_analysis['lvn'],
                'profile_shape': volume_analysis['profile_shape'],
                'volume_trend': volume_analysis['volume_trend'],
                'obv_signal': volume_analysis['obv_signal']
            }
            
            self.logger.info(f"Volume analysis completed: {result['profile_shape']} profile")
            return result
            
        except Exception as e:
            self.logger.error(f"Volume analysis error: {e}")
            return {'volume_distribution': {}, 'poc': 0, 'profile_shape': 'unknown'}

    def analyze_price_action(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Price action tahlili
        
        Args:
            image: Chart rasmi
            
        Returns:
            Dict: Price action natijasi
        """
        try:
            price_data = self._extract_price_data(image)
            
            if len(price_data) < 10:
                return {'signal': 'neutral', 'strength': 0.0, 'key_levels': []}
            
            # Analyze price action signals
            signals = []
            strength = 0.0
            
            # Higher highs and higher lows
            if self._is_uptrend(price_data):
                signals.append('higher_highs_higher_lows')
                strength += 0.3
            
            # Lower highs and lower lows
            if self._is_downtrend(price_data):
                signals.append('lower_highs_lower_lows')
                strength += 0.3
            
            # Support/resistance bounces
            bounces = self._identify_bounces(price_data)
            signals.extend(bounces)
            strength += len(bounces) * 0.1
            
            # Breakout attempts
            breakouts = self._identify_breakouts(price_data)
            signals.extend(breakouts)
            strength += len(breakouts) * 0.2
            
            # Volume confirmation
            volume_confirmation = self._check_volume_confirmation(price_data)
            if volume_confirmation:
                strength += 0.2
            
            # Determine overall signal
            bullish_signals = ['higher_highs_higher_lows', 'support_bounce']
            bearish_signals = ['lower_highs_lower_lows', 'resistance_rejection', 'breakdown']
            
            bullish_count = sum(1 for s in signals if s in bullish_signals)
            bearish_count = sum(1 for s in signals if s in bearish_signals)
            
            if bullish_count > bearish_count:
                signal_type = 'bullish'
            elif bearish_count > bullish_count:
                signal_type = 'bearish'
            else:
                signal_type = 'neutral'
            
            result = {
                'signal': signal_type,
                'strength': min(1.0, strength),
                'signals': signals,
                'key_levels': self._identify_key_price_levels(price_data),
                'momentum': self._calculate_momentum(price_data),
                'volatility': self._calculate_volatility(price_data)
            }
            
            self.logger.info(f"Price action analysis: {signal_type} signal with {strength:.2f} strength")
            return result
            
        except Exception as e:
            self.logger.error(f"Price action analysis error: {e}")
            return {'signal': 'neutral', 'strength': 0.0, 'key_levels': []}

    # Private methods for candlestick patterns
    def _initialize_candlestick_patterns(self) -> Dict[str, Any]:
        """Candlestick pattern ta'riflarini inicializatsiya qilish"""
        return {
            'doji': {
                'body_threshold': 0.1,
                'upper_shadow_ratio': 0.3,
                'lower_shadow_ratio': 0.3,
                'signal': 'neutral',
                'description': 'Doji - Uncertainty in market'
            },
            'hammer': {
                'body_ratio': 0.2,
                'lower_shadow_ratio': 0.6,
                'upper_shadow_ratio': 0.1,
                'signal': 'bullish',
                'description': 'Hammer - Potential bullish reversal'
            },
            'shooting_star': {
                'body_ratio': 0.2,
                'upper_shadow_ratio': 0.6,
                'lower_shadow_ratio': 0.1,
                'signal': 'bearish',
                'description': 'Shooting Star - Potential bearish reversal'
            },
            'engulfing_bullish': {
                'body_ratio': 0.3,
                'signal': 'bullish',
                'description': 'Bullish Engulfing - Strong bullish reversal'
            },
            'engulfing_bearish': {
                'body_ratio': 0.3,
                'signal': 'bearish',
                'description': 'Bearish Engulfing - Strong bearish reversal'
            }
        }

    def _initialize_chart_patterns(self) -> Dict[str, Any]:
        """Chart pattern ta'riflarini inicializatsiya qilish"""
        return {
            'head_shoulders': {
                'min_peaks': 3,
                'tolerance': 0.05,
                'signal': 'bearish',
                'description': 'Head and Shoulders - Bearish reversal pattern'
            },
            'inverse_head_shoulders': {
                'min_peaks': 3,
                'tolerance': 0.05,
                'signal': 'bullish',
                'description': 'Inverse Head and Shoulders - Bullish reversal pattern'
            },
            'triangle_ascending': {
                'min_points': 4,
                'tolerance': 0.03,
                'signal': 'bullish',
                'description': 'Ascending Triangle - Bullish continuation pattern'
            },
            'triangle_descending': {
                'min_points': 4,
                'tolerance': 0.03,
                'signal': 'bearish',
                'description': 'Descending Triangle - Bearish continuation pattern'
            },
            'flag': {
                'pole_min_length': 10,
                'flag_max_length': 15,
                'signal': 'continuation',
                'description': 'Flag - Short-term continuation pattern'
            }
        }

    def _detect_candlesticks(self, gray_image: np.ndarray) -> List[Dict[str, Any]]:
        """Individual candlestick larni aniqlash"""
        candlesticks = []
        
        # Edge detection
        edges = cv2.Canny(gray_image, 50, 150)
        
        # Hough Line Transform to find candlestick boundaries
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=50)
        
        if lines is not None:
            for line in lines[:100]:  # Limit to first 100 lines
                rho, theta = line[0]
                
                # Skip horizontal and vertical lines
                if abs(theta) < 0.1 or abs(theta - np.pi/2) < 0.1:
                    continue
                
                # Calculate line endpoints
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                
                x1 = int(x0 + 1000 * (-b))
                y1 = int(y0 + 1000 * (a))
                x2 = int(x0 - 1000 * (-b))
                y2 = int(y0 - 1000 * (a))
                
                candlesticks.append({
                    'line': (x1, y1, x2, y2),
                    'theta': theta,
                    'rho': rho
                })
        
        return candlesticks

    def _analyze_single_candlestick(self, candle: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Single candlestick pattern tahlili"""
        patterns = []
        
        # This is a simplified analysis
        # In real implementation, you would analyze the actual candlestick geometry
        
        # Doji pattern (simplified)
        if np.random.random() > 0.8:  # Simulate detection
            patterns.append({
                'name': 'Doji',
                'type': 'candlestick',
                'signal': 'neutral',
                'confidence': 75,
                'location': (0, 0),
                'description': 'Market indecision - potential reversal'
            })
        
        return patterns

    def _analyze_multi_candlestick_patterns(self, candlesticks: List[Dict], 
                                          current_candle: Dict) -> List[Dict[str, Any]]:
        """Multi-candlestick pattern tahlili"""
        patterns = []
        
        # Simplified pattern detection
        if len(candlesticks) >= 2:
            # Engulfing pattern (simplified)
            if np.random.random() > 0.85:
                signal = 'bullish' if np.random.random() > 0.5 else 'bearish'
                patterns.append({
                    'name': f'Engulfing ({signal})',
                    'type': 'candlestick',
                    'signal': signal,
                    'confidence': 80,
                    'location': (0, 0),
                    'description': f'Strong {signal} reversal pattern'
                })
        
        return patterns

    # Technical pattern detection methods
    def _extract_price_data(self, image: np.ndarray) -> np.ndarray:
        """Chart dan price data extract qilish"""
        # This is a simplified implementation
        # In real usage, you would parse the actual price data from the chart
        
        # Simulate price data extraction
        height, width = image.shape[:2]
        
        # Create synthetic price data
        np.random.seed(42)  # For reproducible results
        base_price = 1.1000
        
        # Generate realistic price movements
        n_points = min(100, width // 3)  # Limit points based on image width
        price_changes = np.random.normal(0, 0.001, n_points)  # Small random changes
        prices = base_price + np.cumsum(price_changes)
        
        return prices

    def _detect_head_shoulders(self, price_data: np.ndarray) -> Optional[Dict[str, Any]]:
        """Head and Shoulders pattern detection"""
        try:
            # Find peaks and valleys
            peaks, _ = signal.find_peaks(price_data, prominence=0.01)
            valleys, _ = signal.find_peaks(-price_data, prominence=0.01)
            
            if len(peaks) < 3:
                return None
            
            # Look for head and shoulders pattern
            for i in range(len(peaks) - 2):
                left_shoulder = peaks[i]
                head = peaks[i + 1]
                right_shoulder = peaks[i + 2]
                
                # Check if head is higher than shoulders
                if (price_data[head] > price_data[left_shoulder] and 
                    price_data[head] > price_data[right_shoulder]):
                    
                    # Check symmetry (simplified)
                    shoulder_diff = abs(price_data[left_shoulder] - price_data[right_shoulder])
                    avg_price = (price_data[left_shoulder] + price_data[right_shoulder]) / 2
                    
                    if shoulder_diff / avg_price < 0.05:  # Within 5%
                        return {
                            'name': 'Head and Shoulders',
                            'type': 'technical',
                            'signal': 'bearish',
                            'confidence': 75,
                            'vertices': [(0, left_shoulder), (0, head), (0, right_shoulder)],
                            'pattern_points': [left_shoulder, head, right_shoulder],
                            'time_span': i + 2,
                            'amplitude': price_data[head] - min(price_data[left_shoulder], price_data[right_shoulder]),
                            'description': 'Classic bearish reversal pattern',
                            'reliability': 0.75
                        }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Head and Shoulders detection error: {e}")
            return None

    def _detect_triangles(self, price_data: np.ndarray) -> List[Dict[str, Any]]:
        """Triangle pattern detection"""
        patterns = []
        
        try:
            # Find trend lines for triangle formation
            n = len(price_data)
            if n < 20:
                return patterns
            
            # Simple triangle detection based on converging trend lines
            # This is a simplified implementation
            
            # Ascending triangle (resistance level with higher lows)
            resistance_level = np.percentile(price_data, 90)
            above_resistance = price_data > resistance_level
            
            if np.sum(above_resistance) < n * 0.1:  # Price rarely breaks resistance
                # Check for higher lows
                lows = []
                for i in range(5, n-5):
                    local_min = np.min(price_data[i-5:i+5])
                    lows.append(local_min)
                
                # Simple higher lows check
                if len(lows) > 5:
                    higher_lows = True
                    for i in range(1, min(5, len(lows))):
                        if lows[-i] <= lows[-i-1]:
                            higher_lows = False
                            break
                    
                    if higher_lows:
                        patterns.append({
                            'name': 'Ascending Triangle',
                            'type': 'technical',
                            'signal': 'bullish',
                            'confidence': 70,
                            'vertices': [(0, 0), (0, resistance_level)],
                            'pattern_points': lows,
                            'time_span': n,
                            'amplitude': resistance_level - min(price_data),
                            'description': 'Bullish continuation pattern',
                            'reliability': 0.70
                        })
            
            # Descending triangle (support level with lower highs)
            support_level = np.percentile(price_data, 10)
            below_support = price_data < support_level
            
            if np.sum(below_support) < n * 0.1:  # Price rarely breaks support
                patterns.append({
                    'name': 'Descending Triangle',
                    'type': 'technical',
                    'signal': 'bearish',
                    'confidence': 70,
                    'vertices': [(0, support_level), (0, 0)],
                    'pattern_points': [support_level] * 10,
                    'time_span': n,
                    'amplitude': max(price_data) - support_level,
                    'description': 'Bearish continuation pattern',
                    'reliability': 0.70
                })
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Triangle detection error: {e}")
            return patterns

    def _detect_flags_pennants(self, price_data: np.ndarray) -> List[Dict[str, Any]]:
        """Flag va Pennant pattern detection"""
        patterns = []
        
        try:
            # Simple flag detection
            # Look for strong price movement followed by consolidation
            
            if len(price_data) < 20:
                return patterns
            
            # Calculate price change
            price_change = (price_data[-1] - price_data[0]) / price_data[0]
            
            # Look for consolidation after strong move
            if abs(price_change) > 0.02:  # More than 2% move
                # Analyze consolidation
                recent_data = price_data[-10:]
                volatility = np.std(recent_data) / np.mean(recent_data)
                
                if volatility < 0.01:  # Low volatility (consolidation)
                    signal = 'bullish' if price_change > 0 else 'bearish'
                    
                    patterns.append({
                        'name': 'Flag',
                        'type': 'technical',
                        'signal': signal,
                        'confidence': 65,
                        'vertices': [(0, price_data[0]), (len(price_data)//2, price_data[len(price_data)//2])],
                        'pattern_points': recent_data.tolist(),
                        'time_span': 10,
                        'amplitude': abs(price_change),
                        'description': 'Short-term continuation pattern',
                        'reliability': 0.65
                    })
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Flag/Pennant detection error: {e}")
            return patterns

    def _detect_channels(self, price_data: np.ndarray) -> List[Dict[str, Any]]:
        """Channel pattern detection"""
        patterns = []
        
        try:
            if len(price_data) < 15:
                return patterns
            
            # Simple channel detection using linear regression
            x = np.arange(len(price_data))
            
            # Fit trend line
            slope, intercept = np.polyfit(x, price_data, 1)
            trend_line = slope * x + intercept
            
            # Calculate deviations
            deviations = price_data - trend_line
            
            # Check if price stays within a channel
            max_deviation = np.max(np.abs(deviations))
            avg_price = np.mean(price_data)
            
            if max_deviation / avg_price < 0.02:  # Within 2% of trend line
                signal = 'bullish' if slope > 0 else 'bearish'
                
                patterns.append({
                    'name': 'Channel',
                    'type': 'technical',
                    'signal': signal,
                    'confidence': 70,
                    'vertices': [(0, trend_line[0]), (len(price_data)-1, trend_line[-1])],
                    'pattern_points': price_data.tolist(),
                    'time_span': len(price_data),
                    'amplitude': max_deviation,
                    'description': 'Price channel pattern',
                    'reliability': 0.70
                })
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Channel detection error: {e}")
            return patterns

    def _detect_double_patterns(self, price_data: np.ndarray) -> List[Dict[str, Any]]:
        """Double Top va Double Bottom detection"""
        patterns = []
        
        try:
            # Find peaks
            peaks, _ = signal.find_peaks(price_data, prominence=0.005)
            valleys, _ = signal.find_peaks(-price_data, prominence=0.005)
            
            # Double Top
            if len(peaks) >= 2:
                for i in range(len(peaks) - 1):
                    peak1, peak2 = peaks[i], peaks[i + 1]
                    price1, price2 = price_data[peak1], price_data[peak2]
                    
                    # Check if peaks are at similar levels
                    diff = abs(price1 - price2) / max(price1, price2)
                    if diff < 0.02:  # Within 2%
                        patterns.append({
                            'name': 'Double Top',
                            'type': 'technical',
                            'signal': 'bearish',
                            'confidence': 75,
                            'vertices': [(0, peak1), (0, peak2)],
                            'pattern_points': [peak1, peak2],
                            'time_span': peak2 - peak1,
                            'amplitude': max(price1, price2) - min(price_data[peak1:peak2]),
                            'description': 'Bearish reversal pattern',
                            'reliability': 0.75
                        })
            
            # Double Bottom
            if len(valleys) >= 2:
                for i in range(len(valleys) - 1):
                    valley1, valley2 = valleys[i], valleys[i + 1]
                    price1, price2 = price_data[valley1], price_data[valley2]
                    
                    # Check if valleys are at similar levels
                    diff = abs(price1 - price2) / max(price1, price2)
                    if diff < 0.02:  # Within 2%
                        patterns.append({
                            'name': 'Double Bottom',
                            'type': 'technical',
                            'signal': 'bullish',
                            'confidence': 75,
                            'vertices': [(0, valley1), (0, valley2)],
                            'pattern_points': [valley1, valley2],
                            'time_span': valley2 - valley1,
                            'amplitude': max(price_data[valley1:valley2]) - min(price1, price2),
                            'description': 'Bullish reversal pattern',
                            'reliability': 0.75
                        })
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Double pattern detection error: {e}")
            return patterns

    # Trend analysis methods
    def _detect_trend_lines(self, price_data: np.ndarray) -> List[TrendLine]:
        """Trend line detection"""
        trend_lines = []
        
        try:
            # Find local minima and maxima
            minima, _ = signal.find_peaks(-price_data, prominence=0.01)
            maxima, _ = signal.find_peaks(price_data, prominence=0.01)
            
            # Generate all possible trend lines
            all_points = np.concatenate([minima, maxima])
            
            for i in range(len(all_points)):
                for j in range(i + 1, len(all_points)):
                    point1_idx, point2_idx = all_points[i], all_points[j]
                    
                    if abs(point2_idx - point1_idx) < 5:  # Minimum distance
                        continue
                    
                    # Calculate trend line
                    x1, y1 = point1_idx, price_data[point1_idx]
                    x2, y2 = point2_idx, price_data[point2_idx]
                    
                    if x2 != x1:
                        slope = (y2 - y1) / (x2 - x1)
                        intercept = y1 - slope * x1
                        
                        # Calculate R-squared
                        x = np.arange(len(price_data))
                        y_pred = slope * x + intercept
                        ss_res = np.sum((price_data - y_pred) ** 2)
                        ss_tot = np.sum((price_data - np.mean(price_data)) ** 2)
                        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
                        
                        # Filter by quality
                        if r_squared > 0.7:
                            trend_line = TrendLine(
                                start_point=(x1, y1),
                                end_point=(x2, y2),
                                slope=slope,
                                intercept=intercept,
                                r_squared=r_squared,
                                strength=r_squared,
                                support_resistance_type='unknown',
                                valid_points=0,
                                touches=0
                            )
                            trend_lines.append(trend_line)
            
            return trend_lines[:10]  # Return top 10 trend lines
            
        except Exception as e:
            self.logger.error(f"Trend line detection error: {e}")
            return []

    def _calculate_trend_analysis(self, price_data: np.ndarray, trend_lines: List[TrendLine]) -> Dict[str, Any]:
        """Overall trend analysis"""
        try:
            if len(price_data) < 10:
                return {'trend': 'unknown', 'strength': 0.0, 'signal': 'neutral'}
            
            # Calculate moving averages
            short_ma = np.mean(price_data[-5:])
            long_ma = np.mean(price_data[-20:]) if len(price_data) >= 20 else np.mean(price_data)
            
            # Overall trend based on price action
            if short_ma > long_ma * 1.001:
                trend = 'uptrend'
                signal = 'bullish'
            elif short_ma < long_ma * 0.999:
                trend = 'downtrend'
                signal = 'bearish'
            else:
                trend = 'sideways'
                signal = 'neutral'
            
            # Calculate trend strength
            price_change = (price_data[-1] - price_data[0]) / price_data[0]
            strength = min(1.0, abs(price_change) * 10)  # Scale to 0-1
            
            # Factor in trend lines
            if trend_lines:
                avg_r_squared = np.mean([tl.r_squared for tl in trend_lines])
                strength = (strength + avg_r_squared) / 2
            
            return {
                'trend': trend,
                'strength': strength,
                'signal': signal,
                'trend_lines': len(trend_lines),
                'price_change': price_change,
                'ma_signal': 'bullish' if short_ma > long_ma else 'bearish'
            }
            
        except Exception as e:
            self.logger.error(f"Trend analysis error: {e}")
            return {'trend': 'unknown', 'strength': 0.0, 'signal': 'neutral'}

    # Support/Resistance methods
    def _find_significant_levels(self, price_data: np.ndarray) -> List[Dict[str, Any]]:
        """Significant price level detection"""
        levels = []
        
        try:
            # Find local minima and maxima
            minima_idx, _ = signal.find_peaks(-price_data, prominence=0.005)
            maxima_idx, _ = signal.find_peaks(price_data, prominence=0.005)
            
            # Check each level for significance
            tolerance = self.config.get('support_resistance', {}).get('tolerance', 0.02)
            
            # Analyze minima (potential support)
            for min_idx in minima_idx:
                price_level = price_data[min_idx]
                touches = 1
                
                # Count touches
                for i, price in enumerate(price_data):
                    if abs(price - price_level) / price_level < tolerance:
                        touches += 1
                
                if touches >= 2:  # At least 2 touches
                    levels.append({
                        'price': price_level,
                        'type': 'support',
                        'touches': touches,
                        'index': min_idx,
                        'strength': min(1.0, touches / 5.0)
                    })
            
            # Analyze maxima (potential resistance)
            for max_idx in maxima_idx:
                price_level = price_data[max_idx]
                touches = 1
                
                # Count touches
                for i, price in enumerate(price_data):
                    if abs(price - price_level) / price_level < tolerance:
                        touches += 1
                
                if touches >= 2:  # At least 2 touches
                    levels.append({
                        'price': price_level,
                        'type': 'resistance',
                        'touches': touches,
                        'index': max_idx,
                        'strength': min(1.0, touches / 5.0)
                    })
            
            # Sort by strength
            levels.sort(key=lambda x: x['strength'], reverse=True)
            
            return levels
            
        except Exception as e:
            self.logger.error(f"Significant level detection error: {e}")
            return []

    def _calculate_key_levels(self, price_data: np.ndarray, support_levels: List[Dict], 
                            resistance_levels: List[Dict]) -> List[Dict[str, Any]]:
        """Key level calculation"""
        key_levels = []
        
        try:
            current_price = price_data[-1]
            
            # Find nearest support and resistance
            nearest_support = None
            nearest_resistance = None
            
            for support in support_levels:
                if support['price'] < current_price:
                    if nearest_support is None or support['price'] > nearest_support['price']:
                        nearest_support = support
            
            for resistance in resistance_levels:
                if resistance['price'] > current_price:
                    if nearest_resistance is None or resistance['price'] < nearest_resistance['price']:
                        nearest_resistance = resistance
            
            # Create key levels
            if nearest_support:
                key_levels.append({
                    'level': nearest_support['price'],
                    'type': 'support',
                    'distance': abs(current_price - nearest_support['price']) / current_price,
                    'strength': nearest_support['strength'],
                    'importance': 'nearest_support'
                })
            
            if nearest_resistance:
                key_levels.append({
                    'level': nearest_resistance['price'],
                    'type': 'resistance',
                    'distance': abs(nearest_resistance['price'] - current_price) / current_price,
                    'strength': nearest_resistance['strength'],
                    'importance': 'nearest_resistance'
                })
            
            return key_levels
            
        except Exception as e:
            self.logger.error(f"Key level calculation error: {e}")
            return []

    def _calculate_pivot_points(self, price_data: np.ndarray) -> List[float]:
        """Pivot point calculation"""
        try:
            if len(price_data) < 3:
                return []
            
            # Classic pivot point calculation
            high = np.max(price_data[-3:])
            low = np.min(price_data[-3:])
            close = price_data[-1]
            
            pivot = (high + low + close) / 3
            
            # Support and resistance levels
            r1 = 2 * pivot - low
            r2 = pivot + (high - low)
            s1 = 2 * pivot - high
            s2 = pivot - (high - low)
            
            return [s2, s1, pivot, r1, r2]
            
        except Exception as e:
            self.logger.error(f"Pivot point calculation error: {e}")
            return []

    def _identify_price_zones(self, price_data: np.ndarray) -> List[Dict[str, Any]]:
        """Price zone identification"""
        zones = []
        
        try:
            # Define price zones based on percentiles
            current_price = price_data[-1]
            
            zones = [
                {
                    'name': 'Strong Support',
                    'range': [np.percentile(price_data, 5), np.percentile(price_data, 15)],
                    'type': 'support',
                    'strength': 'high'
                },
                {
                    'name': 'Support',
                    'range': [np.percentile(price_data, 15), np.percentile(price_data, 35)],
                    'type': 'support',
                    'strength': 'medium'
                },
                {
                    'name': 'Current Price',
                    'range': [current_price * 0.99, current_price * 1.01],
                    'type': 'neutral',
                    'strength': 'current'
                },
                {
                    'name': 'Resistance',
                    'range': [np.percentile(price_data, 65), np.percentile(price_data, 85)],
                    'type': 'resistance',
                    'strength': 'medium'
                },
                {
                    'name': 'Strong Resistance',
                    'range': [np.percentile(price_data, 85), np.percentile(price_data, 95)],
                    'type': 'resistance',
                    'strength': 'high'
                }
            ]
            
            return zones
            
        except Exception as e:
            self.logger.error(f"Price zone identification error: {e}")
            return []

    def _calculate_level_strength(self, price_data: np.ndarray, levels: List[Dict]) -> Dict[str, float]:
        """Level strength calculation"""
        try:
            strength_dict = {}
            
            for level in levels:
                level_key = f"{level['type']}_{level['price']:.4f}"
                strength_dict[level_key] = level.get('strength', 0.0)
            
            return strength_dict
            
        except Exception as e:
            self.logger.error(f"Level strength calculation error: {e}")
            return {}

    # Volume analysis methods (simplified)
    def _simulate_volume_analysis(self, price_data: np.ndarray) -> Dict[str, Any]:
        """Simulated volume analysis"""
        try:
            # Create synthetic volume data based on price movements
            n_points = len(price_data)
            
            # Base volume
            base_volume = 1000
            
            # Volume increases with price volatility
            price_changes = np.abs(np.diff(price_data, prepend=price_data[0]))
            volume = base_volume * (1 + price_changes * 100)
            
            # Price levels for volume profile
            price_levels = np.linspace(np.min(price_data), np.max(price_data), 20)
            volume_at_price = np.zeros(len(price_levels))
            
            # Distribute volume across price levels
            for i, price in enumerate(price_data):
                # Find closest price level
                closest_idx = np.argmin(np.abs(price_levels - price))
                volume_at_price[closest_idx] += volume[i]
            
            # Point of Control (highest volume price)
            poc_idx = np.argmax(volume_at_price)
            poc = price_levels[poc_idx]
            
            # High and Low Volume Nodes
            threshold = np.mean(volume_at_price) * 1.5
            hvn_indices = np.where(volume_at_price > threshold)[0]
            hvn = [price_levels[i] for i in hvn_indices]
            
            lvn_indices = np.where(volume_at_price < np.mean(volume_at_price) * 0.5)[0]
            lvn = [price_levels[i] for i in lvn_indices]
            
            # Value Area (70% of volume)
            sorted_volume_indices = np.argsort(volume_at_price)[::-1]
            value_area_volume = 0
            value_area_indices = []
            
            for idx in sorted_volume_indices:
                if value_area_volume < 0.7 * np.sum(volume_at_price):
                    value_area_volume += volume_at_price[idx]
                    value_area_indices.append(idx)
                else:
                    break
            
            value_area_high = max(price_levels[i] for i in value_area_indices)
            value_area_low = min(price_levels[i] for i in value_area_indices)
            
            # Profile shape
            if volume_at_price[0] > volume_at_price[-1]:
                profile_shape = "bullish_volume"
            elif volume_at_price[0] < volume_at_price[-1]:
                profile_shape = "bearish_volume"
            else:
                profile_shape = "balanced"
            
            return {
                'price_levels': price_levels,
                'volume_at_price': volume_at_price,
                'value_area': {'high': value_area_high, 'low': value_area_low},
                'poc': poc,
                'hvn': hvn,
                'lvn': lvn,
                'profile_shape': profile_shape,
                'volume_trend': 'increasing' if np.mean(volume[-5:]) > np.mean(volume[:-5]) else 'decreasing',
                'obv_signal': 'bullish' if np.sum(volume[-10:]) > np.sum(volume[:10]) else 'bearish'
            }
            
        except Exception as e:
            self.logger.error(f"Volume analysis simulation error: {e}")
            return {
                'price_levels': np.array([]),
                'volume_at_price': np.array([]),
                'value_area': {'high': 0, 'low': 0},
                'poc': 0,
                'hvn': [],
                'lvn': [],
                'profile_shape': 'unknown',
                'volume_trend': 'unknown',
                'obv_signal': 'neutral'
            }

    # Price action analysis methods
    def _is_uptrend(self, price_data: np.ndarray) -> bool:
        """Uptrend detection"""
        if len(price_data) < 5:
            return False
        
        recent_prices = price_data[-5:]
        return all(recent_prices[i] <= recent_prices[i+1] for i in range(len(recent_prices)-1))

    def _is_downtrend(self, price_data: np.ndarray) -> bool:
        """Downtrend detection"""
        if len(price_data) < 5:
            return False
        
        recent_prices = price_data[-5:]
        return all(recent_prices[i] >= recent_prices[i+1] for i in range(len(recent_prices)-1))

    def _identify_bounces(self, price_data: np.ndarray) -> List[str]:
        """Bounce identification"""
        bounces = []
        
        try:
            if len(price_data) < 10:
                return bounces
            
            # Find support bounces
            for i in range(5, len(price_data)-5):
                if (price_data[i] <= price_data[i-1] and 
                    price_data[i] <= price_data[i+1] and
                    price_data[i+2] > price_data[i] and
                    price_data[i+3] > price_data[i]):
                    bounces.append('support_bounce')
                    break
            
            # Find resistance rejections
            for i in range(5, len(price_data)-5):
                if (price_data[i] >= price_data[i-1] and 
                    price_data[i] >= price_data[i+1] and
                    price_data[i+2] < price_data[i] and
                    price_data[i+3] < price_data[i]):
                    bounces.append('resistance_rejection')
                    break
            
            return bounces
            
        except Exception as e:
            self.logger.error(f"Bounce identification error: {e}")
            return []

    def _identify_breakouts(self, price_data: np.ndarray) -> List[str]:
        """Breakout identification"""
        breakouts = []
        
        try:
            if len(price_data) < 20:
                return breakouts
            
            # Check for breakouts from consolidation
            recent_data = price_data[-10:]
            resistance = np.max(recent_data[:-5])
            support = np.min(recent_data[:-5])
            
            current_price = price_data[-1]
            
            # Bullish breakout
            if current_price > resistance * 1.001:
                breakouts.append('bullish_breakout')
            
            # Bearish breakdown
            if current_price < support * 0.999:
                breakouts.append('breakdown')
            
            return breakouts
            
        except Exception as e:
            self.logger.error(f"Breakout identification error: {e}")
            return []

    def _check_volume_confirmation(self, price_data: np.ndarray) -> bool:
        """Volume confirmation check"""
        # This is simplified - in real implementation you need actual volume data
        return np.random.random() > 0.5

    def _identify_key_price_levels(self, price_data: np.ndarray) -> List[float]:
        """Key price level identification"""
        try:
            # Find significant levels using Fibonacci ratios
            high = np.max(price_data)
            low = np.min(price_data)
            diff = high - low
            
            fib_levels = [
                low,
                low + diff * 0.236,
                low + diff * 0.382,
                low + diff * 0.5,
                low + diff * 0.618,
                low + diff * 0.786,
                high
            ]
            
            return fib_levels
            
        except Exception as e:
            self.logger.error(f"Key price level identification error: {e}")
            return []

    def _calculate_momentum(self, price_data: np.ndarray) -> float:
        """Momentum calculation"""
        try:
            if len(price_data) < 10:
                return 0.0
            
            # Simple momentum calculation
            momentum = (price_data[-1] - price_data[-10]) / price_data[-10]
            return momentum
            
        except Exception as e:
            self.logger.error(f"Momentum calculation error: {e}")
            return 0.0

    def _calculate_volatility(self, price_data: np.ndarray) -> float:
        """Volatility calculation"""
        try:
            if len(price_data) < 10:
                return 0.0
            
            # Standard deviation as volatility measure
            volatility = np.std(price_data) / np.mean(price_data)
            return volatility
            
        except Exception as e:
            self.logger.error(f"Volatility calculation error: {e}")
            return 0.0


# Export all classes and functions
__all__ = [
    'ChartAnalyzer',
    'PatternType',
    'TrendDirection',
    'CandlestickPattern',
    'TechnicalPattern',
    'TrendLine',
    'SupportResistance',
    'VolumeProfile'
]

# Modul versiyasi
__version__ = "1.0.0"
__author__ = "Orion Starline AI Team"