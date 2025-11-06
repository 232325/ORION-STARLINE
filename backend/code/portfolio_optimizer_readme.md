# Multi-Asset Portfolio Optimizer

Bu loyiha turli xil optimizatsiya usullarini qo'llab-quvvatlaydigan professional ko'p aktivli portfolio optimizatorini o'z ichiga oladi.

## Asosiy xususiyatlari

### Optimizatsiya Usullari
- **Quantum-Inspired Optimization** - Kvant algoritmlari asosidagi samarali optimizatsiya
- **Modern Portfolio Theory (Markowitz)** - Klassik portfolio nazariyasi
- **Black-Litterman Model** - Investor nigohlari bilan birga optimizatsiya
- **Risk Parity Optimization** - Risk muvozanatlashtirish
- **Maximum Sharpe Ratio** - Maksimal risk-daromad nisbati
- **Minimum Variance** - Minimal volatilite

### Risk Metrikalar
- **Value at Risk (VaR)** - Potentsial zarar miqdori
- **Conditional VaR (CVaR)** - Shartli potentsial zarar
- **Maximum Drawdown** - Maksimal pasayish
- **Sharpe Ratio** - Risk-moslashtirilgan daromad
- **Sortino Ratio** - Faqat salbiy riskni hisobga olgan ratio
- **Information Ratio** - Benchmark ga nisbatan ko'rsatkich

### Asset Class Support
- **Stocks**: Technology, Healthcare, Finance, Energy sektorlari
- **Forex**: Major currency pairs (EURUSD, GBPUSD, USDJPY, va boshqalar)
- **Metals**: Gold, Silver, Platinum, Palladium
- **Dynamic Rebalancing**: Avtomatik qayta muvozanatlash

### Constraint Management
- Maksimal va minimal pozitsiya hajmi
- Sektor allocation limitlari
- Geographic allocation constraintlari
- Likvidlik talablari
- Transaction cost optimizatsiyasi

## Foydalanish

### Asosiy Optimizatsiya

```python
from portfolio_optimizer import PortfolioOptimizer

# Optimizatorni yaratish
optimizer = PortfolioOptimizer(risk_free_rate=0.03)

# Ma'lumotlar tayyorlash
assets_data = {
    'AAPL': {'return': 0.15, 'vol': 0.25},
    'MSFT': {'return': 0.12, 'vol': 0.20},
    'GOOGL': {'return': 0.18, 'vol': 0.30},
    # ... boshqa aktivlar
}

# Quantum optimizatsiya
result = optimizer.optimize_portfolio(
    assets_data, 
    method='quantum'
)

# Natijalarni ko'rish
print(optimizer.generate_portfolio_report(result))
```

### Multi-Asset Allocation

```python
from portfolio_optimizer import AssetAllocator

allocator = AssetAllocator()
multi_asset_portfolio = allocator.optimize_multi_asset_portfolio(assets_data)

for asset, weight in multi_asset_portfolio.items():
    print(f"{asset}: {weight:.2%}")
```

### Custom Constraints

```python
constraints = {
    'max_weight': 0.30,  # Maksimal 30%
    'min_weight': 0.05,  # Minimal 5%
    'target_return': 0.10,  # Target 10% daromad
    'sector_limits': {
        'technology': 0.25,  # Tech maksimal 25%
        'healthcare': 0.20,  # Healthcare maksimal 20%
    }
}

result = optimizer.optimize_portfolio(
    assets_data,
    method='quantum',
    constraints=constraints
)
```

### Risk Analysis

```python
from portfolio_optimizer import RiskMetrics
import numpy as np

# Namuna returns
returns = np.random.normal(0.08, 0.15, 252)

risk_calc = RiskMetrics(confidence_level=0.95)

print(f"VaR (95%): {risk_calc.calculate_var(returns):.2%}")
print(f"CVaR (95%): {risk_calc.calculate_cvar(returns):.2%}")
print(f"Max Drawdown: {risk_calc.calculate_max_drawdown(pd.Series(returns)):.2%}")
```

## Fayllar

- `portfolio_optimizer.py` - Asosiy optimizator tizimi
- `demo.py` - To'liq demo va qo'llanma
- `README.md` - Bu fayl

## Installation

```bash
pip install numpy pandas scipy scikit-learn
```

## Demo Ishga Tushirish

```bash
python demo.py
```

## Muhim Eslatma

Bu tizim namuna ma'lumotlar bilan ishlaydi. Real trading uchun:

1. **Ma'lumotlar Manbai**: Yahoo Finance, Alpha Vantage, yoki boshqa API
2. **Historical Data**: Kamida 2-3 yillik historical data
3. **Live Data**: Real-time ma'lumotlar uchun WebSocket API
4. **Risk Management**: Yanada qat'iy risk management
5. **Compliance**: Regulator talablari

## Xavfsizlik

- Faqat real historical ma'lumotlar bilan backtest qiling
- Katta pozitsiyalarni alohida tekshiring
- Diversifikatsiyani ta'minlang
- Regular rebalancing
- Risk limitlari qo'ying

## Development

Bu loyiha quyidagi komponentlardan iborat:

1. **QuantumInspiredOptimizer** - Kvant algoritmlari
2. **ModernPortfolioTheory** - Klassik MPT
3. **BlackLittermanModel** - BL modeli
4. **RiskParityOptimizer** - Risk parity
5. **RiskMetrics** - Risk hisoblash
6. **AssetAllocator** - Ko'p aktivli allocation
7. **PortfolioOptimizer** - Boshqaruvchi class

Har bir komponent mustaqil ishlatilishi mumkin yoki birgalikda integratsiya qilinishi mumkin.

## Lisenziya

Bu loyiha ta'lim maqsadlarida yaratilgan. Real tradingda foydalanishdan oldin professional maslahat oling.