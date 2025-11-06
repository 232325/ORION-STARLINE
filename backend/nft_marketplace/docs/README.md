# MetalNFT Marketplace 🚀

## Qimmatbop Metallarga Asoslangan NFT Bozor

Bu loyiha qimmatbop metallarga (oltin, kumush, платина, palladiy) asoslangan autentik NFT tokenlari uchun to'liq integratsiyalashgan NFT bozor platformasi hisoblanadi.

## ✨ Asosiy Xususiyatlar

### 🔗 NFT Marketplace Integration
- **OpenSea API Integration** - global bozorda mavjudlik va sinxronizatsiya
- **Foundation Marketplace** - premium san'at va collector pieces
- **SuperRare Integration** - eksklyuziv digital san'at asarlari
- **Rarible Marketplace** - multi-chain NFT trading
- **Custom Marketplace** - o'z platformada savdo qilish imkoniyati

### 🥇 Physical Metal-backed NFTs
- **Real Metal Backing** - har bir NFT real metallga bog'langan
- **Gold Storage Verification** - oltin aktivlari uchun vault tasdiqlash
- **Silver Vault Certificates** - kumush sertifikalari
- **Platinum Authentication** - платина autentifikatsiya
- **Palladium Custody NFTs** - palladiy custody tokenlari
- **Blockchain Proof of Ownership** - blockchain da mulk huquqi isboti

### 🛡️ Metal Certification System
- **On-chain Assay Certificates** - zanjir ustida assay sertifikalari
- **Purity Verification** - metall tozaligi tekshiruvi
- **Storage Facility Audits** - saqlash facility auditlari
- **Insurance Integration** - sug'urta integratsiyasi
- **Legal Framework Compliance** - qonuniy compliance

### 💰 NFT Trading Features
- **Metal NFT Auctions** - metall NFT auctionlari
- **Fixed Price Listings** - qat'iy narxda ro'yxat
- **Secondary Market Liquidity** - ikkilamchi bozor likvidligi
- **Price Discovery Mechanisms** - narx aniqlash mexanizmlari
- **Royalty Distributions** - royalty taqsimoti

### ⚙️ Technical Implementation
- **ERC-721 Metal Token Standard** - ERC-721 metall token standardi
- **Metadata Schemas for Metals** - metall uchun metadata sxemalari
- **IPFS Storage Integration** - IPFS saqlash integratsiyasi
- **Oracle Price Feeds** - oracle narx feedlari
- **Smart Contract Automation** - smart contract avtomatizatsiya

## 🏗️ Arxitektura

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │   Navbar        │ │   HomePage      │ │  Marketplace    │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │  Portfolio      │ │ CreateListing   │ │    Auction      │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │ Certification   │ │ MetalDetails    │ │    Footer       │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                         Web3 Context
                              │
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND SERVICES                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │ Certification   │ │ Price Oracle    │ │  Webhook API    │   │
│  │ System          │ │ Service         │ │                 │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    SMART CONTRACTS                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │   MetalNFT      │ │   Marketplace   │ │   Royalty       │   │
│  │   (ERC-721)     │ │                 │ │   Management    │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     BLOCKCHAIN LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  Ethereum Mainnet / Sepolia Testnet                            │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Loyiha Struktura

```
code/nft_marketplace/
├── contracts/                    # Smart Contracts
│   ├── MetalNFT.sol             # Asosiy NFT contract
│   └── MetalNFTMarketplace.sol  # Bozor contract
├── frontend/                     # React Frontend
│   └── metal-nft-marketplace/
│       ├── src/
│       │   ├── components/      # React Components
│       │   ├── contexts/        # React Contexts
│       │   ├── pages/          # Page Components
│       │   └── App.tsx         # Main App
├── backend/                     # Backend Services
│   └── metal_certification_system.py
├── api/                         # Marketplace API Integrations
│   ├── opensea_integration.py
│   ├── foundation_integration.py
│   └── superrare_rarible_integration.py
├── config/                      # Configuration Files
│   └── config.js
├── docs/                       # Documentation
└── tests/                      # Test Files
```

## 🛠️ O'rnatish va Sozlash

### 1. Smart Contract Deploy qilish

```bash
# Hardhat install qilish
npm install -g hardhat

# Dependencies install qilish
npm install @openzeppelin/contracts

# Contract compile qilish
npx hardhat compile

# Testnet ga deploy qilish
npx hardhat run scripts/deploy.js --network sepolia
```

### 2. Frontend Sozlash

```bash
cd frontend/metal-nft-marketplace

# Dependencies install qilish
npm install

# Development server ishga tushirish
npm run dev

# Production build
npm run build
```

### 3. Backend Sozlash

```bash
cd backend

# Python dependencies install qilish
pip install aiohttp asyncio dataclasses

# Metal certification system ishga tushirish
python metal_certification_system.py
```

### 4. API Keys Sozlash

`config/config.js` faylida quyidagi API keylarni sozlang:

```javascript
// OpenSea API
OPENSEA_API_KEY=your_opensea_api_key

// Foundation API
FOUNDATION_API_KEY=your_foundation_api_key

// SuperRare API
SUPERRARE_API_KEY=your_superrare_api_key

// IPFS (Pinata)
PINATA_API_KEY=your_pinata_api_key
```

## 💻 Foydalanish

### NFT Yaratish

1. **Metall Melting va Assay** - laboratoriyada metall sinov
2. **Storage Certificate** - saqlash facility dan certificate olish
3. **NFT Mint** - blockchain da NFT yaratish
4. **Metadata IPFS** - metadata ni IPFS ga saqlash
5. **Marketplace Listing** - bozorda savdoga qo'yish

### Savdo Jarayoni

1. **Fixed Price Listing** - qat'iy narxda ro'yxat
2. **Auction Listing** - auction formatida ro'yxat
3. **Bid Placements** - bid qo'yish
4. **Sale Completion** - savdoni yakunlash
5. **Royalty Distribution** - royalty taqsimoti

### Certification Process

1. **Assay Verification** - laboratoriya tekshiruvi
2. **Storage Verification** - saqlash tekshiruvi
3. **Audit Process** - auditor tekshiruvi
4. **Legal Compliance** - qonuniy compliance
5. **On-chain Certification** - zanjir ustida certification

## 🔗 API Integratsiya

### OpenSea Integration

```python
from api.opensea_integration import OpenSeaAPI

# OpenSea API dan foydalanish
opensea = OpenOpenSeaAPI("your_api_key")
assets = await opensea.get_assets(collection="metal-nft")
```

### Foundation Integration

```python
from api.foundation_integration import FoundationAPI

# Foundation dan foydalanish
foundation = FoundationAPI()
artworks = await foundation.get_artworks(limit=20)
```

### SuperRare Integration

```python
from api.superrare_rarible_integration import SuperRareAPI

# SuperRare dan foydalanish
superrare = SuperRareAPI()
artworks = await superrare.get_artworks(status="available")
```

## 🛡️ Xavfsizlik

### Smart Contract Xavfsizligi
- **ReentrancyGuard** - reentrancy hujumlardan himoya
- **Access Control** - owner va authorized verifiers
- **Input Validation** - barcha inputlarni validatsiya
- **Safe Math** - overflow himoyasi

### Web3 Xavfsizligi
- **Wallet Integration** - MetaMask va boshqa walletlar
- **Transaction Signing** - tranzaksiya imzolash
- **Private Key Protection** - private key himoyasi
- **Network Verification** - to'g'ri tarmoqni tekshirish

## 📊 Metrikl va Analytics

### Platform Statistics
- **Total Volume** - jami savdo hajmi
- **Active Listings** - aktiv ro'yxatlar soni
- **Floor Price** - eng past narx
- **Royalty Earnings** - royalty daromadlari

### Metal Statistics
- **Gold NFT Count** - oltin NFT soni
- **Silver NFT Count** - kumush NFT soni
- **Platinum NFT Count** - платина NFT soni
- **Verification Rate** - tasdiqlash darajasi

## 🔧 Konfiguratsiya

Barcha konfiguratsiya `config/config.js` faylida mavjud:

```javascript
// Smart contract addresses
METAL_NFT_CONTRACT = "0x..."
MARKETPLACE_CONTRACT = "0x..."

// API keys
OPENSEA_API_KEY = "..."
FOUNDATION_API_KEY = "..."

// Platform settings
PLATFORM_FEE_PERCENTAGE = 2.5
MAX_AUCTION_DURATION = 2592000
```

## 🚀 Deployment

### Production Deployment

1. **Smart Contracts** - mainnet ga deploy qilish
2. **Frontend** - Vercel yoki Netlify ga deploy
3. **Backend** - AWS EC2 yoki Heroku ga deploy
4. **Database** - PostgreSQL va Redis sozlash
5. **Monitoring** - logging va monitoring

### Environment Variables

`.env` faylida quyidagi o'zgaruvchilarni sozlang:

```bash
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
PRIMARY_RPC_URL=https://...
JWT_SECRET=...
```

## 📚 Hujjatlar

- [API Reference](./docs/api-reference.md)
- [Smart Contract Documentation](./docs/contracts.md)
- [Frontend Guide](./docs/frontend.md)
- [Deployment Guide](./docs/deployment.md)

## 🤝 Hissa qo'shish

1. Repository ni fork qiling
2. Feature branch yarating (`git checkout -b feature/amazing-feature`)
3. O'zgarishlaringizni commit qiling (`git commit -m 'Add amazing feature'`)
4. Branch ni push qiling (`git push origin feature/amazing-feature`)
5. Pull Request yarating

## 📄 Litsenziya

Bu loyiha MIT litsenziyasi ostida tarqatiladi. Batafsil ma'lumot uchun `LICENSE` faylini ko'ring.

## 📞 Yordam

Agar savollaringiz bo'lsa:
- GitHub Issues oching
- Email: support@metalnft.com
- Discord: [MetalNFT Community](https://discord.gg/metalnft)

## 🎯 Kelajak Rejalar

- [ ] Cross-chain integration (Polygon, BSC)
- [ ] Mobile app (React Native)
- [ ] AI-powered price prediction
- [ ] Advanced analytics dashboard
- [ ] Staking mechanism
- [ ] DAO governance
- [ ] Carbon neutral certification
- [ ] Real-time metal prices

---

**MetalNFT** - qimmatbop metallarga asoslangan NFT bozorining kelajagi! 🥇