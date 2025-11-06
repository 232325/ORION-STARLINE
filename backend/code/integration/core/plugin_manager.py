"""
Plugin Manager
==============

Plugin architecture va modul management uchun Plugin Manager.
Plugin discovery, loading, va lifecycle management ta'minlaydi.
"""

import os
import sys
import importlib
import inspect
import logging
from typing import Dict, List, Any, Optional, Callable, Type
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json
import time
from pathlib import Path

@dataclass
class PluginInfo:
    """Plugin haqida ma'lumot"""
    name: str
    version: str
    description: str
    author: str
    module_type: str
    entry_point: str
    dependencies: List[str]
    capabilities: List[str]
    config_schema: Dict[str, Any]
    file_path: str
    load_time: float
    status: str = "loaded"

class PluginInterface(ABC):
    """Plugin asosiy interface"""
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Plugin-ni ishga tushirish"""
        pass
    
    @abstractmethod
    async def execute(self, action: str, data: Dict[str, Any]) -> Any:
        """Plugin-ni ishga tushirish"""
        pass
    
    @abstractmethod
    async def shutdown(self):
        """Plugin-ni to'xtatish"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Plugin capabilities-ni olish"""
        pass
    
    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
        """Plugin health status-ni olish"""
        pass

class PluginManager:
    """
    Plugin Manager
    
    Plugin-larni discovery, loading, va management qilish uchun.
    Dynamic plugin loading va lifecycle management ta'minlaydi.
    """
    
    def __init__(self, plugin_directories: List[str] = None):
        self.plugin_directories = plugin_directories or []
        self.plugins: Dict[str, PluginInfo] = {}
        self.plugin_instances: Dict[str, PluginInterface] = {}
        self.plugin_loaders: Dict[str, Any] = {}
        
        self.logger = logging.getLogger(__name__)
        
        # Default plugin directories
        if not self.plugin_directories:
            self.plugin_directories = [
                "/workspace/code/integration/plugins",
                "/workspace/code/plugins",
                "/workspace/code/integration/ai_trading/plugins",
                "/workspace/code/integration/quantum/plugins",
                "/workspace/code/integration/blockchain/plugins"
            ]
        
        self.logger.info("Plugin Manager initialized")
    
    async def initialize(self) -> bool:
        """Plugin Manager-ni ishga tushirish"""
        try:
            self.logger.info("Plugin Manager ishga tushirilmoqda...")
            
            # Plugin directories yaratish
            for directory in self.plugin_directories:
                os.makedirs(directory, exist_ok=True)
            
            # Plugin-larni discover va load qilish
            await self._discover_plugins()
            await self._load_plugins()
            
            self.logger.info(f"Plugin Manager ishga tushdi. {len(self.plugins)} plugin topildi")
            return True
            
        except Exception as e:
            self.logger.error(f"Plugin Manager ishga tushishda xato: {e}")
            return False
    
    async def shutdown(self):
        """Plugin Manager-ni to'xtatish"""
        try:
            self.logger.info("Plugin Manager to'xtatilmoqda...")
            
            # Barcha plugin-larni to'xtatish
            for plugin_name in list(self.plugins.keys()):
                await self.unload_plugin(plugin_name)
            
            self.plugins.clear()
            self.plugin_instances.clear()
            self.plugin_loaders.clear()
            
            self.logger.info("Plugin Manager to'xtatildi")
            
        except Exception as e:
            self.logger.error(f"Plugin Manager to'xtatishda xato: {e}")
    
    async def _discover_plugins(self):
        """Plugin-larni discover qilish"""
        for plugin_dir in self.plugin_directories:
            if not os.path.exists(plugin_dir):
                continue
            
            self.logger.info(f"Plugin directory scan qilinmoqda: {plugin_dir}")
            
            for root, dirs, files in os.walk(plugin_dir):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        await self._discover_plugin_file(os.path.join(root, file))
    
    async def _discover_plugin_file(self, file_path: str):
        """Plugin faylini discover qilish"""
        try:
            plugin_info = await self._extract_plugin_info(file_path)
            if plugin_info:
                self.plugins[plugin_info.name] = plugin_info
                self.logger.info(f"Plugin discover qilindi: {plugin_info.name}")
        except Exception as e:
            self.logger.error(f"Plugin discover qilishda xato {file_path}: {e}")
    
    async def _extract_plugin_info(self, file_path: str) -> Optional[PluginInfo]:
        """Plugin faylidan plugin info extract qilish"""
        try:
            # Fayl ichidan plugin metadata extract qilish
            # Bu yerda fayl ichidagi comment yoki docstring dan ma'lumot olish mumkin
            # Hozircha minimal implementation
            
            file_name = os.path.basename(file_path).replace('.py', '')
            
            # Minimal plugin info yaratish
            plugin_info = PluginInfo(
                name=file_name,
                version="1.0.0",
                description=f"Plugin: {file_name}",
                author="Unknown",
                module_type="custom",
                entry_point=f"{file_name}.Plugin",
                dependencies=[],
                capabilities=[],
                config_schema={},
                file_path=file_path,
                load_time=time.time()
            )
            
            return plugin_info
            
        except Exception as e:
            self.logger.error(f"Plugin info extract qilishda xato: {e}")
            return None
    
    async def _load_plugins(self):
        """Plugin-larni load qilish"""
        for plugin_name, plugin_info in self.plugins.items():
            try:
                await self.load_plugin(plugin_name)
            except Exception as e:
                self.logger.error(f"Plugin load qilishda xato {plugin_name}: {e}")
    
    async def load_plugin(self, plugin_name: str, config: Dict[str, Any] = None) -> bool:
        """Plugin-ni load qilish"""
        try:
            if plugin_name not in self.plugins:
                self.logger.error(f"Plugin topilmadi: {plugin_name}")
                return False
            
            plugin_info = self.plugins[plugin_name]
            
            if plugin_name in self.plugin_instances:
                self.logger.warning(f"Plugin allaqachon yuklangan: {plugin_name}")
                return True
            
            self.logger.info(f"Plugin yuklanmoqda: {plugin_name}")
            
            # Plugin-ni import qilish
            spec = importlib.util.spec_from_file_location(
                plugin_name, plugin_info.file_path
            )
            
            if not spec or not spec.loader:
                self.logger.error(f"Plugin modulni load qilish mumkin emas: {plugin_name}")
                return False
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Plugin class-ni topish
            plugin_class = getattr(module, 'Plugin', None)
            if not plugin_class:
                # Standart nomlar bilan qidirish
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (inspect.isclass(attr) and 
                        issubclass(attr, PluginInterface) and 
                        attr != PluginInterface):
                        plugin_class = attr
                        break
            
            if not plugin_class:
                self.logger.error(f"Plugin interface topilmadi: {plugin_name}")
                return False
            
            # Plugin instance yaratish
            plugin_instance = plugin_class()
            
            # Plugin-ni ishga tushirish
            if config:
                plugin_info.config.update(config)
            
            success = await plugin_instance.initialize(plugin_info.config)
            if not success:
                self.logger.error(f"Plugin ishga tushmadi: {plugin_name}")
                return False
            
            # Plugin-ni saqlash
            self.plugin_instances[plugin_name] = plugin_instance
            self.plugin_loaders[plugin_name] = module
            plugin_info.status = "active"
            
            # Plugin capabilities-ni olish
            try:
                capabilities = await plugin_instance.get_capabilities()
                plugin_info.capabilities = capabilities
            except:
                pass  # Optional method
            
            self.logger.info(f"Plugin muvaffaqiyatli yuklandi: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Plugin yuklashda xato {plugin_name}: {e}")
            return False
    
    async def unload_plugin(self, plugin_name: str) -> bool:
        """Plugin-ni unload qilish"""
        try:
            if plugin_name not in self.plugins:
                self.logger.error(f"Plugin topilmadi: {plugin_name}")
                return False
            
            self.logger.info(f"Plugin yuklanmoqda: {plugin_name}")
            
            # Plugin instance-ni to'xtatish
            if plugin_name in self.plugin_instances:
                plugin_instance = self.plugin_instances[plugin_name]
                try:
                    await plugin_instance.shutdown()
                except Exception as e:
                    self.logger.error(f"Plugin to'xtatishda xato {plugin_name}: {e}")
                
                del self.plugin_instances[plugin_name]
            
            # Module-ni clear qilish
            if plugin_name in sys.modules:
                del sys.modules[plugin_name]
            
            if plugin_name in self.plugin_loaders:
                del self.plugin_loaders[plugin_name]
            
            # Plugin info-ni yangilash
            self.plugins[plugin_name].status = "unloaded"
            
            self.logger.info(f"Plugin muvaffaqiyatli yuklandi: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Plugin yuklashda xato {plugin_name}: {e}")
            return False
    
    async def reload_plugin(self, plugin_name: str, config: Dict[str, Any] = None) -> bool:
        """Plugin-ni qayta load qilish"""
        try:
            await self.unload_plugin(plugin_name)
            return await self.load_plugin(plugin_name, config)
        except Exception as e:
            self.logger.error(f"Plugin qayta yuklashda xato {plugin_name}: {e}")
            return False
    
    async def execute_plugin(self, plugin_name: str, action: str, 
                           data: Dict[str, Any] = None) -> Any:
        """Plugin-ni execute qilish"""
        try:
            if plugin_name not in self.plugin_instances:
                self.logger.error(f"Plugin instance topilmadi: {plugin_name}")
                return None
            
            plugin_instance = self.plugin_instances[plugin_name]
            return await plugin_instance.execute(action, data or {})
            
        except Exception as e:
            self.logger.error(f"Plugin execute qilishda xato {plugin_name}: {e}")
            return None
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Plugin haqida ma'lumot olish"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """Barcha plugin-lar ro'yxati"""
        return [
            {
                'name': info.name,
                'version': info.version,
                'description': info.description,
                'status': info.status,
                'capabilities': info.capabilities,
                'load_time': info.load_time
            }
            for info in self.plugins.values()
        ]
    
    def get_active_plugins(self) -> List[str]:
        """Faol plugin-lar ro'yxati"""
        return [
            name for name, info in self.plugins.items() 
            if info.status == "active"
        ]
    
    async def get_plugin_health(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Plugin health status olish"""
        try:
            if plugin_name not in self.plugin_instances:
                return None
            
            plugin_instance = self.plugin_instances[plugin_name]
            return await plugin_instance.get_health_status()
            
        except Exception as e:
            self.logger.error(f"Plugin health olishda xato {plugin_name}: {e}")
            return None
    
    def get_plugins_by_capability(self, capability: str) -> List[str]:
        """Capability bo'yicha plugin-lar topish"""
        plugins_with_capability = []
        for plugin_name, plugin_info in self.plugins.items():
            if capability in plugin_info.capabilities:
                plugins_with_capability.append(plugin_name)
        return plugins_with_capability
    
    async def validate_plugin_config(self, plugin_name: str, 
                                   config: Dict[str, Any]) -> bool:
        """Plugin config validation"""
        try:
            if plugin_name not in self.plugins:
                return False
            
            plugin_info = self.plugins[plugin_name]
            config_schema = plugin_info.config_schema
            
            if not config_schema:
                return True  # No validation required
            
            # Minimal schema validation
            required_fields = config_schema.get('required', [])
            for field in required_fields:
                if field not in config:
                    self.logger.error(f"Plugin {plugin_name} config validation failed: missing {field}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Plugin config validation da xato {plugin_name}: {e}")
            return False
    
    def get_plugin_stats(self) -> Dict[str, Any]:
        """Plugin statistics"""
        total_plugins = len(self.plugins)
        active_plugins = len(self.get_active_plugins())
        
        # Plugin types bo'yicha taqsimot
        plugin_types = {}
        for plugin_info in self.plugins.values():
            plugin_type = plugin_info.module_type
            plugin_types[plugin_type] = plugin_types.get(plugin_type, 0) + 1
        
        return {
            'total_plugins': total_plugins,
            'active_plugins': active_plugins,
            'inactive_plugins': total_plugins - active_plugins,
            'plugin_types': plugin_types,
            'loaded_plugins': list(self.plugin_instances.keys())
        }