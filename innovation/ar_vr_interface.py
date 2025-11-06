"""
Orion Starline AR/VR Trading Interface Module
Augmented Reality va Virtual Reality trading interfeysi

AR/VR Features:
- 3D trading dashboards
- Immersive market visualization
- Gesture-based trading
- VR trading environments
- Haptic feedback integration
- Real-time data overlays
- Interactive 3D charts
- Spatial audio alerts
"""

import numpy as np
import pandas as pd
import json
import asyncio
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import pygame
import math
from abc import ABC, abstractmethod
import logging
from concurrent.futures import ThreadPoolExecutor
import threading
import queue

@dataclass
class Vector3D:
    """3D vektor ma'lumotlari"""
    x: float
    y: float
    z: float
    
    def __add__(self, other):
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __mul__(self, scalar: float):
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

@dataclass
class TradeAction:
    """Trading harakati"""
    action_type: str  # BUY, SELL, HOLD
    asset: str
    quantity: float
    price: float
    confidence: float
    timestamp: datetime

@dataclass
class MarketData3D:
    """3D market ma'lumotlari"""
    price: float
    volume: float
    timestamp: datetime
    position: Vector3D
    color: Tuple[int, int, int]

class VRTradingEnvironment:
    """VR trading muhit"""
    
    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height
        self.camera_position = Vector3D(0, 0, 5)
        self.camera_rotation = Vector3D(0, 0, 0)
        self.trading_objects = {}
        self.haptic_feedback_enabled = True
        self.audio_enabled = True
        self.logger = logging.getLogger(__name__)
        
        # VR tracking data
        self.head_position = Vector3D(0, 0, 0)
        self.left_hand_position = Vector3D(-1, 0, 0)
        self.right_hand_position = Vector3D(1, 0, 0)
        
        # Trading state
        self.current_portfolio = {}
        self.market_data_3d = []
        self.active_orders = []
        
    def initialize_vr_session(self) -> Dict[str, Any]:
        """VR session boshlanishi"""
        return {
            'session_id': f"vr_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'resolution': f"{self.width}x{self.height}",
            'refresh_rate': 90,  # Hz
            'tracking_enabled': True,
            'haptic_feedback': self.haptic_feedback_enabled,
            'spatial_audio': self.audio_enabled,
            'init_time': datetime.now().isoformat()
        }
        
    def update_head_tracking(self, position: Vector3D, rotation: Vector3D):
        """Head tracking yangilash"""
        self.head_position = position
        self.camera_position = position
        self.camera_rotation = rotation
        
    def update_hand_tracking(self, left_hand: Vector3D, right_hand: Vector3D):
        """Hand tracking yangilash"""
        self.left_hand_position = left_hand
        self.right_hand_position = right_hand
        
    def handle_gesture_trading(self, gesture_type: str, position: Vector3D) -> Optional[TradeAction]:
        """Gesture-based trading"""
        
        # Gesture patterns for trading
        gesture_mapping = {
            'pinch': 'BUY',
            'open_palm': 'SELL',
            'thumbs_up': 'HOLD',
            'point': 'INFO'
        }
        
        action_type = gesture_mapping.get(gesture_type)
        if not action_type:
            return None
            
        # Determine asset from position
        asset = self._get_asset_from_position(position)
        
        # Calculate confidence based on hand position clarity
        confidence = self._calculate_gesture_confidence(position)
        
        return TradeAction(
            action_type=action_type,
            asset=asset,
            quantity=100,  # Default quantity
            price=self._get_current_price(asset),
            confidence=confidence,
            timestamp=datetime.now()
        )
        
    def _get_asset_from_position(self, position: Vector3D) -> str:
        """Position dan asset aniqlash"""
        # Simplified asset mapping based on spatial zones
        if position.x < -2:
            return "BTC"
        elif position.x < 0:
            return "ETH"
        elif position.x < 2:
            return "AAPL"
        else:
            return "TSLA"
        
    def _calculate_gesture_confidence(self, position: Vector3D) -> float:
        """Gesture confidence hisoblash"""
        # Base confidence on distance from center and stability
        distance_from_center = math.sqrt(position.x**2 + position.y**2 + position.z**2)
        base_confidence = max(0.0, 1.0 - (distance_from_center / 5.0))
        return min(1.0, base_confidence + 0.3)
        
    def _get_current_price(self, asset: str) -> float:
        """Current asset narxi"""
        mock_prices = {"BTC": 45000, "ETH": 3000, "AAPL": 175, "TSLA": 200}
        return mock_prices.get(asset, 100)

class ARTradingOverlay:
    """AR trading overlay"""
    
    def __init__(self, camera_matrix: np.ndarray = None):
        self.camera_matrix = camera_matrix or np.eye(3)
        self.ar_objects = {}
        self.trading_data_overlay = []
        self.real_world_anchors = {}
        self.logger = logging.getLogger(__name__)
        
    def create_ar_trading_dashboard(self, viewport_bounds: Tuple[int, int, int, int]) -> Dict[str, Any]:
        """AR trading dashboard yaratish"""
        
        dashboard_config = {
            'viewport': viewport_bounds,
            'transparency': 0.8,
            'scaling_factor': 1.0,
            'refresh_rate': 60,
            'objects': [
                {
                    'type': 'portfolio_widget',
                    'position': [0.1, 0.1, 0],
                    'size': [0.3, 0.2],
                    'data': 'current_portfolio'
                },
                {
                    'type': 'price_ticker',
                    'position': [0.1, 0.8, 0],
                    'size': [0.8, 0.1],
                    'data': 'live_prices'
                },
                {
                    'type': 'risk_meter',
                    'position': [0.9, 0.5, 0],
                    'size': [0.1, 0.3],
                    'data': 'risk_metrics'
                }
            ]
        }
        
        return dashboard_config
        
    def add_market_data_overlay(self, detection_data: Dict[str, Any]) -> None:
        """Market data overlay qo'shish"""
        
        overlay_data = {
            'timestamp': datetime.now().isoformat(),
            'market_prices': detection_data.get('prices', {}),
            'alerts': detection_data.get('alerts', []),
            'indicators': detection_data.get('technical_indicators', {}),
            'position': detection_data.get('world_position', [0, 0, 0])
        }
        
        self.trading_data_overlay.append(overlay_data)
        
    def recognize_trading_objects(self, image_frame: np.ndarray) -> Dict[str, Any]:
        """Trading obyektlarini tanish"""
        
        # Simulated object recognition
        detected_objects = {
            'qr_codes': [
                {'position': [100, 200], 'data': 'BTC_PRICE_45000'},
                {'position': [300, 150], 'data': 'ETH_PRICE_3000'}
            ],
            'text_regions': [
                {'text': 'BUY BTC', 'confidence': 0.9, 'position': [50, 50]},
                {'text': 'SELL ETH', 'confidence': 0.8, 'position': [200, 300]}
            ],
            'hand_gestures': [
                {'gesture': 'pinch', 'position': [150, 250], 'confidence': 0.85}
            ]
        }
        
        return detected_objects
        
    def generate_ar_trading_commands(self, detected_objects: Dict[str, Any]) -> List[TradeAction]:
        """AR trading commands yaratish"""
        
        commands = []
        
        # Process hand gestures
        for gesture in detected_objects.get('hand_gestures', []):
            if gesture['confidence'] > 0.8:
                commands.append(TradeAction(
                    action_type='BUY',
                    asset='BTC',
                    quantity=100,
                    price=45000,
                    confidence=gesture['confidence'],
                    timestamp=datetime.now()
                ))
                
        # Process text commands
        for text_region in detected_objects.get('text_regions', []):
            text = text_region['text'].upper()
            if 'BUY' in text:
                asset = 'BTC' if 'BTC' in text else 'ETH'
                commands.append(TradeAction(
                    action_type='BUY',
                    asset=asset,
                    quantity=50,
                    price=45000 if asset == 'BTC' else 3000,
                    confidence=text_region['confidence'],
                    timestamp=datetime.now()
                ))
            elif 'SELL' in text:
                asset = 'ETH' if 'ETH' in text else 'BTC'
                commands.append(TradeAction(
                    action_type='SELL',
                    asset=asset,
                    quantity=50,
                    price=3000 if asset == 'ETH' else 45000,
                    confidence=text_region['confidence'],
                    timestamp=datetime.now()
                ))
                
        return commands

class ImmersiveChartRenderer:
        """Immersive 3D chart renderer"""
        
        def __init__(self):
            self.chart_data = {}
            self.render_settings = {
                'chart_type': 'candlestick',
                'timeframe': '1H',
                'indicators': ['RSI', 'MACD', 'Bollinger_Bands'],
                'color_scheme': 'dark',
                'animation_speed': 1.0
            }
            self.camera_angles = {}
            self.chart_animations = {}
            
        def render_3d_candlestick_chart(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
            """3D candlestick chart render"""
            
            # Prepare 3D data
            chart_3d = {
                'symbol': symbol,
                'candles': [],
                'indicators': {},
                'camera_angle': {'elevation': 45, 'azimuth': 45},
                'lighting': {
                    'ambient': 0.3,
                    'directional': 0.7,
                    'shadows': True
                }
            }
            
            # Generate 3D candles
            for i, row in data.iterrows():
                candle = {
                    'position': Vector3D(i * 0.1, row['open'], 0),
                    'size': Vector3D(0.05, abs(row['close'] - row['open']), 0.02),
                    'color': (0, 255, 0) if row['close'] > row['open'] else (255, 0, 0),
                    'wick': {
                        'position': Vector3D(i * 0.1, min(row['open'], row['close']), 0),
                        'size': Vector3D(0.02, abs(row['high'] - row['low']), 0.02),
                        'color': (128, 128, 128)
                    }
                }
                chart_3d['candles'].append(candle)
                
            # Add volume as 3D bars
            chart_3d['volume_bars'] = []
            for i, row in data.iterrows():
                volume_bar = {
                    'position': Vector3D(i * 0.1, 0, -0.5),
                    'size': Vector3D(0.05, row['volume'] / 1000000, 0.05),
                    'color': (100, 100, 255)
                }
                chart_3d['volume_bars'].append(volume_bar)
                
            return chart_3d
            
        def render_order_flow_3d(self, order_data: List[Dict[str, Any]]) -> Dict[str, Any]:
            """3D order flow visualization"""
            
            order_flow_3d = {
                'buy_orders': [],
                'sell_orders': [],
                'market_depth': [],
                'time': []
            }
            
            # Convert orders to 3D
            for i, order in enumerate(order_data):
                order_3d = {
                    'position': Vector3D(order['price'] * 0.001, order['quantity'], i * 0.1),
                    'size': Vector3D(0.1, 0.1, 0.1),
                    'color': (0, 255, 0) if order['side'] == 'buy' else (255, 0, 0),
                    'transparency': 0.7
                }
                
                if order['side'] == 'buy':
                    order_flow_3d['buy_orders'].append(order_3d)
                else:
                    order_flow_3d['sell_orders'].append(order_3d)
                    
            return order_flow_3d
            
        def add_technical_indicators_3d(self, chart_data: Dict[str, Any], 
                                      indicators: Dict[str, np.ndarray]) -> Dict[str, Any]:
            """3D technical indicators"""
            
            indicator_3d = {}
            
            for indicator_name, values in indicators.items():
                indicator_points = []
                for i, value in enumerate(values):
                    point = {
                        'position': Vector3D(i * 0.1, value, 1),
                        'color': self._get_indicator_color(indicator_name),
                        'size': Vector3D(0.03, 0.03, 0.03)
                    }
                    indicator_points.append(point)
                    
                indicator_3d[indicator_name] = indicator_points
                
            chart_data['indicators'] = indicator_3d
            return chart_data
            
        def _get_indicator_color(self, indicator_name: str) -> Tuple[int, int, int]:
            """Indicator ranglarini aniqlash"""
            colors = {
                'RSI': (255, 165, 0),      # Orange
                'MACD': (255, 20, 147),     # Deep Pink
                'Bollinger_Bands': (0, 191, 255),  # Deep Sky Blue
                'Moving_Average': (255, 215, 0)    # Gold
            }
            return colors.get(indicator_name, (255, 255, 255))

class SpatialAudioManager:
    """Spatial audio manager"""
    
    def __init__(self):
        self.audio_sources = {}
        self.sound_library = {
            'buy_signal': 'sounds/buy_notification.wav',
            'sell_signal': 'sounds/sell_notification.wav',
            'alert': 'sounds/alert.wav',
            'market_update': 'sounds/market_update.wav',
            'error': 'sounds/error.wav'
        }
        self.volume_settings = {
            'alerts': 0.8,
            'market_updates': 0.5,
            'notifications': 0.6,
            'background': 0.2
        }
        
    def create_spatial_audio_feedback(self, event_type: str, 
                                     position: Vector3D, 
                                     intensity: float = 1.0) -> Dict[str, Any]:
        """Spatial audio feedback yaratish"""
        
        audio_feedback = {
            'sound_file': self.sound_library.get(event_type, 'sounds/default.wav'),
            'position': position,
            'volume': self._calculate_spatial_volume(position, intensity),
            'frequency': self._calculate_audio_frequency(event_type, intensity),
            'duration': 2.0,  # seconds
            'spatial_blend': True
        }
        
        return audio_feedback
        
    def _calculate_spatial_volume(self, position: Vector3D, intensity: float) -> float:
        """Spatial volume hisoblash"""
        distance = math.sqrt(position.x**2 + position.y**2 + position.z**2)
        base_volume = max(0.0, 1.0 - (distance / 10.0))
        return min(1.0, base_volume * intensity)
        
    def _calculate_audio_frequency(self, event_type: str, intensity: float) -> float:
        """Audio frequency hisoblash"""
        base_frequencies = {
            'buy_signal': 440,   # A4
            'sell_signal': 330,  # E4
            'alert': 660,        # E5
            'market_update': 220, # A3
            'error': 110         # A2
        }
        
        base_freq = base_frequencies.get(event_type, 440)
        return base_freq * intensity
        
    def generate_market_soundscape(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Market soundscape yaratish"""
        
        soundscape = {
            'background_noise': 'sounds/market_ambient.wav',
            'pulse_rate': self._calculate_market_pulse(market_data),
            'tension_level': self._calculate_market_tension(market_data),
            'dynamic_elements': []
        }
        
        # Add dynamic sound elements based on market volatility
        volatility = market_data.get('volatility', 0.5)
        if volatility > 0.7:
            soundscape['dynamic_elements'].append({
                'sound': 'sounds/high_volatility.wav',
                'intensity': volatility,
                'position': Vector3D(0, 0, 2)
            })
            
        return soundscape
        
    def _calculate_market_pulse(self, market_data: Dict[str, Any]) -> float:
        """Market pulse hisoblash"""
        volume = market_data.get('volume', 1000000)
        price_change = market_data.get('price_change', 0)
        
        # Base pulse on volume, modified by price volatility
        base_pulse = min(2.0, volume / 1000000)
        volatility_modifier = 1 + abs(price_change)
        
        return base_pulse * volatility_modifier
        
    def _calculate_market_tension(self, market_data: Dict[str, Any]) -> float:
        """Market tension hisoblash"""
        price_volatility = market_data.get('volatility', 0.5)
        volume_spike = market_data.get('volume_spike', False)
        
        tension = price_volatility
        if volume_spike:
            tension += 0.3
            
        return min(1.0, tension)

class HapticFeedbackManager:
    """Haptic feedback manager"""
    
    def __init__(self):
        self.haptic_devices = ['left_controller', 'right_controller', 'headset']
        self.feedback_patterns = {
            'light_tap': {'duration': 50, 'intensity': 0.3},
            'medium_tap': {'duration': 100, 'intensity': 0.6},
            'strong_tap': {'duration': 200, 'intensity': 1.0},
            'vibration': {'duration': 300, 'intensity': 0.8},
            'pulse': {'duration': 500, 'intensity': 0.5, 'pattern': 'pulsing'}
        }
        
    def generate_trading_feedback(self, trade_action: TradeAction, 
                                 confidence: float) -> Dict[str, Any]:
        """Trading feedback yaratish"""
        
        if confidence < 0.3:
            pattern = 'light_tap'
            device = 'left_controller'
        elif confidence < 0.7:
            pattern = 'medium_tap'
            device = 'right_controller'
        else:
            pattern = 'strong_tap'
            device = 'both_controllers'
            
        feedback_config = self.feedback_patterns[pattern]
        
        return {
            'device': device,
            'pattern': pattern,
            'duration': feedback_config['duration'],
            'intensity': feedback_config['intensity'] * confidence,
            'repeat': 1 if confidence < 0.8 else 2
        }
        
    def generate_market_alert_feedback(self, alert_type: str, 
                                      severity: float) -> Dict[str, Any]:
        """Market alert feedback"""
        
        if severity > 0.8:
            pattern = 'vibration'
            repeat = 3
        elif severity > 0.5:
            pattern = 'strong_tap'
            repeat = 2
        else:
            pattern = 'medium_tap'
            repeat = 1
            
        feedback_config = self.feedback_patterns[pattern]
        
        return {
            'device': 'headset',
            'pattern': pattern,
            'duration': feedback_config['duration'],
            'intensity': feedback_config['intensity'] * severity,
            'repeat': repeat
        }
        
    def create_portfolio_feedback(self, portfolio_change: Dict[str, Any]) -> Dict[str, Any]:
        """Portfolio holati feedback"""
        
        change_percent = portfolio_change.get('change_percent', 0)
        severity = abs(change_percent) / 10.0  # Normalize to 0-1
        
        if change_percent > 0:
            pattern = 'medium_tap'
        else:
            pattern = 'vibration'
            
        feedback_config = self.feedback_patterns[pattern]
        
        return {
            'device': 'both_controllers',
            'pattern': pattern,
            'duration': feedback_config['duration'],
            'intensity': min(1.0, feedback_config['intensity'] + severity),
            'repeat': 2 if severity > 0.5 else 1
        }

class ARVRTradingSystem:
    """Asosiy AR/VR trading tizimi"""
    
    def __init__(self):
        self.vr_environment = VRTradingEnvironment()
        self.ar_overlay = ARTradingOverlay()
        self.chart_renderer = ImmersiveChartRenderer()
        self.audio_manager = SpatialAudioManager()
        self.haptic_manager = HapticFeedbackManager()
        self.is_active = False
        self.logger = logging.getLogger(__name__)
        
    async def initialize_trading_session(self) -> Dict[str, Any]:
        """Trading session boshlash"""
        
        self.is_active = True
        
        # Initialize VR
        vr_config = self.vr_environment.initialize_vr_session()
        
        # Setup AR overlay
        ar_config = self.ar_overlay.create_ar_trading_dashboard((0, 0, 1920, 1080))
        
        # Initialize audio and haptic systems
        audio_config = {'enabled': True, 'spatial_audio': True}
        haptic_config = {'enabled': True, 'feedback_level': 'medium'}
        
        session_config = {
            'session_id': f"arvr_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'start_time': datetime.now().isoformat(),
            'vr_config': vr_config,
            'ar_config': ar_config,
            'audio_config': audio_config,
            'haptic_config': haptic_config,
            'status': 'active'
        }
        
        return session_config
        
    async def process_vr_trading_input(self, head_position: Vector3D,
                                     head_rotation: Vector3D,
                                     left_hand: Vector3D,
                                     right_hand: Vector3D,
                                     gestures: List[Dict[str, Any]]) -> List[TradeAction]:
        """VR trading input processing"""
        
        # Update tracking
        self.vr_environment.update_head_tracking(head_position, head_rotation)
        self.vr_environment.update_hand_tracking(left_hand, right_hand)
        
        # Process gestures
        trade_actions = []
        for gesture in gestures:
            action = self.vr_environment.handle_gesture_trading(
                gesture['type'], 
                Vector3D(*gesture['position'])
            )
            if action:
                trade_actions.append(action)
                
        return trade_actions
        
    async def process_ar_trading_input(self, camera_frame: np.ndarray,
                                     detected_objects: Dict[str, Any]) -> List[TradeAction]:
        """AR trading input processing"""
        
        # Recognize trading objects
        objects = self.ar_overlay.recognize_trading_objects(camera_frame)
        
        # Generate commands
        commands = self.ar_overlay.generate_ar_trading_commands(objects)
        
        # Update overlay with detected data
        self.ar_overlay.add_market_data_overlay({
            'prices': {'BTC': 45000, 'ETH': 3000},
            'alerts': [],
            'technical_indicators': {},
            'world_position': detected_objects.get('position', [0, 0, 0])
        })
        
        return commands
        
    async def render_immersive_charts(self, market_data: pd.DataFrame,
                                    indicators: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Immersive charts render"""
        
        # Generate 3D candlestick chart
        chart_3d = self.chart_renderer.render_3d_candlestick_chart("BTC/USD", market_data)
        
        # Add technical indicators
        chart_3d = self.chart_renderer.add_technical_indicators_3d(chart_3d, indicators)
        
        # Render order flow
        order_flow_data = [
            {'price': 44900, 'quantity': 1.5, 'side': 'buy'},
            {'price': 44950, 'quantity': 2.0, 'side': 'buy'},
            {'price': 45000, 'quantity': 3.0, 'side': 'sell'},
            {'price': 45050, 'quantity': 1.0, 'side': 'sell'}
        ]
        order_flow_3d = self.chart_renderer.render_order_flow_3d(order_flow_data)
        
        return {
            'main_chart': chart_3d,
            'order_flow': order_flow_3d,
            'render_settings': self.chart_renderer.render_settings,
            'timestamp': datetime.now().isoformat()
        }
        
    async def generate_multimodal_feedback(self, trade_action: TradeAction,
                                         market_state: Dict[str, Any]) -> Dict[str, Any]:
        """Multimodal feedback generation"""
        
        # Audio feedback
        audio_feedback = self.audio_manager.create_spatial_audio_feedback(
            'buy_signal' if trade_action.action_type == 'BUY' else 'sell_signal',
            Vector3D(trade_action.price * 0.001, 0, 1),
            trade_action.confidence
        )
        
        # Haptic feedback
        haptic_feedback = self.haptic_manager.generate_trading_feedback(
            trade_action, trade_action.confidence
        )
        
        # Market soundscape
        soundscape = self.audio_manager.generate_market_soundscape(market_state)
        
        return {
            'audio': audio_feedback,
            'haptic': haptic_feedback,
            'soundscape': soundscape,
            'timestamp': datetime.now().isoformat()
        }
        
    async def comprehensive_trading_session(self) -> Dict[str, Any]:
        """Comprehensive trading session"""
        
        if not self.is_active:
            await self.initialize_trading_session()
            
        # Generate sample market data
        dates = pd.date_range(start='2023-01-01', periods=100, freq='H')
        market_data = pd.DataFrame({
            'timestamp': dates,
            'open': np.random.randn(100).cumsum() + 45000,
            'high': np.random.randn(100).cumsum() + 45200,
            'low': np.random.randn(100).cumsum() + 44800,
            'close': np.random.randn(100).cumsum() + 45000,
            'volume': np.random.randint(1000, 10000, 100)
        })
        
        indicators = {
            'RSI': np.random.uniform(30, 70, 100),
            'MACD': np.random.randn(100).cumsum(),
            'Bollinger_Bands': np.random.randn(100).cumsum() * 200 + 45000
        }
        
        # Render charts
        charts = await self.render_immersive_charts(market_data, indicators)
        
        # Generate trade actions
        sample_gestures = [
            {'type': 'pinch', 'position': [0.5, 1.0, 0]},
            {'type': 'open_palm', 'position': [-0.5, 0.5, 0]}
        ]
        
        head_pos = Vector3D(0, 0, 0)
        head_rot = Vector3D(0, 0, 0)
        left_hand = Vector3D(-1, 0, 0)
        right_hand = Vector3D(1, 0, 0)
        
        vr_actions = await self.process_vr_trading_input(
            head_pos, head_rot, left_hand, right_hand, sample_gestures
        )
        
        # Generate feedback for first action
        feedback = {}
        if vr_actions:
            feedback = await self.generate_multimodal_feedback(
                vr_actions[0], {'volatility': 0.5, 'volume': 5000}
            )
            
        return {
            'session_status': 'active',
            'charts': charts,
            'trade_actions': [asdict(action) for action in vr_actions],
            'feedback': feedback,
            'timestamp': datetime.now().isoformat()
        }

# Demo function
async def demo_arvr_trading():
    """AR/VR trading demo"""
    print("🥽 AR/VR Trading System Demo")
    print("=" * 50)
    
    # Initialize AR/VR system
    arvr_system = ARVRTradingSystem()
    
    # Comprehensive trading session
    session_data = await arvr_system.comprehensive_trading_session()
    
    print(f"Session Status: {session_data['session_status']}")
    print(f"Generated {len(session_data['trade_actions'])} trade actions")
    
    # Display trade actions
    for i, action in enumerate(session_data['trade_actions']):
        print(f"Action {i+1}: {action['action_type']} {action['asset']} "
              f"@ ${action['price']} (confidence: {action['confidence']:.2f})")
    
    print(f"\n3D Charts: {len(session_data['charts']['main_chart']['candles'])} candles")
    print(f"Order Flow: {len(session_data['charts']['order_flow']['buy_orders'])} buy orders")
    
    # Feedback details
    if session_data.get('feedback'):
        feedback = session_data['feedback']
        print(f"\nAudio Feedback: {feedback['audio']['sound_file']}")
        print(f"Haptic Pattern: {feedback['haptic']['pattern']}")
        print(f"Market Tension: {feedback['soundscape']['tension_level']:.2f}")
    
    return session_data

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Run demo
    asyncio.run(demo_arvr_trading())