# Smart Contract Deployment va Testing Tizimi

## 📋 Mundarija

1. [Kirish](#kirish)
2. [O'rnatish](#o-rnatish)
3. [Deployment](#deployment)
4. [Testing](#testing)
5. [Monitoring](#monitoring)
6. [Xavfsizlik](#xavfsizlik)
7. [Performance](#performance)
8. [Contributing](#contributing)

## Kirish

Bu tizim Ethereum smart contractlarini deploy qilish va test qilish uchun yaratilgan to'liq echimdir. U quyidagi asosiy xususiyatlarga ega:

### ✨ Asosiy Xususiyatlar

- **Multi-Network Support**: Mainnet, Testnet, va Local networks
- **Hardhat va Truffle Integration**: Ikki framework ham qo'llab-quvvatlanadi
- **Automated Testing**: Unit, Integration, E2E, Performance, Load testing
- **CI/CD Pipeline**: GitHub Actions bilan to'liq avtomatlashtirilgan
- **Real-time Monitoring**: Contract events va performance tracking
- **Security Scanning**: Avtomatik xavfsizlik tahlili
- **Gas Optimization**: Gas usage tracking va optimization

## O'rnatish

### Talablar

- Node.js 16+ yoki 18+
- npm yoki yarn
- Git
- Blockchain RPC APIs (Alchemy, Infura)

### 1. Repository ni Clone qiling

```bash
git clone <repository-url>
cd smart-contract-deployment-testing
```

### 2. Dependencies ni o'rnating

```bash
npm install
```

### 3. Environment Variables ni sozlang

```bash
cp .env.example .env
```

`.env` faylini to'ldiring:

```env
# Blockchain APIs
ALCHEMY_API_KEY=your_alchemy_api_key
INFURA_API_KEY=your_infura_api_key

# Private Keys (EHTIYOT!)
PRIVATE_KEY=your_private_key
MNEMONIC=your_mnemonic_phrase

# Explorer APIs
ETHERSCAN_API_KEY=your_etherscan_key
POLYGONSCAN_API_KEY=your_polygonscan_key
BSCSCAN_API_KEY=your_bscscan_key

# Monitoring
SLACK_WEBHOOK=your_slack_webhook
EMAIL_USER=your_email
EMAIL_PASS=your_email_password
```

### 4. Contract ABI ni tayyorlang

```bash
mkdir -p scripts/abis
# Contract ABI fayllarini bu papkaga joylashtiring
```

## Deployment

### Manual Deployment

#### Hardhat bilan

```bash
# Testnet ga deploy qilish
npm run deploy:testnet

# Mainnet ga deploy qilish
npm run deploy:mainnet

# Local ga deploy qilish
npm run deploy:local
```

#### Truffle bilan

```bash
# Testnet ga deploy
npx truffle migrate --network sepolia

# Mainnet ga deploy
npx truffle migrate --network mainnet
```

### Automated Deployment

Deployment CI/CD pipeline orqali avtomatik amalga oshiriladi:

```bash
# GitHub Actions workflow fayllari
.github/workflows/
├── ci-cd.yml          # Asosiy CI/CD pipeline
└── security.yml       # Xavfsizlik skaneri
```

### Deployment Configuration

```javascript
// config/deployment.config.js
module.exports = {
    sepolia: {
        deployToken: true,
        deployGovernance: true,
        tokenName: "MainToken",
        tokenSymbol: "MTK",
        initialSupply: ethers.parseEther("100000000")
    }
};
```

## Testing

### Test Turlari

#### 1. Unit Tests

```bash
npm run test:unit
```

Unit test misoli:

```javascript
describe("MainContract Unit Tests", function () {
    it("Should deploy with correct owner", async function () {
        expect(await mainContract.owner()).to.equal(owner.address);
    });
});
```

#### 2. Integration Tests

```bash
npm run test:integration
```

Cross-contract interaction testlari:

```javascript
describe("Integration Tests", function () {
    it("Should handle cross-contract operations", async function () {
        await mainContract.connect(user1).complexOperation(user2.address);
        expect(await tokenContract.balanceOf(user2.address)).to.equal(amount);
    });
});
```

#### 3. End-to-End Tests

```bash
npm run test:e2e
```

To'liq user journey testlari:

```javascript
describe("E2E Tests", function () {
    it("Should complete user onboarding flow", async function () {
        // 1. User registration
        await mainContract.connect(user).mintTokens(user.address, "1000");
        
        // 2. Governance participation
        await governanceContract.connect(user).createProposal("Test", "Desc", "100");
        await governanceContract.connect(user).vote(0, "100");
        
        // 3. Token operations
        await tokenContract.connect(user).transfer(otherUser.address, "50");
    });
});
```

#### 4. Performance Tests

```bash
npm run test:performance
```

Gas usage va speed testlari:

```javascript
describe("Performance Tests", function () {
    it("Should measure gas usage", async function () {
        const gasUsed = await measureGasUsage(async () => {
            await tokenContract.transfer(recipient, amount);
        });
        expect(gasUsed).to.be.lessThan(100000);
    });
});
```

#### 5. Load Testing

```bash
npm run test:load
```

Yuqori yuklama testlari:

```javascript
// test/load/load-test.js
const loadTester = new LoadTester();

// HTTP endpoint load test
await loadTester.testHttpEndpoint('https://api.example.com', {
    maxRequests: 1000,
    concurrency: 10
});

// Contract function load test
await loadTester.testSmartContract(contractAddress, {
    name: 'transfer',
    type: 'transaction',
    args: [recipient, amount]
}, {
    concurrentCalls: 20,
    totalCalls: 200
});
```

### Coverage Reporting

```bash
npm run coverage
```

Coverage hisobotini ko'rish:

```bash
open coverage/index.html
```

## Monitoring

### Real-time Contract Monitoring

```bash
npm run monitor
```

Monitor configuration:

```javascript
// Contract qo'shish
const contractAbi = require('./abis/contractAbi.json');
await monitor.addContract('0x123...', contractAbi, 'mainnet');
```

### Metrics Server

Monitoring metrikalar `/metrics` endpoint dan olinadi:

```bash
curl http://localhost:8080/metrics
```

Mavjud metrikalar:
- `contract_transactions_total`: Umumiy transactionlar
- `contract_gas_used`: Gas usage histogram
- `contract_execution_time`: Execution time histogram
- `contract_events_total`: Eventlarning soni
- `contract_error_rate`: Error rate

### Grafana Dashboard

```bash
# Grafana configuration
GRAFANA_URL=http://localhost:3000
GRAFANA_API_KEY=your_grafana_key
```

### Alerting

Xavfsizlik va muhim eventlar uchun alerting:

```javascript
// Slack notification
await sendAlert('large_transfer', {
    contract: '0x123...',
    from: user.address,
    value: ethers.formatEther(amount)
});

// Email notification
await sendEmailAlert({
    type: 'contract_paused',
    severity: 'high',
    data: { contract: '0x123...' }
});
```

## Xavfsizlik

### Automated Security Scanning

```bash
# GitHub Actions da avtomatik ishlaydi
npm run security-scan
```

Xavfsizlik skanerlari:

#### 1. Slither

```bash
slither contracts/ --print human-summary
```

#### 2. Mythril

```bash
myth analyze contracts/**/*.sol --execution-timeout 300
```

#### 3. Securify

```bash
securify2 contracts/ --json > securify-report.json
```

#### 4. Custom Security Tests

```javascript
describe("Security Tests", function () {
    it("Should prevent reentrancy attacks", async function () {
        // Reentrancy protection test
        await expectRevert(
            contract.withdraw(ethers.parseEther("1")),
            "ReentrancyGuard: reentrant call"
        );
    });
});
```

### Access Control Audit

```bash
npm run audit:access-control
```

Role-based access control testing:

```javascript
describe("Access Control", function () {
    it("Should enforce role restrictions", async function () {
        await expectRevert(
            contract.connect(user).adminFunction(),
            "AccessControl: account is missing role"
        );
    });
});
```

### Gas Security Analysis

```bash
npm run audit:gas
```

Gas limit va DoS protection:

```javascript
describe("Gas Security", function () {
    it("Should prevent gas DoS attacks", async function () {
        const largeArray = new Array(10000).fill(0);
        await expectRevert(
            contract.processArray(largeArray),
            "Array too large"
        );
    });
});
```

## Performance

### Gas Optimization

#### 1. Gas Usage Tracking

```javascript
// Automated gas tracking
const gasUsed = await measureGasUsage(async () => {
    const tx = await contract.transfer(recipient, amount);
    return tx.wait();
});

console.log(`Transfer gas usage: ${gasUsed} gas`);
```

#### 2. Gas Reports

```bash
npm run gas-report
```

#### 3. Gas Limit Checks

```javascript
// Gas limit validation
const gasEstimate = await contract.transfer.estimateGas(recipient, amount);
expect(gasEstimate).to.be.lessThan(100000);
```

### Transaction Speed Optimization

#### 1. Batch Operations

```javascript
// Efficient batch processing
const batchSize = 10;
for (let i = 0; i < totalOperations; i += batchSize) {
    const batch = operations.slice(i, i + batchSize);
    await Promise.all(batch.map(op => contract.executeOperation(op)));
}
```

#### 2. Caching Strategies

```javascript
// State caching for repeated reads
const cachedBalance = await cache.get(`balance_${address}`);
if (!cachedBalance) {
    const balance = await contract.balanceOf(address);
    await cache.set(`balance_${address}`, balance, 300); // 5 min cache
    return balance;
}
return cachedBalance;
```

### Load Balancing

#### 1. Multi-Provider Setup

```javascript
const providers = [
    new ethers.JsonRpcProvider(process.env.ALCHEMY_URL_1),
    new ethers.JsonRpcProvider(process.env.ALCHEMY_URL_2),
    new ethers.JsonRpcProvider(process.env.INFURA_URL)
];

let currentProvider = 0;

async function sendTransaction() {
    try {
        const provider = providers[currentProvider];
        const signer = provider.getSigner();
        const contract = new ethers.Contract(address, abi, signer);
        return await contract.transfer(recipient, amount);
    } catch (error) {
        // Switch to next provider
        currentProvider = (currentProvider + 1) % providers.length;
        return sendTransaction();
    }
}
```

## API Documentation

### Contract Interface

#### MainContract

```solidity
contract MainContract {
    // Admin functions
    function addAdmin(address account) external onlyOwner;
    function removeAdmin(address account) external onlyOwner;
    
    // Pause/Unpause
    function pause() external onlyOwner;
    function unpause() external onlyOwner;
    
    // User functions
    function mintTokens(address to, uint256 amount) external;
    function transfer(address to, uint256 amount) external;
    
    // View functions
    function owner() external view returns (address);
    function paused() external view returns (bool);
}
```

#### TokenContract

```solidity
contract TokenContract {
    // ERC20 standard functions
    function transfer(address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    
    // Custom functions
    function mint(address to, uint256 amount) external;
    function burn(uint256 amount) external;
}
```

### SDK Usage

```javascript
const { Web3 } = require('web3');
const contractAbi = require('./abis/contractAbi.json');

const web3 = new Web3('https://mainnet.infura.io/v3/YOUR_API_KEY');
const contract = new web3.eth.Contract(contractAbi, '0x123...');

// Call contract methods
const balance = await contract.methods.balanceOf('0x456...').call();
await contract.methods.transfer('0x456...', '1000').send({
    from: '0x789...',
    gas: '21000'
});
```

## Contributing

### Development Setup

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Install dependencies: `npm install`
4. Run tests: `npm test`
5. Commit changes: `git commit -am 'Add new feature'`
6. Push branch: `git push origin feature/new-feature`
7. Create Pull Request

### Code Standards

#### Solidity Style Guide

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title ContractName
 * @dev Contract description
 * @author Your Name
 */
contract ContractName {
    // State variables ( camelCase )
    uint256 public totalSupply;
    address public owner;
    
    // Events (PascalCase)
    event Transfer(address indexed from, address indexed to, uint256 value);
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    // Functions ( camelCase )
    function transferTokens(address to, uint256 amount) external onlyOwner {
        // Implementation
    }
}
```

#### JavaScript Style Guide

```javascript
// Use const/let instead of var
const contractAddress = '0x123...';
let transactionHash;

// Use descriptive variable names
const userBalance = await getUserBalance(userAddress);
const gasLimit = 21000;

// Error handling
try {
    const result = await contract.transfer(recipient, amount);
    console.log('Transfer successful:', result.hash);
} catch (error) {
    console.error('Transfer failed:', error.message);
    throw error;
}
```

### Testing Guidelines

1. **Unit Tests**: Har bir function uchun test yozish
2. **Edge Cases**: Barcha edge case larni qamrab olish
3. **Gas Testing**: Gas usage validation
4. **Security Testing**: Xavfsizlik testing
5. **Performance Testing**: Performance benchmarking

### Documentation

- README.md ni yangilab turish
- API documentation qo'shish
- Code comments yozish
- Changelog tutib borish

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Security scans pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added for new features
```

## Troubleshooting

### Common Issues

#### 1. Deployment Failures

```bash
# Gas estimation error
Error: Transaction reverted: { "gasLimit":{"hex":"0x1c9c38","value":3000000} }

# Solution: Increase gas limit
npm run deploy:testnet -- --gas-limit 5000000
```

#### 2. Test Timeouts

```bash
# Increase timeout
it("Should complete within time", async function () {
    this.timeout(60000); // 1 minute
    // Test implementation
});
```

#### 3. Network Issues

```javascript
// Provider switching
const providers = [
    'https://eth-mainnet.alchemyapi.io/v2/...',
    'https://mainnet.infura.io/v3/...'
];

let providerIndex = 0;
async function getProvider() {
    return new ethers.JsonRpcProvider(providers[providerIndex]);
}
```

### Performance Issues

#### 1. High Gas Usage

```solidity
// Optimize loops
for (uint256 i = 0; i < length; i++) {
    // Avoid state variable updates in loop
    User storage user = users[i];
    // Process user
}
```

#### 2. Transaction Delays

```javascript
// Use priority fee for faster inclusion
const tx = await contract.transfer(recipient, amount, {
    maxFeePerGas: ethers.parseUnits("50", "gwei"),
    maxPriorityFeePerGas: ethers.parseUnits("2", "gwei")
});
```

## License

Bu project MIT license ostida litsenziyalangan.

## Support

Agar savollaringiz bo'lsa:

1. [Documentation](./docs/) ni o'qib ko'ring
2. [Issues](./issues/) yarating
3. [Discussions](./discussions/) da muhokama qiling
4. Email: support@yourcompany.com

---

**© 2024 Smart Contract Deployment va Testing Tizimi**