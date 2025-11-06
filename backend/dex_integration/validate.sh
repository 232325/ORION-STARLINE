#!/bin/bash

# Metal Tokenization System va DEX Integration - Validation Script
# Bu script loyihaning barcha komponentlarini test qiladi va validatsiya qiladi

echo "🚀 Metal Tokenization System va DEX Integration"
echo "=================================================="
echo "Validation script boshlanmoqda..."
echo ""

# Rangli chiqish uchun
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 1. Environment check
echo "🔍 1. Environment validation..."
echo "==================================="

# Node.js version check
NODE_VERSION=$(node --version 2>/dev/null)
if [ $? -eq 0 ]; then
    print_success "Node.js installed: $NODE_VERSION"
else
    print_error "Node.js topilmadi"
    exit 1
fi

# npm check
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_success "npm installed: $NPM_VERSION"
else
    print_error "npm topilmadi"
    exit 1
fi

# Hardhat check
if npx hardhat --version &> /dev/null; then
    HARDHAT_VERSION=$(npx hardhat --version)
    print_success "Hardhat installed: $HARDHAT_VERSION"
else
    print_error "Hardhat topilmadi"
    exit 1
fi

echo ""

# 2. Dependencies validation
echo "📦 2. Dependencies validation..."
echo "==================================="

if [ -f "package.json" ]; then
    print_success "package.json mavjud"
else
    print_error "package.json topilmadi"
    exit 1
fi

# Check if node_modules exists
if [ -d "node_modules" ]; then
    print_success "node_modules papkasi mavjud"
else
    print_warning "node_modules topilmadi. Dependencies o'rnatilmoqda..."
    npm install
    if [ $? -eq 0 ]; then
        print_success "Dependencies muvaffaqiyatli o'rnatildi"
    else
        print_error "Dependencies o'rnatishda xato"
        exit 1
    fi
fi

# Check critical dependencies
CRITICAL_DEPS=("@openzeppelin/contracts" "hardhat" "@nomicfoundation/hardhat-toolbox")
for dep in "${CRITICAL_DEPS[@]}"; do
    if [ -d "node_modules/$dep" ]; then
        print_success "Dependency topildi: $dep"
    else
        print_warning "Dependency topilmadi: $dep"
    fi
done

echo ""

# 3. Solidity contracts validation
echo "📜 3. Smart Contracts validation..."
echo "====================================="

# Check contract files
CONTRACT_FILES=(
    "contracts/MetalTokenizationSystem.sol"
    "contracts/tokens/MetalToken.sol"
    "contracts/tokens/MetalNFT.sol"
    "contracts/dex/DEXAggregator.sol"
    "contracts/amm/CustomMetalAMM.sol"
    "contracts/compliance/ComplianceRegistry.sol"
    "contracts/storage/MetalStorageVault.sol"
)

for file in "${CONTRACT_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "Contract topildi: $file"
    else
        print_error "Contract topilmadi: $file"
    fi
done

echo ""

# 4. Contract compilation
echo "🔨 4. Contract compilation..."
echo "============================="

# Compile contracts
npx hardhat compile
COMPILE_EXIT_CODE=$?

if [ $COMPILE_EXIT_CODE -eq 0 ]; then
    print_success "Barcha contractlar muvaffaqiyatli compile qilindi"
else
    print_error "Contract compilationda xato"
    exit 1
fi

echo ""

# 5. Test execution
echo "🧪 5. Test execution..."
echo "========================"

# Run tests
npx hardhat test
TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -eq 0 ]; then
    print_success "Barcha testlar muvaffaqiyatli o'tdi"
else
    print_error "Test executionda xato"
fi

echo ""

# 6. Gas optimization check
echo "⚡ 6. Gas optimization check..."
echo "==============================="

if npx hardhat test test/MetalTokenizationSystemTest.js --silent | grep -q "gas"; then
    print_info "Gas usage testi bajarildi"
else
    print_warning "Gas usage testi topilmadi"
fi

echo ""

# 7. Security validation
echo "🔒 7. Security validation..."
echo "============================"

# Check for common security patterns
SECURITY_CHECKS=(
    "modifier onlyAdmin"         # Admin access control
    "modifier whenNotPaused"     # Pause functionality
    "modifier nonReentrant"      # Reentrancy protection
    "require("                   # Input validation
    "SafeMath"                   # Safe math operations
)

for check in "${SECURITY_CHECKS[@]}"; do
    if grep -r "$check" contracts/ &> /dev/null; then
        print_success "Security pattern topildi: $check"
    else
        print_warning "Security pattern topilmadi: $check"
    fi
done

echo ""

# 8. Compliance features validation
echo "📋 8. Compliance features..."
echo "============================"

COMPLIANCE_PATTERNS=(
    "KYC"                        # Know Your Customer
    "AML"                        # Anti Money Laundering
    "ComplianceRegistry"         # Compliance system
    "freezeAccount"              # Account freezing
    "audit"                      # Audit functionality
)

for pattern in "${COMPLIANCE_PATTERNS[@]}"; do
    if grep -r "$pattern" contracts/ &> /dev/null; then
        print_success "Compliance feature topildi: $pattern"
    else
        print_warning "Compliance feature topilmadi: $pattern"
    fi
done

echo ""

# 9. DEX integration validation
echo "🔄 9. DEX integration features..."
echo "================================="

DEX_PATTERNS=(
    "UniswapV3"                 # Uniswap V3 integration
    "SushiSwap"                 # SushiSwap integration
    "PancakeSwap"               # PancakeSwap integration
    "DEXAggregator"             # DEX aggregator
    "swapTokens"                # Token swap functionality
)

for pattern in "${DEX_PATTERNS[@]}"; do
    if grep -r "$pattern" contracts/ &> /dev/null; then
        print_success "DEX integration topildi: $pattern"
    else
        print_warning "DEX integration topilmadi: $pattern"
    fi
done

echo ""

# 10. Metal tokenization validation
echo "🥇 10. Metal tokenization features..."
echo "====================================="

METAL_PATTERNS=(
    "MetalType"                 # Metal types
    "MetalToken"                # ERC-20 metal tokens
    "MetalNFT"                  # ERC-721 metal NFTs
    "physical backing"          # Physical backing
    "storage"                   # Storage functionality
)

for pattern in "${METAL_PATTERNS[@]}"; do
    if grep -r "$pattern" contracts/ &> /dev/null; then
        print_success "Metal tokenization topildi: $pattern"
    else
        print_warning "Metal tokenization topilmadi: $pattern"
    fi
done

echo ""

# 11. Documentation validation
echo "📚 11. Documentation validation..."
echo "=================================="

DOCUMENTATION_FILES=(
    "README.md"
    "docs/API_DOCUMENTATION.md"
    "package.json"
    "hardhat.config.js"
    "contracts/MetalTokenizationSystem.sol"
)

for file in "${DOCUMENTATION_FILES[@]}"; do
    if [ -f "$file" ]; then
        SIZE=$(wc -c < "$file")
        print_success "Documentation topildi: $file (${SIZE} bytes)"
    else
        print_warning "Documentation topilmadi: $file"
    fi
done

echo ""

# 12. Deployment scripts validation
echo "🚀 12. Deployment scripts..."
echo "============================"

DEPLOYMENT_SCRIPTS=(
    "scripts/deploy-local.js"
    "scripts/deploy-testnet.js"
    "scripts/deploy-mainnet.js"
)

for script in "${DEPLOYMENT_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        print_success "Deployment script topildi: $script"
    else
        print_warning "Deployment script topilmadi: $script"
    fi
done

echo ""

# 13. Test coverage validation
echo "📊 13. Test coverage..."
echo "======================"

if npx hardhat coverage --testFiles "test/MetalTokenizationSystemTest.js" &> /dev/null; then
    print_success "Test coverage hisobot tayyor"
else
    print_warning "Test coverage hisobot topilmadi"
fi

echo ""

# 14. Performance analysis
echo "⚡ 14. Performance analysis..."
echo "============================="

# Check for gas optimization patterns
GAS_PATTERNS=(
    "gas optimization"
    "bulk operations"
    "batch transactions"
    "circuit breaker"
    "MEV protection"
)

for pattern in "${GAS_PATTERNS[@]}"; do
    if grep -r -i "$pattern" contracts/ &> /dev/null; then
        print_success "Performance feature topildi: $pattern"
    else
        print_warning "Performance feature topilmadi: $pattern"
    fi
done

echo ""

# 15. Final summary
echo "📋 15. Final summary..."
echo "======================"

# Count statistics
TOTAL_CONTRACTS=$(find contracts/ -name "*.sol" | wc -l)
TOTAL_TESTS=$(find test/ -name "*.js" -o -name "*.sol" | wc -l)
TOTAL_SCRIPTS=$(find scripts/ -name "*.js" | wc -l)

print_info "Jami contractlar: $TOTAL_CONTRACTS"
print_info "Jami testlar: $TOTAL_TESTS"
print_info "Jami scriptlar: $TOTAL_SCRIPTS"

# Check project structure
REQUIRED_DIRS=("contracts" "interfaces" "utils" "test" "scripts" "docs")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        print_success "Papkaning mavjudligi: $dir/"
    else
        print_error "Papka topilmadi: $dir/"
    fi
done

echo ""

# Final validation result
echo "🎉 VALIDATION SUMMARY"
echo "====================="

if [ $COMPILE_EXIT_CODE -eq 0 ] && [ $TEST_EXIT_CODE -eq 0 ]; then
    print_success "Barcha asosiy validation testlar o'tdi!"
    print_success "Loyiha production ga tayyor!"
    echo ""
    print_info "Keyingi qadamlar:"
    echo "  1. npm install (agar kerak bo'lsa)"
    echo "  2. .env faylini to'g'ri sozlang"
    echo "  3. npx hardhat test"
    echo "  4. npx hardhat run scripts/deploy-local.js"
    echo ""
else
    print_error "Ba'zi validation testlar muvaffaqiyatsiz!"
    print_error "Iltimos xatolarni tuzating va qaytadan ishga tushiring."
fi

echo ""
echo "✨ Validation tugallandi!"
echo "Support: [your-support-email]"

# Return exit code based on validation result
if [ $COMPILE_EXIT_CODE -eq 0 ] && [ $TEST_EXIT_CODE -eq 0 ]; then
    exit 0
else
    exit 1
fi