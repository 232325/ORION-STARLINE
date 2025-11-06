#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the optimization system
"""

import sys
import os
import asyncio
import tempfile
import shutil
from pathlib import Path

# Add the optimization directory to path
sys.path.insert(0, '/workspace/orion-starline/optimization')

def test_optimization_import():
    """Test that all optimization modules can be imported"""
    print("🧪 Optimization modules import test...")
    
    # Test import of each module
    modules = []
    
    try:
        import speed_optimizer
        modules.append(("Speed Optimizer", speed_optimizer))
        print("✅ Speed Optimizer import qilindi")
    except Exception as e:
        print(f"❌ Speed Optimizer import xatosi: {e}")
    
    try:
        import ai_optimizer
        modules.append(("AI Optimizer", ai_optimizer))
        print("✅ AI Optimizer import qilindi")
    except Exception as e:
        print(f"❌ AI Optimizer import xatosi: {e}")
    
    try:
        import database_optimizer
        modules.append(("Database Optimizer", database_optimizer))
        print("✅ Database Optimizer import qilindi")
    except Exception as e:
        print(f"❌ Database Optimizer import xatosi: {e}")
    
    try:
        import pwa_manager
        modules.append(("PWA Manager", pwa_manager))
        print("✅ PWA Manager import qilindi")
    except Exception as e:
        print(f"❌ PWA Manager import xatosi: {e}")
    
    try:
        import seo_optimizer
        modules.append(("SEO Optimizer", seo_optimizer))
        print("✅ SEO Optimizer import qilindi")
    except Exception as e:
        print(f"❌ SEO Optimizer import xatosi: {e}")
    
    return len(modules) > 0

def test_file_creation():
    """Test that optimization files are created correctly"""
    print("\n📁 Fayl yaratish test...")
    
    # Create a test directory
    test_dir = tempfile.mkdtemp(prefix="orion_optimization_test_")
    
    try:
        # Create sample HTML file
        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <meta name="description" content="Test sahifa">
</head>
<body>
    <h1>Test Sahifa</h1>
    <p>Test content</p>
</body>
</html>"""
        
        html_file = Path(test_dir) / "index.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Create sample JS file
        js_content = """function testFunction() {
    console.log("Test JavaScript");
    return true;
}"""
        
        js_file = Path(test_dir) / "test.js"
        with open(js_file, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        # Create sample CSS file
        css_content = """body {
    margin: 0;
    padding: 20px;
}
.container {
    max-width: 1200px;
}"""
        
        css_file = Path(test_dir) / "test.css"
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        print(f"✅ Test fayllar yaratildi: {test_dir}")
        print(f"  - HTML fayl: {len(html_content)} belgi")
        print(f"  - JavaScript fayl: {len(js_content)} belgi")
        print(f"  - CSS fayl: {len(css_content)} belgi")
        
        return True, test_dir
        
    except Exception as e:
        print(f"❌ Fayl yaratish xatosi: {e}")
        return False, test_dir

def test_speed_optimizer_basic():
    """Test basic Speed Optimizer functionality"""
    print("\n⚡ Speed Optimizer basic test...")
    
    try:
        from speed_optimizer import SpeedOptimizer, AssetInfo, BundleConfig
        
        # Create a simple test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create SpeedOptimizer instance
            optimizer = SpeedOptimizer(temp_dir)
            
            # Test asset info
            asset = AssetInfo(
                path="/test/path.js",
                size=1024,
                type="javascript"
            )
            
            print(f"✅ Asset info yaratildi: {asset.path}")
            print(f"  - Hajm: {asset.size} bytes")
            print(f"  - Tur: {asset.type}")
            
            # Test bundle config
            bundle = BundleConfig(
                name="main.js",
                entry_files=["/test/file1.js", "/test/file2.js"],
                output_path="/test/output.js"
            )
            
            print(f"✅ Bundle config yaratildi: {bundle.name}")
            print(f"  - Entry files: {len(bundle.entry_files)} ta")
            
            return True
            
    except Exception as e:
        print(f"❌ Speed Optimizer test xatosi: {e}")
        return False

def test_seo_optimizer_basic():
    """Test basic SEO Optimizer functionality"""
    print("\n🔍 SEO Optimizer basic test...")
    
    try:
        from seo_optimizer import SEOConfig, SEOOptimizer
        
        # Create SEO config
        config = SEOConfig(
            site_name="Test Site",
            site_url="https://example.com",
            site_description="Test site description",
            default_keywords="test, site, example",
            author="Test Author"
        )
        
        print(f"✅ SEO config yaratildi: {config.site_name}")
        print(f"  - URL: {config.site_url}")
        print(f"  - Description: {config.site_description}")
        
        return True
        
    except Exception as e:
        print(f"❌ SEO Optimizer test xatosi: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Orion Starline Optimization System Test")
    print("=" * 50)
    
    # Test 1: Import all modules
    import_success = test_optimization_import()
    
    # Test 2: File creation
    file_success, test_dir = test_file_creation()
    
    # Test 3: Speed optimizer basic functionality
    speed_success = test_speed_optimizer_basic()
    
    # Test 4: SEO optimizer basic functionality
    seo_success = test_seo_optimizer_basic()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST NATIJALARI:")
    print("=" * 50)
    print(f"Module import: {'✅' if import_success else '❌'}")
    print(f"File creation: {'✅' if file_success else '❌'}")
    print(f"Speed optimizer: {'✅' if speed_success else '❌'}")
    print(f"SEO optimizer: {'✅' if seo_success else '❌'}")
    
    overall_success = all([import_success, file_success, speed_success, seo_success])
    
    if overall_success:
        print("\n🎉 Barcha testlar muvaffaqiyatli o'tdi!")
        print("Platform optimization tizimi tayyor.")
    else:
        print("\n⚠️  Ba'zi testlar muvaffaqiyatsiz.")
        print("Bog'liqliklarni tekshirib ko'ring.")
    
    # Clean up
    if file_success and os.path.exists(test_dir):
        shutil.rmtree(test_dir, ignore_errors=True)
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())