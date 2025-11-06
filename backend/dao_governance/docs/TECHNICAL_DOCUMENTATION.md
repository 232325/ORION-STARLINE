# DAO Governance System - Texnik Dokumentatsiya

## 📋 Mundarija

1. [Tizim Arxitekturasi](#tizim-arxitekturasi)
2. [Smart Contract Tarkibi](#smart-contract-tarkibi)
3. [Ovoz Berish Mexanizmlari](#ovoz-berish-mexanizmlari)
4. [Kafolat (Treasury) Boshqaruvi](#kafolat-treasury-boshqaruvi)
5. [A'zolar Boshqaruvi](#azolar-boshqaruvi)
6. [Xavfslik Tadbirlari](#xavfslik-tadbirlari)
7. [API Va Interface](#api-va-interface)
8. [Deployment Va Konfiguratsiya](#deployment-va-konfiguratsiya)
9. [Testing](#testing)
10. [Monitoring Va Analytics](#monitoring-va-analytics)

---

## 🏗️ Tizim Arxitekturasi

### Asosiy Prinsiplar

```
┌─────────────────────────────────────────────────────────────┐
│                    DAO Governance System                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ DAO         │  │ Governance  │  │ Treasury    │         │
│  │ Contract    │  │ Token       │  │ Contract    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                │                │                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Voting      │  │ Member      │  │ Emergency   │         │
│  │ System      │  │ Registry    │  │ Functions   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Ma'lumotlar Oqimi

1. **Proposal Lifecycle**: Create → Vote → Execute
2. **Voting Power**: Token Balance + Staking + Delegation
3. **Treasury Operations**: Deposit → Approve → Execute
4. **Member Management**: Register → Verify → Delegate

---

## 📜 Smart Contract Tarkibi

### 1. DAO Contract (`DAO.sol`)

**Asosiy funksiyalar:**

```solidity
// A'zolar boshqaruvi
function addMember(address _member, string memory _role) external onlyAdmin;
function removeMember(address _member) external onlyAdmin;
function updateMember(address _member, string memory _newRole) external;

// Proposal boshqaruvi
function createProposal(...) external onlyMember returns (uint256);
function castVote(uint256 _proposalId, uint8 support) external onlyMember;
function executeProposal(uint256 _proposalId) external onlyAdmin;

// Emergency funksiyalar
function emergencyPause() external onlyGuardian;
function emergencyTransfer(address _to, uint256 _amount, string memory _reason) external;
```

**Konfiguratsiya parametrlari:**

```solidity
uint256 public quorum = 1000000; // Minimum voting power
uint256 public votingPeriod = 604800; // 7 days
uint256 public timelockDelay = 86400; // 1 day execution delay
```

### 2. Governance Token Contract (`GovernanceToken.sol`)

**ERC20 funksiyalari:**

```solidity
// Asosiy token operatsiyalari
function mint(address _to, uint256 _amount, string memory _reason) external onlyOwner;
function burn(uint256 _amount, string memory _reason) external;
function transferAndLock(address _to, uint256 _amount, uint256 _duration) external returns (uint256);

// Staking tizimi
function stake(uint256 _amount, uint256 _duration) external;
function unstake(uint256 _amount) external;
function claimRewards() external;

// Voting power boshqaruvi
function getVotingPower(address _account) external view returns (uint256);
function lockVotingPower(uint256 _amount, uint256 _duration) external returns (uint256);
```

**Staking parametrlari:**

```solidity
uint256 public stakingRewardRate = 100; // 1% per block
uint256 public constant MAX_MULTIPLIER = 500; // 5x max voting power

// Voting power multipliers
votingLockMultipliers[30 days] = 100;   // 1x
votingLockMultipliers[90 days] = 150;   // 1.5x
votingLockMultipliers[365 days] = 300;  // 3x
votingLockMultipliers[730 days] = 500;  // 5x
```

### 3. Treasury Contract (`Treasury.sol`)

**Kafolat operatsiyalari:**

```solidity
// Asosiy funksiyalar
function deposit(string memory _reason) external payable;
function withdraw(address payable _to, uint256 _amount, string memory _reason) external;
function emergencyWithdraw(address payable _to, uint256 _amount, string memory _reason) external;

// Multi-signature
function createTransaction(address _to, uint256 _amount, string memory _reason, bytes memory _data) external;
function approveTransaction(uint256 _txId) external;
function executeTransaction(uint256 _txId) external;

// Budget va Grant
function createBudget(string memory _category, uint256 _amount, uint256 _duration) external;
function allocateBudget(uint256 _budgetId, uint256 _amount) external;
function createGrant(address _recipient, uint256 _amount, string memory _description) external returns (uint256);
```

**Konfiguratsiya:**

```solidity
uint256 public requiredSignatures = 3; // Multi-sig threshold
uint256 public emergencyThreshold = 100 ether; // Emergency limit
```

### 4. Voting Contract (`Voting.sol`)

**Ovoz berish turlari:**

```solidity
// Ovoz berish mexanizmlari
enum VotingMechanism {
    SimpleMajority,    // Oddiy ko'pchilik
    TokenWeighted,     // Token miqdoriga qarab
    Quadratic,         // Kvadrat ovoz berish
    Delegation,        // Delegatsiya asoslangan
    MultiPhase         // Ko'p bosqichli
}

// Funksiyalar
function castVote(uint256 _proposalId, uint8 _support, bytes memory _signature) external payable;
function castVoteWithDelegation(uint256 _proposalId, uint8 _support) external;
function delegateVoting(address _delegatee) external;
function createSnapshot(uint256 _proposalId) external;
```

### 5. Member Registry Contract (`MemberRegistry.sol`)

**A'zolar boshqaruvi:**

```solidity
// A'zo operatsiyalari
function addMember(address _member, string memory _role) external onlyOwner;
function verifyMember(address _member) external onlyOwner;
function suspendMember(address _member, string memory _reason) external onlyOwner;

// Role va permission
function createRole(string memory _role, string[] memory _permissions) external onlyOwner;
function hasPermission(address _member, string memory _permission) external view returns (bool);
```

---

## 🗳️ Ovoz Berish Mexanizmlari

### 1. Simple Majority (Oddiy Ko'pchilik)

**Qoidasi:** Eng ko'p ovoz olgan taraf g'olib

```javascript
// Foydalanish misoli
await dao.castVote(proposalId, 1); // 1 = For, 0 = Against, 2 = Abstain

// Natija hisoblash
if (votesFor > votesAgainst && votesFor >= quorum) {
    proposalState = "SUCCEEDED";
}
```

**Afzalliklari:**
- Oddiy va tez
- Eng kam gas xarajat
- Eng keng tarqalgan

**Kamchiliklari:**
- Ichki mayda hisobga olmaydi
- Katta investorslar haddan tashqari ta'sir qilishi mumkin

### 2. Token-Weighted Voting

**Qoidasi:** Token miqdoriga qarab ovoz quvvati

```javascript
// Voting power hisoblash
votingPower = tokenBalance + stakedTokens + delegatedTokens;

// Ovoz berish
await voting.castVote(proposalId, 1, "0x");

// Natija
totalVotingPower = sum(all voter voting powers);
proposalSuccess = votesFor > votesAgainst && votesFor >= quorum;
```

**Afzalliklari:**
- Konkret investment ko'rsatkichini aks ettiradi
- Professional qaror qabul qilish

**Kamchiliklari:**
- Eng katta tokensorlar g'olib chiqishi mumkin
- Democracy tamoyiliga zid

### 3. Quadratic Voting

**Qoidasi:** O'ziga xos voice allocation, cost = votes²

```javascript
// Quadratic voting misoli
const votingPower = 100; // 100 votes
const cost = votingPower * votingPower; // 10,000 wei

await voting.castVote(proposalId, 1, signature, {
    value: ethers.parseEther(cost / 1e18)
});
```

**Afzalliklari:**
- Har bir insonga bir xil ovoz beradi
- Sensitive issues uchun ideal
- Nodavomat effektlarni kamaytiradi

**Kamchiliklari:**
- Payment talab qilinadi
- Murakkab hisoblash
- Gas xarajati yuqori

### 4. Delegation-Based Voting

**Qoidasi:** Delegatlarga ovoz topshirish

```javascript
// Delegatsiya
await memberRegistry.delegateVoting(delegateeAddress);

// Delegat ovoz berish
await dao.castVote(proposalId, 1); // Delegatee's vote applies to all delegators

// Natijalar
delegatorVotingPower = delegatee's voting power;
```

**Afzalliklari:**
- Community representation
- Expertise-based voting
- Efficient decision making

**Kamchiliklari:**
- Delegat corruption risk
- Centralization risk

### 5. Multi-Phase Voting

**Qoidasi:** Bosqichma-bosqich qaror qabul qilish

```javascript
// Bosqich yaratish
await voting.startPhase(proposalId, 1, "Discussion Phase", 3 * 24 * 60 * 60); // 3 days
await voting.startPhase(proposalId, 2, "Voting Phase", 7 * 24 * 60 * 60); // 7 days

// Bosqichni o'tkazish
await voting.advancePhase(proposalId);
```

**Afzalliklari:**
- Progressive decision making
- Community engagement
- Quality control

**Kamchiliklari:**
- Uzoq vaqt davom etadi
- Murakkab boshqarish
- Coordination costs

---

## 💰 Kafolat (Treasury) Boshqaruvi

### Multi-Signature Operatsiyalar

**Xarajat jarayoni:**

1. **Create Transaction**
```javascript
const txId = await treasury.createTransaction(
    recipientAddress,
    amount,
    "Grant payment",
    transactionData
);
```

2. **Multiple Approvals**
```javascript
await treasury.approveTransaction(txId); // Admin 1
await treasury.approveTransaction(txId); // Admin 2
await treasury.approveTransaction(txId); // Admin 3 (final)
```

3. **Auto Execution**
```javascript
// Agar kerakli imzolashlar to'lsa, avtomatik bajariladi
```

### Budget Management

**Budget yaratish:**

```javascript
const budgetId = await treasury.createBudget(
    "Community Development",
    ethers.parseEther("50000"), // 50K tokens
    180 * 24 * 60 * 60 // 180 days
);
```

**Budget sarf qilish:**

```javascript
await treasury.spendBudget(
    budgetId,
    ethers.parseEther("10000"),
    "Community event funding"
);
```

### Grant Distribution

**Grant yaratish:**

```javascript
const grantId = await treasury.createGrant(
    recipientAddress,
    ethers.parseEther("25000"),
    "Blockchain education grant"
);
```

**Grant bajarish:**

```javascript
await treasury.executeGrant(grantId);
// Funds automatically transferred to recipient
```

---

## 👥 A'zolar Boshqaruvi

### Roles Va Permissions

**Role Hierarchy:**

```
Admin (10000 VP)
├── Treasury Manager (5000 VP)
├── Delegate (3000 VP)
├── Proposer (2000 VP)
├── Verified (1500 VP)
└── Member (1000 VP)
```

**Permission Matrix:**

```javascript
const permissions = {
    "admin": ["*"], // All permissions
    "treasury_manager": ["treasury.operate", "proposal.create"],
    "delegate": ["vote", "receive.delegation", "proposal.create"],
    "member": ["vote", "proposal.create"],
    "verified": ["vote", "proposal.create"],
    "auditor": ["read", "audit"]
};
```

### Verification Levels

**KYC/AML Tizimi:**

```javascript
enum VerificationStatus {
    None,       // 0 - No verification
    Email,      // 1 - Email verified
    Phone,      // 2 - Phone verified
    KYC,        // 3 - Full identity verified
    Premium     // 4 - High-value member
}
```

**Member Lifecycle:**

1. **Registration** → Pending verification
2. **KYC Process** → Document submission
3. **Verification** → Status upgrade
4. **Active Member** → Full participation rights
5. **Potential Suspension** → If rules violated

### Delegation System

**Delegatsiya qoidalari:**

```javascript
// Delegatsiya cheklovlari
MAX_DELEGATION_WEIGHT = 1000; // 1000x cap
delegationGracePeriod = 86400; // 24 hours before voting

// Delegation lifecycle
1. Start delegation
2. Cannot vote independently
3. Delegatee votes on behalf
4. Can revoke delegation anytime
5. 24h delay before new delegation
```

---

## 🔒 Xavfslik Tadbirlari

### Emergency Mechanisms

**Emergency Pause:**

```solidity
function emergencyPause() external onlyGuardian {
    require(block.timestamp >= lastEmergencyAction.add(emergencyCooldown), "Cooldown active");
    emergencyMode = true;
    _pause();
}
```

**Emergency Transfer:**

```solidity
function emergencyTransfer(address _to, uint256 _amount, string memory _reason) external onlyGuardian {
    require(emergencyMode, "Not in emergency mode");
    require(_amount <= emergencyThreshold, "Exceeds emergency limit");
    // Transfer funds to safe location
}
```

### Anti-Capture Protections

**Whale Control Detection:**

```solidity
function checkWhaleControl(uint256 _proposalId) external view returns (bool) {
    uint256 whalePercentage = (votesFor * 10000) / totalVotingPower;
    return whalePercentage > 5000; // > 50% triggers alert
}
```

**Delegation Limits:**

```solidity
function enforceDelegationLimits(address _delegatee, uint256 _proposalId) external view returns (bool) {
    uint256 totalWeight = getDelegatedWeight(_delegatee);
    return totalWeight <= MAX_DELEGATION_WEIGHT;
}
```

**Time Locking:**

```solidity
function activateTimeLock(address _target, uint256 _delay) external onlyOwner {
    timeLockEnd[proposalId] = block.timestamp.add(_delay);
}
```

### Input Validation

**Address Validation:**

```solidity
modifier validAddress(address _address) {
    require(_address != address(0), "Invalid address");
    require(_address.code.length > 0 || _address == tx.origin, "Contract address not allowed");
    _;
}
```

**Amount Validation:**

```solidity
modifier validAmount(uint256 _amount) {
    require(_amount > 0, "Amount must be positive");
    require(_amount <= type(uint256).max / 2, "Amount too large");
    _;
}
```

### Reentrancy Protection

**ReentrancyGuard:**

```solidity
contract DAO is IDAO, ReentrancyGuard {
    function castVote(uint256 _proposalId, uint8 support) external onlyMember nonReentrant {
        // Vote logic
    }
}
```

**Pull Payment Pattern:**

```solidity
// Instead of push payments
function withdraw() external nonReentrant {
    uint256 amount = pendingWithdrawals[msg.sender];
    pendingWithdrawals[msg.sender] = 0;
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success, "Transfer failed");
}
```

---

## 🔌 API Va Interface

### Contract Addresses (Example)

```javascript
const contracts = {
    mainnet: {
        DAO: "0x1234...",
        GovernanceToken: "0x5678...",
        Treasury: "0x9abc...",
        Voting: "0xdef0...",
        MemberRegistry: "0x1234..."
    },
    polygon: {
        DAO: "0xabcd...",
        // ... other addresses
    }
};
```

### JavaScript SDK

**Basic Setup:**

```javascript
import { ethers } from 'ethers';

// Provider setup
const provider = new ethers.JsonRpcProvider(process.env.RPC_URL);
const wallet = new ethers.Wallet(privateKey, provider);

// Contract instances
const dao = new ethers.Contract(DAO_ADDRESS, DAO_ABI, wallet);
const governanceToken = new ethers.Contract(GOV_TOKEN_ADDRESS, GOV_TOKEN_ABI, wallet);
const treasury = new ethers.Contract(TREASURY_ADDRESS, TREASURY_ABI, wallet);
```

**Common Operations:**

```javascript
// Create proposal
const tx = await dao.createProposal(
    title,
    description,
    encodedData,
    votingType,
    votingPeriod,
    requiredPower
);

// Cast vote
const voteTx = await dao.castVote(proposalId, support);

// Stake tokens
const stakeTx = await governanceToken.stake(amount, duration);

// Delegate voting
const delegateTx = await memberRegistry.delegateVoting(delegateeAddress);
```

### Python Integration

```python
from web3 import Web3
from eth_account import Account

# Setup
w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = Account.from_key(private_key)

# Contract interaction
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)
tx = contract.functions.createProposal(title, description, data).build_transaction({
    'from': account.address,
    'gas': 2000000,
    'gasPrice': w3.eth.gas_price,
    'nonce': w3.eth.get_transaction_count(account.address)
})

# Sign and send
signed_tx = account.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
```

---

## 🚀 Deployment Va Konfiguratsiya

### Network Configuration

**Mainnet (Ethereum):**

```javascript
module.exports = {
  networks: {
    mainnet: {
      url: process.env.MAINNET_RPC_URL,
      accounts: [process.env.PRIVATE_KEY],
      gas: "auto",
      gasPrice: "auto",
      timeout: 120000,
      confirmations: 3
    }
  }
};
```

**BSC (Binance Smart Chain):**

```javascript
bsc: {
  url: process.env.BSC_RPC_URL,
  chainId: 56,
  accounts: [process.env.PRIVATE_KEY],
  gasPrice: 5000000000, // 5 gwei
  timeout: 60000,
  confirmations: 3
}
```

### Environment Variables

```bash
# Required
PRIVATE_KEY=0x...
MAINNET_RPC_URL=https://...

# Optional
ETHERSCAN_API_KEY=...
BSCSCAN_API_KEY=...
REPORT_GAS=true
VERIFY_CONTRACTS=true
```

### Deployment Process

**1. Pre-deployment Check:**

```bash
# Check balance
npx hardhat run scripts/check-balance.js --network mainnet

# Verify gas costs
npm run gas-report

# Test on testnet first
npm run deploy:testnet
```

**2. Mainnet Deployment:**

```bash
# Deploy all contracts
npm run deploy:mainnet

# Verify contracts
npm run verify:contract

# Post-deployment setup
npm run setup:post-deployment
```

**3. Post-deployment Verification:**

```javascript
// Verify deployment
const deploymentInfo = require('./deployments/mainnet-deployment.json');

// Check contract ownership
const owner = await governanceToken.owner();
console.log("Token owner:", owner);

// Verify DAO permissions
const isAdmin = await dao.isAdmin(deployerAddress);
console.log("Deployer is admin:", isAdmin);

// Test basic functions
const balance = await treasury.getBalance();
console.log("Treasury balance:", ethers.formatEther(balance), "ETH");
```

---

## 🧪 Testing

### Test Categories

**Unit Tests:**

```javascript
describe("DAO Core", function () {
  it("Should add members correctly", async function () {
    await dao.connect(owner).addMember(addr1.address, "member");
    const member = await dao.getMember(addr1.address);
    expect(member.active).to.be.true;
  });

  it("Should prevent unauthorized access", async function () {
    await expect(
      dao.connect(addr1).updateQuorum(ethers.parseEther("500000"))
    ).to.be.revertedWith("Not admin");
  });
});
```

**Integration Tests:**

```javascript
describe("DAO Integration", function () {
  it("Should handle complete governance workflow", async function () {
    // 1. Add members
    await dao.addMember(addr1.address, "member");
    await dao.addMember(addr2.address, "delegate");

    // 2. Create proposal
    const proposalId = await createProposal("Test", "Description");

    // 3. Cast votes
    await dao.connect(addr1).castVote(proposalId, 1);
    await dao.connect(addr2).castVote(proposalId, 1);

    // 4. Execute proposal
    await timeTravel(7 * 24 * 60 * 60); // Advance time
    await dao.connect(owner).executeProposal(proposalId);

    const proposal = await dao.getProposal(proposalId);
    expect(proposal.executed).to.be.true;
  });
});
```

**Gas Optimization Tests:**

```javascript
describe("Gas Optimization", function () {
  it("Should not exceed gas limits", async function () {
    const tx = await dao.connect(owner).addMember(addr1.address, "member");
    const receipt = await tx.wait();
    
    expect(receipt.gasUsed).to.be.lessThan(100000);
  });
});
```

### Test Coverage

```bash
# Run all tests with coverage
npm run test:coverage

# Specific test categories
npm run test:unit
npm run test:integration
npm run test:security
npm run test:gas
```

**Coverage Goals:**
- Unit tests: >95%
- Integration tests: 100% of workflows
- Security tests: All vulnerability patterns
- Gas optimization: All public functions

---

## 📊 Monitoring Va Analytics

### On-Chain Metrics

**Governance Metrics:**

```javascript
// Dashboard data structure
const governanceMetrics = {
  totalMembers: 0,
  activeProposals: 0,
  totalVotingPower: 0,
  participationRate: 0,
  proposalSuccessRate: 0,
  averageVotingTime: 0,
  treasuryBalance: 0,
  monthlyBudgetUtilization: 0
};
```

**Member Activity:**

```javascript
const memberMetrics = {
  newMembers: 0,
  verifiedMembers: 0,
  delegations: 0,
  reputationChanges: 0,
  suspensions: 0
};
```

**Voting Analytics:**

```javascript
const votingAnalytics = {
  totalVotesCast: 0,
  delegationVotes: 0,
  quadraticVotes: 0,
  averageParticipation: 0,
  whaleControlAlerts: 0
};
```

### Off-Chain Analytics

**Community Engagement:**

```javascript
// Discord/Telegram integration
const communityMetrics = {
  discordMembers: 0,
  telegramMembers: 0,
  forumPosts: 0,
  governanceDiscussions: 0,
  proposalFeedback: 0
};
```

**Performance Metrics:**

```javascript
const performanceMetrics = {
  avgProposalTime: 0, // days from creation to execution
  governanceEfficiency: 0, // proposals executed / total
  treasuryROI: 0, // return on investments
  memberSatisfaction: 0, // survey scores
  technicalUptime: 0 // system availability
};
```

### Alert System

**Critical Alerts:**

```javascript
const alerts = {
  emergency: [
    "Emergency pause activated",
    "Large treasury withdrawal detected",
    "Governance attack detected"
  ],
  warning: [
    "Low participation rate",
    "Proposal deadline approaching",
    "Unusual voting patterns"
  ],
  info: [
    "New member joined",
    "Proposal created",
    "Voting threshold reached"
  ]
};
```

### Reporting

**Daily Reports:**

```javascript
// Automated daily report
const dailyReport = {
  date: new Date().toISOString(),
  proposals: {
    created: 2,
    active: 5,
    executed: 1,
    failed: 0
  },
  voting: {
    totalVotes: 15000,
    participationRate: 0.75,
    uniqueVoters: 45
  },
  treasury: {
    balance: "1,234,567.89 DAI",
    transactions: 3,
    amountSpent: "45,678.90 DAI"
  }
};
```

**Weekly Reports:**

```javascript
const weeklyReport = {
  period: "2024-01-01 to 2024-01-07",
  governance: {
    proposalsCreated: 8,
    proposalsExecuted: 6,
    averageExecutionTime: 4.2, // days
    governanceScore: 0.85 // 0-1 scale
  },
  community: {
    newMembers: 25,
    verifications: 18,
    delegations: 12,
    communityGrowth: 0.15 // 15% increase
  },
  financial: {
    budgetUtilization: 0.68,
    grantDisbursed: 125000,
    treasuryGrowth: 0.05
  }
};
```

---

## 🎯 Kelgusidagi Rivojlantirish

### Planned Features

**V2 Enhancements:**
- Layer 2 integration (Polygon, Arbitrum)
- NFT-based governance tokens
- Cross-chain treasury management
- AI-powered governance recommendations
- Mobile DAO governance app

**V3 Vision:**
- SubDAO support (nested DAOs)
- ZK-proof voting
- Automated governance execution
- DeFi protocol integration
- DAO merge/split capabilities

### Community Governance Evolution

**Current Phase:** Basic governance with voting and treasury
**Next Phase:** Advanced features with AI and cross-chain
**Future Phase:** Autonomous protocol evolution

---

## 📞 Yordam Va Dastak

**Texnik qo'llab-quvvatlash:**
- Email: tech@yourdao.org
- Discord: [DAO Governance](https://discord.gg/dao-governance)
- GitHub Issues: [Report bugs](https://github.com/your-org/dao-governance/issues)

**Community:**
- Telegram: @dao_governance
- Forum: [forum.yourdao.org](https://forum.yourdao.org)
- Documentation: [docs.yourdao.org](https://docs.yourdao.org)

**Aloqa:**
- Partnership: partners@yourdao.org
- Press: press@yourdao.org
- Security: security@yourdao.org

---

*Ushbu dokumentatsiya DAO Governance System ning to'liq texnik tavsifini beradi. Qo'shimcha savollar uchun community channels ga murojaat qiling.*