# 🤝 Contributing to Orion Starline

Orion Starline jamoasiga xush kelibsiz! Bu qo'llanma sizga loyihaga qanday hissa qo'shishni o'rgatadi.

## 📋 Mundarija

- [Code of Conduct](#code-of-conduct)
- [Development Setup](#development-setup)
- [Contributing Workflow](#contributing-workflow)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)

## 📜 Code of Conduct

Biz barcha hisso qo'shuvchilarga hurmat bilan munosabatda bo'lishimizni kutamiz. Har qanday shovinistik, tazyiq qiluvchi yoki takabburlik xatti-harakatlarga yo'l qo'yilmaydi.

### Bizning standartlarimiz
- Hurmatli va inklyuziv til
- Konstruktiv feedback
- Fokusning professional maqsadda bo'lishi
- Boshqa hamjihatning hurmati

## 🚀 Development Setup

### 1. Repository-ni fork qilish
```bash
# Fork qiling: https://github.com/your-username/orion-starline
git clone https://github.com/your-username/orion-starline.git
cd orion-starline

# Original repo-ni upstream sifatida qo'shing
git remote add upstream https://github.com/original-repo/orion-starline.git
```

### 2. Development environment
```bash
# Frontend
cd frontend
npm install

# Backend
cd ../backend
pip install -r requirements.txt

# Setup
cp .env.example .env
# .env faylni muharrir bilan oching
```

### 3. Create development branch
```bash
git checkout -b feature/your-feature-name
# yoki
git checkout -b fix/bug-description
# yoki
git checkout -b improvement/enhancement-name
```

## 🔄 Contributing Workflow

### 1. Sync with upstream
```bash
git fetch upstream
git checkout main
git merge upstream/main
```

### 2. Create feature branch
```bash
git checkout -b feature/amazing-feature
```

### 3. Make changes
- Kod yozing
- Testlarni qo'shing
- Documentation yangilang

### 4. Commit changes
```bash
git add .
git commit -m "feat: add amazing feature

- Feature description
- Implementation details
- Testing notes"
```

### 5. Push to your fork
```bash
git push origin feature/amazing-feature
```

### 6. Create Pull Request
GitHub orqali Pull Request yarating.

## 💻 Code Standards

### Frontend (TypeScript/React)
```typescript
// File: src/components/TradingCard.tsx
import React from 'react';

interface TradingCardProps {
  symbol: string;
  price: number;
  change: number;
  onAction: (action: string) => void;
}

/**
 * Trading card component for displaying market data
 */
export const TradingCard: React.FC<TradingCardProps> = ({
  symbol,
  price,
  change,
  onAction,
}) => {
  const isPositive = change >= 0;
  
  return (
    <div className="card">
      <h3>{symbol}</h3>
      <p className={isPositive ? 'text-green' : 'text-red'}>
        ${price.toFixed(2)} ({change.toFixed(2)}%)
      </p>
      <button onClick={() => onAction('trade')}>
        Trade
      </button>
    </div>
  );
};
```

### Backend (Python)
```python
# File: app/models/trading.py
from sqlalchemy import Column, Integer, String, Float
from app.db.base import Base

class TradingPosition(Base):
    """Trading position model"""
    __tablename__ = "trading_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    side = Column(String)  # LONG or SHORT
    size = Column(Float)
    entry_price = Column(Float)
    current_price = Column(Float)
    pnl = Column(Float)
    
    def calculate_pnl(self) -> float:
        """Calculate PnL for the position"""
        if self.side == "LONG":
            return (self.current_price - self.entry_price) * self.size
        else:
            return (self.entry_price - self.current_price) * self.size
```

### Naming Conventions
- **Branches**: `feature/description`, `fix/issue`, `improvement/enhancement`
- **Commits**: Conventional commits (feat, fix, docs, style, refactor, test, chore)
- **Files**: camelCase for JS/TS, snake_case for Python

### Code Style

#### Frontend
```bash
# ESLint va Prettier configuration
npm run lint
npm run format
```

#### Backend
```bash
# Black, isort, flake8
black app/
isort app/
flake8 app/
```

## 🧪 Testing Guidelines

### Frontend Testing
```typescript
// File: src/components/__tests__/TradingCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { TradingCard } from '../TradingCard';

describe('TradingCard', () => {
  it('should display symbol and price correctly', () => {
    render(
      <TradingCard
        symbol="BTCUSDT"
        price={46000}
        change={2.5}
        onAction={jest.fn()}
      />
    );
    
    expect(screen.getByText('BTCUSDT')).toBeInTheDocument();
    expect(screen.getByText('$46,000.00')).toBeInTheDocument();
  });
});
```

### Backend Testing
```python
# File: tests/test_trading.py
import pytest
from app.models.trading import TradingPosition

def test_calculate_pnl_long_position():
    position = TradingPosition(
        symbol="BTCUSDT",
        side="LONG",
        size=0.1,
        entry_price=45000,
        current_price=46000
    )
    
    pnl = position.calculate_pnl()
    assert pnl == 100.0  # (46000 - 45000) * 0.1
```

### Test Coverage
```bash
# Test coverage check
npm run test:coverage
```

Minimum test coverage: 80%

## 📚 Documentation

### Code Documentation
```typescript
/**
 * Calculate technical indicators for trading signals
 * @param prices Array of historical prices
 * @param period RSI calculation period
 * @returns RSI value between 0-100
 */
export function calculateRSI(prices: number[], period: number = 14): number {
  // Implementation
}
```

### API Documentation
Swagger/OpenAPI hujjatlari yangilab turishi kerak:
```yaml
# /docs/api.yaml
paths:
  /api/v1/positions:
    get:
      summary: Get trading positions
      responses:
        200:
          description: List of positions
          schema:
            type: array
            items:
              $ref: '#/definitions/Position'
```

### README Updates
Yangi xususiyat qo'shgan bo'lsam, README.md yangilab turishim kerak.

## 🔍 Pull Request Process

### 1. Pre-submit checklist
- [ ] Code follows project standards
- [ ] Tests are written and passing
- [ ] Documentation is updated
- [ ] No console.log() in production code
- [ ] Environment variables documented
- [ ] Breaking changes noted

### 2. PR Description
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
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Code is well-commented
- [ ] Documentation updated
```

### 3. Review Process
1. **Automated checks** must pass
2. **Code review** by maintainer
3. **Testing** in development environment
4. **Approval** from reviewer
5. **Merge** to main branch

### 4. After Merge
- [ ] Delete feature branch
- [ ] Update related documentation
- [ ] Announce changes if significant

## 🐛 Issue Guidelines

### Bug Reports
```markdown
**Bug Description**
Clear description of the issue

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected Behavior**
What should happen

**Screenshots**
If applicable

**Environment**
- OS: [e.g. macOS Big Sur]
- Browser: [e.g. Chrome 96]
- Version: [e.g. 2.0.0]
```

### Feature Requests
```markdown
**Feature Description**
Clear description of the desired feature

**Problem Statement**
What problem does this solve?

**Proposed Solution**
How should this work?

**Alternatives Considered**
Other solutions considered

**Additional Context**
Any other context or screenshots
```

## 📋 Commit Message Convention

### Format
```
type(scope): subject

body (optional)

footer (optional)
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### Examples
```bash
feat(trading): add grid trading algorithm

- Implement grid trading strategy
- Add risk management features
- Update API documentation

Closes #123

fix(portfolio): calculate PnL correctly

- Fix floating point precision issue
- Add unit test for edge cases

BREAKING CHANGE: PnL calculation now returns decimal
```

## 🎯 Priority Areas for Contribution

### High Priority
- AI trading algorithms
- Security improvements
- Performance optimization
- Mobile app features

### Medium Priority
- UI/UX improvements
- Documentation
- Testing infrastructure
- Deployment automation

### Good First Issues
- Documentation improvements
- Bug fixes
- Code refactoring
- Test coverage

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- GitHub contributors page
- Project release notes
- Annual contributor awards

## ❓ Getting Help

- **Discord**: [Join our Discord](https://discord.gg/orionstarline)
- **GitHub Discussions**: For questions
- **Issues**: For bugs and features
- **Email**: contributors@orionstarline.com

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Rahmat! Har bir hissa muhim va qadr qilinadi! 🚀**