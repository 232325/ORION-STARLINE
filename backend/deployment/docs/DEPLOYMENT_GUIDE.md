# Deployment Guide

## Quick Start

### 1. Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd smart-contract-deployment-testing

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### 2. Smart Contract Development

Create your smart contracts in the `contracts/` directory:

```solidity
// contracts/MyContract.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

contract MyContract is Ownable, Pausable {
    event ValueUpdated(uint256 newValue);
    
    uint256 public value;
    
    constructor(uint256 _initialValue) {
        value = _initialValue;
        transferOwnership(msg.sender);
    }
    
    function updateValue(uint256 _newValue) external whenNotPaused onlyOwner {
        value = _newValue;
        emit ValueUpdated(_newValue);
    }
    
    function pause() external onlyOwner {
        _pause();
    }
    
    function unpause() external onlyOwner {
        _unpause();
    }
}
```

### 3. Compile Contracts

```bash
# Compile all contracts
npm run compile

# Check compilation output
ls artifacts/contracts/
```

### 4. Run Tests

```bash
# Unit tests
npm run test:unit

# Integration tests
npm run test:integration

# End-to-end tests
npm run test:e2e

# All tests with coverage
npm run test
npm run coverage
```

### 5. Deploy

#### Local Network (Development)

```bash
# Start local hardhat network
npx hardhat node

# In another terminal, deploy
npm run deploy:local
```

#### Testnet (Sepolia)

```bash
# Deploy to Sepolia testnet
npm run deploy:testnet

# Verify contracts (auto-verification enabled)
npm run verify
```

#### Mainnet

```bash
# Deploy to Ethereum mainnet (CAREFUL - costs real ETH!)
npm run deploy:mainnet

# Manual verification
npm run verify -- --network mainnet
```

### 6. Monitoring

```bash
# Start monitoring
npm run monitor

# Check metrics
curl http://localhost:8080/metrics

# Generate monitoring report
curl http://localhost:8080/report
```

## Detailed Configuration

### Network Configuration

Edit `hardhat.config.js` to add custom networks:

```javascript
networks: {
    custom: {
        url: "https://your-custom-rpc.com",
        accounts: [PRIVATE_KEY],
        chainId: 12345,
        gasPrice: "auto",
        gas: "auto"
    }
}
```

### Deployment Configuration

Customize deployment settings in `config/deployment.config.js`:

```javascript
module.exports = {
    mainnet: {
        deployToken: true,
        deployGovernance: true,
        tokenName: "YourToken",
        tokenSymbol: "YTK",
        initialSupply: ethers.parseEther("1000000000"),
        requireProxy: true,        // Use proxy pattern
        multisigOwner: "0x123..."  // Multi-sig wallet address
    }
};
```

### Gas Optimization

Enable gas reporting:

```bash
# Add to package.json scripts
"gas-report": "hardhat test test/gas/"

# Set environment variable
REPORT_GAS=1 npm run test
```

## Advanced Deployment

### Proxy Pattern (Upgradeable Contracts)

```bash
# Deploy proxy admin
npm run deploy:proxy-admin

# Deploy implementation
npm run deploy:implementation

# Deploy proxy
npm run deploy:proxy -- --implementation <IMPLEMENTATION_ADDRESS>

# Upgrade contract
npm run upgrade:contract -- --new-implementation <NEW_IMPLEMENTATION>
```

### Multi-signature Deployment

```javascript
// scripts/deploy-multisig.js
const { ethers } = require("hardhat");

async function main() {
    const multisigWallet = await ethers.getContractFactory("MultiSigWallet");
    const multisig = await multisigWallet.deploy([
        "0xOwner1...",
        "0xOwner2...",
        "0xOwner3..."
    ], 2); // 2 confirmations required

    await multisig.deployed();
    console.log("Multi-sig deployed to:", multisig.address);
}
```

### Batch Deployment

```javascript
// scripts/deploy-batch.js
async function deployBatch() {
    const contracts = [
        { name: "TokenContract", args: ["Token", "TKN", "1000000"] },
        { name: "GovernanceContract", args: [] },
        { name: "StakingContract", args: [] }
    ];

    for (const contract of contracts) {
        console.log(`Deploying ${contract.name}...`);
        const Factory = await ethers.getContractFactory(contract.name);
        const instance = await Factory.deploy(...contract.args);
        await instance.waitForDeployment();
        console.log(`${contract.name} deployed to:`, await instance.getAddress());
    }
}
```

## CI/CD Pipeline

### GitHub Actions Workflow

The system includes automated CI/CD pipeline:

```yaml
# .github/workflows/ci-cd.yml
name: Smart Contract CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - run: npm run test
      - run: npm run lint
      
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm run deploy:mainnet
        env:
          PRIVATE_KEY: ${{ secrets.PRIVATE_KEY }}
```

### Automated Testing

Tests run automatically on every commit:

- ✅ Unit tests (fast)
- ✅ Integration tests (medium)
- ✅ E2E tests (comprehensive)
- ✅ Performance tests (gas analysis)
- ✅ Security scans (static analysis)

### Security Gates

Pipeline includes security gates:

```bash
# Security scanning
npm run security-scan

# License compliance
npm run license-check

# Code coverage (must be >80%)
npm run coverage
```

## Troubleshooting

### Common Issues

#### 1. Deployment Failures

**Error:** `insufficient funds for gas`

**Solution:**
```bash
# Check your wallet balance
npx hardhat console --network mainnet
> ethers.provider.getBalance("YOUR_ADDRESS")

# Use testnet for development
npm run deploy:testnet
```

#### 2. Contract Verification Fails

**Error:** `Contract verification failed`

**Solution:**
```bash
# Verify manually
npx hardhat verify --network mainnet CONTRACT_ADDRESS "Constructor Arg 1" "Constructor Arg 2"

# Or disable auto-verification
unset AUTO_VERIFY_CONTRACTS
npm run deploy:mainnet
```

#### 3. Gas Estimation Errors

**Error:** `gas required exceeds allowance`

**Solution:**
```javascript
// Increase gas limit in deployment script
const tx = await contract.deploy(..., {
    gasLimit: 5000000,
    gasPrice: ethers.parseUnits("30", "gwei")
});
```

#### 4. Network Connectivity Issues

**Error:** `could not fetch chain ID`

**Solution:**
```javascript
// Add multiple RPC providers
const provider = new ethers.JsonRpcProvider([
    process.env.ALCHEMY_API_URL,
    process.env.INFURA_API_URL
]);
```

### Debug Mode

Enable verbose logging:

```bash
DEBUG=* npm run deploy:mainnet
```

### Local Testing

Test contracts locally before mainnet:

```bash
# Start local network
npx hardhat node

# Deploy to local
npm run deploy:local

# Run all tests
npm run test

# Check gas usage
REPORT_GAS=1 npm run test
```

## Performance Optimization

### Gas Optimization

1. **Minimize Storage Operations**
   ```solidity
   // Bad
   for (uint i = 0; i < length; i++) {
       data[i] = value; // Storage write each iteration
   }
   
   // Good
   for (uint i = 0; i < length; i++) {
       tempData[i] = value; // Memory write
   }
   data = tempData; // Single storage write
   ```

2. **Use Custom Errors**
   ```solidity
   // Bad
   require(condition, "Long error message string");
   
   // Good
   error CustomError();
   if (!condition) revert CustomError();
   ```

3. **Optimize Loop Bounds**
   ```solidity
   // Bad
   for (uint i = 0; i < array.length; i++) { ... }
   
   // Good
   uint length = array.length;
   for (uint i = 0; i < length; i++) { ... }
   ```

### Transaction Speed

1. **Use Priority Fees**
   ```javascript
   const tx = await contract.transfer(recipient, amount, {
       maxFeePerGas: ethers.parseUnits("50", "gwei"),
       maxPriorityFeePerGas: ethers.parseUnits("2", "gwei")
   });
   ```

2. **Batch Operations**
   ```javascript
   // Instead of multiple transactions
   await contract.batchTransfer(recipients, amounts);
   ```

## Security Best Practices

### 1. Access Control
- Use `onlyOwner` modifier
- Implement role-based access control
- Use `Ownable` contract from OpenZeppelin

### 2. Reentrancy Protection
```solidity
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract MyContract is ReentrancyGuard {
    function withdraw() external nonReentrant {
        // Withdrawal logic
    }
}
```

### 3. Input Validation
```solidity
function transfer(address to, uint256 amount) external {
    require(to != address(0), "Invalid address");
    require(amount > 0, "Amount must be positive");
    require(amount <= balanceOf[msg.sender], "Insufficient balance");
    // Transfer logic
}
```

### 4. Emergency Procedures
```solidity
import "@openzeppelin/contracts/security/Pausable.sol";

contract MyContract is Pausable {
    function emergencyPause() external onlyOwner {
        _pause();
    }
}
```

## Maintenance

### Regular Tasks

1. **Monitor Gas Prices**
   ```bash
   npm run monitor:gas
   ```

2. **Update Dependencies**
   ```bash
   npm audit
   npm update
   ```

3. **Security Updates**
   ```bash
   npm run security-scan
   ```

4. **Backup Contracts**
   ```bash
   npm run backup:contracts
   ```

### Monitoring Alerts

Setup alerts for:
- Large transactions
- Contract pauses
- Ownership changes
- Gas price spikes
- Error rate increases

## Support

For technical support:

1. Check the [troubleshooting guide](#troubleshooting)
2. Search [existing issues](https://github.com/your-repo/issues)
3. Create a new issue with:
   - Environment details
   - Error messages
   - Steps to reproduce
   - Expected vs actual behavior

---

**Happy Deploying! 🚀**