# DAO Governance System 🚀

## 📖 Loyiha tavsifi

**DAO Governance System** - bu Decentralized Autonomous Organization (DAO) boshqaruvi uchun to'liq integratsiyalashgan blockchain tizim. Ushbu tizim markazlashtirilmagan boshqaruv, ovoz berish mexanizmlari, kafolat (treasury) boshqaruvi va a'zolar boshqaruvini ta'minlaydi.

### 🎯 Asosiy xususiyatlari

- ✅ **Markazlashtirilmagan boshqaruv** - To'liq otomatik DAO boshqaruvi
- 🗳️ **Turli xil ovoz berish turlari** - Token-weighted, Quadratic, Delegation-based
- 💰 **Multi-signature treasury** - Xavfsiz kafolat boshqaruvi
- 👥 **A'zolar ro'yxati** - Verification va KYC tizimi
- 🔒 **Timelock mexanizmlari** - Xavfsizlik va protection
- 📊 **Snapshot-based governance** - Tarixiy voting power tracking
- 🛡️ **Anti-capture mexanizmlari** - Whale control va delegation limiting

## 🏗️ Tizim arxitekturasi

### Smart Contract tarkibi

```
contracts/
├── DAO.sol                 # Asosiy DAO boshqaruv kontrakti
├── GovernanceToken.sol     # Governance va staking token
├── Treasury.sol            # Kafolat boshqaruvi
├── Voting.sol              # Ovoz berish mexanizmlari
├── MemberRegistry.sol      # A'zolar ro'yxati
└── interfaces/             # Contract interfeyslari
    ├── IDAO.sol
    ├── IGovernanceToken.sol
    ├── ITreasury.sol
    └── IVoting.sol
```

### Asosiy komponentlar

#### 1. **DAO Contract** (`DAO.sol`)
- Proposal yaratish va boshqaruvi
- Ovoz berish natijalarini hisoblash
- Emergency funksiyalar
- Quorum va threshold management

#### 2. **GovernanceToken** (`GovernanceToken.sol`)
- ERC20 governance token
- Staking va reward tizimi
- Voting power multipliers
- Distribution va vesting

#### 3. **Treasury** (`Treasury.sol`)
- Multi-signature xarajatlar
- Budget allocation
- Grant distribution
- Emergency fund management

#### 4. **Voting** (`Voting.sol`)
- Token-weighted voting
- Quadratic voting
- Delegation-based voting
- Multi-phase voting
- Anti-capture mechanisms

#### 5. **MemberRegistry** (`MemberRegistry.sol`)
- Member verification
- Role-based permissions
- KYC/AML integration
- Reputation system

## 🚀 O'rnatish va ishga tushirish

### Talablar

- Node.js 18+
- npm yoki yarn
- Git

### O'rnatish

```bash
# Repository ni clone qilish
git clone https://github.com/your-org/dao-governance-system.git
cd dao-governance-system

# Dependencies o'rnatish
npm install

# Environment variables ni sozlash
cp .env.example .env
# .env faylini to'g'ri ma'lumotlar bilan to'ldiring
```

### Development

```bash
# Smart contract'lar compile qilish
npm run compile

# Test'lar ishga tushirish
npm test

# Local network'da deploy qilish
npm run deploy:local

# Coverage report
npm run coverage
```

### Production Deploy

```bash
# Ethereum testnet (Goerli)
npm run deploy:testnet

# Ethereum mainnet
npm run deploy:mainnet

# Boshqa networklar uchun
npm run deploy:bsc
npm run deploy:polygon
npm run deploy:arbitrum
```

## 📚 Foydalanish

### 1. DAO'ni sozlash

```javascript
// DAO contract initializatsiya
const DAO = await ethers.getContractFactory("DAO");
const dao = await DAO.deploy();
await dao.deployed();

// Guardian address o'rnatish
await dao.setGuardianAddress(ownerAddress);

// Admin qo'shish
await dao.addAdmin(proposerAddress);
```

### 2. Member qo'shish

```javascript
// Yangi a'zo qo'shish
await dao.addMember(memberAddress, "member");

// Delegat qilish
await dao.delegateVoting(delegateAddress);
```

### 3. Proposal yaratish

```javascript
// Yangi taklif yaratish
const proposalId = await dao.createProposal(
    "Proposall nomi",
    "Proposall tavsifi",
    proposalData, // Contract call uchun encoded data
    0, // Simple voting
    7 * 24 * 60 * 60, // 7 kun voting period
    ethers.parseEther("1000") // Minimum 1000 voting power
);
```

### 4. Ovoz berish

```javascript
// Oddiy ovoz berish
await dao.castVote(proposalId, 1); // 0: against, 1: for, 2: abstain

// Quadratic voting
await voting.castVote(proposalId, 1, signature, {
    value: ethers.parseEther("10") // Payment required
});
```

### 5. Treasury operatsiyalari

```javascript
// Kafolatga mablag' qo'shish
await treasury.deposit("Initial funding", {
    value: ethers.parseEther("100")
});

// Xarajat yaratish
const txId = await treasury.createTransaction(
    recipientAddress,
    ethers.parseEther("50"),
    "Grant payment",
    transactionData
);

// Transaction imzolash
await treasury.approveTransaction(txId);
```

## 🗳️ Ovoz berish turlari

### 1. **Simple Majority**
- Oddiy ko'pchilik ovoz berish
- Eng oddiy va tez ovoz berish tizimi

### 2. **Token-Weighted**
- Token miqdoriga qarab voting power
- Professional investorlar uchun

### 3. **Quadratic Voting**
- O'ziga xos voice allocation
- Sensitive issues uchun ideal
- Payment required (cost = votes²)

### 4. **Delegation-Based**
- Delegatlarga ovoz topshirish
- Community representation
- Anti-capture limits

### 5. **Multi-Phase Voting**
- Progressive decision making
- Complex proposals uchun
- Phase-by-phase confirmation

## 💰 Treasury boshqaruvi

### Multi-Signature operatsiyalar
- Kerakli imzolashlar soni: 3 (default)
- Emergency threshold: 100 ETH (default)
- Budget allocation systems
- Grant distribution programs

### Xarajat turlari
- **Budget Allocation**: Maqsadli budjetlar
- **Grant Distribution**: Community grants
- **Operational Expenses**: Kunlik operatsiyalar
- **Emergency Funds**: Favqulodda xarajatlar

## 👥 A'zolar boshqaruvi

### Roles va Permissions
- **Admin**: Full access
- **Treasury Manager**: Treasury operations
- **Delegate**: Voting delegation
- **Member**: Basic voting rights
- **Verified**: Enhanced voting power
- **Auditor**: Read-only access

### Verification levels
- **None**: Basic member
- **Email**: Email verified
- **Phone**: Phone verified
- **KYC**: Full identity verified
- **Premium**: High-value member

## 🔒 Xavfsizlik xususiyatlari

### Emergency mechanisms
- **Emergency Pause**: Barcha funksiyalarni to'xtatish
- **Guardian Address**: Emergency control
- **Time Delays**: Unauthorized changes prevent
- **Multi-Signature**: Critical operations require multiple approvals

### Anti-capture protections
- **Delegation Limits**: Max 1000x delegation weight
- **Whale Detection**: 50%+ control alerts
- **Time Locking**: Delegation grace periods
- **Snapshot Protection**: Historical vote protection

## 📊 Monitoring va Analytics

### On-chain metrics
- Total voting power
- Participation rates
- Proposal success rates
- Treasury balance tracking
- Member activity metrics

### Off-chain analytics
- Community engagement
- Governance efficiency
- Financial sustainability
- Security incident tracking

## 🧪 Testing

### Test categories
```bash
# Unit tests
npm run test:unit

# Integration tests
npm run test:integration

# End-to-end tests
npm run test:e2e

# Gas optimization tests
npm run test:gas

# Security audit tests
npm run test:security
```

### Test coverage
- Unit tests: >95% coverage
- Integration tests: All workflows
- Security tests: Vulnerability scanning
- Performance tests: Gas optimization

## 🔧 Configuration

### Network settings
```javascript
// hardhat.config.js
networks: {
  mainnet: {
    url: process.env.MAINNET_RPC_URL,
    accounts: [process.env.PRIVATE_KEY],
    gas: "auto",
    gasPrice: "auto"
  }
}
```

### Contract parameters
```javascript
const config = {
  quorum: ethers.parseEther("1000000"), // 1M voting power
  votingPeriod: 7 * 24 * 60 * 60, // 7 days
  timelockDelay: 24 * 60 * 60, // 1 day
  maxProposalsPerMember: 5,
  emergencyThreshold: ethers.parseEther("100") // 100 ETH
};
```

## 🐛 Troubleshooting

### Common issues

**Deployment fails**
- Check gas limit and network congestion
- Verify private key and RPC URLs
- Ensure sufficient ETH for deployment

**Voting not working**
- Verify member verification status
- Check proposal timing and periods
- Confirm sufficient voting power

**Treasury transactions stuck**
- Check required signatures count
- Verify multi-sig wallet configuration
- Review emergency cooldown periods

### Support resources
- 📚 [Documentation](docs/)
- 💬 [Community Discord](https://discord.gg/dao-governance)
- 🐛 [Issue Tracker](https://github.com/your-org/dao-governance/issues)
- 📧 [Email Support](support@yourdao.org)

## 🤝 Contributing

### Development workflow
1. Fork the repository
2. Create feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit pull request

### Code standards
- Solidity: 0.8.19+
- Testing: 95%+ coverage
- Documentation: All public functions
- Security: No known vulnerabilities

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenZeppelin team for secure contract libraries
- Compound Governance for governance patterns inspiration
- Ethereum community for decentralized governance research
- All contributors and community members

---

**DAO Governance System** - Markazlashtirilmagan boshqaruv kelajagi uchun! 🚀