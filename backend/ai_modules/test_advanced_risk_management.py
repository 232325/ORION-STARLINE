#!/usr/bin/env python3
"""
Advanced Risk Management System - Test va Demo Script
=====================================================

Bu script Advanced Risk Management tizimini test qilish va demo qilish
uchun ishlatiladi.

Author: Orion Starline AI Trading System
Date: 2025-11-05
Version: 1.0.0
"""

import asyncio
import sys
import os
import json
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add parent directory to path
sys.path.append('/workspace/orion-starline/backend')
sys.path.append('/workspace/orion-starline/backend/ai_modules')

# Import our modules
try:
    from advanced_risk_management import (
        AdvancedRiskManager,
        Position,
        RiskLevel,
        RiskType,
        Alert,
        create_sample_positions,
        demo_advanced_risk_management
    )
except ImportError as e:
    print(f"Import xatoligi: {e}")
    print("advanced_risk_management.py fayli mavjudligini tekshiring")
    sys.exit(1)


class RiskManagementTester:
    """Risk Management tizimi test class"""
    
    def __init__(self):
        self.risk_manager = AdvancedRiskManager()
        self.test_results = []
        self.performance_metrics = {}
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Barcha testlarni o'tkazish"""
        print("🧪 Advanced Risk Management System Test Suite")
        print("=" * 60)
        
        test_suites = [
            ("Basic Risk Scoring", self.test_basic_risk_scoring),
            ("Portfolio Stress Testing", self.test_portfolio_stress_testing),
            ("VaR Calculations", self.test_var_calculations),
            ("Risk Controls", self.test_risk_controls),
            ("Liquidity Assessment", self.test_liquidity_assessment),
            ("Credit Risk", self.test_credit_risk),
            ("Regulatory Compliance", self.test_regulatory_compliance),
            ("Alert System", self.test_alert_system),
            ("Database Operations", self.test_database_operations),
            ("Real-time Monitoring", self.test_real_time_monitoring)
        ]
        
        for test_name, test_func in test_suites:
            print(f"\n📋 {test_name}")
            print("-" * 40)
            
            try:
                start_time = datetime.now()
                result = await test_func()
                end_time = datetime.now()
                
                execution_time = (end_time - start_time).total_seconds() * 1000
                
                test_result = {
                    'test_name': test_name,
                    'status': 'PASS' if result.get('passed', False) else 'FAIL',
                    'execution_time_ms': execution_time,
                    'details': result,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.test_results.append(test_result)
                
                status_icon = "✅" if test_result['status'] == 'PASS' else "❌"
                print(f"{status_icon} Test tugallandi: {test_result['status']} ({execution_time:.2f}ms)")
                
                if 'message' in result:
                    print(f"   Xabar: {result['message']}")
                
            except Exception as e:
                error_result = {
                    'test_name': test_name,
                    'status': 'ERROR',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                
                self.test_results.append(error_result)
                print(f"❌ Test xatoligi: {e}")
        
        # Test natijalarini ko'rsatish
        await self._display_test_summary()
        
        # Test report yaratish
        await self._generate_test_report()
        
        return {
            'total_tests': len(self.test_results),
            'passed': len([r for r in self.test_results if r['status'] == 'PASS']),
            'failed': len([r for r in self.test_results if r['status'] == 'FAIL']),
            'errors': len([r for r in self.test_results if r['status'] == 'ERROR']),
            'results': self.test_results
        }
    
    async def test_basic_risk_scoring(self) -> Dict[str, Any]:
        """Basic risk scoring test"""
        try:
            # Test positions
            positions = create_sample_positions()
            
            # Calculate risk score
            risk_score, risk_level = self.risk_manager.risk_scorer.get_risk_score(
                positions, {}, {}, {}, {}
            )
            
            # Basic validations
            assert isinstance(risk_score, (int, float)), "Risk score float bo'lishi kerak"
            assert 0 <= risk_score <= 1, "Risk score 0-1 oralig'ida bo'lishi kerak"
            assert isinstance(risk_level, RiskLevel), "Risk level to'g'ri enum bo'lishi kerak"
            
            return {
                'passed': True,
                'risk_score': risk_score,
                'risk_level': risk_level.value,
                'message': f"Risk scoring ishlayapti. Score: {risk_score:.3f}, Level: {risk_level.value}"
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'message': f"Risk scoring test xatoligi: {e}"
            }
    
    async def test_portfolio_stress_testing(self) -> Dict[str, Any]:
        """Portfolio stress testing test"""
        try:
            positions = create_sample_positions()
            
            # Run stress test
            stress_results = self.risk_manager.stress_tester.run_full_stress_test(positions)
            
            # Validations
            assert 'scenarios' in stress_results, "Stress test natijalari mavjud emas"
            assert len(stress_results['scenarios']) > 0, "Hech qanday scenario yo'q"
            
            # Check scenario results
            scenario_count = len(stress_results['scenarios'])
            total_loss = sum([
                s.get('total_loss', 0) for s in stress_results['scenarios'].values()
            ])
            
            return {
                'passed': True,
                'scenarios_tested': scenario_count,
                'total_loss': total_loss,
                'message': f"Stress test muvaffaqiyatli. {scenario_count} scenario test qilindi."
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'message': f"Stress test xatoligi: {e}"
            }
    
    async def test_var_calculations(self) -> Dict[str, Any]:
        """VaR calculations test"""
        try:
            positions = create_sample_positions()
            
            # Create sample returns data
            import pandas as pd
            returns_data = pd.DataFrame({
                'AAPL': np.random.normal(0.001, 0.025, 252),
                'GOOGL': np.random.normal(0.001, 0.030, 252),
                'US10Y': np.random.normal(0.0002, 0.005, 252),
                'EURUSD': np.random.normal(0.0001, 0.012, 252),
                'GOLD': np.random.normal(0.0005, 0.020, 252)
            })
            
            # Calculate VaR
            var_results = self.risk_manager.var_calculator.calculate_portfolio_var(
                positions, returns_data
            )
            
            # Validations
            assert isinstance(var_results, dict), "VaR natijalari dict bo'lishi kerak"
            assert 'historical_var' in var_results, "Historical VaR yo'q"
            assert var_results['historical_var'] >= 0, "Historical VaR manfiy bo'lishi mumkin emas"
            
            return {
                'passed': True,
                'var_95': var_results.get('historical_var', 0),
                'var_99': var_results.get('parametric_var', 0),
                'expected_shortfall': var_results.get('expected_shortfall', 0),
                'message': "VaR hisoblash ishlayapti"
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'message': f"VaR calculation xatoligi: {e}"
            }
    
    async def test_risk_controls(self) -> Dict[str, Any]:
        """Risk controls test"""
        try:
            positions = create_sample_positions()
            
            # Test position limits
            position_limits_check = self.risk_manager.risk_controls.check_position_limits(
                positions, {}
            )
            
            # Test stop loss rules for first position
            if positions:
                first_position = positions[0]
                stop_loss_rule = self.risk_manager.risk_controls.setup_stop_loss_rules(
                    first_position, stop_loss_percentage=0.05
                )
                
                stop_loss_check = self.risk_manager.risk_controls.check_stop_loss(
                    first_position, first_position.price * 0.95  # Simulate price drop
                )
            
            # Validations
            assert 'violations' in position_limits_check, "Position limits check natijasi yo'q"
            assert isinstance(position_limits_check['violations'], list), "Violations list bo'lishi kerak"
            
            return {
                'passed': True,
                'position_violations': len(position_limits_check['violations']),
                'stop_loss_setup': stop_loss_rule is not None,
                'message': "Risk controls ishlayapti"
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'message': f"Risk controls xatoligi: {e}"
            }
    
    async def test_liquidity_assessment(self) -> Dict[str, Any]:
        """Liquidity assessment test"""
        try:
            positions = create_sample_positions()
            
            # Sample liquidity data
            liquidity_data = {
                'AAPL': {'bid': 149.5, 'ask': 150.5, 'mid_price': 150.0, 'bid_depth': 50000, 'ask_depth': 55000},
                'GOOGL': {'bid': 1995.0, 'ask': 2005.0, 'mid_price': 2000.0, 'bid_depth': 10000, 'ask_depth': 12000}
            }
            
            # Assess portfolio liquidity
            liquidity_assessment = self.risk_manager.liquidity_analyzer.assess_portfolio_liquidity(
                positions, liquidity_data
            )
            
            # Validations
            assert 'portfolio_liquidity' in liquidity_assessment, "Portfolio liquidity ma'lumotlari yo'q"
            
            portfolio_liq = liquidity_assessment['portfolio_liquidity']
            assert 'overall_liquidity_score' in portfolio_liq, "Overall liquidity score yo'q"
            assert 0 <= portfolio_liq['overall_liquidity_score'] <= 1, "Liquidity score noto'g'ri oraliqda"
            
            return {
                'passed': True,
                'liquidity_score': portfolio_liq['overall_liquidity_score'],
                'liquidity_level': portfolio_liq.get('liquidity_risk_level', 'UNKNOWN'),
                'message': "Liquidity assessment ishlayapti"
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'message': f"Liquidity assessment xatoligi: {e}"
            }
    
    async def test_credit_risk(self) -> Dict[str, Any]:
        """Credit risk test"""
        try:
            positions = create_sample_positions()
            
            # Sample credit data
            credit_data = {
                'AAPL': {'credit_rating': 'AA+', 'financial_metrics': {'debt_to_equity': 0.5}},
                'GOOGL': {'credit_rating': 'AA', 'financial_metrics': {'debt_to_equity': 0.3}}
            }
            
            # Assess portfolio credit risk
            credit_assessment = self.risk_manager.credit_evaluator.assess_portfolio_credit_risk(
                positions, credit_data
            )
            
            # Validations
            assert 'portfolio_credit_risk' in credit_assessment, "Portfolio credit risk ma'lumotlari yo'q"
            
            portfolio_credit = credit_assessment['portfolio_credit_risk']
            assert 'total_credit_exposure' in portfolio_credit, "Total credit exposure yo'q"
            assert portfolio_credit['total_credit_exposure'] > 0, "Total exposure 0 dan katta bo'lishi kerak"
            
            return {
                'passed': True,
                'total_exposure': portfolio_credit['total_credit_exposure'],
                'expected_loss': portfolio_credit.get('expected_credit_loss', 0),
                'counterparties': portfolio_credit.get('number_of_counterparties', 0),
                'message': "Credit risk assessment ishlayapti"
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'message': f"Credit risk xatoligi: {e}"
            }
    
    async def test_regulatory_compliance(self) -> Dict[str, Any]:
        """Regulatory compliance test"""
        try:
            positions = create_sample_positions()
            
            # Sample capital data
            capital_data = {
                'tier_1_capital': 5000000,
                'total_capital': 6000000,
                'high_quality_liquid_assets': 2000000,
                'net_cash_outflows_30d': 1500000
            }
            
            # Basel III compliance
            basel_compliance = self.risk_manager.compliance_checker.check_basel_iii_compliance(
                positions, None, capital_data
            )
            
            # MiFID II compliance
            trading_data = {
                'transparent_orders': 95,
                'total_orders': 100,
                'execution_quality_score': 0.85,
                'reported_transactions': 98,
                'total_transactions': 100
            }
            
            mifid_compliance = self.risk_manager.compliance_checker.check_mifid_ii_compliance(
                trading_data
            )
            
            # Validations
            assert 'overall_compliant' in basel_compliance, "Basel III compliance ma'lumotlari yo'q"
            assert 'overall_compliant' in mifid_compliance, "MiFID II compliance ma'lumotlari yo'q"
            
            return {
                'passed': True,
                'basel_iii_compliant': basel_compliance['overall_compliant'],
                'mifid_ii_compliant': mifid_compliance['overall_compliant'],
                'message': "Regulatory compliance ishlayapti"
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'message': f"Regulatory compliance xatoligi: {e}"
            }
    
    async def test_alert_system(self) -> Dict[str, Any]:
        """Alert system test"""
        try:
            # Create test alert
            test_alert = Alert(
                alert_id=f"test_alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                risk_type=RiskType.MARKET,
                level=RiskLevel.HIGH,
                message="Test alert message",
                metric_value=0.75,
                threshold=0.60
            )
            
            # Add alert to dashboard
            self.risk_manager.dashboard.add_alert(test_alert)
            
            # Get active alerts
            active_alerts = self.risk_manager.dashboard.get_active_alerts()
            
            # Generate alert report
            alert_report = self.risk_manager.dashboard.generate_alert_report()
            
            # Validations
            assert len(active_alerts) > 0, "Active alerts topilmadi"
            assert 'total_active_alerts' in alert_report, "Alert report ma'lumotlari yo'q"
            assert test_alert.alert_id in [a.alert_id for a in active_alerts], "Test alert topilmadi"
            
            return {
                'passed': True,
                'active_alerts_count': len(active_alerts),
                'alert_report_generated': True,
                'test_alert_present': test_alert.alert_id in [a.alert_id for a in active_alerts],
                'message': "Alert system ishlayapti"
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'message': f"Alert system xatoligi: {e}"
            }
    
    async def test_database_operations(self) -> Dict[str, Any]:
        """Database operations test"""
        try:
            from advanced_risk_management import RiskMetrics
            
            # Create test metrics
            test_metrics = RiskMetrics(
                portfolio_value=1000000,
                var_1d=50000,
                var_5d=100000,
                var_10d=150000,
                expected_shortfall=60000,
                sharpe_ratio=1.2,
                max_drawdown=0.08,
                beta=1.1,
                alpha=0.02,
                volatility=0.15,
                concentration_risk=0.25,
                liquidity_score=0.85,
                timestamp=datetime.now()
            )
            
            # Insert metrics
            self.risk_manager.db.insert_risk_metrics(test_metrics)
            
            # Retrieve metrics
            recent_metrics = self.risk_manager.db.get_recent_risk_metrics(days=1)
            
            # Validations
            assert len(recent_metrics) > 0, "Hech qanday metrics topilmadi"
            assert recent_metrics[0].portfolio_value == test_metrics.portfolio_value, "Portfolio value mos emas"
            
            return {
                'passed': True,
                'metrics_stored': len(recent_metrics),
                'portfolio_value_match': recent_metrics[0].portfolio_value == test_metrics.portfolio_value,
                'message': "Database operations ishlayapti"
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'message': f"Database operations xatoligi: {e}"
            }
    
    async def test_real_time_monitoring(self) -> Dict[str, Any]:
        """Real-time monitoring test"""
        try:
            # Start monitoring
            self.risk_manager.start_real_time_monitoring(update_interval=1)  # 1 soniya
            
            # Wait a bit for monitoring to run
            await asyncio.sleep(3)
            
            # Check system status
            status = self.risk_manager.get_system_status()
            
            # Stop monitoring
            self.risk_manager.stop_real_time_monitoring()
            
            # Validations
            assert 'is_running' in status, "System status ma'lumotlari yo'q"
            assert 'monitoring_active' in status, "Monitoring status ma'lumotlari yo'q"
            assert isinstance(status['is_running'], bool), "is_running boolean bo'lishi kerak"
            
            return {
                'passed': True,
                'monitoring_started': status['monitoring_active'],
                'monitoring_stopped': not status['is_running'],
                'system_status': status,
                'message': "Real-time monitoring ishlayapti"
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'message': f"Real-time monitoring xatoligi: {e}"
            }
    
    async def _display_test_summary(self):
        """Test natijalarini ko'rsatish"""
        print("\n" + "=" * 60)
        print("📊 Test Natijalari Xulosasi")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed = len([r for r in self.test_results if r['status'] == 'FAIL'])
        errors = len([r for r in self.test_results if r['status'] == 'ERROR'])
        
        print(f"Umumiy testlar: {total_tests}")
        print(f"✅ Muvaffaqiyatli: {passed}")
        print(f"❌ Muvaffaqiyatsiz: {failed}")
        print(f"⚠️ Xatoliklar: {errors}")
        print(f"📈 Muvaffaqiyat darajasi: {(passed/total_tests)*100:.1f}%")
        
        # Performance metrics
        if self.test_results:
            execution_times = [r.get('execution_time_ms', 0) for r in self.test_results if 'execution_time_ms' in r]
            if execution_times:
                avg_time = np.mean(execution_times)
                max_time = max(execution_times)
                min_time = min(execution_times)
                
                print(f"\n⏱️ Performance:")
                print(f"   O'rtacha vaqt: {avg_time:.2f}ms")
                print(f"   maksimal vaqt: {max_time:.2f}ms")
                print(f"   minimal vaqt: {min_time:.2f}ms")
        
        # Failed tests
        failed_tests = [r for r in self.test_results if r['status'] == 'FAIL']
        if failed_tests:
            print(f"\n❌ Muvaffaqiyatsiz testlar:")
            for test in failed_tests:
                print(f"   - {test['test_name']}: {test.get('message', 'Noma\'lum xato')}")
        
        # Errors
        error_tests = [r for r in self.test_results if r['status'] == 'ERROR']
        if error_tests:
            print(f"\n⚠️ Xatolikli testlar:")
            for test in error_tests:
                print(f"   - {test['test_name']}: {test.get('error', 'Noma\'lum xato')}")
    
    async def _generate_test_report(self):
        """Test report yaratish"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"/workspace/orion-starline/backend/reports/risk_management_test_report_{timestamp}.json"
        
        report_data = {
            'report_metadata': {
                'report_id': f"TEST_REPORT_{timestamp}",
                'generated_at': datetime.now().isoformat(),
                'test_suite': 'Advanced Risk Management System',
                'version': '1.0.0'
            },
            'test_summary': {
                'total_tests': len(self.test_results),
                'passed': len([r for r in self.test_results if r['status'] == 'PASS']),
                'failed': len([r for r in self.test_results if r['status'] == 'FAIL']),
                'errors': len([r for r in self.test_results if r['status'] == 'ERROR']),
                'success_rate': len([r for r in self.test_results if r['status'] == 'PASS']) / len(self.test_results) * 100
            },
            'test_results': self.test_results,
            'system_info': {
                'python_version': sys.version,
                'numpy_version': np.__version__,
                'platform': sys.platform
            }
        }
        
        try:
            os.makedirs(os.path.dirname(report_filename), exist_ok=True)
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str, ensure_ascii=False)
            
            print(f"\n📋 Test report saqlandi: {report_filename}")
            
        except Exception as e:
            print(f"\n❌ Test report saqlashda xato: {e}")


async def main():
    """Asosiy funksiya"""
    print("🚀 Advanced Risk Management System - Test va Demo")
    print("=" * 60)
    
    try:
        # Tester yaratish
        tester = RiskManagementTester()
        
        # Barcha testlarni o'tkazish
        results = await tester.run_all_tests()
        
        print(f"\n🎯 Test natijasi: {results['passed']}/{results['total_tests']} muvaffaqiyatli")
        
        if results['failed'] == 0 and results['errors'] == 0:
            print("✅ Barcha testlar muvaffaqiyatli o'tdi!")
            return True
        else:
            print("⚠️ Ba'zi testlar muvaffaqiyatsiz bo'ldi")
            return False
            
    except Exception as e:
        print(f"❌ Test suite ishga tushishda xato: {e}")
        return False


if __name__ == "__main__":
    # Test va demo ishga tushirish
    success = asyncio.run(main())
    
    if success:
        print("\n🎉 Advanced Risk Management tizimi test qilindi!")
    else:
        print("\n💥 Test qilishda muammolar bor")
        sys.exit(1)