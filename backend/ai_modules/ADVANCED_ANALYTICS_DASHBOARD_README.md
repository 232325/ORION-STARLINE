# Advanced Analytics Dashboard - Foydalanish Qo'llanmasi

## 📋 Umumiy ma'lumot

Bu modul professional trading tizimi uchun ilg'or analytics dashboard yaratadi va quyidagi asosiy xususiyatlarga ega:

### ✨ Asosiy xususiyatlari

- **Interactive Charts**: Plotly.js yordamida interaktiv grafiklar
- **Real-time Updates**: WebSocket orqali real-time ma'lumot yangilanishlari  
- **Portfolio Analytics**: Sharpe ratio, VaR, Max Drawdown kabi risk metrikalari
- **Data Visualization**: Pie charts, line graphs, heatmaps, correlation matrix
- **Export Functionality**: PDF, Excel, CSV formatlarda ma'lumot eksporti
- **Custom Dashboards**: Foydalanuvchi tomonidan belgilangan dashboard layout
- **KPI Tracking**: Kalit KPI metrikalar monitoringi
- **Comparative Analysis**: Portfolio vs benchmark solishtirish
- **Time Series Analysis**: Tarixiy ishlab chiqarish tahlili
- **Alert System**: Ishlab chiqarish ogohlantirishlari

## 🚀 Tez boshlash

### 1. Demo ishga tushirish
```bash
cd /workspace/orion-starline/backend/ai_modules/
python advanced_analytics_dashboard.py --mode demo
```

### 2. To'liq test
```bash
python advanced_analytics_dashboard.py --mode test
```

### 3. Web server ishga tushirish
```bash
python advanced_analytics_dashboard.py --mode server --host 0.0.0.0 --port 5000
```

## 🛠️ Dashboard struktura

### Asosiy komponentlar

1. **AdvancedAnalyticsDashboard** - Asosiy sinif
2. **KPIMetric** - KPI ma'lumotlari
3. **PortfolioPosition** - Portfolio pozitsiya ma'lumotlari
4. **AlertThreshold** - Ogohlantirish chegaralari

### Web interfeys

- **Flask** - Web framework
- **SocketIO** - Real-time aloqalar
- **Plotly.js** - Interaktiv grafiklar
- **Tailwind CSS** - Responsive dizayn

## 📊 KPI Metrikalar

Dashboard quyidagi KPI larni kuzatadi:

- **Jami Portfel Qiymati** - Portfolio umumiy qiymati
- **Kunlik ROI** - Kunlik investitsiya daromadi
- **Volatillik** - Narx o'zgaruvchanligi
- **Sharpe Ratio** - Riskga nisbatan daromad nisbati
- **Maksimal Drawdown** - Eng yuqoi yo'qotish
- **Win Rate** - Muvaffaqiyatli savdolar foizi
- **Avg Trade Duration** - O'rtacha savdo muddati
- **Profit Factor** - Foyda ko'paytiruvchi

## 📈 Grafik turlari

### 1. Portfolio Pie Chart
```python
chart_data = dashboard.get_chart_data_by_type("portfolio_pie")
```

### 2. Performance Line Chart
```python
chart_data = dashboard.get_chart_data_by_type("performance_line")
```

### 3. Risk Heatmap
```python
chart_data = dashboard.get_chart_data_by_type("risk_heatmap")
```

### 4. KPI Gauge Charts
```python
chart_data = dashboard.get_chart_data_by_type("kpi_gauge")
```

### 5. Correlation Matrix
```python
chart_data = dashboard.get_chart_data_by_type("correlation_matrix")
```

## 💼 Portfolio Analytics

### Metrikalar hisoblash
```python
positions = [
    PortfolioPosition("AAPL", 100, 150.25, 155.80, 15580.00, 555.00, 12.5),
    PortfolioPosition("MSFT", 50, 310.50, 315.25, 15762.50, 237.50, 12.6)
]

metrics = dashboard.calculate_portfolio_metrics(positions)
print(f"Sharpe Ratio: {metrics['sharpe_ratio']}")
print(f"Max Drawdown: {metrics['max_drawdown']}")
```

### Risk metrikalari
```python
# Sharpe ratio hisoblash
returns = [0.01, 0.02, -0.01, 0.03, 0.00]
sharpe = dashboard.calculate_sharpe_ratio(returns)

# Maximum drawdown
values = [100, 102, 98, 105, 103, 107, 110, 108, 112, 115]
max_dd = dashboard.calculate_max_drawdown(values)

# Value at Risk (VaR)
var_95 = dashboard.calculate_var(returns, 0.95)
```

## ⚠️ Ogohlantirish tizimi

### Ogohlantirish chegaralarini sozlash
```python
threshold = AlertThreshold(
    metric_name="Jami Portfel Qiymati",
    warning_threshold=115000,
    critical_threshold=110000,
    direction="below",
    enabled=True
)

dashboard.add_alert_threshold("Jami Portfel Qiymati", threshold)
```

### Ogohlantirishlarni tekshirish
```python
alerts = dashboard.check_alerts()
for alert in alerts:
    print(f"{alert['alert_type']}: {alert['message']}")
```

## 📊 Vaqt seriya tahlili

### Tarixiy ma'lumotlar tahlili
```python
data = [100, 102, 98, 105, 103, 107, 110, 108, 112, 115]
analysis = dashboard.analyze_time_series(data)

print(f"Trend direction: {analysis['trend_direction']}")
print(f"Volatility: {analysis['volatility']}")
print(f"R-squared: {analysis['trend_r_squared']}")
```

### Tarixiy ishlab chiqarish
```python
performance = dashboard.get_historical_performance("AAPL", 365)
print(f"Total Return: {performance['metrics']['portfolio_return']:.2f}%")
print(f"Sharpe Ratio: {performance['metrics']['sharpe_ratio']:.3f}")
```

## 🔄 Benchmark solishtirish

### Portfolio vs Benchmark
```python
comparison = dashboard.compare_to_benchmark("SPY")
print(f"Portfolio Return: {comparison['portfolio_return']:.2f}%")
print(f"Benchmark Return: {comparison['benchmark_return']:.2f}%")
print(f"Alpha: {comparison['alpha']:.2f}%")
print(f"Correlation: {comparison['correlation']:.3f}")
```

## 📤 Ma'lumotlarni eksport qilish

### PDF eksport
```python
file_path = dashboard.export_data("pdf")
print(f"PDF yaratildi: {file_path}")
```

### Excel eksport  
```python
file_path = dashboard.export_data("excel")
print(f"Excel yaratildi: {file_path}")
```

### CSV eksport
```python
file_path = dashboard.export_data("csv")
print(f"CSV yaratildi: {file_path}")
```

## 🎨 Custom Dashboards

### Custom dashboard saqlash
```python
dashboard_config = {
    "name": "My Custom Dashboard",
    "layout": {
        "columns": 2,
        "rows": 3
    },
    "widgets": [
        {"type": "kpi_card", "metric": "Jami Portfel Qiymati"},
        {"type": "chart", "chart_type": "portfolio_pie"},
        {"type": "chart", "chart_type": "performance_line"}
    ]
}

dashboard_id = dashboard.save_custom_dashboard(dashboard_config)
print(f"Custom dashboard ID: {dashboard_id}")
```

### Custom dashboard olish
```python
dashboards = dashboard.get_custom_dashboards()
for dashboard in dashboards['dashboards']:
    print(f"Dashboard: {dashboard['name']} (ID: {dashboard['id']})")
```

## 🌐 Web API endpointlar

### KPI ma'lumotlari
```bash
GET /api/kpis
# Barcha KPI metrikalarini qaytaradi
```

### Portfolio ma'lumotlari  
```bash
GET /api/portfolio
# Portfolio xulosasi va pozitsiyalar
```

### Ishlab chiqarish ma'lumotlari
```bash
GET /api/performance
# Vaqt seriya ishlab chiqarish ma'lumotlari
```

### Grafik ma'lumotlari
```bash
GET /api/charts/<chart_type>
# Turli xil grafik ma'lumotlari
```

### Ma'lumotlarni eksport qilish
```bash
GET /api/export/<format_type>
# format_type: pdf, excel, csv
```

### Custom dashboard
```bash
GET /api/custom-dashboard  # Barcha dashboardlarni olish
POST /api/custom-dashboard  # Yangi dashboard saqlash
```

## 🔧 Konfiguratsiya

### Standart konfiguratsiya
```python
config = {
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

dashboard = AdvancedAnalyticsDashboard(config)
```

## 🧪 Test va Demo

### Barcha xususiyatlarni test qilish
```python
# To'liq test
python advanced_analytics_dashboard.py --mode test
```

### Demo ishga tushirish
```python
# Demo ma'lumotlari bilan
python advanced_analytics_dashboard.py --mode demo
```

### Interactive testing
```python
dashboard = AdvancedAnalyticsDashboard()

# KPI test
kpis = dashboard.get_current_kpis()
print(f"KPI count: {len(kpis)}")

# Portfolio test  
portfolio = dashboard.get_portfolio_summary()
print(f"Positions: {portfolio['total_positions']}")

# Chart test
for chart_type in ['portfolio_pie', 'performance_line']:
    chart_data = dashboard.get_chart_data_by_type(chart_type)
    print(f"{chart_type}: Success")

# Export test
for format_type in ['pdf', 'excel', 'csv']:
    file_path = dashboard.export_data(format_type)
    print(f"{format_type}: {file_path}")

# Alert test
alerts = dashboard.check_alerts()
print(f"Alerts: {len(alerts)}")
```

## 📱 Real-time Updates

### WebSocket ma'lumotlari

Dashboard quyidagi WebSocket eventlarni qo'llab-quvvatlaydi:

- `connected` - Mijoz ulanishi
- `kpi_update` - KPI yangilanishlari  
- `portfolio_update` - Portfolio yangilanishlari
- `alerts` - Yangi ogohlantirishlar

### JavaScript ulanish
```javascript
const socket = io();

socket.on('kpi_update', (data) => {
    console.log('KPI updated:', data.kpis);
});

socket.on('portfolio_update', (data) => {
    console.log('Portfolio updated:', data.portfolio);
});

socket.on('alerts', (data) => {
    console.log('New alerts:', data.alerts);
});
```

## 🎯 Eng yaxshi amaliyotlar

1. **Performance**: Katta ma'lumotlar uchun pagination ishlatish
2. **Security**: API endpointlarda autentifikatsiya qo'shish  
3. **Monitoring**: Logging va error handling
4. **Scalability**: Redis yoki boshqa cache ishlatish
5. **Database**: SQLite o'rniga PostgreSQL ishlatish

## 🐛 Xatolarni tuzatish

### Ko'p uchraydigan muammolar

1. **Flask server ishga tushmaydi**
   ```bash
   # Port bandligi
   python advanced_analytics_dashboard.py --mode server --port 5001
   ```

2. **WebSocket ulanmagan**
   - Browser konsoli tekshirish
   - CORS sozlamalarini tekshirish

3. **Grafiklar ko'rinmaydi**
   - Plotly.js kutubxonasi yuklanganligini tekshirish
   - Network tabida xatoliklarni ko'rish

4. **Export xatolari**
   - Fayl yozish huquqlarini tekshirish
   - /tmp papkasida joy borligini tekshirish

## 📞 Yordam

Agar muammo yuz bersa:

1. **Log fayllarni ko'rish**: Console output ni tekshirish
2. **Test qilish**: `--mode test` flag ishlatish  
3. **Demo**: `--mode demo` flag ishlatish
4. **Debug mode**: `--debug` flag qo'shish

## 🔄 Versiya tarixi

- **v1.0.0** - Dastlabki reliz (2025-11-05)
  - Barcha asosiy xususiyatlar
  - Interactive charts
  - Real-time updates
  - Export functionality
  - Alert system

---

**🚀 Professional Trading Analytics Dashboard - Orion-Starline AI Team**