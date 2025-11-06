"""
Configuration Manager for Latency Optimization System
"""

import json
import yaml
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
import os
import logging

logger = logging.getLogger(__name__)


@dataclass
class NetworkConfig:
    """Network optimization configuration"""
    enable_kernel_bypass: bool = False
    enable_user_space_tcp: bool = False
    network_interface: str = "eth0"
    packet_filtering: bool = True
    qos_enabled: bool = True
    traffic_priorities: Dict[str, int] = None
    max_packet_size: int = 1500
    buffer_size: int = 65536
    tx_queue_count: int = 8
    rx_queue_count: int = 8
    enable_vlan: bool = False
    
    def __post_init__(self):
        if self.traffic_priorities is None:
            self.traffic_priorities = {
                'critical': 1,
                'market_data': 2,
                'orders': 3,
                'heartbeat': 4,
                'info': 5
            }


@dataclass  
class HardwareConfig:
    """Hardware optimization configuration"""
    cpu_affinity_enabled: bool = True
    numa_enabled: bool = True
    memory_preallocation: bool = True
    cache_friendly_structures: bool = True
    simd_enabled: bool = True
    parallel_processing: bool = True
    core_affinity_mask: str = "0xFF"  # CPU cores mask
    numa_node: int = 0
    memory_limit_gb: int = 32
    cache_line_size: int = 64  # bytes
    vectorization: bool = True
    
    def get_cpu_cores(self) -> list:
        """Get CPU cores from affinity mask"""
        cores = []
        for i in range(64):  # Support up to 64 cores
            if (self.core_affinity_mask & (1 << i)):
                cores.append(i)
        return cores


@dataclass
class SoftwareConfig:
    """Software optimization configuration"""
    zero_copy_enabled: bool = True
    lock_free_algorithms: bool = True
    memory_pools: bool = True
    pre_allocation: bool = True
    compiler_optimizations: bool = True
    profiling_enabled: bool = True
    hot_path_optimization: bool = True
    
    # Memory pool settings
    memory_pool_size: int = 1024 * 1024 * 1024  # 1GB
    chunk_sizes: list = None
    alignment: int = 64  # Cache line aligned
    
    # Lock-free settings
    atomic_operations: bool = True
    wait_free_algorithms: bool = False
    
    def __post_init__(self):
        if self.chunk_sizes is None:
            self.chunk_sizes = [64, 128, 256, 512, 1024, 2048, 4096, 8192]


@dataclass
class MarketDataConfig:
    """Market data processing configuration"""
    tick_buffer_size: int = 100000
    order_book_levels: int = 10
    max_symbols: int = 10000
    price_precision: int = 8
    timestamp_precision: str = "nanoseconds"
    compression_enabled: bool = True
    batch_processing: bool = True
    batch_size: int = 1000
    
    # Feed processing
    feed_aggregation: bool = True
    latency_smoothing: bool = True
    volatility_window: int = 1000


@dataclass
class LatencyConfig:
    """Main latency optimization configuration"""
    network: NetworkConfig = None
    hardware: HardwareConfig = None  
    software: SoftwareConfig = None
    market_data: MarketDataConfig = None
    
    # Global settings
    target_latency_us: int = 10  # Microseconds
    monitoring_interval_ms: int = 100
    alerting_enabled: bool = True
    performance_mode: str = "ultra"  # low, normal, high, ultra
    
    def __post_init__(self):
        if self.network is None:
            self.network = NetworkConfig()
        if self.hardware is None:
            self.hardware = HardwareConfig()
        if self.software is None:
            self.software = SoftwareConfig()
        if self.market_data is None:
            self.market_data = MarketDataConfig()


class ConfigManager:
    """Configuration manager for latency optimization system"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.config: LatencyConfig = LatencyConfig()
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file or environment"""
        if self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    if self.config_file.endswith('.json'):
                        data = json.load(f)
                    elif self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                        data = yaml.safe_load(f)
                    else:
                        logger.warning(f"Unknown config file format: {self.config_file}")
                        return
                
                # Update config from loaded data
                self._update_config_from_dict(data)
                logger.info(f"Configuration loaded from {self.config_file}")
                
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        
        # Override with environment variables
        self._load_from_env()
    
    def _update_config_from_dict(self, data: Dict[str, Any]):
        """Update configuration from dictionary"""
        if 'network' in data:
            network_data = data['network']
            for key, value in network_data.items():
                if hasattr(self.config.network, key):
                    setattr(self.config.network, key, value)
        
        if 'hardware' in data:
            hardware_data = data['hardware']
            for key, value in hardware_data.items():
                if hasattr(self.config.hardware, key):
                    setattr(self.config.hardware, key, value)
        
        if 'software' in data:
            software_data = data['software']
            for key, value in software_data.items():
                if hasattr(self.config.software, key):
                    setattr(self.config.software, key, value)
        
        if 'market_data' in data:
            market_data = data['market_data']
            for key, value in market_data.items():
                if hasattr(self.config.market_data, key):
                    setattr(self.config.market_data, key, value)
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        # Network config
        if os.getenv('LATENCY_NETWORK_INTERFACE'):
            self.config.network.network_interface = os.getenv('LATENCY_NETWORK_INTERFACE')
        if os.getenv('LATENCY_ENABLE_KERNEL_BYPASS'):
            self.config.network.enable_kernel_bypass = os.getenv('LATENCY_ENABLE_KERNEL_BYPASS').lower() == 'true'
        
        # Hardware config
        if os.getenv('LATENCY_CPU_AFFINITY'):
            self.config.hardware.core_affinity_mask = int(os.getenv('LATENCY_CPU_AFFINITY'), 16)
        
        # Software config
        if os.getenv('LATENCY_ZERO_COPY'):
            self.config.software.zero_copy_enabled = os.getenv('LATENCY_ZERO_COPY').lower() == 'true'
        
        # Global config
        if os.getenv('LATENCY_TARGET_LATENCY'):
            self.config.target_latency_us = int(os.getenv('LATENCY_TARGET_LATENCY'))
        if os.getenv('LATENCY_PERFORMANCE_MODE'):
            self.config.performance_mode = os.getenv('LATENCY_PERFORMANCE_MODE')
    
    def save_config(self, config_file: Optional[str] = None):
        """Save configuration to file"""
        file_path = config_file or self.config_file
        if not file_path:
            raise ValueError("No config file specified")
        
        config_dict = asdict(self.config)
        
        try:
            with open(file_path, 'w') as f:
                if file_path.endswith('.json'):
                    json.dump(config_dict, f, indent=2)
                elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    raise ValueError(f"Unsupported config file format: {file_path}")
            
            logger.info(f"Configuration saved to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise
    
    def get_config(self) -> LatencyConfig:
        """Get current configuration"""
        return self.config
    
    def update_config(self, **kwargs):
        """Update configuration parameters"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            elif hasattr(self.config.network, key):
                setattr(self.config.network, key, value)
            elif hasattr(self.config.hardware, key):
                setattr(self.config.hardware, key, value)
            elif hasattr(self.config.software, key):
                setattr(self.config.software, key, value)
            elif hasattr(self.config.market_data, key):
                setattr(self.config.market_data, key, value)
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return issues"""
        issues = []
        
        # Validate target latency
        if self.config.target_latency_us < 1:
            issues.append("Target latency must be at least 1 microsecond")
        
        # Validate memory pool settings
        if self.config.software.memory_pool_size < 1024:
            issues.append("Memory pool size should be at least 1KB")
        
        # Validate chunk sizes
        chunk_sizes = self.config.software.chunk_sizes
        if not all(size > 0 for size in chunk_sizes):
            issues.append("All chunk sizes must be positive")
        
        # Validate CPU affinity mask
        try:
            mask = self.config.hardware.core_affinity_mask
            if isinstance(mask, str) and mask.startswith('0x'):
                int(mask, 16)
            elif isinstance(mask, int):
                if mask <= 0:
                    issues.append("CPU affinity mask must be non-zero")
        except ValueError:
            issues.append("Invalid CPU affinity mask format")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }