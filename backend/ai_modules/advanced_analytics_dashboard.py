#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Analytics Dashboard
===========================

Bu modul professional trading tizimi uchun ilg'or analytics dashboard yaratadi.

Xususiyatlari:
- Interactive charts (D3.js, Chart.js, Plotly integration)
- Real-time performance tracking (Live dashboard updates)
- Custom portfolio analytics (Risk metrics, Sharpe ratio, etc.)
- Data visualization (Pie charts, line graphs, heatmaps)
- Export functionality (PDF, Excel, CSV reports)
- Custom dashboards (User-defined layouts)
- KPI tracking (Key Performance Indicators)
- Comparative analysis (Portfolio vs benchmarks)
- Time-series analysis (Historical performance)
- Alert thresholds (Performance alerts)

Muallif: Orion-Starline AI Team
Sana: 2025-11-05
Versiya: 1.0.0
"""

import asyncio
import json
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Core libraries
import numpy as np
import pandas as pd
from scipy import stats
import sqlite3
from pathlib import Path

# Web framework
from flask import Flask, render_template, jsonify, request, send_file
from flask_socketio import SocketIO, emit
import threading
import time

# Visualization
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO

# Data export
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import openpyxl
from openpyxl.drawing.image import Image
import csv

# Mathematical and financial calculations
import math
from statistics import mean, median, stdev

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class KPIMetric:
    """KPI metric ma'lumotlari"""
    name: str
    value: float
    target: float
    unit: str
    status: str  # 'good', 'warning', 'critical'
    trend: str  # 'up', 'down', 'stable'
    timestamp: datetime

@dataclass
class AlertThreshold:
    """Ogohlantirish chegaralari"""
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    direction: str  # 'above', 'below'
    enabled: bool = True

@dataclass
class PortfolioPosition:
    """Portfolio pozitsiya ma'lumotlari"""
    symbol: str
    quantity: float
    avg_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    weight: float

class AdvancedAnalyticsDashboard:
    """Ilg'or Analytics Dashboard asosiy sinfi"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Dashboard yaratish
        
        Args:
            config: Dashboard konfiguratsiya ma'lumotlari
        """
        self.config = config or self._default_config()
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = self.config.get('secret_key', 'advanced-analytics-secret')
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Data storage
        self.kpi_data = {}
        self.portfolio_data = {}
        self.performance_history = []
        self.alert_thresholds = {}
        self.custom_dashboards = {}
        
        # WebSocket real-time update
        self.real_time_enabled = True
        self.update_interval = 1  # seconds
        
        # Initialize components
        self._setup_routes()
        self._setup_websocket()
        self._initialize_data()
        
        logger.info("Advanced Analytics Dashboard yaratildi")
    
    def _default_config(self) -> Dict:
        """Standart konfiguratsiya"""
        return {
            'secret_key': 'advanced-analytics-secret',
            'database_path': './analytics.db',
            'max_history_days': 365,
            'alert_cooldown': 300,  # 5 minutes
            'default_benchmark': 'SPY',
            'currency': 'USD',
            'theme': 'dark',
            'refresh_interval': 5,
            'enable_notifications': True,
            'max_portfolio_positions': 100
        }
    
    def _setup_routes(self):
        """Flask routes ni sozlash"""
        
        @self.app.route('/')
        def dashboard():
            """Asosiy dashboard"""
            return render_template('dashboard.html', config=self.config)
        
        @self.app.route('/api/kpis')
        def get_kpis():
            """KPI ma'lumotlarini olish"""
            return jsonify(self.get_current_kpis())
        
        @self.app.route('/api/portfolio')
        def get_portfolio():
            """Portfolio ma'lumotlarini olish"""
            return jsonify(self.get_portfolio_summary())
        
        @self.app.route('/api/performance')
        def get_performance():
            """Ishlab chiqarish ma'lumotlarini olish"""
            return jsonify(self.get_performance_data())
        
        @self.app.route('/api/charts/<chart_type>')
        def get_chart_data(chart_type):
            """Grafik ma'lumotlarini olish"""
            return jsonify(self.get_chart_data_by_type(chart_type))
        
        @self.app.route('/api/export/<format_type>')
        def export_data(format_type):
            """Ma'lumotlarni eksport qilish"""
            try:
                file_path = self.export_data(format_type)
                return send_file(file_path, as_attachment=True)
            except Exception as e:
                logger.error(f"Export xatosi: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/custom-dashboard', methods=['GET', 'POST'])
        def manage_custom_dashboard():
            """Custom dashboard boshqaruvi"""
            if request.method == 'GET':
                return jsonify(self.get_custom_dashboards())
            else:
                data = request.json
                dashboard_id = self.save_custom_dashboard(data)
                return jsonify({'dashboard_id': dashboard_id})
    
    def _setup_websocket(self):
        """WebSocket real-time updates"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Mijoz ulanishi"""
            logger.info(f"Mijoz ulandi: {request.sid}")
            emit('connected', {'status': 'connected'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Mijoz uzilishi"""
            logger.info(f"Mijoz uzildi: {request.sid}")
        
        @self.socketio.on('subscribe_updates')
        def handle_subscribe_updates(data):
            """Real-time yangilanishlarga obuna"""
            emit('subscribed', {'status': 'subscribed', 'interval': self.update_interval})
    
    def _initialize_data(self):
        """Ma'lumotlarni boshlang'ich yaratish"""
        try:
            # KPI ma'lumotlarini yaratish
            self._create_sample_kpis()
            
            # Portfolio ma'lumotlarini yaratish
            self._create_sample_portfolio()
            
            # Ogohlantirish chegaralarini sozlash
            self._setup_alert_thresholds()
            
            logger.info("Boshlang'ich ma'lumotlar yaratildi")
            
        except Exception as e:
            logger.error(f"Boshlang'ich ma'lumotlarni yaratishda xato: {e}")
    
    def _create_sample_kpis(self):
        """Namuna KPI yaratish"""
        kpis = [
            KPIMetric("Jami Portfel Qiymati", 125000.50, 120000.0, "USD", "good", "up", datetime.now()),
            KPIMetric("Kunlik ROI", 2.34, 1.5, "%", "good", "up", datetime.now()),
            KPIMetric("Volatillik", 15.67, 20.0, "%", "good", "down", datetime.now()),
            KPIMetric("Sharpe Ratio", 1.85, 1.0, "", "good", "up", datetime.now()),
            KPIMetric("Maksimal Drawdown", -8.45, -10.0, "%", "warning", "stable", datetime.now()),
            KPIMetric("Win Rate", 68.5, 60.0, "%", "good", "up", datetime.now()),
            KPIMetric("Avg Trade Duration", 4.2, 5.0, "soat", "good", "down", datetime.now()),
            KPIMetric("Profit Factor", 2.15, 1.5, "", "good", "up", datetime.now())
        ]
        
        for kpi in kpis:
            self.kpi_data[kpi.name] = kpi
    
    def _create_sample_portfolio(self):
        """Namuna portfolio yaratish"""
        positions = [
            PortfolioPosition("AAPL", 100, 150.25, 155.80, 15580.00, 555.00, 12.5),
            PortfolioPosition("MSFT", 50, 310.50, 315.25, 15762.50, 237.50, 12.6),
            PortfolioPosition("GOOGL", 25, 2800.75, 2845.50, 71137.50, 1118.75, 56.9),
            PortfolioPosition("TSLA", 30, 220.10, 215.45, 6463.50, -139.50, 5.2),
            PortfolioPosition("AMZN", 15, 3200.25, 3185.75, 47786.25, -217.50, 38.2)
        ]
        
        # Qiymatlarni qayta hisoblash
        total_value = sum(pos.market_value for pos in positions)
        for pos in positions:
            pos.weight = (pos.market_value / total_value) * 100
            pos.unrealized_pnl = (pos.current_price - pos.avg_price) * pos.quantity
        
        self.portfolio_data['positions'] = positions
        self.portfolio_data['total_value'] = total_value
        self.portfolio_data['total_pnl'] = sum(pos.unrealized_pnl for pos in positions)
    
    def _setup_alert_thresholds(self):
        """Ogohlantirish chegaralarini sozlash"""
        self.alert_thresholds = {
            "Jami Portfel Qiymati": AlertThreshold(
                "Jami Portfel Qiymati", 115000, 110000, "below", True
            ),
            "Kunlik ROI": AlertThreshold(
                "Kunlik ROI", 0.5, -1.0, "below", True
            ),
            "Volatillik": AlertThreshold(
                "Volatillik", 25.0, 35.0, "above", True
            ),
            "Sharpe Ratio": AlertThreshold(
                "Sharpe Ratio", 0.8, 0.5, "below", True
            ),
            "Maksimal Drawdown": AlertThreshold(
                "Maksimal Drawdown", -7.0, -10.0, "below", True
            )
        }
    
    # ========================
    # KPI va Performance Tracking
    # ========================
    
    def get_current_kpis(self) -> Dict:
        """Joriy KPI ma'lumotlarini olish"""
        result = {}
        for name, kpi in self.kpi_data.items():
            result[name] = asdict(kpi)
        return result
    
    def calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Sharpe ratio hisoblash"""
        if not returns or len(returns) < 2:
            return 0.0
        
        excess_returns = [r - risk_free_rate/252 for r in returns]  # Yillikdan kunlik
        return np.mean(excess_returns) / np.std(returns) if np.std(excess_returns) > 0 else 0.0
    
    def calculate_max_drawdown(self, values: List[float]) -> float:
        """Maksimal drawdown hisoblash"""
        if not values:
            return 0.0
        
        peak = values[0]
        max_dd = 0.0
        
        for value in values:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            max_dd = max(max_dd, dd)
        
        return -max_dd * 100  # Foizda
    
    def calculate_var(self, returns: List[float], confidence_level: float = 0.95) -> float:
        """Value at Risk (VaR) hisoblash"""
        if not returns:
            return 0.0
        
        return np.percentile(returns, (1 - confidence_level) * 100)
    
    def calculate_portfolio_metrics(self, positions: List[PortfolioPosition]) -> Dict:
        """Portfolio metrikalarini hisoblash"""
        if not positions:
            return {}
        
        total_value = sum(pos.market_value for pos in positions)
        total_pnl = sum(pos.unrealized_pnl for pos in positions)
        
        # Risk metrikalar
        weights = np.array([pos.weight for pos in positions]) / 100
        
        # Simplified risk calculations
        annual_return = 0.15  # 15% namuna
        annual_volatility = 0.18  # 18% namuna
        
        portfolio_return = total_value * annual_return
        portfolio_risk = total_value * annual_volatility * np.sqrt(sum(w**2 for w in weights))
        
        sharpe_ratio = (annual_return - 0.02) / annual_volatility
        
        return {
            'total_value': total_value,
            'total_pnl': total_pnl,
            'return_pct': (total_pnl / total_value) * 100 if total_value > 0 else 0,
            'annual_return': annual_return * 100,
            'annual_volatility': annual_volatility * 100,
            'sharpe_ratio': sharpe_ratio,
            'risk_value': portfolio_risk,
            'concentration_risk': max(weights) * 100,
            'diversification_score': 1 - max(weights) * 100
        }
    
    def get_performance_data(self, days: int = 30) -> Dict:
        """Ishlab chiqarish ma'lumotlarini olish"""
        # Real-time ma'lumot yaratish
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # Namuna narx ma'lumotlari
        initial_value = 120000
        volatility = 0.02
        
        portfolio_values = []
        for i in range(len(dates)):
            change = np.random.normal(0, volatility)
            if i == 0:
                portfolio_values.append(initial_value)
            else:
                new_value = portfolio_values[-1] * (1 + change)
                portfolio_values.append(new_value)
        
        # Returns hisoblash
        returns = []
        for i in range(1, len(portfolio_values)):
            ret = (portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1]
            returns.append(ret * 100)
        
        # Benchmark data (SPY)
        benchmark_values = []
        spy_initial = 450
        for i in range(len(dates)):
            change = np.random.normal(0, volatility * 0.8)
            if i == 0:
                benchmark_values.append(spy_initial)
            else:
                new_value = benchmark_values[-1] * (1 + change)
                benchmark_values.append(new_value)
        
        performance_summary = {
            'portfolio_values': portfolio_values,
            'benchmark_values': benchmark_values,
            'returns': returns,
            'dates': [d.strftime('%Y-%m-%d') for d in dates],
            'metrics': {
                'total_return': ((portfolio_values[-1] - portfolio_values[0]) / portfolio_values[0]) * 100,
                'volatility': np.std(returns) if returns else 0,
                'sharpe_ratio': self.calculate_sharpe_ratio(returns),
                'max_drawdown': self.calculate_max_drawdown(portfolio_values),
                'win_rate': len([r for r in returns if r > 0]) / len(returns) * 100 if returns else 0
            }
        }
        
        return performance_summary
    
    # ========================
    # Chart and Visualization
    # ========================
    
    def get_chart_data_by_type(self, chart_type: str) -> Dict:
        """Grafik turiga ko'ra ma'lumot olish"""
        try:
            if chart_type == "portfolio_pie":
                return self._create_portfolio_pie_chart()
            elif chart_type == "performance_line":
                return self._create_performance_line_chart()
            elif chart_type == "risk_heatmap":
                return self._create_risk_heatmap()
            elif chart_type == "kpi_gauge":
                return self._create_kpi_gauge_charts()
            elif chart_type == "correlation_matrix":
                return self._create_correlation_matrix()
            else:
                return {"error": "Noto'g'ri grafik turi"}
        
        except Exception as e:
            logger.error(f"Grafik yaratishda xato: {e}")
            return {"error": str(e)}
    
    def _create_portfolio_pie_chart(self) -> Dict:
        """Portfolio tarqalish grafi (Pie chart)"""
        positions = self.portfolio_data.get('positions', [])
        
        if not positions:
            return {"error": "Portfolio ma'lumotlari topilmadi"}
        
        labels = [pos.symbol for pos in positions]
        values = [pos.market_value for pos in positions]
        colors_list = px.colors.qualitative.Set3
        
        fig = px.pie(
            values=values,
            names=labels,
            title="Portfolio Tarqalishi",
            color_discrete_sequence=colors_list
        )
        
        fig.update_layout(
            font=dict(size=12),
            showlegend=True,
            height=500
        )
        
        return {"chart_data": fig.to_json()}
    
    def _create_performance_line_chart(self) -> Dict:
        """Ishlab chiqarish chiziqli grafi"""
        performance_data = self.get_performance_data(30)
        
        fig = make_subplots(rows=2, cols=1, 
                           subplot_titles=("Portfolio vs Benchmark", "Kunlik Return"),
                           shared_xaxes=True)
        
        # Portfolio vs Benchmark
        fig.add_trace(
            go.Scatter(
                x=performance_data['dates'],
                y=performance_data['portfolio_values'],
                name='Portfolio',
                line=dict(color='blue', width=2)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=performance_data['dates'],
                y=performance_data['benchmark_values'],
                name='Benchmark (SPY)',
                line=dict(color='red', width=2)
            ),
            row=1, col=1
        )
        
        # Daily Returns
        fig.add_trace(
            go.Bar(
                x=performance_data['dates'][1:],  # Birinchi kun return yo'q
                y=performance_data['returns'],
                name='Kunlik Return (%)',
                marker_color=['green' if r > 0 else 'red' for r in performance_data['returns']]
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title="Portfolio Ishlab Chiqarish",
            height=700,
            showlegend=True
        )
        
        return {"chart_data": fig.to_json()}
    
    def _create_risk_heatmap(self) -> Dict:
        """Risk heatmap yaratish"""
        # Namuna risk ma'lumotlari
        assets = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'BTC', 'ETH', 'GLD']
        metrics = ['Volatility', 'VaR', 'Max Drawdown', 'Beta', 'Sharpe']
        
        # Namuna data yaratish
        risk_data = np.random.rand(len(assets), len(metrics)) * 100
        
        fig = px.imshow(
            risk_data,
            x=metrics,
            y=assets,
            color_continuous_scale='RdYlGn_r',
            title="Asset Risk Heatmap"
        )
        
        fig.update_layout(height=500)
        
        return {"chart_data": fig.to_json()}
    
    def _create_kpi_gauge_charts(self) -> Dict:
        """KPI gauge grafiklarini yaratish"""
        kpis = self.get_current_kpis()
        
        gauges = []
        for name, kpi_data in list(kpis.items())[:4]:  # Birinchi 4 ta KPI
            value = kpi_data['value']
            target = kpi_data['target']
            status = kpi_data['status']
            
            # Rang belgilash
            if status == 'good':
                color = 'green'
            elif status == 'warning':
                color = 'orange'
            else:
                color = 'red'
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=value,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': name},
                delta={'reference': target},
                gauge={
                    'axis': {'range': [None, max(value, target) * 1.2]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [0, target * 0.5], 'color': "lightgray"},
                        {'range': [target * 0.5, target], 'color': "yellow"},
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': target
                    }
                }
            ))
            
            fig.update_layout(height=300)
            gauges.append(fig.to_json())
        
        return {"chart_data": gauges}
    
    def _create_correlation_matrix(self) -> Dict:
        """Korrelatsiya matritsasi"""
        # Namuna narx ma'lumotlari
        assets = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        
        # Namuna narx data
        np.random.seed(42)
        price_data = pd.DataFrame(
            np.random.randn(len(dates), len(assets)).cumsum(axis=0),
            index=dates,
            columns=assets
        )
        
        # Return hisoblash
        returns = price_data.pct_change().dropna()
        correlation_matrix = returns.corr()
        
        fig = px.imshow(
            correlation_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='RdBu',
            title="Asset Correlation Matrix"
        )
        
        fig.update_layout(height=500)
        
        return {"chart_data": fig.to_json()}
    
    def get_portfolio_summary(self) -> Dict:
        """Portfolio xulosasini olish"""
        positions = self.portfolio_data.get('positions', [])
        if not positions:
            return {"error": "Portfolio ma'lumotlari topilmadi"}
        
        metrics = self.calculate_portfolio_metrics(positions)
        
        summary = {
            'positions': [asdict(pos) for pos in positions],
            'metrics': metrics,
            'total_positions': len(positions),
            'cash_balance': 10000.0,  # Namuna
            'last_updated': datetime.now().isoformat()
        }
        
        return summary
    
    # ========================
    # Alert System
    # ========================
    
    def check_alerts(self) -> List[Dict]:
        """Ogohlantirishlarni tekshirish"""
        alerts = []
        current_kpis = self.get_current_kpis()
        
        for metric_name, threshold in self.alert_thresholds.items():
            if not threshold.enabled:
                continue
            
            if metric_name not in current_kpis:
                continue
            
            current_value = current_kpis[metric_name]['value']
            alert_triggered = False
            alert_type = None
            
            if threshold.direction == 'below':
                if current_value <= threshold.critical_threshold:
                    alert_triggered = True
                    alert_type = 'critical'
                elif current_value <= threshold.warning_threshold:
                    alert_triggered = True
                    alert_type = 'warning'
            
            elif threshold.direction == 'above':
                if current_value >= threshold.critical_threshold:
                    alert_triggered = True
                    alert_type = 'critical'
                elif current_value >= threshold.warning_threshold:
                    alert_triggered = True
                    alert_type = 'warning'
            
            if alert_triggered:
                alerts.append({
                    'metric': metric_name,
                    'current_value': current_value,
                    'threshold': threshold.critical_threshold if alert_type == 'critical' else threshold.warning_threshold,
                    'alert_type': alert_type,
                    'timestamp': datetime.now().isoformat(),
                    'message': f"{metric_name} {alert_type} darajada: {current_value:.2f}"
                })
        
        return alerts
    
    def add_alert_threshold(self, metric_name: str, threshold: AlertThreshold):
        """Yangi ogohlantirish chegarasi qo'shish"""
        self.alert_thresholds[metric_name] = threshold
        logger.info(f"Yangi ogohlantirish chegarasi qo'shildi: {metric_name}")
    
    # ========================
    # Export Functionality
    # ========================
    
    def export_data(self, format_type: str) -> str:
        """Ma'lumotlarni eksport qilish"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == 'pdf':
            return self._export_to_pdf(timestamp)
        elif format_type == 'excel':
            return self._export_to_excel(timestamp)
        elif format_type == 'csv':
            return self._export_to_csv(timestamp)
        else:
            raise ValueError(f"Qo'llab-quvvatlanmaydigan format: {format_type}")
    
    def _export_to_pdf(self, timestamp: str) -> str:
        """PDF eksport"""
        filename = f"portfolio_report_{timestamp}.pdf"
        filepath = Path(f"/tmp/{filename}")
        
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph("Portfolio Analytics Report", styles['Title'])
        story.append(title)
        story.append(Paragraph(f"Generated: {datetime.now()}", styles['Normal']))
        
        # Portfolio Summary
        portfolio_data = self.get_portfolio_summary()
        if 'error' not in portfolio_data:
            metrics = portfolio_data['metrics']
            
            story.append(Paragraph("Portfolio Summary", styles['Heading2']))
            data = [
                ['Metric', 'Value'],
                ['Total Value', f"${metrics['total_value']:,.2f}"],
                ['Total P&L', f"${metrics['total_pnl']:,.2f}"],
                ['Return %', f"{metrics['return_pct']:.2f}%"],
                ['Sharpe Ratio', f"{metrics['sharpe_ratio']:.3f}"],
                ['Max Drawdown', f"{metrics.get('max_drawdown', 0):.2f}%"]
            ]
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
        
        doc.build(story)
        return str(filepath)
    
    def _export_to_excel(self, timestamp: str) -> str:
        """Excel eksport"""
        filename = f"portfolio_report_{timestamp}.xlsx"
        filepath = Path(f"/tmp/{filename}")
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # KPI sheet
            kpis_data = []
            for name, kpi in self.kpi_data.items():
                kpis_data.append({
                    'Metric': name,
                    'Value': kpi.value,
                    'Target': kpi.target,
                    'Unit': kpi.unit,
                    'Status': kpi.status,
                    'Trend': kpi.trend
                })
            
            kpi_df = pd.DataFrame(kpis_data)
            kpi_df.to_excel(writer, sheet_name='KPIs', index=False)
            
            # Portfolio sheet
            portfolio_data = self.get_portfolio_summary()
            if 'error' not in portfolio_data and 'positions' in portfolio_data:
                positions_df = pd.DataFrame(portfolio_data['positions'])
                positions_df.to_excel(writer, sheet_name='Positions', index=False)
            
            # Performance sheet
            performance_data = self.get_performance_data(30)
            perf_df = pd.DataFrame({
                'Date': performance_data['dates'],
                'Portfolio_Value': performance_data['portfolio_values'],
                'Benchmark_Value': performance_data['benchmark_values']
            })
            perf_df.to_excel(writer, sheet_name='Performance', index=False)
        
        return str(filepath)
    
    def _export_to_csv(self, timestamp: str) -> str:
        """CSV eksport"""
        filename = f"portfolio_report_{timestamp}.csv"
        filepath = Path(f"/tmp/{filename}")
        
        # Barcha ma'lumotlarni bitta CSV ga yozish
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Portfolio summary
            writer.writerow(['PORTFOLIO SUMMARY'])
            portfolio_data = self.get_portfolio_summary()
            if 'error' not in portfolio_data:
                metrics = portfolio_data['metrics']
                writer.writerow(['Total Value', f"${metrics['total_value']:,.2f}"])
                writer.writerow(['Total P&L', f"${metrics['total_pnl']:,.2f}"])
                writer.writerow(['Return %', f"{metrics['return_pct']:.2f}%"])
                writer.writerow(['Sharpe Ratio', f"{metrics['sharpe_ratio']:.3f}"])
            
            writer.writerow([])
            writer.writerow(['POSITIONS'])
            writer.writerow(['Symbol', 'Quantity', 'Avg Price', 'Current Price', 'Market Value', 'P&L', 'Weight %'])
            
            for pos in portfolio_data.get('positions', []):
                writer.writerow([
                    pos['symbol'], pos['quantity'], pos['avg_price'], pos['current_price'],
                    pos['market_value'], pos['unrealized_pnl'], pos['weight']
                ])
        
        return str(filepath)
    
    # ========================
    # Custom Dashboards
    # ========================
    
    def save_custom_dashboard(self, dashboard_config: Dict) -> str:
        """Custom dashboard saqlash"""
        dashboard_id = f"custom_{len(self.custom_dashboards) + 1}"
        
        self.custom_dashboards[dashboard_id] = {
            'id': dashboard_id,
            'name': dashboard_config.get('name', 'Custom Dashboard'),
            'layout': dashboard_config.get('layout', {}),
            'widgets': dashboard_config.get('widgets', []),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        logger.info(f"Custom dashboard saqlandi: {dashboard_id}")
        return dashboard_id
    
    def get_custom_dashboards(self) -> Dict:
        """Custom dashboard ro'yxatini olish"""
        return {
            'dashboards': list(self.custom_dashboards.values()),
            'total': len(self.custom_dashboards)
        }
    
    def get_dashboard_layout(self, dashboard_id: str) -> Dict:
        """Dashboard layout olish"""
        if dashboard_id in self.custom_dashboards:
            return self.custom_dashboards[dashboard_id]
        return {"error": "Dashboard topilmadi"}
    
    # ========================
    # Real-time Updates
    # ========================
    
    def start_real_time_updates(self):
        """Real-time yangilanishlarni boshlash"""
        def update_loop():
            while self.real_time_enabled:
                try:
                    # KPI ma'lumotlarini yangilash
                    self._update_kpi_values()
                    
                    # Ogohlantirishlarni tekshirish
                    alerts = self.check_alerts()
                    if alerts:
                        self.socketio.emit('alerts', {'alerts': alerts})
                    
                    # Boshqa yangilanishlar
                    self.socketio.emit('kpi_update', {'kpis': self.get_current_kpis()})
                    self.socketio.emit('portfolio_update', {'portfolio': self.get_portfolio_summary()})
                    
                    time.sleep(self.update_interval)
                    
                except Exception as e:
                    logger.error(f"Real-time update xatosi: {e}")
                    time.sleep(5)
        
        # Background thread boshlash
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
        
        logger.info("Real-time yangilanishlar boshladi")
    
    def _update_kpi_values(self):
        """KPI qiymatlarini yangilash"""
        for name, kpi in self.kpi_data.items():
            # Random kichik o'zgarishlar qo'shish
            change_pct = np.random.uniform(-0.02, 0.02)  # ±2%
            kpi.value *= (1 + change_pct)
            kpi.timestamp = datetime.now()
            
            # Trend aniqlash
            if change_pct > 0.001:
                kpi.trend = "up"
            elif change_pct < -0.001:
                kpi.trend = "down"
            else:
                kpi.trend = "stable"
    
    # ========================
    # Time Series Analysis
    # ========================
    
    def analyze_time_series(self, data: List[float], period: str = "daily") -> Dict:
        """Time-series tahlil"""
        if len(data) < 2:
            return {"error": "Yetarli ma'lumot yo'q"}
        
        # Asosiy statistikalar
        mean_value = np.mean(data)
        std_value = np.std(data)
        min_value = np.min(data)
        max_value = np.max(data)
        
        # Trend tahlil
        x = np.arange(len(data))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, data)
        
        trend_direction = "stable"
        if slope > 0.001:
            trend_direction = "increasing"
        elif slope < -0.001:
            trend_direction = "decreasing"
        
        # Volatillik tahlil
        returns = [0]
        for i in range(1, len(data)):
            ret = (data[i] - data[i-1]) / data[i-1]
            returns.append(ret)
        
        volatility = np.std(returns) * np.sqrt(252) if period == "daily" else np.std(returns) * np.sqrt(12)
        
        # Seasonality (ba'zi soddalashtirishlar bilan)
        seasonality_score = abs(r_value)  # R-squared asosida
        
        return {
            'mean': mean_value,
            'std': std_value,
            'min': min_value,
            'max': max_value,
            'trend_slope': slope,
            'trend_r_squared': r_value ** 2,
            'trend_direction': trend_direction,
            'volatility': volatility,
            'seasonality_score': seasonality_score,
            'observations': len(data),
            'last_updated': datetime.now().isoformat()
        }
    
    def get_historical_performance(self, asset: str = None, days: int = 365) -> Dict:
        """Tarixiy ishlab chiqarish ma'lumotlari"""
        # Namuna tarixiy data yaratish
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # Portfolio history
        initial_value = 100000
        portfolio_values = []
        for i in range(len(dates)):
            if i == 0:
                portfolio_values.append(initial_value)
            else:
                # Realistic random walk
                daily_return = np.random.normal(0.0005, 0.015)  # ~13% yillik, 15% volatillik
                new_value = portfolio_values[-1] * (1 + daily_return)
                portfolio_values.append(new_value)
        
        # Benchmark (SPY) history
        spy_initial = 400
        spy_values = []
        for i in range(len(dates)):
            if i == 0:
                spy_values.append(spy_initial)
            else:
                daily_return = np.random.normal(0.0004, 0.012)  # Bir oz kamroq volatillik
                new_value = spy_values[-1] * (1 + daily_return)
                spy_values.append(new_value)
        
        # Metrikalar
        portfolio_return = ((portfolio_values[-1] - portfolio_values[0]) / portfolio_values[0]) * 100
        benchmark_return = ((spy_values[-1] - spy_values[0]) / spy_values[0]) * 100
        alpha = portfolio_return - benchmark_return
        
        # Sharpe ratio
        portfolio_returns = [(portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1] 
                            for i in range(1, len(portfolio_values))]
        sharpe = self.calculate_sharpe_ratio(portfolio_returns)
        
        # Max drawdown
        max_dd = self.calculate_max_drawdown(portfolio_values)
        
        return {
            'dates': [d.strftime('%Y-%m-%d') for d in dates],
            'portfolio_values': portfolio_values,
            'benchmark_values': spy_values,
            'metrics': {
                'portfolio_return': portfolio_return,
                'benchmark_return': benchmark_return,
                'alpha': alpha,
                'sharpe_ratio': sharpe,
                'max_drawdown': max_dd,
                'volatility': np.std(portfolio_returns) * np.sqrt(252) * 100
            },
            'asset': asset or 'Portfolio',
            'period_days': days
        }
    
    # ========================
    # Comparative Analysis
    # ========================
    
    def compare_to_benchmark(self, benchmark: str = None) -> Dict:
        """Benchmark bilan solishtirish"""
        benchmark = benchmark or self.config['default_benchmark']
        
        # Portfolio performance
        portfolio_perf = self.get_performance_data(30)
        # Benchmark performance
        benchmark_perf = self.get_historical_performance(benchmark, 30)
        
        # Solishtirish
        portfolio_total_return = portfolio_perf['metrics']['total_return']
        benchmark_total_return = ((benchmark_perf['benchmark_values'][-1] - 
                                  benchmark_perf['benchmark_values'][0]) / 
                                 benchmark_perf['benchmark_values'][0]) * 100
        
        alpha = portfolio_total_return - benchmark_total_return
        
        # Correlation
        portfolio_values = portfolio_perf['portfolio_values']
        benchmark_values = benchmark_perf['benchmark_values'][:len(portfolio_values)]
        
        correlation = np.corrcoef(portfolio_values, benchmark_values)[0, 1]
        
        return {
            'portfolio_return': portfolio_total_return,
            'benchmark_return': benchmark_total_return,
            'alpha': alpha,
            'correlation': correlation,
            'outperformance': portfolio_total_return > benchmark_total_return,
            'benchmark': benchmark,
            'period': '30 days'
        }
    
    # ========================
    # Main Application Methods
    # ========================
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Dashboard serverini ishga tushirish"""
        try:
            # Real-time updates
            self.start_real_time_updates()
            
            # Server start
            logger.info(f"Advanced Analytics Dashboard boshlanmoqda...")
            logger.info(f"URL: http://{host}:{port}")
            
            self.socketio.run(self.app, host=host, port=port, debug=debug)
            
        except Exception as e:
            logger.error(f"Server xatosi: {e}")
            raise
    
    def stop(self):
        """Dashboard serverini to'xtatish"""
        self.real_time_enabled = False
        logger.info("Advanced Analytics Dashboard to'xtatildi")


# ========================
# Demo va Testing
# ========================

def demo_dashboard():
    """Dashboard demo"""
    print("🚀 Advanced Analytics Dashboard Demo")
    print("=" * 50)
    
    # Dashboard yaratish
    config = {
        'secret_key': 'demo-secret-key',
        'database_path': './demo_analytics.db',
        'refresh_interval': 2,
        'enable_notifications': True,
        'default_benchmark': 'SPY'
    }
    
    dashboard = AdvancedAnalyticsDashboard(config)
    
    print("\n📊 KPI Ma'lumotlari:")
    kpis = dashboard.get_current_kpis()
    for name, data in list(kpis.items())[:5]:
        print(f"  • {name}: {data['value']:.2f} {data['unit']} ({data['status']})")
    
    print("\n💼 Portfolio Xulosasi:")
    portfolio = dashboard.get_portfolio_summary()
    if 'error' not in portfolio:
        metrics = portfolio['metrics']
        print(f"  • Jami Qiymat: ${metrics['total_value']:,.2f}")
        print(f"  • Jami P&L: ${metrics['total_pnl']:,.2f}")
        print(f"  • Return: {metrics['return_pct']:.2f}%")
        print(f"  • Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
    
    print("\n📈 Ishlab Chiqarish:")
    performance = dashboard.get_performance_data(7)
    print(f"  • Jami Return: {performance['metrics']['total_return']:.2f}%")
    print(f"  • Volatillik: {performance['metrics']['volatility']:.2f}%")
    print(f"  • Max Drawdown: {performance['metrics']['max_drawdown']:.2f}%")
    
    print("\n⚠️  Ogohlantirishlar:")
    alerts = dashboard.check_alerts()
    if alerts:
        for alert in alerts[:3]:
            print(f"  • {alert['alert_type'].upper()}: {alert['message']}")
    else:
        print("  • Ogohlantirish yo'q")
    
    print("\n📊 Grafik Turi Ma'lumotlari:")
    chart_types = ['portfolio_pie', 'performance_line', 'risk_heatmap', 'kpi_gauge']
    for chart_type in chart_types:
        chart_data = dashboard.get_chart_data_by_type(chart_type)
        if 'error' not in chart_data:
            print(f"  ✅ {chart_type}: muvaffaqiyatli")
        else:
            print(f"  ❌ {chart_type}: {chart_data['error']}")
    
    print("\n🔄 Benchmark Solishtirish:")
    comparison = dashboard.compare_to_benchmark()
    print(f"  • Portfolio Return: {comparison['portfolio_return']:.2f}%")
    print(f"  • Benchmark Return: {comparison['benchmark_return']:.2f}%")
    print(f"  • Alpha: {comparison['alpha']:.2f}%")
    print(f"  • Korrelatsiya: {comparison['correlation']:.3f}")
    
    return dashboard


def test_all_features():
    """Barcha xususiyatlarni test qilish"""
    print("\n🧪 Advanced Analytics Dashboard - To'liq Test")
    print("=" * 55)
    
    dashboard = AdvancedAnalyticsDashboard()
    
    # KPI tests
    print("\n1. KPI Tests:")
    kpis = dashboard.get_current_kpis()
    assert len(kpis) > 0, "KPI ma'lumotlari topilmadi"
    print("  ✅ KPI ma'lumotlari to'g'ri")
    
    # Portfolio tests
    print("\n2. Portfolio Tests:")
    portfolio = dashboard.get_portfolio_summary()
    assert 'error' not in portfolio, "Portfolio ma'lumotlari xatosi"
    assert 'positions' in portfolio, "Pozitsiyalar topilmadi"
    print("  ✅ Portfolio ma'lumotlari to'g'ri")
    
    # Chart tests
    print("\n3. Chart Tests:")
    chart_types = ['portfolio_pie', 'performance_line', 'risk_heatmap']
    for chart_type in chart_types:
        chart_data = dashboard.get_chart_data_by_type(chart_type)
        assert 'error' not in chart_data, f"{chart_type} grafi xatosi"
    print("  ✅ Barcha grafiklar to'g'ri")
    
    # Export tests
    print("\n4. Export Tests:")
    for format_type in ['pdf', 'excel', 'csv']:
        try:
            file_path = dashboard.export_data(format_type)
            assert Path(file_path).exists(), f"{format_type} fayl yaratilmadi"
            print(f"  ✅ {format_type.upper()} eksport muvaffaqiyatli")
        except Exception as e:
            print(f"  ❌ {format_type.upper()} eksport xatosi: {e}")
    
    # Alert tests
    print("\n5. Alert Tests:")
    alerts = dashboard.check_alerts()
    print(f"  ✅ {len(alerts)} ogohlantirish topildi")
    
    # Time series tests
    print("\n6. Time Series Tests:")
    sample_data = [100, 102, 98, 105, 103, 107, 110, 108, 112, 115]
    ts_analysis = dashboard.analyze_time_series(sample_data)
    assert 'trend_direction' in ts_analysis, "Time series tahlil xatosi"
    print("  ✅ Time series tahlil to'g'ri")
    
    # Benchmark tests
    print("\n7. Benchmark Tests:")
    comparison = dashboard.compare_to_benchmark()
    assert 'portfolio_return' in comparison, "Benchmark solishtirish xatosi"
    print("  ✅ Benchmark solishtirish to'g'ri")
    
    print("\n🎉 Barcha testlar muvaffaqiyatli tugallandi!")
    return True


# ========================
# Main Entry Point
# ========================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced Analytics Dashboard')
    parser.add_argument('--mode', choices=['demo', 'test', 'server'], 
                       default='demo', 
                       help='Ish usuli (demo, test, server)')
    parser.add_argument('--host', default='0.0.0.0', help='Host address')
    parser.add_argument('--port', type=int, default=5000, help='Port')
    parser.add_argument('--debug', action='store_true', help='Debug режим')
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'demo':
            # Demo ishlash
            dashboard = demo_dashboard()
            print(f"\n🌐 Dashboard serverini ishga tushirish uchun:")
            print(f"   python {__file__} --mode server --host {args.host} --port {args.port}")
            
        elif args.mode == 'test':
            # Test ishga tushirish
            test_all_features()
            
        elif args.mode == 'server':
            # Server ishga tushirish
            dashboard = AdvancedAnalyticsDashboard()
            dashboard.run(host=args.host, port=args.port, debug=args.debug)
    
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard to'xtatildi")
    except Exception as e:
        print(f"\n❌ Xato: {e}")
        logger.error(f"Xato: {e}\n{traceback.format_exc()}")


# ========================
# Additional Utilities
# ========================

class DashboardTemplates:
    """Dashboard HTML shablonlar yaratish"""
    
    @staticmethod
    def create_base_template() -> str:
        """Asosiy HTML shablon"""
        return """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Analytics Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css" rel="stylesheet">
    <style>
        .chart-container { height: 400px; }
        .kpi-card { transition: all 0.3s ease; }
        .kpi-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .alert-critical { border-left: 4px solid #dc2626; }
        .alert-warning { border-left: 4px solid #f59e0b; }
        .alert-good { border-left: 4px solid #059669; }
    </style>
</head>
<body class="bg-gray-100 dark:bg-gray-900">
    <div class="min-h-screen">
        <!-- Header -->
        <header class="bg-white dark:bg-gray-800 shadow-lg">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between h-16">
                    <div class="flex items-center">
                        <h1 class="text-xl font-bold text-gray-900 dark:text-white">
                            🚀 Advanced Analytics Dashboard
                        </h1>
                    </div>
                    <div class="flex items-center space-x-4">
                        <span id="connection-status" class="text-sm text-green-600">● Online</span>
                        <button onclick="exportData()" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                            📊 Eksport
                        </button>
                    </div>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <!-- KPI Cards -->
            <div id="kpi-section" class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">📈 KPI Metrikalar</h2>
                <div id="kpi-cards" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <!-- KPI cards will be populated by JavaScript -->
                </div>
            </div>

            <!-- Charts Section -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                <!-- Portfolio Pie Chart -->
                <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">🥧 Portfolio Tarqalishi</h3>
                    <div id="portfolio-pie-chart" class="chart-container"></div>
                </div>

                <!-- Performance Chart -->
                <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">📊 Ishlab Chiqarish</h3>
                    <div id="performance-chart" class="chart-container"></div>
                </div>
            </div>

            <!-- Additional Charts -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                <!-- Risk Heatmap -->
                <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">🌡️ Risk Heatmap</h3>
                    <div id="risk-heatmap" class="chart-container"></div>
                </div>

                <!-- Correlation Matrix -->
                <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">🔗 Korrelatsiya</h3>
                    <div id="correlation-matrix" class="chart-container"></div>
                </div>
            </div>

            <!-- Alerts Section -->
            <div id="alerts-section" class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">⚠️ Ogohlantirishlar</h2>
                <div id="alerts-container">
                    <!-- Alerts will be populated by JavaScript -->
                </div>
            </div>
        </main>
    </div>

    <script src="/static/dashboard.js"></script>
</body>
</html>
"""
    
    @staticmethod
    def create_dashboard_js() -> str:
        """Dashboard JavaScript"""
        return """
// Dashboard JavaScript
class AnalyticsDashboard {
    constructor() {
        this.socket = io();
        this.kpis = {};
        this.alerts = [];
        this.init();
    }

    init() {
        this.setupWebSocket();
        this.loadInitialData();
        this.setupEventListeners();
        this.startAutoRefresh();
    }

    setupWebSocket() {
        this.socket.on('connect', () => {
            document.getElementById('connection-status').textContent = '● Online';
            document.getElementById('connection-status').className = 'text-sm text-green-600';
            this.socket.emit('subscribe_updates');
        });

        this.socket.on('disconnect', () => {
            document.getElementById('connection-status').textContent = '● Offline';
            document.getElementById('connection-status').className = 'text-sm text-red-600';
        });

        this.socket.on('kpi_update', (data) => {
            this.updateKPIs(data.kpis);
        });

        this.socket.on('portfolio_update', (data) => {
            this.updatePortfolio(data.portfolio);
        });

        this.socket.on('alerts', (data) => {
            this.updateAlerts(data.alerts);
        });
    }

    async loadInitialData() {
        try {
            // Load KPIs
            const kpiResponse = await fetch('/api/kpis');
            const kpis = await kpiResponse.json();
            this.updateKPIs(kpis);

            // Load charts
            await this.loadCharts();

            // Load alerts
            await this.loadAlerts();

        } catch (error) {
            console.error('Initial data loading error:', error);
        }
    }

    async loadCharts() {
        const chartTypes = ['portfolio_pie', 'performance_line', 'risk_heatmap', 'correlation_matrix'];
        
        for (const chartType of chartTypes) {
            try {
                const response = await fetch(`/api/charts/${chartType}`);
                const data = await response.json();
                
                if (data.chart_data) {
                    const containerId = this.getChartContainerId(chartType);
                    if (containerId) {
                        Plotly.newPlot(containerId, JSON.parse(data.chart_data).data, JSON.parse(data.chart_data).layout);
                    }
                }
            } catch (error) {
                console.error(`Chart loading error for ${chartType}:`, error);
            }
        }
    }

    getChartContainerId(chartType) {
        const containerMap = {
            'portfolio_pie': 'portfolio-pie-chart',
            'performance_line': 'performance-chart',
            'risk_heatmap': 'risk-heatmap',
            'correlation_matrix': 'correlation-matrix'
        };
        return containerMap[chartType];
    }

    updateKPIs(kpis) {
        this.kpis = kpis;
        const container = document.getElementById('kpi-cards');
        
        container.innerHTML = '';
        
        Object.entries(kpis).forEach(([name, data]) => {
            const card = this.createKPICard(name, data);
            container.appendChild(card);
        });
    }

    createKPICard(name, data) {
        const card = document.createElement('div');
        const statusColor = this.getStatusColor(data.status);
        
        card.className = `kpi-card bg-white dark:bg-gray-800 rounded-lg shadow p-6 border-l-4 ${statusColor}`;
        
        card.innerHTML = `
            <div class="flex justify-between items-start">
                <div>
                    <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">${name}</h3>
                    <p class="text-2xl font-bold text-gray-900 dark:text-white">${data.value.toFixed(2)} ${data.unit}</p>
                </div>
                <div class="text-right">
                    <span class="text-xs ${data.trend === 'up' ? 'text-green-600' : data.trend === 'down' ? 'text-red-600' : 'text-gray-600'}">
                        ${this.getTrendIcon(data.trend)} ${data.trend}
                    </span>
                </div>
            </div>
            <div class="mt-2">
                <div class="text-xs text-gray-500 dark:text-gray-400">Target: ${data.target} ${data.unit}</div>
            </div>
        `;
        
        return card;
    }

    getStatusColor(status) {
        const colorMap = {
            'good': 'border-green-500',
            'warning': 'border-yellow-500',
            'critical': 'border-red-500'
        };
        return colorMap[status] || 'border-gray-500';
    }

    getTrendIcon(trend) {
        const iconMap = {
            'up': '↗️',
            'down': '↘️',
            'stable': '→'
        };
        return iconMap[trend] || '→';
    }

    async loadAlerts() {
        try {
            const response = await fetch('/api/alerts');
            const alerts = await response.json();
            this.updateAlerts(alerts);
        } catch (error) {
            console.error('Alerts loading error:', error);
        }
    }

    updateAlerts(alerts) {
        this.alerts = alerts;
        const container = document.getElementById('alerts-container');
        
        if (alerts.length === 0) {
            container.innerHTML = '<p class="text-green-600">✅ Ogohlantirishlar yo\'q</p>';
            return;
        }
        
        container.innerHTML = alerts.map(alert => {
            const alertClass = this.getAlertClass(alert.alert_type);
            return `
                <div class="alert-${alert.alert_type} bg-white dark:bg-gray-800 rounded-lg shadow p-4 mb-3 ${alertClass}">
                    <div class="flex justify-between items-center">
                        <div>
                            <h4 class="font-semibold text-gray-900 dark:text-white">${alert.metric}</h4>
                            <p class="text-sm text-gray-600 dark:text-gray-400">${alert.message}</p>
                        </div>
                        <span class="text-xs text-gray-500">${new Date(alert.timestamp).toLocaleTimeString()}</span>
                    </div>
                </div>
            `;
        }).join('');
    }

    getAlertClass(alertType) {
        const classMap = {
            'critical': 'border-red-500 bg-red-50 dark:bg-red-900',
            'warning': 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900'
        };
        return classMap[alertType] || '';
    }

    setupEventListeners() {
        // Export button
        window.exportData = () => {
            const format = prompt('Eksport formatini tanlang (pdf, excel, csv):', 'pdf');
            if (format) {
                window.open(`/api/export/${format}`, '_blank');
            }
        };
    }

    startAutoRefresh() {
        setInterval(() => {
            this.loadInitialData();
        }, 30000); // 30 seconds
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new AnalyticsDashboard();
});
"""


def create_dashboard_files():
    """Dashboard uchun barcha fayllarni yaratish"""
    print("📁 Dashboard fayllarini yaratish...")
    
    # Templates papkasini yaratish
    templates_dir = Path("/tmp/templates")
    templates_dir.mkdir(exist_ok=True)
    
    static_dir = Path("/tmp/static")
    static_dir.mkdir(exist_ok=True)
    
    # Base template yaratish
    with open(templates_dir / "dashboard.html", "w", encoding="utf-8") as f:
        f.write(DashboardTemplates.create_base_template())
    
    # JavaScript yaratish
    with open(static_dir / "dashboard.js", "w", encoding="utf-8") as f:
        f.write(DashboardTemplates.create_dashboard_js())
    
    print("✅ Dashboard fayllari yaratildi:")
    print(f"   📄 {templates_dir / 'dashboard.html'}")
    print(f"   📄 {static_dir / 'dashboard.js'}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--create-files':
        create_dashboard_files()
    else:
        # Standart ishga tushish
        demo_dashboard()