# Orion Starline Mobile App

![React Native](https://img.shields.io/badge/React_Native-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![iOS](https://img.shields.io/badge/iOS-000000?style=for-the-badge&logo=ios&logoColor=white)
![Android](https://img.shields.io/badge/Android-3DDC84?style=for-the-badge&logo=android&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Expo](https://img.shields.io/badge/Expo-1B1F3A?style=for-the-badge&logo=expo&logoColor=white)

## 📱 Loyiha Haqida

**Orion Starline** - bu ilg'or AI texnologiyalari bilan jihozlangan professional trading platforma. Bu React Native mobil ilovasi iOS va Android qurilmalar uchun to'liq optimallashgan bo'lib, real-time trading, portfolio boshqaruvi, va aqlli trading signallari imkoniyatlarini taklif qiladi.

### ✨ Asosiy Xususiyatlar

- **🤖 AI-Powered Trading Signals** - Orion Starline AI tomonidan generatsiya qilingan trading signallari
- **🔒 Biometrik Autentifikatsiya** - Touch ID va Face ID yordamida xavfsiz kirish
- **📡 Real-time Data** - Real-vaqt ma'lumotlar va narxlarni kuzatish
- **📊 Portfolio Tracking** - Portfolio boshqaruvi va P&L kuzatuvi
- **🔔 Push Notifications** - Trading alerts va bildirishnomalar
- **📱 Responsive Design** - Barcha ekran o'lchamlari uchun optimallashgan
- **⚡ Offline Mode** - Internet aloqasi bo'lmaganda ham ishlaydi
- **🌍 iOS & Android Support** - Ikkala platform uchun to'liq qo'llab-quvvatlash

## 🚀 Tez Boshlanish

### O'rnatish

```bash
# Repository ni clone qilish
git clone https://github.com/orion-starline/mobile-app.git
cd mobile-app

# Dependencies ni o'rnatish
npm install

# Expo CLI ni global o'rnatish (agar yo'q bo'lsa)
npm install -g expo-cli
```

### Ishga Tushirish

```bash
# Development server ni ishga tushirish
expo start

# iOS Simulator da ishga tushirish
expo start --ios

# Android Emulator da ishga tushirish
expo start --android

# Web versiyada
expo start --web
```

### Expo Go bilan Test

1. **iOS**: App Store dan "Expo Go" app ni yuklab oling
2. **Android**: Google Play Store dan "Expo Go" app ni yuklab oling
3. QR kod ni skaner qiling yoki manual kiritish

## 🏗️ Arxitektura

### Fayl Struktura

```
mobile/
├── mobile_app.py          # Asosiy ilova komponenti
├── mobile_ui.py           # UI komponentlari va dizayn sistemasi
├── mobile_features.py     # Barcha xususiyatlar va servislar
├── package.json           # Dependencies va konfiguratsiya
├── assets/                # Ikonkalar va rasmlar
│   ├── icon.png
│   ├── splash.png
│   └── notification-icon.png
├── src/
│   ├── components/        # Qayta ishlatiladigan komponentlar
│   ├── screens/           # Bosh sahifalar
│   ├── services/          # API va servislar
│   ├── utils/             # Yordamchi funktsiyalar
│   ├── hooks/             # Custom hooks
│   └── types/             # TypeScript tip определения
└── __tests__/            # Unit testlar
```

### Texnologiyalar Stack

#### Core
- **React Native 0.72** - UI Framework
- **Expo 49** - Development Platform
- **TypeScript** - Type Safety
- **React Navigation** - Navigation

#### UI & Styling
- **React Native Elements** - UI Components
- **React Native Vector Icons** - Icon Library
- **Expo Linear Gradient** - Gradient Support
- **React Native Chart Kit** - Charts & Graphs

#### Services
- **AsyncStorage** - Local Data Storage
- **SecureStore** - Sensitive Data Storage
- **Expo Notifications** - Push Notifications
- **Expo Location** - GPS Location
- **Expo Camera** - Camera & QR Scanner

#### State Management
- **React Context** - Global State
- **React Hooks** - Local State
- **AsyncStorage** - Persistence

## 📋 Functionality

### 🔐 Authentication
- Foydalanuvchi login/logout
- Biometrik autentifikatsiya (Touch ID/Face ID)
- Offline authentication
- Secure token storage

### 📊 Trading Interface
- Real-time price monitoring
- Buy/Sell order placement
- Stop-loss va Take-profit settings
- Market analysis tools
- Trading signals dashboard

### 📈 Portfolio Management
- Position tracking
- P&L calculation
- Risk management
- Performance analytics
- Export capabilities

### 🔔 Notifications
- Trading alerts
- Market updates
- Price alerts
- System notifications
- Custom notification settings

### 🌐 Connectivity
- Real-time WebSocket connection
- Offline data caching
- Background sync
- Network status monitoring

### 🎯 Advanced Features
- QR code scanner
- Document scanning
- Face recognition
- Accelerometer monitoring
- Device security features

## 🔧 Konfiguratsiya

### Environment Variables

`.env` faylida quyidagi o'zgaruvchilarni sozlang:

```env
API_URL=https://api.orion-starline.com
WS_URL=wss://ws.orion-starline.com
ENVIRONMENT=production
EXPO_PUBLIC_API_URL=https://api.orion-starline.com
```

### Expo Configuration

`app.json` faylida ilova sozlamalarini boshqaring:

```json
{
  "expo": {
    "name": "Orion Starline",
    "slug": "orion-starline-mobile",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#1e3a8a"
    }
  }
}
```

## 🏗️ Build va Deploy

### Development Build

```bash
# iOS uchun
expo run:ios

# Android uchun
expo run:android
```

### Production Build

```bash
# EAS Build ni sozlang
eas build:configure

# iOS uchun production build
eas build --platform ios --profile production

# Android uchun production build
eas build --platform android --profile production

# Web uchun
eas build --platform web --profile production
```

### App Store Deploy

```bash
# iOS
eas submit --platform ios

# Google Play Store
eas submit --platform android
```

## 🧪 Testing

### Unit Tests

```bash
# Barcha testlarni ishga tushirish
npm test

# Coverage report
npm run test:coverage
```

### E2E Testing

```bash
# Detox bilan E2E testlar
npm run test:e2e:ios
npm run test:e2e:android
```

### Manual Testing

```bash
# Expo Doctor - konfiguratsiya tekshirish
expo doctor

# Performance monitoring
npm run test:performance
```

## 🔒 Xavfsizlik

### Data Protection
- Sensitive ma'lumotlar SecureStore da
- Biometric authentication
- Certificate pinning
- SSL/TLS encryption

### Best Practices
- Input validation
- Secure coding practices
- Regular security audits
- Dependency vulnerability scanning

### Permissions

Ilova quyidagi ruxsatlarni so'raydi:

```xml
<!-- Android permissions -->
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.USE_FINGERPRINT" />
<uses-permission android:name="android.permission.USE_BIOMETRIC" />

<!-- iOS permissions -->
<key>NSFaceIDUsageDescription</key>
<string>Face ID for secure access</string>
```

## 📊 Performance

### Optimizations
- Lazy loading
- Image optimization
- Memory management
- Battery optimization
- Network optimization

### Metrics
- App launch time
- Memory usage
- Network requests
- Battery consumption
- Crash reports

## 🛠️ Development

### Code Style

```bash
# Linting
npm run lint

# Format code
npm run format

# Type checking
npm run type-check
```

### Git Workflow

```bash
# Feature branch yaratish
git checkout -b feature/new-feature

# Changes commit
git commit -m "feat: add new trading feature"

# Push va PR
git push origin feature/new-feature
```

### Debug Tools

- **Flipper** - React Native debugger
- **Reactotron** - Development console
- **Expo DevTools** - Expo development
- **Chrome DevTools** - Web debugging

## 📚 API Integration

### Trading API

```typescript
// Trading operations
POST /api/trade
GET /api/positions
PUT /api/positions/:id
DELETE /api/positions/:id
```

### Market Data API

```typescript
// Real-time market data
GET /api/market-data
GET /api/symbols/:symbol/price
GET /api/symbols/:symbol/history
```

### User API

```typescript
// User management
POST /api/auth/login
POST /api/auth/logout
GET /api/user/profile
PUT /api/user/profile
```

## 🔄 Updates & Maintenance

### Over-the-Air Updates

```bash
# OTA update yuborish
expo publish

# Specific version uchun
expo publish --release-channel production
```

### Monitoring

- **Crashlytics** - Crash monitoring
- **Analytics** - User behavior
- **Performance** - App metrics
- **Logs** - Error tracking

## 🆘 Troubleshooting

### Common Issues

#### Build Errors

```bash
# Clean build
expo install --fix

# Clear cache
expo r -c

# Reset Metro bundler
npx react-native start --reset-cache
```

#### Permission Issues

```bash
# iOS - Clean build folder
cd ios && xcodebuild clean

# Android - Clean gradle
cd android && ./gradlew clean
```

#### Network Issues

```bash
# Network debugging
expo doctor --network-config

# Debug mode
expo start --debug
```

## 🤝 Contributing

### Contribution Guidelines

1. Fork the repository
2. Create feature branch
3. Follow code standards
4. Add tests for new features
5. Submit pull request

### Development Setup

```bash
# Fork va clone
git clone https://github.com/your-username/mobile-app.git

# Setup development environment
npm install

# Run development server
expo start
```

### Code Standards

- ESLint rules
- Prettier formatting
- TypeScript strict mode
- Component documentation
- Test coverage requirements

## 📄 License

MIT License - Batafsil ma'lumot uchun [LICENSE](LICENSE) faylini ko'ring.

## 📞 Support

### Contact Information

- **Email**: support@orion-starline.com
- **Website**: https://orion-starline.com
- **Documentation**: https://docs.orion-starline.com
- **Discord**: https://discord.gg/orion-starline

### FAQ

#### Q: Biometrik autentifikatsiya ishlamayapti?
A: Device settings da Face ID/Touch ID yoqilganligini va app permissions ni tekshiring.

#### Q: Offline rejim qanday ishlaydi?
A: App ma'lumotlarni local storage da saqlaydi va internet aloqasi bo'lganda sync qiladi.

#### Q: Push bildirishnomalar kelmayapti?
A: Notification permissions va background app refresh settings ni tekshiring.

#### Q: Trading signallar qanday ishlaydi?
A: AI algoritmi real-time market data tahlil qilib trading signallar generatsiya qiladi.

## 🎯 Roadmap

### Version 1.1 (Q1 2025)
- [ ] Advanced charting tools
- [ ] Multi-language support
- [ ] Dark mode
- [ ] Widget support

### Version 1.2 (Q2 2025)
- [ ] AI trading bot
- [ ] Social trading features
- [ ] Advanced risk management
- [ ] Cryptocurrency support

### Version 2.0 (Q3 2025)
- [ ] DeFi integration
- [ ] NFT trading
- [ ] Cross-chain support
- [ ] Advanced analytics

## 🙏 Acknowledgments

- **React Native Community** - Framework va tools
- **Expo Team** - Development platform
- **TradingView** - Charting solutions
- **Firebase** - Push notifications
- **AWS** - Cloud infrastructure

---

**Made with ❤️ by Orion Starline AI Trading System**

*Professional AI-Powered Trading Platform*