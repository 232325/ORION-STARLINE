# DEX Integration va Metal-backed Tokenization Tizimi

## 🚀 Loyiha Taqdimoti

Ushbu loyiha qimmatbaho metallar tokenizatsiyasi va ko'p DEX platformalar bilan integratsiyani qo'llab-quvvatlaydigan kompleks DeFi tizimini ta'minlaydi.

## 📋 Qisqacha Ko'rinish

### Asosiy Komponentlar
- **Metal Tokenization**: Qimmatbaho metallarni ERC-20 va ERC-721 tokenlari sifatida tasvirlash
- **DEX Integration**: Uniswap V3, SushiSwap, PancakeSwap va Curve Finance bilan integratsiya
- **Custom AMM**: Maxsus Automated Market Maker tizimi
- **Compliance System**: KYC/AML va regulatory compliance
- **Physical Storage**: Metallarni jismoniy saqlash va boshqarish

### Metallar
- **Oltin (Gold)**: 24k sifatli investitsiya sinfidagi oltin
- **Kumush (Silver)**: 999 eng yuqori sofliqdagi kumush
- **Platina (Platinum)**: Investitsiya sinfidagi platina
- **Palladium (Palladium)**: Qo'llab-quvvatlanadigan palladium

## 🏗️ Tizim Arxitekturasi

```
Metal Tokenization System
├── 🎨 Frontend (React/Vue.js)
├── 🔧 Backend (Node.js/Express)
├── ⛓️ Blockchain Layer
│   ├── MetalToken (ERC-20)
│   ├── MetalNFT (ERC-721)
│   ├── DEXAggregator
│   ├── CustomMetalAMM
│   ├── ComplianceRegistry
│   └── MetalStorageVault
└── 📊 Analytics & Monitoring
```

## 🛠️ O'rnatish va Sozlash

### Talablar
- Node.js 16+
- Hardhat
- Solidity ^0.8.0
- MetaMask yoki boshqa Web3 wallet

### O'rnatish

```bash
# Repository ni clone qilish
git clone [repository-url]
cd dex_integration

# Dependencies o'rnatish
npm install

# .env fayl yaratish
cp .env.example .env

# Hardhat network sozlamalari
npx hardhat compile
npx hardhat test
```

### Environment Variables

```env
# Network URLs
MAINNET_RPC_URL=https://mainnet.infura.io/v3/YOUR_KEY
TESTNET_RPC_URL=https://testnet.bscscan.com/api/YOUR_KEY
PRIVATE_KEY=your_private_key

# API Keys
ETHERSCAN_API_KEY=your_etherscan_key
BSCSCAN_API_KEY=your_bscscan_key
POLYGONSCAN_API_KEY=your_polygonscan_key

# Gas Settings
REPORT_GAS=true
```

## 🚀 Deployment

### Local Development

```bash
# Hardhat local network
npx hardhat node

# Deploy local
npx hardhat run scripts/deploy-local.js --network localhost

# Test
npx hardhat test
```

### Testnet Deployment

```bash
# Binance Smart Chain Testnet
npx hardhat run scripts/deploy-testnet.js --network testnet

# Polygon Testnet
npx hardhat run scripts/deploy-polygon-testnet.js --network polygon
```

### Mainnet Deployment

```bash
# Production deployment
npx hardhat run scripts/deploy-mainnet.js --network mainnet
```

## 📚 API Dokumentatsiya

### Metal Token (ERC-20) API

```javascript
// Metall tokenlarini mint qilish
await metalToken.mintMetal(
  toAddress,           // Qaysi adresga
  amount,              // Qancha miqdor
  metalType,           // Qaysi metal turi (0: Gold, 1: Silver, etc.)
  proofOfReserve       // Jismoniy zaxira isbotu
);

// Balansni tekshirish
const balance = await metalToken.balanceOf(userAddress);
const totalSupply = await metalToken.totalSupply();

// Jismoniy metallarni yechib olish
await metalToken.withdrawPhysical(
  toAddress,
  amount
);
```

### Metal NFT (ERC-721) API

```javascript
// Unique metallarni NFT sifatida mint qilish
const tokenId = await metalNFT.mintMetalItem(
  toAddress,
  {
    serialNumber: "GOLD-2024-001",
    weight: 100,        // grammda
    purity: 999,        // 99.9%
    metalType: 0,       // Gold
    grade: 1,           // Investment grade
    custodian: custodianAddress,
    storageLocation: "New York Vault, Manhattan",
    authenticityHash: "0x..."
  }
);

// NFT ma'lumotlarini olish
const certificate = await metalNFT.getCertificate(tokenId);
const owner = await metalNFT.ownerOf(tokenId);
```

### DEX Aggregator API

```javascript
// Token swap qilish
await dexAggregator.swapTokens({
  tokenIn: goldTokenAddress,
  tokenOut: usdcAddress,
  amountIn: "1000000000000000000", // 1 GOLD
  minAmountOut: "580000000000000000000", // min 580 USDC
  deadline: Math.floor(Date.now() / 1000) + 300,
  path: [goldTokenAddress, usdcAddress],
  fees: [3000], // 0.3% fee
  dexId: 0      // Uniswap V3
});

// Eng yaxshi route ni topish
const bestRoute = await dexAggregator.findBestRoute(swapParams);
```

### Compliance API

```javascript
// KYC registration
await complianceRegistry.registerCompliance(
  userAddress,
  {
    status: 2, // KYC_APPROVED
    riskLevel: 0, // LOW
    jurisdiction: "US",
    verificationType: "Passport",
    expiryDate: Math.floor(Date.now() / 1000) + (365 * 24 * 60 * 60)
  },
  proofData
);

// Compliance status tekshirish
const status = await complianceRegistry.getComplianceStatus(userAddress);
const riskLevel = await complianceRegistry.getRiskLevel(userAddress);

// Transaction monitoring
const txHash = await complianceRegistry.recordTransaction(
  from,
  to,
  amount,
  "US",
  "TOKEN_SWAP"
);
```

### Storage Vault API

```javascript
// Metallarni saqlash
const depositId = await storageVault.recordMetalDeposit(
  "New York Vault, Manhattan", // location
  0,                          // Gold metal type
  10000,                      // 10kg weight
  999,                        // 99.9% purity
  "GOLD-2024-001",           // serial number
  depositorAddress,
  "0x..."                    // deposit proof
);

// Saqlangan metallarni ko'rish
const deposits = await storageVault.getDepositsByLocation("New York Vault, Manhattan");

// Metallarni yechib olish
await storageVault.withdrawMetal(
  "New York Vault, Manhattan",
  depositId,
  recipientAddress,
  5000,                      // 5kg
  "0x..."                    // withdrawal proof
);
```

## 🎯 Foydalanish Misollari

### 1. Metall Tokenlarini Mint Qilish

```javascript
const { ethers } = require("hardhat");

async function mintGoldTokens() {
    const [deployer] = await ethers.getSigners();
    
    // Metal token contract instance
    const metalToken = await ethers.getContract("MetalToken");
    
    // 1000 oltin token mint qilish
    const amount = ethers.utils.parseEther("1000");
    const proof = ethers.utils.formatBytes32String("proof-123");
    
    await metalToken.mintMetal(
        deployer.address,
        amount,
        0, // Gold type
        proof
    );
    
    console.log("✅ Gold tokens minted!");
    console.log("Balance:", await metalToken.balanceOf(deployer.address));
}
```

### 2. NFT Metall Yaratish

```javascript
async function createMetalNFT() {
    const metalNFT = await ethers.getContract("MetalNFT");
    
    const certificate = {
        serialNumber: "GOLD-2024-001",
        weight: 100,           // 100g
        purity: 999,           // 99.9%
        metalType: 0,          // Gold
        grade: 1,              // Investment grade
        custodian: deployer.address,
        storageLocation: "New York Vault, Manhattan",
        isTokenized: true,
        tokenizationDate: Math.floor(Date.now() / 1000),
        authenticityHash: ethers.utils.formatBytes32String("auth-123")
    };
    
    const tokenId = await metalNFT.mintMetalItem(
        deployer.address,
        certificate
    );
    
    console.log("✅ Metal NFT created!");
    console.log("Token ID:", tokenId.toString());
}
```

### 3. DEX Swap Operatsiyasi

```javascript
async function swapTokens() {
    const dexAggregator = await ethers.getContract("DEXAggregator");
    
    const swapParams = {
        tokenIn: goldTokenAddress,
        tokenOut: usdcAddress,
        amountIn: ethers.utils.parseEther("1"), // 1 GOLD
        minAmountOut: ethers.utils.parseEther("580"), // min 580 USDC
        deadline: Math.floor(Date.now() / 1000) + 300,
        path: [goldTokenAddress, usdcAddress],
        fees: [3000], // 0.3% fee
        dexId: 0, // Uniswap V3
        isMultiHop: false
    };
    
    // Approve token first
    const goldToken = await ethers.getContractAt("IERC20", goldTokenAddress);
    await goldToken.approve(dexAggregator.address, swapParams.amountIn);
    
    // Execute swap
    const tx = await dexAggregator.swapTokens(swapParams);
    const receipt = await tx.wait();
    
    console.log("✅ Swap completed!");
    console.log("Gas used:", receipt.gasUsed.toString());
}
```

### 4. Compliance Verification

```javascript
async function verifyCompliance() {
    const complianceRegistry = await ethers.getContract("ComplianceRegistry");
    
    // KYC registration
    const complianceData = {
        status: 2, // KYC_APPROVED
        riskLevel: 0, // LOW
        jurisdiction: "US",
        verificationType: "Passport",
        verificationDate: Math.floor(Date.now() / 1000),
        expiryDate: Math.floor(Date.now() / 1000) + (365 * 24 * 60 * 60),
        verifier: deployer.address,
        isAccredited: true,
        spendingLimit: ethers.utils.parseEther("1000000"),
        dataHash: ethers.constants.HashZero
    };
    
    const proof = ethers.utils.toUtf8Bytes("KYC verification proof");
    
    await complianceRegistry.registerCompliance(
        userAddress,
        complianceData,
        proof
    );
    
    console.log("✅ User compliance verified!");
    
    // Check status
    const status = await complianceRegistry.getComplianceStatus(userAddress);
    console.log("Status:", status.toString());
}
```

### 5. Physical Metal Deposit

```javascript
async function depositPhysicalMetal() {
    const storageVault = await ethers.getContract("MetalStorageVault");
    
    const depositId = await storageVault.recordMetalDeposit(
        "New York Vault, Manhattan",
        0,                          // Gold
        5000,                       // 5kg
        999,                        // 99.9% purity
        "GOLD-2024-001",
        deployer.address,
        ethers.utils.formatBytes32String("deposit-proof-123"),
        "LBMA Certified"
    );
    
    console.log("✅ Physical metal deposited!");
    console.log("Deposit ID:", depositId.toString());
    
    // Check facility usage
    const utilization = await storageVault.getCapacityUtilization("New York Vault, Manhattan");
    console.log("Capacity utilization:", utilization.toString() / 100, "%");
}
```

## 🔒 Xavfsizlik

### Access Control
```solidity
// Admin roles
bytes32 public constant SYSTEM_ADMIN_ROLE = keccak256("SYSTEM_ADMIN_ROLE");
bytes32 public constant TOKEN_MANAGER_ROLE = keccak256("TOKEN_MANAGER_ROLE");
bytes32 public constant COMPLIANCE_ROLE = keccak256("COMPLIANCE_ROLE");

// Usage
modifier onlyRole(bytes32 role) {
    require(hasRole(role, msg.sender), "Unauthorized");
    _;
}
```

### MEV Protection
```solidity
// Random delays and transaction batching
function calculateRandomDelay(uint256 seed, uint256 minDelay, uint256 maxDelay) 
    internal pure returns (uint256) {
    return minDelay.add(seed % (maxDelay - minDelay + 1));
}
```

### Slippage Protection
```javascript
// Dynamic slippage calculation
function calculateDynamicSlippage(poolLiquidity, tradeAmount, baseSlippage) {
    const liquidityRatio = tradeAmount.mul(10000).div(poolLiquidity);
    
    if (liquidityRatio > 5000) { // > 50% of liquidity
        return baseSlippage.mul(150).div(100); // 50% higher
    } else if (liquidityRatio > 2000) { // > 20% of liquidity
        return baseSlippage.mul(120).div(100); // 20% higher
    }
    
    return baseSlippage;
}
```

## 📊 Monitoring va Analytics

### System Health Metrics
```javascript
// Real-time monitoring
const health = await tokenizationSystem.getSystemHealth();
console.log("TVL:", health.tvl / 10**18);
console.log("Backing Ratio:", health.backingRatio / 100 + "%");
console.log("Active Deposits:", health.activeDeposits);
console.log("Total Users:", health.totalUsers);
```

### Transaction Analytics
```javascript
// Compliance monitoring
const status = await complianceRegistry.getComplianceStatus(userAddress);
const reports = await complianceRegistry.getSuspiciousReports(userAddress);

// Storage utilization
const facilityInfo = await storageVault.getFacilityInfo("New York Vault, Manhattan");
console.log("Utilization:", facilityInfo.currentUsage / facilityInfo.capacity * 100 + "%");
```

## 🧪 Testing

### Unit Tests
```bash
# Run all tests
npx hardhat test

# Run specific test file
npx hardhat test test/MetalTokenizationSystemTest.js

# Run with gas reporting
REPORT_GAS=true npx hardhat test
```

### Test Coverage
```bash
# Generate coverage report
npx hardhat coverage
```

### Manual Testing Script
```javascript
// test/manual-testing.js
async function manualTest() {
    console.log("🔍 Manual testing started...");
    
    // Test all major functions
    await testTokenMint();
    await testNFTMint();
    await testDEXSwap();
    await testCompliance();
    await testStorage();
    
    console.log("✅ All tests passed!");
}
```

## 🏢 Enterprise Integration

### API Endpoints
```
POST /api/v1/mint/gold
GET /api/v1/balances/:address
POST /api/v1/swap/tokens
GET /api/v1/compliance/status/:address
POST /api/v1/storage/deposit
GET /api/v1/analytics/health
```

### Webhooks
```javascript
// Real-time notifications
const webhooks = {
    onMint: "https://your-app.com/webhooks/mint",
    onSwap: "https://your-app.com/webhooks/swap",
    onCompliance: "https://your-app.com/webhooks/compliance",
    onStorage: "https://your-app.com/webhooks/storage"
};
```

### Batch Operations
```javascript
// Batch minting
await tokenizationSystem.batchMint([
    { to: user1, metalType: 0, amount: 1000 },
    { to: user2, metalType: 1, amount: 2000 },
    { to: user3, metalType: 0, amount: 1500 }
]);
```

## 🔧 Maintenance

### Regular Tasks
- **Daily**: Monitor system health and compliance alerts
- **Weekly**: Review transaction patterns and suspicious activity
- **Monthly**: Audit storage facilities and update insurance coverage
- **Quarterly**: Update regulatory reporting and compliance documentation

### Emergency Procedures
```javascript
// Emergency pause
await tokenizationSystem.pause();

// Emergency withdrawal
await tokenizationSystem.emergencyWithdraw(token, amount);

// Circuit breaker activation
await priceProtection.triggerCircuitBreaker(reason);
```

## 📞 Yordam va Support

### Documentation
- [Smart Contract API](./contracts/README.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [Security Audit](./docs/SECURITY.md)
- [Compliance Guide](./docs/COMPLIANCE.md)

### Community
- GitHub Issues: [Repository Issues]
- Telegram: [Community Channel]
- Discord: [Developer Chat]

### Professional Support
- Technical Support: support@your-domain.com
- Compliance Questions: compliance@your-domain.com
- Security Issues: security@your-domain.com

---

## 📈 Kelajak Rejalar

### Qisqa muddat (1-3 oy)
- [ ] Frontend dashboard yaratish
- [ ] Mobile app development
- [ ] Additional DEX integrations
- [ ] Enhanced analytics features

### O'rta muddat (3-6 oy)
- [ ] Cross-chain bridge integration
- [ ] Advanced DeFi products (lending, derivatives)
- [ ] Institutional custody solutions
- [ ] Regulatory approvals

### Uzun muddat (6-12 oy)
- [ ] Multiple blockchain support
- [ ] AI-powered risk management
- [ ] Global storage network expansion
- [ ] Central bank digital currency (CBDC) integration

---

**Loyiha MiniMax tomonidan ishlab chiqilgan**
© 2024 DEX Integration Team