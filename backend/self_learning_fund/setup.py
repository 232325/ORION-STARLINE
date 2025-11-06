#!/usr/bin/env python3
"""
Self-Learning Trading Fund Setup Script

Ushbu script tizimni o'rnatish va sozlab olish uchun yordam beradi.
"""

import os
import sys
import subprocess
import yaml
from pathlib import Path
import argparse


def check_python_version():
    """Python versiyasini tekshirish"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 yoki undan yuqori versiyasi kerak!")
        print(f"Hozirgi versiyasi: {sys.version}")
        sys.exit(1)
    print(f"✅ Python versiyasi: {sys.version}")


def create_virtual_environment(venv_path="venv"):
    """Virtual environment yaratish"""
    venv_path = Path(venv_path)
    
    if venv_path.exists():
        print(f"⚠️  {venv_path} papkasi mavjud. Mavjud environment o'chirilsinmi? (y/n): ", end="")
        response = input().lower().strip()
        if response == 'y':
            import shutil
            shutil.rmtree(venv_path)
        else:
            print("Mavjud environment ishlatiladi.")
            return venv_path
    
    print("📦 Virtual environment yaratilmoqda...")
    subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
    print(f"✅ Virtual environment yaratildi: {venv_path}")
    return venv_path


def install_requirements(venv_path, requirements_file="requirements.txt"):
    """Kerakli paketlarni o'rnatish"""
    venv_path = Path(venv_path)
    
    # Pip path
    if os.name == 'nt':  # Windows
        pip_path = venv_path / "Scripts" / "pip"
    else:  # Linux/Mac
        pip_path = venv_path / "bin" / "pip"
    
    print("📥 Kerakli paketlar o'rnatilmoqda...")
    
    # Upgrade pip first
    subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
    
    # Install requirements
    if Path(requirements_file).exists():
        subprocess.run([str(pip_path), "install", "-r", requirements_file], check=True)
        print("✅ Barcha paketlar muvaffaqiyatli o'rnatildi!")
    else:
        print(f"⚠️  {requirements_file} fayli topilmadi. Core paketlar o'rnatilmoqda...")
        core_packages = [
            "numpy>=1.21.0",
            "pandas>=1.3.0",
            "torch>=1.12.0",
            "scikit-learn>=1.0.0",
            "pyyaml>=6.0",
            "matplotlib>=3.5.0",
            "yfinance>=0.1.70"
        ]
        for package in core_packages:
            subprocess.run([str(pip_path), "install", package], check=True)
        print("✅ Core paketlar o'rnatildi!")


def setup_configuration():
    """Konfiguratsiya fayllarini sozlash"""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # Konfiguratsiya fayllari nomlari
    config_files = [
        ("system_config.yaml", "Tizim konfiguratsiyasi"),
        ("model_config.yaml", "Model konfiguratsiyasi"),
        ("trading_config.yaml", "Trading konfiguratsiyasi")
    ]
    
    print("\n📋 Konfiguratsiya sozlamalari:")
    print("=" * 50)
    
    for filename, description in config_files:
        config_path = config_dir / filename
        example_path = config_dir / f"{filename}.example"
        
        if not config_path.exists() and not example_path.exists():
            print(f"⚠️  {filename} topilmadi ({description})")
            continue
        
        # Example faylni asosiy faylga ko'chiramiz
        if example_path.exists() and not config_path.exists():
            import shutil
            shutil.copy(example_path, config_path)
            print(f"✅ {filename} yaratildi ({description})")
        elif config_path.exists():
            print(f"ℹ️  {filename} mavjud ({description})")
    
    print("\n📝 Konfiguratsiya yo'riqnoma:")
    print("1. config/system_config.yaml - Tizim sozlamalari")
    print("2. config/model_config.yaml - Model parametrlari")  
    print("3. config/trading_config.yaml - Trading qoidalari")
    print("\n💡 Fayllarni tahrirlab o'zingizga moslang!")


def create_directory_structure():
    """Loyiha papkalarini yaratish"""
    directories = [
        "logs",
        "data",
        "models",
        "reports",
        "backups",
        "tests",
        "docs",
        "examples/data"
    ]
    
    print("\n📁 Loyiha struktura yaratilmoqda:")
    
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # .gitkeep faylini yaratish (agar git loyihasi bo'lsa)
        if (Path(".git").exists()):
            gitkeep = dir_path / ".gitkeep"
            if not gitkeep.exists():
                gitkeep.touch()
        
        print(f"  ✅ {directory}/")
    
    print("\n✅ Loyiha struktura tayyorlandi!")


def setup_environment_file():
    """Environment variables faylini yaratish"""
    env_file = Path(".env")
    
    if env_file.exists():
        print(f"ℹ️  {env_file} mavjud")
        return
    
    env_template = """# Self-Learning Trading Fund Environment Variables

# API Keys (kerak bo'lsa to'ldiring)
YAHOO_FINANCE_API_KEY=
OANDA_API_KEY=
BINANCE_API_KEY=
BLOOMBERG_API_KEY=

# Database Configuration
DATABASE_URL=sqlite:///data/trading.db
REDIS_URL=redis://localhost:6379/0

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=
EMAIL_PASSWORD=

# Telegram Bot
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Monitoring
MLFLOW_TRACKING_URI=sqlite:///mlflow.db
WANDB_PROJECT=trading-fund

# Security
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here

# Development
DEBUG=False
LOG_LEVEL=INFO
"""
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_template)
    
    print(f"✅ {env_file} yaratildi!")
    print("💡 API kalitlari va boshqa muhit o'zgaruvchilarini to'ldiring!")


def create_gitignore():
    """Gitignore faylini yaratish"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# Environment Variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
logs/
*.log

# Data
data/raw/
data/processed/
*.csv
*.xlsx
*.json

# Models
models/*.pth
models/*.pt
models/*.pkl

# Reports
reports/*.pdf
reports/*.html

# Cache
.cache/
.pytest_cache/
.mypy_cache/

# OS
.DS_Store
Thumbs.db

# Secrets
secrets/
*.key
*.pem

# Backups
backups/*.zip
backups/*.tar.gz

# Jupyter
.ipynb_checkpoints

# MLflow
mlruns/
.mlflow/

# Tensorboard
logs/

# Coverage
htmlcov/
.coverage
coverage.xml

# Temporary files
tmp/
temp/
"""
    
    gitignore_path = Path(".gitignore")
    with open(gitignore_path, 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    print("✅ .gitignore yaratildi!")


def run_tests():
    """Testlarni ishga tushirish"""
    print("\n🧪 Testlar ishga tushirilmoqda...")
    
    try:
        # Asosiy import test
        test_imports = """
try:
    import numpy as np
    import pandas as pd
    import torch
    import sklearn
    import yaml
    print("✅ Barcha asosiy paketlar muvaffaqiyatli import qilindi!")
except ImportError as e:
    print(f"❌ Import xatosi: {e}")
    sys.exit(1)
"""
        
        exec(test_imports)
        print("✅ Import testlari muvaffaqiyatli!")
        
    except Exception as e:
        print(f"❌ Test xatosi: {e}")
        return False
    
    return True


def create_quick_start_script():
    """Tezkor boshlanish scriptini yaratish"""
    script_content = '''#!/usr/bin/env python3
"""
Quick Start Script for Self-Learning Trading Fund
Tezkor boshlanish uchun
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def main():
    print("🚀 Self-Learning Trading Fund - Tezkor Demo")
    print("=" * 50)
    
    try:
        # Import demo
        from examples.main_demo import main as demo_main
        
        print("\\nDemo ishga tushirilmoqda...")
        await demo_main()
        
    except ImportError as e:
        print(f"❌ Import xatosi: {e}")
        print("💡 Iltimos, barcha paketlar o'rnatilganligini tekshiring:")
        print("   pip install -r requirements.txt")
        
    except Exception as e:
        print(f"❌ Demo xatosi: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    script_path = Path("quick_start.py")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ quick_start.py yaratildi!")


def print_next_steps():
    """Keyingi qadamlarni ko'rsatish"""
    print("\n" + "=" * 60)
    print("🎉 SOZLAMALAR MUVAFFAQIYATLI TUGALLANDI!")
    print("=" * 60)
    
    print("\n📋 KEYINGI QADAMLAR:")
    print("1. 📝 Konfiguratsiya fayllarini tahrirlang:")
    print("   - config/system_config.yaml")
    print("   - config/model_config.yaml")
    print("   - config/trading_config.yaml")
    
    print("\n2. 🔑 API kalitlarini o'rnating (kerak bo'lsa):")
    print("   - .env faylini oching")
    print("   - API kalitlarni qo'shing")
    
    print("\n3. 🚀 Demo ishga tushiring:")
    print("   python quick_start.py")
    print("   # yoki")
    print("   python examples/main_demo.py")
    
    print("\n4. 📚 Qo'shimcha ma'lumot:")
    print("   - README.md faylini o'qib chiqing")
    print("   - config/ papkasidagi barcha sozlamalarni ko'ring")
    print("   - examples/ papkasidagi demo fayllarni tekshiring")
    
    print("\n💡 MASLAHATLAR:")
    print("   - Development muhitida ishlash uchun paper trading ni yoqish")
    print("   - Real trading dan oldin backtesting qiling")
    print("   - Risk management sozlamalarini ehtiyotkorlik bilan o'rnating")


def main():
    """Asosiy setup funksiyasi"""
    parser = argparse.ArgumentParser(description="Self-Learning Trading Fund Setup")
    parser.add_argument("--venv", default="venv", help="Virtual environment papkasi")
    parser.add_argument("--requirements", default="requirements.txt", help="Requirements fayli")
    parser.add_argument("--skip-deps", action="store_true", help="Dependencies o'rnatishni o'tkazib ketish")
    parser.add_argument("--skip-tests", action="store_true", help="Testlarni o'tkazib ketish")
    
    args = parser.parse_args()
    
    print("🤖 Self-Learning Trading Fund Setup")
    print("=" * 50)
    
    # 1. Python versiyasini tekshirish
    check_python_version()
    
    # 2. Virtual environment yaratish
    venv_path = create_virtual_environment(args.venv)
    
    # 3. Dependencies o'rnatish
    if not args.skip_deps:
        install_requirements(venv_path, args.requirements)
    
    # 4. Directory structure yaratish
    create_directory_structure()
    
    # 5. Konfiguratsiya setup
    setup_configuration()
    
    # 6. Environment file yaratish
    setup_environment_file()
    
    # 7. Gitignore yaratish
    create_gitignore()
    
    # 8. Quick start script yaratish
    create_quick_start_script()
    
    # 9. Testlarni ishga tushirish
    if not args.skip_tests:
        if not run_tests():
            print("⚠️  Ba'zi testlar muvaffaqiyatsiz tugallandi, lekin setup davom etdi.")
    
    # 10. Keyingi qadamlarni ko'rsatish
    print_next_steps()
    
    print("\n🎯 Setup tugallandi! Baraka toping!")


if __name__ == "__main__":
    main()