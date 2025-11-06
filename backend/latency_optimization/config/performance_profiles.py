"""
Performance Profiles for Latency Optimization System
"""

from enum import Enum
from typing import Dict, Any
from dataclasses import dataclass
from .config_manager import LatencyConfig, NetworkConfig, HardwareConfig, SoftwareConfig, MarketDataConfig


class PerformanceMode(Enum):
    """Performance optimization modes"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    ULTRA = "ultra"


@dataclass
class PerformanceProfile:
    """Performance optimization profile"""
    name: str
    description: str
    target_latency_us: int
    network_config: Dict[str, Any]
    hardware_config: Dict[str, Any]
    software_config: Dict[str, Any]
    market_data_config: Dict[str, Any]


class PerformanceProfileManager:
    """Manager for performance profiles"""
    
    def __init__(self):
        self.profiles = self._create_profiles()
    
    def _create_profiles(self) -> Dict[str, PerformanceProfile]:
        """Create predefined performance profiles"""
        return {
            'low': PerformanceProfile(
                name='Low Performance',
                description='Basic latency optimization for development and testing',
                target_latency_us=100,
                network_config={
                    'enable_kernel_bypass': False,
                    'enable_user_space_tcp': False,
                    'packet_filtering': True,
                    'qos_enabled': True,
                    'buffer_size': 32768,
                    'tx_queue_count': 2,
                    'rx_queue_count': 2
                },
                hardware_config={
                    'cpu_affinity_enabled': False,
                    'numa_enabled': False,
                    'memory_preallocation': False,
                    'simd_enabled': False,
                    'parallel_processing': False,
                    'core_affinity_mask': '0x1',
                    'numa_node': 0,
                    'memory_limit_gb': 8,
                    'vectorization': False
                },
                software_config={
                    'zero_copy_enabled': False,
                    'lock_free_algorithms': False,
                    'memory_pools': False,
                    'pre_allocation': False,
                    'compiler_optimizations': False,
                    'profiling_enabled': True,
                    'hot_path_optimization': False,
                    'memory_pool_size': 64 * 1024 * 1024,  # 64MB
                    'atomic_operations': False
                },
                market_data_config={
                    'tick_buffer_size': 10000,
                    'order_book_levels': 5,
                    'max_symbols': 1000,
                    'compression_enabled': False,
                    'batch_processing': True,
                    'batch_size': 100
                }
            ),
            
            'normal': PerformanceProfile(
                name='Normal Performance',
                description='Balanced optimization for production use',
                target_latency_us=50,
                network_config={
                    'enable_kernel_bypass': False,
                    'enable_user_space_tcp': True,
                    'packet_filtering': True,
                    'qos_enabled': True,
                    'buffer_size': 65536,
                    'tx_queue_count': 4,
                    'rx_queue_count': 4
                },
                hardware_config={
                    'cpu_affinity_enabled': True,
                    'numa_enabled': True,
                    'memory_preallocation': True,
                    'simd_enabled': True,
                    'parallel_processing': True,
                    'core_affinity_mask': '0xF',
                    'numa_node': 0,
                    'memory_limit_gb': 16,
                    'vectorization': True
                },
                software_config={
                    'zero_copy_enabled': True,
                    'lock_free_algorithms': True,
                    'memory_pools': True,
                    'pre_allocation': True,
                    'compiler_optimizations': True,
                    'profiling_enabled': True,
                    'hot_path_optimization': True,
                    'memory_pool_size': 256 * 1024 * 1024,  # 256MB
                    'atomic_operations': True
                },
                market_data_config={
                    'tick_buffer_size': 50000,
                    'order_book_levels': 10,
                    'max_symbols': 5000,
                    'compression_enabled': True,
                    'batch_processing': True,
                    'batch_size': 500
                }
            ),
            
            'high': PerformanceProfile(
                name='High Performance',
                description='Aggressive optimization for trading systems',
                target_latency_us=25,
                network_config={
                    'enable_kernel_bypass': True,
                    'enable_user_space_tcp': True,
                    'packet_filtering': True,
                    'qos_enabled': True,
                    'buffer_size': 131072,
                    'tx_queue_count': 8,
                    'rx_queue_count': 8,
                    'enable_vlan': True
                },
                hardware_config={
                    'cpu_affinity_enabled': True,
                    'numa_enabled': True,
                    'memory_preallocation': True,
                    'simd_enabled': True,
                    'parallel_processing': True,
                    'core_affinity_mask': '0xFF',
                    'numa_node': 0,
                    'memory_limit_gb': 32,
                    'vectorization': True
                },
                software_config={
                    'zero_copy_enabled': True,
                    'lock_free_algorithms': True,
                    'memory_pools': True,
                    'pre_allocation': True,
                    'compiler_optimizations': True,
                    'profiling_enabled': True,
                    'hot_path_optimization': True,
                    'memory_pool_size': 512 * 1024 * 1024,  # 512MB
                    'atomic_operations': True,
                    'wait_free_algorithms': True
                },
                market_data_config={
                    'tick_buffer_size': 100000,
                    'order_book_levels': 20,
                    'max_symbols': 10000,
                    'compression_enabled': True,
                    'batch_processing': True,
                    'batch_size': 1000,
                    'feed_aggregation': True,
                    'latency_smoothing': True
                }
            ),
            
            'ultra': PerformanceProfile(
                name='Ultra Performance',
                description='Maximum optimization for microsecond trading',
                target_latency_us=10,
                network_config={
                    'enable_kernel_bypass': True,
                    'enable_user_space_tcp': True,
                    'packet_filtering': True,
                    'qos_enabled': True,
                    'buffer_size': 262144,
                    'tx_queue_count': 16,
                    'rx_queue_count': 16,
                    'enable_vlan': True,
                    'max_packet_size': 1500
                },
                hardware_config={
                    'cpu_affinity_enabled': True,
                    'numa_enabled': True,
                    'memory_preallocation': True,
                    'simd_enabled': True,
                    'parallel_processing': True,
                    'core_affinity_mask': '0xFFFF',
                    'numa_node': 0,
                    'memory_limit_gb': 64,
                    'vectorization': True
                },
                software_config={
                    'zero_copy_enabled': True,
                    'lock_free_algorithms': True,
                    'memory_pools': True,
                    'pre_allocation': True,
                    'compiler_optimizations': True,
                    'profiling_enabled': True,
                    'hot_path_optimization': True,
                    'memory_pool_size': 1024 * 1024 * 1024,  # 1GB
                    'atomic_operations': True,
                    'wait_free_algorithms': True,
                    'alignment': 64
                },
                market_data_config={
                    'tick_buffer_size': 200000,
                    'order_book_levels': 50,
                    'max_symbols': 20000,
                    'compression_enabled': True,
                    'batch_processing': True,
                    'batch_size': 2000,
                    'feed_aggregation': True,
                    'latency_smoothing': True,
                    'volatility_window': 500
                }
            )
        }
    
    def get_profile(self, profile_name: str) -> PerformanceProfile:
        """Get a performance profile by name"""
        if profile_name.lower() not in self.profiles:
            raise ValueError(f"Unknown performance profile: {profile_name}")
        
        return self.profiles[profile_name.lower()]
    
    def get_all_profiles(self) -> Dict[str, PerformanceProfile]:
        """Get all available performance profiles"""
        return self.profiles.copy()
    
    def apply_profile(self, config: LatencyConfig, profile_name: str) -> LatencyConfig:
        """Apply a performance profile to configuration"""
        profile = self.get_profile(profile_name)
        
        # Update network config
        for key, value in profile.network_config.items():
            if hasattr(config.network, key):
                setattr(config.network, key, value)
        
        # Update hardware config
        for key, value in profile.hardware_config.items():
            if hasattr(config.hardware, key):
                setattr(config.hardware, key, value)
        
        # Update software config
        for key, value in profile.software_config.items():
            if hasattr(config.software, key):
                setattr(config.software, key, value)
        
        # Update market data config
        for key, value in profile.market_data_config.items():
            if hasattr(config.market_data, key):
                setattr(config.market_data, key, value)
        
        # Update global config
        config.target_latency_us = profile.target_latency_us
        config.performance_mode = profile.name.lower().replace(' ', '_')
        
        return config
    
    def create_custom_profile(self, name: str, description: str, 
                            base_profile: str = 'normal',
                            overrides: Dict[str, Any] = None) -> PerformanceProfile:
        """Create a custom performance profile"""
        base = self.get_profile(base_profile)
        
        # Start with base profile
        config = {
            'target_latency_us': base.target_latency_us,
            'network_config': base.network_config.copy(),
            'hardware_config': base.hardware_config.copy(),
            'software_config': base.software_config.copy(),
            'market_data_config': base.market_data_config.copy()
        }
        
        # Apply overrides
        if overrides:
            for section in overrides:
                if section in config:
                    config[section].update(overrides[section])
                else:
                    config[section] = overrides[section]
        
        return PerformanceProfile(
            name=name,
            description=description,
            **config
        )
    
    def list_profiles(self) -> Dict[str, str]:
        """List all available profiles with descriptions"""
        return {name: profile.description for name, profile in self.profiles.items()}
    
    def validate_profile(self, profile: PerformanceProfile) -> Dict[str, Any]:
        """Validate a performance profile"""
        issues = []
        
        # Validate target latency
        if profile.target_latency_us <= 0:
            issues.append("Target latency must be positive")
        
        # Validate chunk sizes in software config
        chunk_sizes = profile.software_config.get('chunk_sizes', [])
        if chunk_sizes and not all(size > 0 for size in chunk_sizes):
            issues.append("All chunk sizes must be positive")
        
        # Validate memory pool size
        pool_size = profile.software_config.get('memory_pool_size', 0)
        if pool_size <= 0:
            issues.append("Memory pool size must be positive")
        
        # Validate buffer sizes
        buffer_size = profile.network_config.get('buffer_size', 0)
        if buffer_size <= 0:
            issues.append("Buffer size must be positive")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }