#!/usr/bin/env python3
"""
AI Trading System - Comprehensive Test Runner
Barcha testlarni bajarish va hisobot tayyorlash
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime
import argparse

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

class TestRunner:
    """Test boshqaruvchisi"""
    
    def __init__(self, test_dir: str = None):
        self.test_dir = test_dir or os.path.dirname(os.path.abspath(__file__))
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_suites": [],
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": 0,
                "success_rate": 0.0
            }
        }
    
    def run_single_test_file(self, test_file: str, verbose: bool = False) -> dict:
        """Bitta test faylini bajarish"""
        print(f"🔍 Test fayl: {test_file}")
        
        cmd = ["python", "-m", "pytest", test_file, "-v", "--tb=short"]
        if not verbose:
            cmd.append("-q")
        
        try:
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.test_dir
            )
            end_time = time.time()
            
            # Parse pytest output
            output_lines = result.stdout.split('\n')
            test_summary = self._parse_pytest_output(output_lines)
            
            test_result = {
                "file": os.path.basename(test_file),
                "status": "passed" if result.returncode == 0 else "failed",
                "duration": round(end_time - start_time, 2),
                "output": result.stdout,
                "error_output": result.stderr if result.stderr else "",
                "summary": test_summary
            }
            
            if result.returncode == 0:
                print(f"✅ {os.path.basename(test_file)} - O'TDI")
            else:
                print(f"❌ {os.path.basename(test_file)} - XATO")
            
            return test_result
            
        except Exception as e:
            print(f"💥 {os.path.basename(test_file)} - EXCEPTION: {e}")
            return {
                "file": os.path.basename(test_file),
                "status": "error",
                "error": str(e),
                "duration": 0,
                "output": "",
                "error_output": "",
                "summary": {}
            }
    
    def _parse_pytest_output(self, output_lines: list) -> dict:
        """Pytest natijasini tahlil qilish"""
        summary = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0
        }
        
        # Find summary line
        for line in output_lines:
            if "passed" in line or "failed" in line:
                # Example: "5 passed, 2 failed in 1.23s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed" and i > 0:
                        try:
                            summary["passed"] = int(parts[i-1])
                        except:
                            pass
                    elif part == "failed" and i > 0:
                        try:
                            summary["failed"] = int(parts[i-1])
                        except:
                            pass
                    elif part == "skipped" and i > 0:
                        try:
                            summary["skipped"] = int(parts[i-1])
                        except:
                            pass
                    elif part == "error" and i > 0:
                        try:
                            summary["errors"] = int(parts[i-1])
                        except:
                            pass
        
        summary["total"] = (summary["passed"] + summary["failed"] + 
                          summary["skipped"] + summary["errors"])
        
        return summary
    
    def run_all_tests(self, verbose: bool = False) -> dict:
        """Barcha testlarni bajarish"""
        print("🧪 AI Trading System - API Test Runner")
        print("=" * 60)
        
        # Find all test files
        test_files = []
        for root, dirs, files in os.walk(self.test_dir):
            for file in files:
                if file.startswith("test_") and file.endswith(".py"):
                    test_files.append(os.path.join(root, file))
        
        if not test_files:
            print("⚠️  Test fayllar topilmadi!")
            return self.results
        
        print(f"📁 {len(test_files)} ta test fayl topildi")
        print("-" * 60)
        
        # Run each test file
        for test_file in test_files:
            result = self.run_single_test_file(test_file, verbose)
            self.results["test_suites"].append(result)
            
            # Update summary
            summary = result.get("summary", {})
            self.results["summary"]["total_tests"] += summary.get("total", 0)
            self.results["summary"]["passed"] += summary.get("passed", 0)
            self.results["summary"]["failed"] += summary.get("failed", 0)
            self.results["summary"]["skipped"] += summary.get("skipped", 0)
            self.results["summary"]["errors"] += summary.get("errors", 0)
        
        # Calculate success rate
        total_tests = self.results["summary"]["total_tests"]
        if total_tests > 0:
            self.results["summary"]["success_rate"] = round(
                (self.results["summary"]["passed"] / total_tests) * 100, 2
            )
        
        return self.results
    
    def print_summary(self):
        """Test natijalarini chiqarish"""
        summary = self.results["summary"]
        
        print("\n" + "=" * 60)
        print("📊 TEST NATIJALARI")
        print("=" * 60)
        print(f"📅 Vaqt: {self.results['timestamp']}")
        print(f"📁 Test suits: {len(self.results['test_suites'])}")
        print(f"📋 Jami testlar: {summary['total_tests']}")
        print(f"✅ Muvaffaqiyatli: {summary['passed']}")
        print(f"❌ Muvaffaqiyatsiz: {summary['failed']}")
        print(f"⏭️  Skip qilingan: {summary['skipped']}")
        print(f"💥 Xatolar: {summary['errors']}")
        print(f"📈 Muvaffaqiyat darajasi: {summary['success_rate']}%")
        
        # Success indicator
        if summary['success_rate'] == 100:
            print("🎉 BARCHA TESTLAR MUVAFFAQIYATLI O'TDI!")
        elif summary['success_rate'] >= 90:
            print("👍 Yuqori muvaffaqiyat darajasi!")
        elif summary['success_rate'] >= 70:
            print("⚠️  O'rta muvaffaqiyat darajasi")
        else:
            print("🔴 Past muvaffaqiyat darajasi - tekshirish kerak!")
        
        # Failed tests summary
        failed_tests = [suite for suite in self.results["test_suites"] if suite["status"] != "passed"]
        if failed_tests:
            print("\n❌ XATOLAR:")
            for test in failed_tests:
                print(f"  - {test['file']}: {test.get('error', 'Unknown error')}")
    
    def save_report(self, filename: str = None):
        """Test hisobotini faylga saqlash"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.json"
        
        report_path = os.path.join(self.test_dir, filename)
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Hisobot saqlandi: {report_path}")
        except Exception as e:
            print(f"❌ Hisobot saqlashda xato: {e}")
    
    def run_specific_test(self, test_name: str, verbose: bool = False):
        """Ma'lum test nomi bo'yicha testni bajarish"""
        test_files = []
        for root, dirs, files in os.walk(self.test_dir):
            for file in files:
                if file.startswith("test_") and file.endswith(".py") and test_name in file:
                    test_files.append(os.path.join(root, file))
        
        if not test_files:
            print(f"⚠️  '{test_name}' nomli test topilmadi!")
            return
        
        print(f"🔍 '{test_name}' testlarini bajarish:")
        for test_file in test_files:
            self.run_single_test_file(test_file, verbose)
        
        self.print_summary()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI Trading System Test Runner")
    parser.add_argument("--test", "-t", help="Ma'lum test nomi")
    parser.add_argument("--verbose", "-v", action="store_true", help=" batafsil chiqish")
    parser.add_argument("--save", "-s", help="Hisobot fayl nomi")
    parser.add_argument("--dir", "-d", help="Test papkasi yo'li")
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = TestRunner(test_dir=args.dir)
    
    print("🚀 AI Trading System API Test Runner")
    print("⚡ Test boshlanmoqda...")
    
    if args.test:
        runner.run_specific_test(args.test, args.verbose)
    else:
        runner.run_all_tests(args.verbose)
    
    runner.print_summary()
    
    if args.save:
        runner.save_report(args.save)
    
    print("\n✅ Test runner tugadi!")

if __name__ == "__main__":
    main()