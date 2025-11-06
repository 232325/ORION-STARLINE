# Hybrid Quantum-Classical Forex Arbitrage System

Ushbu tizim Quantum Computing va Classical ma'lumotlarni qayta ishlash texnologiyalarini birlashtirgan ilg'or Forex Arbitrage savdoni avtomatlashtirish tizimi hisoblanadi.

## Xususiyatlari

### 🔬 Quantum-Classical Hybrid Architecture
- **Classical Pre-processing**: Real-time market data olish va validatsiya
- **Quantum Core Processing**: Quantum algoritmlar bilan correlation, volatility, va momentum tahlili
- **Classical Post-processing**: Quantum natijalarni savdo imkoniyatlariga aylantirish
- **Error Handling**: Comprehensive xatolik boshqaruvi va recovery
- **Performance Monitoring**: Real-time monitoring va analytics

### 💱 Forex Arbitrage Algoritmlari
- **Triangular Arbitrage**: Valuta uchburchak arbitrage
- **Cross-currency Arbitrage**: Cross-currency imkoniyatlari
- **Time-zone Arbitrage**: Vaqt zonasiga asoslangan arbitrage
- **Quantum Correlation Analysis**: Quantum entanglement asosida correlation
- **Quantum Volatility Modeling**: Quantum superposition volatility modellari

### 🚀 High-Performance Execution
- **Low-latency Processing**: <100ms processing time
- **High-frequency Trading**: Real-time trade execution
- **Risk Management**: Comprehensive risk assessment
- **Audit Trails**: To'liq audit trail va compliance
- **Regulatory Compliance**: Regulation qoidalariga rioya qilish

## Tizim Arxitekturasi

```
┌─────────────────────────────────────────────────────────────┐
│                    Main Orchestrator                        │
├─────────────────────────────────────────────────────────────┤
│  Classical Preprocessor  │  Quantum Processor              │
│  - Data Acquisition      │  - Correlation Analysis          │
│  - Validation           │  - Volatility Modeling          │
│  - Feature Engineering  │  - Momentum Analysis            │
│                         │  - Quantum State Calculation    │
├─────────────────────────────────────────────────────────────┤
│  Classical Postprocessor │  Arbitrage Detector             │
│  - Result Processing    │  - Pattern Detection            │
│  - Optimization         │  - Opportunity Identification   │
│  - Risk Assessment      │  - Signal Generation            │
├─────────────────────────────────────────────────────────────┤
│  Arbitrage Executor      │  Performance Monitor            │
│  - Trade Execution      │  - Real-time Metrics            │
│  - Order Management     │  - Health Monitoring           │
│  - Position Management  │  - Alert Management             │
└─────────────────────────────────────────────────────────────┘
```

## O'rnatish va Sozlash

### 1. Talablar
```bash
# Python 3.8+
pip install -r requirements.txt
```

### 2. Asosiy Komponentlar

#### Configuration (`config/config.py`)
- Quantum backend konfiguratsiyasi
- Forex data source settings
- Arbitrage parameters
- Risk management settings

#### Database Setup (`utils/database.py`)
```python
from utils.database import setup_database
setup_database()
```

### 3. Tizimni Ishga Tushirish

#### Demo Mode
```python
python main.py --mode demo --duration 10
```

#### Interactive Mode
```python
python main.py --mode interactive
```

#### Programmatic Usage
```python
from core.orchestrator import initialize_system, start_system

# Initialize system
if initialize_system():
    # Start trading
    if start_system():
        # System is running...
        time.sleep(300)  # Run for 5 minutes
```

## Foydalanish

### 1. System Status Ko'rish
```python
from core.orchestrator import get_system_status

status = get_system_status()
print(f"System State: {status['state']}")
print(f"Opportunities: {status['metrics']['total_opportunities']}")
print(f"Profits: ${status['metrics']['total_profit']:.2f}")
```

### 2. Custom Market Data
```python
from utils.data_models import MarketData, MarketPrice
from datetime import datetime, timezone

# Create custom market data
market_data = MarketData()
market_data.add_price("EURUSD", 1.1000, 1.1002, "custom_feed")
market_data.add_price("GBPUSD", 1.2500, 1.2502, "custom_feed")
```

### 3. Quantum Processing
```python
from quantum.core_processor import QuantumProcessor

processor = QuantumProcessor(config.quantum_config)
quantum_features = processor.process_market_data(market_data)
print(f"Correlation Entanglement: {quantum_features.correlation_entanglement}")
print(f"Volatility Superposition: {quantum_features.volatility_superposition}")
```

### 4. Arbitrage Detection
```python
from arbitrage.detector import ArbitrageDetector

detector = ArbitrageDetector(config.arbitrage_config)
opportunities = detector.detect_opportunities(market_data, quantum_features)

for opportunity in opportunities:
    print(f"Profit Potential: {opportunity.calculations.profit_potential:.3f}%")
    print(f"Risk Score: {opportunity.risk_level:.3f}")
```

## Performance Metrics

### Real-time Monitoring
- **Processing Latency**: <100ms average
- **Success Rate**: >95% trade success rate
- **Profit per Trade**: Monitor real-time profitability
- **System Health**: CPU, Memory, Network monitoring

### Analytics Dashboard
```python
from utils.database import db_manager

# Get 24-hour performance summary
summary = db_manager.get_performance_summary(hours=24)
print(f"Total Opportunities: {summary['opportunities']['total_opportunities']}")
print(f"Success Rate: {summary['executions']['successful_executions']}/{summary['executions']['total_executions']}")
```

## Configuration

### Quantum Settings (`config/quantum_config.py`)
```python
QuantumConfig(
    backend_name="qasm_simulator",
    quantum_registers=20,
    classical_registers=20,
    shots=1024,
    max_circuits=100
)
```

### Forex Settings (`config/forex_config.py`)
```python
ForexConfig(
    api_base_url="https://api.fxapi.com",
    update_interval=0.1,  # 100ms
    min_arbitrage_threshold=0.0001  # 0.01%
)
```

### Arbitrage Settings (`config/arbitrage_config.py`)
```python
ArbitrageConfig(
    min_profit_threshold=0.0005,  # 0.05%
    max_execution_time=0.5,  # 500ms
    risk_limit=0.1,  # 10% of portfolio
    max_position_size=1000000  # $1M
)
```

## API Reference

### Core Classes

#### `HybridQuantumForexSystem`
Main system orchestrator class.

```python
system = HybridQuantumForexSystem()
system.initialize()
system.start()
status = system.get_status()
system.stop()
```

#### `ClassicalPreprocessor`
Market data pre-processing and validation.

```python
preprocessor = ClassicalPreprocessor(config)
market_data = await preprocessor.get_latest_data()
processed_data = preprocessor.process_data(market_data)
```

#### `QuantumProcessor`
Quantum computation and analysis.

```processor = QuantumProcessor(config)
quantum_features = processor.process_market_data(market_data)
advantage_score = processor.get_quantum_advantage_score(market_data)
```

#### `ArbitrageDetector`
Arbitrage opportunity detection and analysis.

```python
detector = ArbitrageDetector(config)
opportunities = detector.detect_opportunities(market_data, quantum_features)
```

#### `ArbitrageExecutor`
Trade execution and order management.

```python
executor = ArbitrageExecutor(config)
execution = await executor.execute_arbitrage(opportunity)
```

### Data Models

#### `MarketData`
```python
market_data = MarketData()
market_data.add_price("EURUSD", 1.1000, 1.1002, "source")
price = market_data.get_price("EURUSD")
```

#### `ArbitrageOpportunity`
```python
opportunity = ArbitrageOpportunity(
    arbitrage_type=ArbitrageType.TRIANGULAR,
    currencies=['EUR', 'USD', 'JPY'],
    pairs=['EURUSD', 'USDJPY', 'EURJPY'],
    calculations=ArbitrageCalculation(...)
)
```

## Testing

### Run Test Suite
```python
python tests/test_system.py
```

### Individual Component Tests
```python
# Test quantum processing
python -c "from tests.test_system import SystemTester; t = SystemTester(); asyncio.run(t.test_quantum_processing())"

# Test arbitrage detection
python -c "from tests.test_system import SystemTester; t = SystemTester(); asyncio.run(t.test_arbitrage_detection())"
```

## Monitoring va Debugging

### Error Handling
```python
from utils.error_handler import ErrorHandler

error_handler = ErrorHandler()
error_handler.handle_error(exception, "component_name", context)
```

### Performance Monitoring
```python
from monitoring.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor(config)
monitor.start()
health = monitor.get_system_health()
report = monitor.generate_report('daily')
```

### Database Analytics
```python
from utils.database import db_manager

# Get performance summary
summary = db_manager.get_performance_summary(hours=24)

# Export data
filename = db_manager.export_data('arbitrage_opportunities')

# Get database stats
stats = db_manager.get_database_stats()
```

## Troubleshooting

### Common Issues

1. **Quantum Backend Connection**
   ```bash
   # Check quantum backend status
   python -c "from quantum.core_processor import QuantumProcessor; p = QuantumProcessor(); print(p.test_connection())"
   ```

2. **Database Errors**
   ```bash
   # Reset database
   python -c "from utils.database import setup_database; setup_database()"
   ```

3. **Performance Issues**
   ```bash
   # Check system resources
   python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%, Memory: {psutil.virtual_memory().percent}%')"
   ```

### Logging
```python
import logging
logging.getLogger('hybrid_quantum_forex').setLevel(logging.DEBUG)
```

## Architecture Details

### Quantum Algorithms Implemented

1. **Correlation Entanglement Analysis**
   - Quantum entanglement between currency pairs
   - Correlation strength measurement
   - Entanglement-based correlation scoring

2. **Volatility Superposition**
   - Quantum superposition for volatility modeling
   - Coherence-based volatility calculation
   - Superposition coherence measurement

3. **Momentum Entanglement**
   - Momentum correlation analysis
   - Quantum momentum state calculation
   - Entanglement-based momentum scoring

### Classical Algorithms

1. **Triangular Arbitrage**
   - Direct vs implied rate calculation
   - Profit potential estimation
   - Execution complexity analysis

2. **Cross-Currency Arbitrage**
   - USD-based rate calculation
   - Cross-rate profit analysis
   - Liquidity assessment

3. **Statistical Arbitrage**
   - Z-score based opportunities
   - Mean reversion detection
   - Correlation breakdown analysis

### Risk Management

1. **Position Limits**
   - Maximum position size: $1M
   - Leverage limits: 10x
   - Risk per trade: 2% stop loss

2. **Real-time Risk Assessment**
   - Market risk scoring
   - Liquidity risk assessment
   - Operational risk calculation
   - Quantum uncertainty measurement

3. **Performance Risk**
   - Drawdown limits
   - Success rate monitoring
   - Error rate tracking

## Future Enhancements

1. **Real Quantum Hardware Integration**
   - IBM Quantum Network
   - Google Quantum AI
   - Amazon Braket

2. **Advanced Quantum Algorithms**
   - Quantum Machine Learning
   - Variational Quantum Eigensolvers
   - Quantum Approximate Optimization

3. **Machine Learning Integration**
   - Deep reinforcement learning
   - Pattern recognition
   - Predictive modeling

4. **Regulatory Compliance**
   - MiFID II compliance
   - SEC regulations
   - Automated reporting

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Authors

- **Quantum Development Team** - Hybrid quantum-classical algorithms
- **Forex Trading Team** - Market data and arbitrage strategies
- **System Architecture Team** - Performance and reliability
- **Risk Management Team** - Risk assessment and compliance

## Support

For support, please email support@hybridquantumforex.com or join our Slack channel.

## Acknowledgments

- Qiskit Development Team for quantum computing framework
- Forex community for market insights and data
- Quantum computing researchers for algorithm development
- Open source contributors for various libraries and tools