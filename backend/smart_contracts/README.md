# Trading Smart Contracts

## 🚀 Loyiha ta'rifi

Bu loyiha zamonaviy **AI Trading Smart Contracts** tizimi bo'lib, quyidagi asosiy komponentlardan iborat:

- **AI Trading Contract** - Reinforcement Learning signal execution
- **Portfolio Manager Contract** - Multi-asset management
- **Risk Management Contract** - Stop-loss, take-profit va boshqa risk boshqaruvi
- **Settlement Contract** - Order fulfillment va transaction execution
- **Fee Management Contract** - Trading fees va revenue distribution
- **Multi-Asset Support** - StockToken, ForexToken, MetalToken

## 📋 Tizim Arxitekturasi

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Trading System                         │
├─────────────────────────────────────────────────────────────┤
│  AITrading.sol    │  PortfolioManager.sol   │  RiskMgmt.sol │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│  Settlement.sol   │  FeeManagement.sol      │  Tokens       │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│  StockToken.sol   │  ForexToken.sol         │  MetalToken.sol│
└─────────────────────────────────────────────────────────────┘
```

## 🛠 Asosiy Xususiyatlari

### Core Trading Contracts

#### 1. **AI Trading Contract** (`AITrading.sol`)
- **RL Signal Execution**: Reinforcement learning signallarini bajarish
- **Confidence Threshold**: Signal bajarish uchun minimal ishonchlilik darajasi
- **Position Size Limits**: maksimal pozitsiya hajmi cheklovlari
- **Emergency Pause**: Foydalanuvchi tomonidan to'xtatish imkoniyati
- **Market Integration**: Narx feed'lari va market data integratsiyasi

```solidity
// Signal submission
bytes32 signalId = aiTrading.submitSignal(
    75,           // Action: -100 to 100 (short to long)
    1000000,      // Amount in base currency
    800,          // Confidence: 0-1000 (80%)
    marketHash    // Market data hash
);
```

#### 2. **Portfolio Manager** (`PortfolioManager.sol`)
- **Multi-Asset Support**: Turli aktiv turlari bilan ishlash
- **Dynamic Rebalancing**: Avtomatik portfel balanslash
- **Position Tracking**: Pozitsiyalarni kuzatish
- **Performance Metrics**: Rentabellik ko'rsatkichlari
- **Weight Management**: Asset vaznlarini boshqarish

```solidity
// Portfolio creation
address portfolio = portfolioManager.createPortfolio();

// Add asset with weight
portfolioManager.addAsset(
    USDC_ADDRESS, 2000,  // 20% target weight
    3000, 1000           // Max 30%, Min 10%
);
```

#### 3. **Risk Management** (`RiskManagement.sol`)
- **Stop-Loss/Take-Profit**: Avtomatik stop-loss va take-profit
- **Daily Loss Limits**: Kunlik yo'qotish limitlari
- **Leverage Controls**: Leverage nisbati nazorati
- **Circuit Breaker**: Avariya to'satdan to'xtashi
- **Position Sizing**: Pozitsiya hajmi hisoblash

```solidity
// Risk validation
(bool isValid, string memory reason) = riskManager.validateTrade(
    asset, 500000,    // Position size
    price, 2          // Leverage
);
```

#### 4. **Settlement** (`Settlement.sol`)
- **Order Management**: Buyurtma boshqaruvi
- **Market/Limit Orders**: Market va limit order turlari
- **Partial Fills**: Qisman bajarilish
- **Batch Operations**: Toplamli operatsiyalar
- **Fee Calculation**: Trading fees hisoblash

```solidity
// Create order
bytes32 orderId = settlement.createOrder(
    USDC_ADDRESS,     // Asset
    1000000,          // Amount
    100000000,        // Price (1.00 USD)
    0,                // Stop price
    OrderType.MARKET, // Order type
    OrderSide.BUY,    // Order side
    expiry            // Expiry time
);
```

#### 5. **Fee Management** (`FeeManagement.sol`)
- **Tiered Fees**: Darajali fees tizimi
- **Volume Discounts**: Hajm bo'yicha chegirmalar
- **Revenue Distribution**: Daromad tarqatish
- **Maker/Taker Fees**: Market maker/taker fees
- **Custom Fee Structures**: Har bir asset uchun maxsus fee strukturalar

```solidity
// Calculate fee
uint256 fee = feeManager.calculateFee(
    tradeId, trader, asset, 
    amount, price, isMaker
);
```

### Multi-Asset Support

#### **Stock Token** (`StockToken.sol`)
```solidity
// Create stock token for AAPL
StockToken aapl = new StockToken(
    address(0),        // Stock contract
    "AAPL",            // Symbol
    "Apple Inc.",      // Company name
    15728600000        // Shares outstanding
);
```

**Xususiyatlari:**
- Dividend payments
- Corporate actions support
- Price oracle integration
- Burn/mint capabilities
- Share tracking

#### **Forex Token** (`ForexToken.sol`)
```solidity
// Create forex token
ForexToken forex = new ForexToken();

// Add currency
forex.addCurrency(Currency.EUR, "EUR", 2);

// Update exchange rate
forex.updateExchangeRate("EURUSD", 1095000); // 1.095 USD
```

**Xususiyatlari:**
- Multiple currency pairs
- Real-time exchange rates
- Cross-rate calculations
- 6-decimal precision
- Currency management

#### **Metal Token** (`MetalToken.sol`)
```solidity
// Create metal token
MetalToken metals = new MetalToken();

// Add storage
metals.addStorage(storageAddress, "Vault A", 10000000);

// Deposit physical gold
metals.depositPhysical(MetalType.GOLD, 1000, storageAddress);
```

**Xususiyatlari:**
- Physical metal backing
- Storage facility management
- Price per ounce tracking
- Metal purity tracking
- Gram/ounce conversions

## 🔒 Xavfsizlik Xususiyatlari

### 1. **Access Control**
```solidity
// Role-based access control
modifier onlyAdmin() {
    require(hasRole(DEFAULT_ADMIN_ROLE, msg.sender), "Unauthorized");
    _;
}

modifier onlyOracle() {
    require(hasRole(ORACLE_ROLE, msg.sender), "Oracle required");
    _;
}
```

### 2. **Reentrancy Protection**
```solidity
// ReentrancyGuard integration
contract SecureContract is ReentrancyGuard {
    function sensitiveFunction() external nonReentrant {
        // Protected logic
    }
}
```

### 3. **Input Validation**
```solidity
// Input validation
if (amount == 0) revert ZeroAmount();
if (price == 0) revert InvalidPrice();
if (leverage > MAX_LEVERAGE) revert LeverageExceeded(leverage, MAX_LEVERAGE);
```

### 4. **Safe Mathematics**
```solidity
// Using SecurityUtils library
uint256 result = amount.safeAdd(bonus);
uint256 percentage = amount.basisPoints(500); // 5%
```

### 5. **Emergency Controls**
```solidity
// Emergency pause
function emergencyPause() external onlyAdmin {
    _pause();
}

// Circuit breaker
function activateCircuitBreaker(string reason) external onlyRiskOfficer {
    _circuitBreakerActive = true;
    _circuitBreakerReason = reason;
}
```

## 🛠 Installation va Setup

### 1. **Prerequisites**
```bash
# Node.js (version 18+)
node --version

# npm
npm --version

# Git
git --version
```

### 2. **Installation**
```bash
# Clone repository
git clone https://github.com/your-username/trading-smart-contracts.git
cd trading-smart-contracts

# Install dependencies
npm install

# Setup environment
cp .env.example .env
```

### 3. **Environment Configuration**
```bash
# .env file
PRIVATE_KEY=your_private_key_here
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_KEY
MAINNET_RPC_URL=https://mainnet.infura.io/v3/YOUR_INFURA_KEY
ETHERSCAN_API_KEY=your_etherscan_api_key
POLYGONSCAN_API_KEY=your_polygonscan_api_key
```

## 🚀 Deployment

### **Local Deployment**
```bash
# Start local blockchain
npx hardhat node

# Deploy to local network
npx hardhat run scripts/deploy.js --network localhost
```

### **Testnet Deployment**
```bash
# Deploy to Sepolia
npx hardhat run scripts/deploy.js --network sepolia

# Verify contracts
npx hardhat verify --network sepolia DEPLOYED_CONTRACT_ADDRESS
```

### **Mainnet Deployment**
```bash
# Deploy to mainnet (use with caution!)
npx hardhat run scripts/deploy.js --network mainnet

# Verify on Etherscan
npx hardhat verify --network mainnet DEPLOYED_CONTRACT_ADDRESS
```

## 🧪 Testing

### **Run Tests**
```bash
# Run all tests
npm test

# Run with gas reporting
REPORT_GAS=true npm test

# Run specific test
npx hardhat test test/AITrading.test.js

# Coverage report
npm run test:coverage
```

### **Test Structure**
```
test/
├── AITrading.test.js           # AI Trading tests
├── PortfolioManager.test.js    # Portfolio management tests
├── RiskManagement.test.js      # Risk management tests
├── Settlement.test.js          # Settlement tests
├── FeeManagement.test.js       # Fee management tests
├── StockToken.test.js          # Stock token tests
├── ForexToken.test.js          # Forex token tests
├── MetalToken.test.js          # Metal token tests
└── integration/
    ├── full-system.test.js     # Full system integration
    └── gas-optimization.test.js # Gas optimization tests
```

## 📊 Gas Optimization

### **Implemented Optimizations**

1. **Batch Operations**
```solidity
// Batch order filling
function batchFill(bytes32[] memory orderIds, uint256[] memory fillAmounts) 
    external nonReentrant {
    for (uint256 i = 0; i < orderIds.length; i++) {
        _fillOrder(orderIds[i], fillAmounts[i]);
    }
}
```

2. **Efficient Data Structures**
```solidity
// Using mappings instead of arrays for better gas efficiency
mapping(address => Position) public positions;
mapping(bytes32 => Order) public orders;
```

3. **Event-Driven Architecture**
```solidity
// Using events for off-chain processing
emit PositionUpdated(trader, asset, oldPosition, newPosition);
```

4. **Immutable Parameters**
```solidity
// Using immutable for constants
address public immutable feeManager;
uint256 public immutable decimals;
```

## 🔧 Configuration

### **Trading Configuration**
```json
{
  "executionThreshold": 500,
  "maxPositionSize": "1000000000000000000000000",
  "rebalanceThreshold": 500,
  "stopLossPercentage": 1000,
  "takeProfitPercentage": 2000
}
```

### **Oracle Configuration**
```json
{
  "priceFeeds": {
    "ethereum": "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419",
    "usdc": "0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6"
  },
  "staleThresholds": {
    "stockPrice": 3600,
    "forexRate": 1800
  }
}
```

## 📈 Monitoring va Analytics

### **Key Metrics**
- Total trading volume
- Active positions
- Risk metrics
- Fee revenue
- System performance

### **Alert System**
```javascript
// Risk alerts
if (dailyLoss > maxDailyLoss) {
    emit RiskAlert("DAILY_LOSS_EXCEEDED", dailyLoss);
    activateCircuitBreaker("Daily loss limit breached");
}
```

### **Performance Tracking**
```solidity
// Portfolio performance
function getPortfolioPerformance(address trader) 
    external view returns (PerformanceMetrics memory) {
    return PortfolioMetrics.get(trader);
}
```

## 🔍 Security Audit

### **Audit Checklist**
- [ ] Access control testing
- [ ] Reentrancy attack prevention
- [ ] Integer overflow/underflow protection
- [ ] Input validation
- [ ] Emergency pause functionality
- [ ] Oracle manipulation resistance
- [ ] Flash loan attack prevention
- [ ] MEV protection

### **Security Tools**
```bash
# Slither analysis
npx slither .

# MythX analysis
npx mythx

# Securify analysis
npx securify
```

## 📚 API Reference

### **AI Trading Interface**
```solidity
interface IAITrading {
    function submitSignal(int256 action, uint256 amount, uint256 confidence, bytes32 marketHash) 
        external returns (bytes32 signalId);
    function executeSignal(bytes32 signalId) external returns (ExecutionResult memory);
    function getSignal(bytes32 signalId) external view returns (TradingSignal memory);
}
```

### **Portfolio Manager Interface**
```solidity
interface IPortfolioManager {
    function createPortfolio() external returns (address portfolio);
    function openPosition(address asset, uint256 amount, uint256 price) external;
    function rebalancePortfolio() external;
    function getPortfolioValue(address owner) external view returns (uint256);
}
```

## 🤝 Contributing

### **Development Workflow**
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
npm test
npm run lint:fix

# Commit changes
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/your-feature-name
```

### **Code Standards**
- Follow Solidity style guide
- Use meaningful variable names
- Add comprehensive tests
- Document all functions
- Implement proper error handling

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### **Documentation**
- [API Documentation](docs/api.md)
- [Deployment Guide](docs/deployment.md)
- [Security Guide](docs/security.md)
- [Integration Guide](docs/integration.md)

### **Community**
- [Discord](https://discord.gg/trading-contracts)
- [Telegram](https://t.me/trading_contracts)
- [Forum](https://forum.trading-contracts.com)

### **Bug Reports**
Please use the [GitHub Issues](https://github.com/your-username/trading-smart-contracts/issues) page to report bugs.

---

**Disclaimer**: This software is provided as-is without warranty. Trading involves risk and you should conduct your own research before using these contracts in production.