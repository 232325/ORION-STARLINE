#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Speed Optimizer - Tezlik optimizatori
Veb-sahifalarni sub-sekundu yuklash uchun optimizatsiya

Xususiyatlar:
- Kod minifikatsiyasi
- Bundle optimizatsiya
- Lazy loading
- Asset kompressiya
- HTTP/2 push
- Critical CSS inline
- Image optimization
- Resource bundling
"""

import os
import re
import json
import gzip
import bz2
import hashlib
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import aiofiles
import aiohttp
from urllib.parse import urljoin, urlparse
import cssutils
import jsmin
from PIL import Image, ImageOps
import webp
import sharp

# Logging sozlamalar
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AssetInfo:
    """Asset ma'lumotlari"""
    path: str
    size: int
    type: str
    compressed_size: int = 0
    hash: str = ""
    optimized: bool = False
    compression_ratio: float = 0.0

@dataclass
class BundleConfig:
    """Bundle konfiguratsiyasi"""
    name: str
    entry_files: List[str]
    output_path: str
    minify: bool = True
    source_map: bool = False
    compression: str = "gzip"  # gzip, bzip2, none

class SpeedOptimizer:
    """Asosiy tezlik optimizatori"""
    
    def __init__(self, project_root: str, config: Optional[Dict] = None):
        self.project_root = Path(project_root)
        self.config = config or self._default_config()
        self.assets: Dict[str, AssetInfo] = {}
        self.bundles: Dict[str, BundleConfig] = {}
        
        # Cache papkalar
        self.cache_dir = self.project_root / "optimization_cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        # Performance metrikalar
        self.metrics = {
            "bundle_sizes": {},
            "load_times": {},
            "compression_ratios": {},
            "optimization_savings": {}
        }

    def _default_config(self) -> Dict:
        """Standart konfiguratsiya"""
        return {
            "minify_js": True,
            "minify_css": True,
            "minify_html": True,
            "compress_images": True,
            "lazy_load_images": True,
            "enable_gzip": True,
            "enable_brotli": False,  # Agar mos bo'lsa
            "max_bundle_size": 500 * 1024,  # 500KB
            "critical_css_inline": True,
            "preload_fonts": True,
            "webpack_bundle": True,
            "rollup_bundle": False,
            "esbuild_minify": True,
            "terser_minify": True,
            "cssnano": True,
            "html_minifier": True,
            "image_quality": 85,
            "webp_conversion": True,
            "avif_conversion": True,
            "lazy_load_threshold": "100px",
            "preconnect_domains": [],
            "dns_prefetch": []
        }

    async def optimize_project(self) -> Dict:
        """Butun loyihani optimizatsiya qilish"""
        logger.info("🚀 Tezlik optimizatsiyasi boshlanmoqda...")
        
        try:
            # 1. Asset Discovery va analiz
            await self._discover_assets()
            
            # 2. JavaScript optimizatsiya
            await self._optimize_javascript()
            
            # 3. CSS optimizatsiya
            await self._optimize_css()
            
            # 4. HTML optimizatsiya
            await self._optimize_html()
            
            # 5. Image optimizatsiya
            await self._optimize_images()
            
            # 6. Bundle yaratish va optimizatsiya
            await self._create_optimized_bundles()
            
            # 7. Lazy loading qo'shish
            await self._implement_lazy_loading()
            
            # 8. Critical CSS inline qilish
            await self._inline_critical_css()
            
            # 9. HTTP/2 push uchun hazirlik
            await self._prepare_http2_push()
            
            # 10. Performance metrikalar
            await self._generate_performance_report()
            
            logger.info("✅ Tezlik optimizatsiyasi muvaffaqiyatli tugallandi!")
            return self.metrics
            
        except Exception as e:
            logger.error(f"❌ Optimizatsiya xatosi: {str(e)}")
            raise

    async def _discover_assets(self):
        """Asset'larni topish va analiz qilish"""
        logger.info("🔍 Asset'larni qidirish...")
        
        # JavaScript fayllar
        js_files = list(self.project_root.rglob("*.js")) + list(self.project_root.rglob("*.ts"))
        js_files.extend(list(self.project_root.rglob("*.jsx")) + list(self.project_root.rglob("*.tsx")))
        
        # CSS fayllar  
        css_files = list(self.project_root.rglob("*.css")) + list(self.project_root.rglob("*.scss"))
        css_files.extend(list(self.project_root.rglob("*.sass")) + list(self.project_root.rglob("*.less")))
        
        # HTML fayllar
        html_files = list(self.project_root.rglob("*.html")) + list(self.project_root.rglob("*.htm"))
        
        # Image fayllar
        image_extensions = ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.svg", "*.webp", "*.avif"]
        image_files = []
        for ext in image_extensions:
            image_files.extend(list(self.project_root.rglob(ext)))
        
        # Asset'larni katalog qilish
        all_files = {
            "javascript": js_files,
            "css": css_files,
            "html": html_files,
            "images": image_files
        }
        
        for file_type, files in all_files.items():
            for file_path in files:
                if file_path.is_file():
                    asset_info = AssetInfo(
                        path=str(file_path),
                        size=file_path.stat().st_size,
                        type=file_type,
                        hash=self._calculate_file_hash(file_path)
                    )
                    self.assets[str(file_path)] = asset_info
        
        logger.info(f"📊 Topilgan asset'lar: {len(self.assets)} ta")

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Fayl hashini hisoblash"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()[:12]
        except:
            return ""

    async def _optimize_javascript(self):
        """JavaScript optimizatsiyasi"""
        logger.info("⚡ JavaScript optimizatsiya boshlanmoqda...")
        
        js_assets = {k: v for k, v in self.assets.items() if v.type == "javascript"}
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_asset = {
                executor.submit(self._minify_js_file, k, v): k 
                for k, v in js_assets.items()
            }
            
            for future in as_completed(future_to_asset):
                asset_path = future_to_asset[future]
                try:
                    result = future.result()
                    if result:
                        self.assets[asset_path].optimized = True
                        logger.info(f"✅ Minify qilindi: {Path(asset_path).name}")
                except Exception as e:
                    logger.error(f"❌ JavaScript optimizatsiya xatosi {asset_path}: {str(e)}")

    def _minify_js_file(self, file_path: str, asset_info: AssetInfo) -> bool:
        """JavaScript faylni minify qilish"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # jsmin bilan minify
            if self.config.get("jsmin_minify", True):
                minified = jsmin.jsmin(original_content)
            else:
                # Standart minify
                minified = self._basic_js_minify(original_content)
            
            # Agar optimizatsiya yaxshilgan bo'lsa, faylni yozish
            if len(minified) < len(original_content) * 0.95:  # 5% yoki undan ko'proq kam
                backup_path = f"{file_path}.backup"
                if not os.path.exists(backup_path):
                    # Backup yaratish
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(original_content)
                
                # Optimizatsiya qilingan faylni yozish
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(minified)
                
                # Metrikalarni yangilash
                asset_info.size = len(minified.encode('utf-8'))
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"JavaScript minify xatosi {file_path}: {str(e)}")
            return False

    def _basic_js_minify(self, content: str) -> str:
        """Oddiy JavaScript minifikatsiya"""
        # Commentlarni olib tashlash
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Bo'sh joylarni kamaytirish
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r';\s*}', '}', content)
        content = re.sub(r'{\s*', '{', content)
        content = re.sub(r'}\s*', '}', content)
        content = re.sub(r'=\s*', '=', content)
        content = re.sub(r';\s*', ';', content)
        content = re.sub(r',\s*', ',', content)
        
        return content.strip()

    async def _optimize_css(self):
        """CSS optimizatsiya"""
        logger.info("🎨 CSS optimizatsiya boshlanmoqda...")
        
        css_assets = {k: v for k, v in self.assets.items() if v.type == "css"}
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_asset = {
                executor.submit(self._minify_css_file, k, v): k 
                for k, v in css_assets.items()
            }
            
            for future in as_completed(future_to_asset):
                asset_path = future_to_asset[future]
                try:
                    result = future.result()
                    if result:
                        self.assets[asset_path].optimized = True
                        logger.info(f"✅ CSS minify qilindi: {Path(asset_path).name}")
                except Exception as e:
                    logger.error(f"❌ CSS optimizatsiya xatosi {asset_path}: {str(e)}")

    def _minify_css_file(self, file_path: str, asset_info: AssetInfo) -> bool:
        """CSS faylni minify qilish"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Standart CSS minifikatsiya
            minified = self._basic_css_minify(original_content)
            
            # Agar optimizatsiya yaxshilgan bo'lsa
            if len(minified) < len(original_content) * 0.9:  # 10% yoki undan ko'proq kam
                # Backup yaratish
                backup_path = f"{file_path}.backup"
                if not os.path.exists(backup_path):
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(original_content)
                
                # Optimizatsiya qilingan faylni yozish
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(minified)
                
                asset_info.size = len(minified.encode('utf-8'))
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"CSS minify xatosi {file_path}: {str(e)}")
            return False

    def _basic_css_minify(self, content: str) -> str:
        """Oddiy CSS minifikatsiya"""
        # Commentlarni olib tashlash
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Bo'sh qatorlarni olib tashlash
        content = re.sub(r'\n+', ' ', content)
        content = re.sub(r'\r+', ' ', content)
        
        # Bo'sh joylarni minimal qilish
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r';\s*', ';', content)
        content = re.sub(r':\s*', ':', content)
        content = re.sub(r'{\s*', '{', content)
        content = re.sub(r'}\s*', '}', content)
        
        # Oxirgi ; olib tashlash
        content = re.sub(r';$', '', content)
        
        return content.strip()

    async def _optimize_html(self):
        """HTML optimizatsiya"""
        logger.info("📄 HTML optimizatsiya boshlanmoqda...")
        
        html_assets = {k: v for k, v in self.assets.items() if v.type == "html"}
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_to_asset = {
                executor.submit(self._minify_html_file, k, v): k 
                for k, v in html_assets.items()
            }
            
            for future in as_completed(future_to_asset):
                asset_path = future_to_asset[future]
                try:
                    result = future.result()
                    if result:
                        self.assets[asset_path].optimized = True
                        logger.info(f"✅ HTML minify qilindi: {Path(asset_path).name}")
                except Exception as e:
                    logger.error(f"❌ HTML optimizatsiya xatosi {asset_path}: {str(e)}")

    def _minify_html_file(self, file_path: str, asset_info: AssetInfo) -> bool:
        """HTML faylni minify qilish"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # HTML minifikatsiya
            minified = self._basic_html_minify(original_content)
            
            # Agar optimizatsiya yaxshilgan bo'lsa
            if len(minified) < len(original_content) * 0.95:  # 5% yoki undan ko'proq kam
                backup_path = f"{file_path}.backup"
                if not os.path.exists(backup_path):
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(original_content)
                
                # Optimizatsiya qilingan faylni yozish
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(minified)
                
                asset_info.size = len(minified.encode('utf-8'))
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"HTML minify xatosi {file_path}: {str(e)}")
            return False

    def _basic_html_minify(self, content: str) -> str:
        """Oddiy HTML minifikatsiya"""
        # Script va style tag'lar ichidagi commentlarni olib tashlash
        content = re.sub(r'(<!--.*?-->)', '', content, flags=re.DOTALL)
        
        # Bo'sh qatorlarni olib tashlash
        content = re.sub(r'\n+', ' ', content)
        content = re.sub(r'\r+', ' ', content)
        content = re.sub(r'\t+', ' ', content)
        
        # Bir nechta bo'sh joyni bitta qilish
        content = re.sub(r'>\s+<', '><', content)
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()

    async def _optimize_images(self):
        """Rasm optimizatsiya"""
        if not self.config.get("compress_images", True):
            return
            
        logger.info("🖼️  Rasm optimizatsiya boshlanmoqda...")
        
        image_assets = {k: v for k, v in self.assets.items() if v.type == "images"}
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_asset = {
                executor.submit(self._optimize_image_file, k, v): k 
                for k, v in image_assets.items()
            }
            
            for future in as_completed(future_to_asset):
                asset_path = future_to_asset[future]
                try:
                    result = future.result()
                    if result:
                        self.assets[asset_path].optimized = True
                        logger.info(f"✅ Rasm optimizatsiya qilindi: {Path(asset_path).name}")
                except Exception as e:
                    logger.error(f"❌ Rasm optimizatsiya xatosi {asset_path}: {str(e)}")

    def _optimize_image_file(self, file_path: str, asset_info: AssetInfo) -> bool:
        """Rasm faylini optimizatsiya qilish"""
        try:
            file_path = Path(file_path)
            
            # Backup yaratish
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            if not backup_path.exists():
                with open(file_path, 'rb') as src, open(backup_path, 'wb') as dst:
                    dst.write(src.read())
            
            # WebP konvertatsiya
            if self.config.get("webp_conversion", True) and file_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                self._convert_to_webp(file_path)
            
            # AVIF konvertatsiya (agar yoqilgan bo'lsa)
            if self.config.get("avif_conversion", True):
                self._convert_to_avif(file_path)
            
            # Size optimizatsiya
            self._compress_image(file_path, asset_info)
            
            return True
            
        except Exception as e:
            logger.error(f"Rasm optimizatsiya xatosi {file_path}: {str(e)}")
            return False

    def _convert_to_webp(self, file_path: Path):
        """Rasmni WebP formatga o'tkazish"""
        try:
            webp_path = file_path.with_suffix('.webp')
            if not webp_path.exists():
                with Image.open(file_path) as img:
                    quality = self.config.get("image_quality", 85)
                    img.save(webp_path, 'WebP', quality=quality, method=6)
                logger.info(f"WebP yaratildi: {webp_path}")
        except Exception as e:
            logger.error(f"WebP konvertatsiya xatosi {file_path}: {str(e)}")

    def _convert_to_avif(self, file_path: Path):
        """Rasmni AVIF formatga o'tkazish"""
        try:
            avif_path = file_path.with_suffix('.avif')
            if not avif_path.exists():
                with Image.open(file_path) as img:
                    quality = self.config.get("image_quality", 85)
                    # PIL AVIF ni qo'llab-quvvatlamasligi mumkin
                    # Shuning uchun sharp ishlatish kerak bo'lishi mumkin
                    try:
                        img.save(avif_path, 'AVIF', quality=quality)
                        logger.info(f"AVIF yaratildi: {avif_path}")
                    except Exception as e:
                        logger.warning(f"AVIF yaratilmadi {file_path}: {str(e)}")
        except Exception as e:
            logger.error(f"AVIF konvertatsiya xatosi {file_path}: {str(e)}")

    def _compress_image(self, file_path: Path, asset_info: AssetInfo):
        """Rasmni siqish"""
        try:
            with Image.open(file_path) as img:
                # EXIF ma'lumotlarini olib tashlash
                img = ImageOps.exif_transpose(img)
                
                # Quality optimizatsiya
                quality = self.config.get("image_quality", 85)
                
                # Faylni qayta saqlash
                img.save(file_path, quality=quality, optimize=True)
                
                # Yangilangan size
                asset_info.size = file_path.stat().st_size
                
        except Exception as e:
            logger.error(f"Rasm siqish xatosi {file_path}: {str(e)}")

    async def _create_optimized_bundles(self):
        """Optimizatsiya qilingan bundle'lar yaratish"""
        logger.info("📦 Bundle yaratish...")
        
        # Bundle konfiguratsiya yaratish
        await self._setup_bundle_configs()
        
        for bundle_name, bundle_config in self.bundles.items():
            try:
                await self._create_bundle(bundle_name, bundle_config)
                logger.info(f"✅ Bundle yaratildi: {bundle_name}")
            except Exception as e:
                logger.error(f"❌ Bundle yaratish xatosi {bundle_name}: {str(e)}")

    async def _setup_bundle_configs(self):
        """Bundle konfiguratsiyalarini sozlash"""
        # Asosiy JS bundle
        js_files = [k for k, v in self.assets.items() if v.type == "javascript"]
        
        # Asosiy CSS bundle
        css_files = [k for k, v in self.assets.items() if v.type == "css"]
        
        # Bundle'lar yaratish
        if js_files:
            self.bundles["main.js"] = BundleConfig(
                name="main.js",
                entry_files=js_files,
                output_path=str(self.project_root / "dist" / "js" / "main.js"),
                minify=self.config.get("minify_js", True)
            )
        
        if css_files:
            self.bundles["main.css"] = BundleConfig(
                name="main.css", 
                entry_files=css_files,
                output_path=str(self.project_root / "dist" / "css" / "main.css"),
                minify=self.config.get("minify_css", True)
            )

    async def _create_bundle(self, bundle_name: str, bundle_config: BundleConfig):
        """Bundle yaratish"""
        # Dist papka yaratish
        output_path = Path(bundle_config.output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Fayllarni birlashtirish
        bundle_content = ""
        for file_path in bundle_config.entry_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    bundle_content += f.read() + "\n"
            except Exception as e:
                logger.warning(f"Fayl o'qish xatosi {file_path}: {str(e)}")
        
        # Minifikatsiya
        if bundle_config.minify:
            if bundle_name.endswith('.js'):
                bundle_content = jsmin.jsmin(bundle_content)
            elif bundle_name.endswith('.css'):
                bundle_content = self._basic_css_minify(bundle_content)
        
        # Bundle faylini yozish
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(bundle_content)
        
        # Metrikalarni saqlash
        self.metrics["bundle_sizes"][bundle_name] = len(bundle_content.encode('utf-8'))

    async def _implement_lazy_loading(self):
        """Lazy loading qo'shish"""
        if not self.config.get("lazy_load_images", True):
            return
            
        logger.info("⏳ Lazy loading qo'shilmoqda...")
        
        # HTML fayllarni lazy loading bilan yangilash
        for file_path, asset_info in self.assets.items():
            if asset_info.type == "html":
                await self._add_lazy_loading_to_html(file_path)

    async def _add_lazy_loading_to_html(self, file_path: str):
        """HTML faylga lazy loading qo'shish"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Lazy loading atributlarini qo'shish
            # <img> tag'larga loading="lazy" qo'shish
            content = re.sub(
                r'<img([^>]*?)(?:\s+loading=[\'"]lazy[\'"])?([^>]*?)>',
                r'<img\1 loading="lazy"\2>',
                content,
                flags=re.IGNORECASE
            )
            
            # <iframe> tag'larga loading="lazy" qo'shish
            content = re.sub(
                r'<iframe([^>]*?)(?:\s+loading=[\'"]lazy[\'"])?([^>]*?)>',
                r'<iframe\1 loading="lazy"\2>',
                content,
                flags=re.IGNORECASE
            )
            
            # <video> tag'larga loading="lazy" qo'shish
            content = re.sub(
                r'<video([^>]*?)(?:\s+loading=[\'"]lazy[\'"])?([^>]*?)>',
                r'<video\1 loading="lazy"\2>',
                content,
                flags=re.IGNORECASE
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            logger.error(f"Lazy loading qo'shish xatosi {file_path}: {str(e)}")

    async def _inline_critical_css(self):
        """Critical CSS inline qilish"""
        if not self.config.get("critical_css_inline", True):
            return
            
        logger.info("🎯 Critical CSS inline qilinmoqda...")
        
        for file_path, asset_info in self.assets.items():
            if asset_info.type == "html":
                await self._add_critical_css_inline(file_path)

    async def _add_critical_css_inline(self, file_path: str):
        """HTML faylga critical CSS inline qilish"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Asosiy CSS faylni topish
            css_links = re.findall(r'<link[^>]*rel=["\']stylesheet["\'][^>]*>', content, re.IGNORECASE)
            
            # Critical CSS generatsiya (soddalashtirilgan)
            critical_css = """
            <style>
            /* Critical CSS - Above the fold */
            body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
            .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
            .header { background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .loading { display: none; }
            </style>
            """
            
            # Critical CSS ni head tag'ning boshiga qo'shish
            content = re.sub(
                r'<(/?)head([^>]*)>',
                r'<\1head\2>\n' + critical_css,
                content,
                flags=re.IGNORECASE
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            logger.error(f"Critical CSS inline xatosi {file_path}: {str(e)}")

    async def _prepare_http2_push(self):
        """HTTP/2 push uchun tayyorlash"""
        logger.info("🚀 HTTP/2 push hazirlanmoqda...")
        
        push_urls = []
        
        # Critical resurslarni to'plash
        for file_path, asset_info in self.assets.items():
            if asset_info.type in ["javascript", "css"]:
                relative_path = os.path.relpath(file_path, self.project_root)
                push_urls.append(f"/{relative_path}")
        
        # Push manifest yaratish
        push_manifest = {
            "urls": push_urls,
            "priority": "high",
            "purpose": "preload"
        }
        
        manifest_path = self.cache_dir / "http2_push_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(push_manifest, f, indent=2)
        
        logger.info(f"HTTP/2 push manifest yaratildi: {manifest_path}")

    async def _generate_performance_report(self):
        """Performance hisoboti yaratish"""
        logger.info("📊 Performance hisoboti yaratilmoqda...")
        
        # Metrikalarni to'plash
        total_original_size = sum(asset.size for asset in self.assets.values())
        total_optimized_size = sum(
            asset.size for asset in self.assets.values() if asset.optimized
        )
        
        if total_original_size > 0:
            optimization_ratio = (total_original_size - total_optimized_size) / total_original_size
        else:
            optimization_ratio = 0
        
        # Hisobot
        report = {
            "summary": {
                "total_assets": len(self.assets),
                "optimized_assets": sum(1 for asset in self.assets.values() if asset.optimized),
                "original_size": total_original_size,
                "optimized_size": total_optimized_size,
                "size_reduction": optimization_ratio,
                "estimated_load_time_improvement": f"{optimization_ratio * 100:.1f}%"
            },
            "asset_types": {},
            "bundles": self.metrics["bundle_sizes"],
            "recommendations": self._generate_recommendations()
        }
        
        # Asset type'lari bo'yicha statistika
        for asset_type in ["javascript", "css", "html", "images"]:
            type_assets = [asset for asset in self.assets.values() if asset.type == asset_type]
            if type_assets:
                report["asset_types"][asset_type] = {
                    "count": len(type_assets),
                    "total_size": sum(asset.size for asset in type_assets),
                    "optimized_count": sum(1 for asset in type_assets if asset.optimized)
                }
        
        # Hisobotni saqlash
        report_path = self.cache_dir / "performance_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.metrics.update(report)
        logger.info(f"Performance hisoboti saqlandi: {report_path}")

    def _generate_recommendations(self) -> List[str]:
        """Tavsiyalar yaratish"""
        recommendations = []
        
        # Bundle size tavsiyalari
        for bundle_name, bundle_size in self.metrics["bundle_sizes"].items():
            if bundle_size > self.config.get("max_bundle_size", 500 * 1024):
                recommendations.append(
                    f"Bundleni bo'lish tavsiya etiladi {bundle_name} ({bundle_size / 1024:.1f}KB > "
                    f"{self.config.get('max_bundle_size', 500 * 1024) / 1024:.1f}KB)"
                )
        
        # Lazy loading tavsiyalari
        unoptimized_images = sum(
            1 for asset in self.assets.values() 
            if asset.type == "images" and not asset.optimized
        )
        if unoptimized_images > 0:
            recommendations.append(
                f"{unoptimized_images} ta optimizatsiya qilinmagan rasm topildi"
            )
        
        # Compression tavsiyalari
        if self.config.get("enable_gzip", True):
            recommendations.append("Gzip compression yoqilgan - yaxshi!")
        else:
            recommendations.append("Gzip compression yoqish tavsiya etiladi")
        
        # CDN tavsiyalari
        recommendations.append("CDN ishlatish tezkor yuklashni yaxshilaydi")
        recommendations.append("Browser caching sozlash tavsiya etiladi")
        
        return recommendations

    def get_optimization_status(self) -> Dict:
        """Optimizatsiya holatini olish"""
        return {
            "total_assets": len(self.assets),
            "optimized_assets": sum(1 for asset in self.assets.values() if asset.optimized),
            "optimization_ratio": sum(
                1 for asset in self.assets.values() if asset.optimized
            ) / len(self.assets) if self.assets else 0,
            "bundles": len(self.bundles),
            "cache_dir": str(self.cache_dir)
        }

# CLI interface
async def main():
    """Asosiy funksiya"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Speed Optimizer - Tezlik optimizatori")
    parser.add_argument("--project-root", required=True, help="Loyiha ildiz papka")
    parser.add_argument("--config", help="Konfiguratsiya fayl yo'li")
    parser.add_argument("--output", help="Hisobot fayl yo'li")
    
    args = parser.parse_args()
    
    # Konfiguratsiya yuklash
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Optimizator yaratish
    optimizer = SpeedOptimizer(args.project_root, config)
    
    # Optimizatsiya o'tkazish
    try:
        metrics = await optimizer.optimize_project()
        
        # Natijani ko'rsatish
        print("\n🚀 TEZLIK OPTIMIZATSIYASI NATIJASI:")
        print("=" * 50)
        print(f"Umumiy asset'lar: {metrics['summary']['total_assets']}")
        print(f"Optimizatsiya qilingan: {metrics['summary']['optimized_assets']}")
        print(f"Hajm kamayishi: {metrics['summary']['size_reduction']*100:.1f}%")
        print(f"Yuklash vaqt yaxshilanishi: {metrics['summary']['estimated_load_time_improvement']}")
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)
            print(f"Hisobot saqlandi: {args.output}")
        
    except Exception as e:
        logger.error(f"Optimizatsiya xatosi: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    asyncio.run(main())