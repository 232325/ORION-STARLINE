# DAO Governance System - Fayllar Ro'yxati

## 📁 Loyiha Strukturasi

```
code/dao_governance/
├── 📄 PROJECT_SUMMARY.md          # Loyiha xulosa va ma'lumotlari
├── 📄 README.md                   # Asosiy qo'llanma
├── 📄 package.json               # Project dependencies va scripts
├── 📄 hardhat.config.js          # Hardhat konfiguratsiyasi
├── 📄 .env.example               # Environment variables namuna
│
├── 📁 contracts/                 # Smart Contracts (5 ta)
│   ├── 📄 DAO.sol                # Asosiy DAO boshqaruv kontrakti
│   ├── 📄 Treasury.sol           # Multi-signature kafolat boshqaruvi
│   ├── 📄 Voting.sol             # Ovoz berish mexanizmlari
│   ├── 📄 GovernanceToken.sol    # ERC20 governance va staking token
│   └── 📄 MemberRegistry.sol     # A'zolar ro'yxati va verification
│
├── 📁 interfaces/                # Contract Interfaces (4 ta)
│   ├── 📄 IDAO.sol               # DAO asosiy interfeysi
│   ├── 📄 ITreasury.sol          # Treasury boshqaruv interfeysi
│   ├── 📄 IVoting.sol            # Ovoz berish tizimi interfeysi
│   └── 📄 IGovernanceToken.sol   # Governance token interfeysi
│
├── 📁 scripts/                   # Deployment Scripts (2 ta)
│   ├── 📄 deploy.js              # Asosiy deployment script
│   └── 📄 advanced-deploy.js     # Kengaytirilgan deployment script
│
├── 📁 test/                      # Test Files (1 ta)
│   └── 📄 DAOGovernanceSystem.test.js # To'liq test suite
│
├── 📁 docs/                      # Documentation (1 ta)
│   └── 📄 TECHNICAL_DOCUMENTATION.md  # Texnik dokumentatsiya
│
└── 📁 config/                    # Configuration (bo'sh)
    └── 📄 (Configuration files kelgusi foydalanish uchun)
```

## 📊 Statistika

**Jami fayllar:** 15 ta fayl  
**Jami kod satrlari:** 3,045+  
**Smart contracts:** 5 ta  
**Interfaces:** 4 ta  
**Test fayllar:** 1 ta  
**Dokumentatsiya:** 2 ta  
**Scripts:** 2 ta  

## 🚀 Tez boshlanish

```bash
# 1. Dependencies o'rnatish
npm install

# 2. Environment sozlash
cp .env.example .env
# .env faylini to'ldiring

# 3. Contracts compile qilish
npm run compile

# 4. Test ishga tushirish
npm test

# 5. Local deployment
npm run deploy:local

# 6. Coverage report
npm run coverage
```

## 📋 Asosiy Funksiyalar

### DAO Contract (DAO.sol)
- ✅ A'zolar boshqaruvi
- ✅ Proposal yaratish va boshqaruvi
- ✅ Ovoz berish mexanizmlari
- ✅ Emergency funksiyalar
- ✅ Quorum va threshold management

### Treasury Contract (Treasury.sol)
- ✅ Multi-signature operatsiyalar
- ✅ Budget allocation
- ✅ Grant distribution
- ✅ Emergency fund management
- ✅ Transaction approval workflow

### Voting Contract (Voting.sol)
- ✅ Simple majority voting
- ✅ Token-weighted voting
- ✅ Quadratic voting
- ✅ Delegation-based voting
- ✅ Multi-phase voting
- ✅ Anti-capture protections

### GovernanceToken Contract (GovernanceToken.sol)
- ✅ ERC20 governance token
- ✅ Staking va reward tizimi
- ✅ Voting power multipliers
- ✅ Distribution va vesting
- ✅ Lock mechanisms

### MemberRegistry Contract (MemberRegistry.sol)
- ✅ Member verification
- ✅ Role-based permissions
- ✅ KYC/AML integration
- ✅ Reputation system
- ✅ Delegation management

## 🔧 Development Commands

```bash
# Code linting
npm run lint

# Gas report
npm run gas-report

# Contract flattening
npm run flatten

# Contract verification
npm run verify:contract

# Deploy to testnet
npm run deploy:testnet

# Deploy to mainnet
npm run deploy:mainnet
```

## 📚 Hujjatlar

1. **[README.md](README.md)** - Asosiy qo'llanma va quick start
2. **[TECHNICAL_DOCUMENTATION.md](docs/TECHNICAL_DOCUMENTATION.md)** - Batafsil texnik dokumentatsiya
3. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Loyiha xulosa va statistika

## 🤝 Community

- **Discord:** [DAO Governance Community](https://discord.gg/dao-governance)
- **Telegram:** [@dao_governance](https://t.me/dao_governance)
- **GitHub:** [Issues va Pull Requests](https://github.com/your-org/dao-governance)

## 📞 Yordam

- **Texnik Support:** tech@yourdao.org
- **Security Issues:** security@yourdao.org
- **Community Manager:** community@yourdao.org

---

**Bu tizim to'liq ishlaydigan DAO governance system bo'lib, barcha kerakli funksiyalar implementatsiya qilingan!** 🎉