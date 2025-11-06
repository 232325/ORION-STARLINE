#!/bin/bash

# Orion Starline Mobile App Deployment Script
# iOS va Android uchun avtomatik build va deploy

set -e  # Exit on any error

echo "🚀 Orion Starline Mobile App Deployment"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="Orion Starline"
BUILD_TYPE=${BUILD_TYPE:-"staging"}  # staging, production
PLATFORM=${PLATFORM:-"all"}  # ios, android, web, all
VERSION=${1:-$(node -p "require('./package.json').version")}
BUILD_NUMBER=${BUILD_NUMBER:-$(date +%Y%m%d%H%M%S)}

# Check if required environment variables are set
check_env_vars() {
    echo "🔍 Checking environment variables..."
    
    if [ "$BUILD_TYPE" = "production" ]; then
        required_vars=(
            "EXPO_PROJECT_ID"
            "IOS_CERTIFICATE_PATH" 
            "IOS_CERTIFICATE_PASSWORD"
            "ANDROID_KEYSTORE_PATH"
            "ANDROID_KEYSTORE_PASSWORD"
            "ANDROID_KEYSTORE_ALIAS"
        )
        
        for var in "${required_vars[@]}"; do
            if [ -z "${!var}" ]; then
                echo -e "${RED}❌ Error: $var is not set${NC}"
                exit 1
            fi
        done
    fi
    
    echo -e "${GREEN}✅ Environment variables OK${NC}"
}

# Install dependencies
install_dependencies() {
    echo "📦 Installing dependencies..."
    
    # Install npm dependencies
    npm ci
    
    # Install Expo CLI if not present
    if ! command -v expo &> /dev/null; then
        echo "Installing Expo CLI..."
        npm install -g @expo/cli
    fi
    
    # Clear Expo cache
    expo r -c
    
    echo -e "${GREEN}✅ Dependencies installed${NC}"
}

# Pre-build checks
pre_build_checks() {
    echo "🔍 Running pre-build checks..."
    
    # Check Node.js version
    node_version=$(node -v)
    required_version="v18"
    if [[ "$(printf '%s\n' "$required_version" "$node_version" | sort -V | head -n1)" == "$required_version" ]]; then
        echo "✅ Node.js version OK: $node_version"
    else
        echo -e "${RED}❌ Node.js version must be >= $required_version${NC}"
        exit 1
    fi
    
    # Check if package.json exists
    if [ ! -f "package.json" ]; then
        echo -e "${RED}❌ package.json not found${NC}"
        exit 1
    fi
    
    # Validate Expo configuration
    if ! expo doctor &> /dev/null; then
        echo -e "${YELLOW}⚠️  Expo doctor found some issues, continuing anyway${NC}"
    else
        echo "✅ Expo configuration OK"
    fi
    
    echo -e "${GREEN}✅ Pre-build checks passed${NC}"
}

# Build for specific platform
build_ios() {
    echo "🍎 Building for iOS..."
    
    if [ "$BUILD_TYPE" = "production" ]; then
        echo "Building iOS for production..."
        eas build --platform ios --profile production --non-interactive
    else
        echo "Building iOS for staging..."
        eas build --platform ios --profile staging --non-interactive
    fi
    
    echo -e "${GREEN}✅ iOS build completed${NC}"
}

build_android() {
    echo "🤖 Building for Android..."
    
    if [ "$BUILD_TYPE" = "production" ]; then
        echo "Building Android for production..."
        eas build --platform android --profile production --non-interactive
    else
        echo "Building Android for staging..."
        eas build --platform android --profile staging --non-interactive
    fi
    
    echo -e "${GREEN}✅ Android build completed${NC}"
}

build_web() {
    echo "🌐 Building for Web..."
    
    if [ "$BUILD_TYPE" = "production" ]; then
        echo "Building web for production..."
        eas build --platform web --profile production --non-interactive
    else
        echo "Building web for staging..."
        eas build --platform web --profile staging --non-interactive
    fi
    
    echo -e "${GREEN}✅ Web build completed${NC}"
}

# Submit to app stores
submit_ios() {
    echo "📱 Submitting to App Store..."
    
    if [ "$BUILD_TYPE" = "production" ]; then
        echo "Submitting to production App Store..."
        eas submit --platform ios --profile production --non-interactive
    else
        echo "Submitting to TestFlight..."
        eas submit --platform ios --profile staging --non-interactive
    fi
    
    echo -e "${GREEN}✅ iOS submission completed${NC}"
}

submit_android() {
    echo "🤖 Submitting to Google Play..."
    
    if [ "$BUILD_TYPE" = "production" ]; then
        echo "Submitting to production Google Play..."
        eas submit --platform android --profile production --non-interactive
    else
        echo "Submitting to internal testing..."
        eas submit --platform android --profile staging --non-interactive
    fi
    
    echo -e "${GREEN}✅ Android submission completed${NC}"
}

# Run tests
run_tests() {
    echo "🧪 Running tests..."
    
    # Type checking
    echo "Running TypeScript type checking..."
    npx tsc --noEmit
    
    # Linting
    echo "Running ESLint..."
    npm run lint
    
    # Unit tests
    echo "Running unit tests..."
    npm test
    
    echo -e "${GREEN}✅ All tests passed${NC}"
}

# Generate build info
generate_build_info() {
    echo "📋 Generating build info..."
    
    build_info_file="build-info.json"
    
    cat > "$build_info_file" << EOF
{
  "appName": "$APP_NAME",
  "version": "$VERSION",
  "buildNumber": "$BUILD_NUMBER",
  "buildType": "$BUILD_TYPE",
  "platform": "$PLATFORM",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "gitCommit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
  "gitBranch": "$(git branch --show-current 2>/dev/null || echo 'unknown')",
  "nodeVersion": "$(node -v)",
  "npmVersion": "$(npm -v)",
  "expoVersion": "$(expo --version)"
}
EOF
    
    echo "Build info saved to $build_info_file"
    cat "$build_info_file"
    
    echo -e "${GREEN}✅ Build info generated${NC}"
}

# Cleanup
cleanup() {
    echo "🧹 Cleaning up..."
    
    # Clear Metro cache
    npx react-native start --reset-cache &
    sleep 2
    kill $!
    
    # Remove temporary files
    find . -name "*.log" -type f -delete 2>/dev/null || true
    find . -name "*.tmp" -type f -delete 2>/dev/null || true
    
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Main deployment flow
main() {
    echo "Starting deployment process..."
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                echo "Usage: $0 [VERSION] [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --platform PLATFORM     Platform to build (ios, android, web, all) [default: all]"
                echo "  --build-type TYPE       Build type (staging, production) [default: staging]"
                echo "  --build-number NUM      Custom build number [auto-generated]"
                echo "  --skip-tests           Skip running tests"
                echo "  --submit               Submit to app stores after build"
                echo "  --help, -h             Show this help"
                echo ""
                echo "Environment variables:"
                echo "  BUILD_TYPE             Build type (staging, production)"
                echo "  PLATFORM              Platform (ios, android, web, all)"
                exit 0
                ;;
            --platform)
                PLATFORM="$2"
                shift 2
                ;;
            --build-type)
                BUILD_TYPE="$2"
                shift 2
                ;;
            --build-number)
                BUILD_NUMBER="$2"
                shift 2
                ;;
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --submit)
                SUBMIT=true
                shift
                ;;
            *)
                VERSION="$1"
                shift
                ;;
        esac
    done
    
    echo -e "${BLUE}📋 Deployment Configuration:${NC}"
    echo "   App Name: $APP_NAME"
    echo "   Version: $VERSION"
    echo "   Build Type: $BUILD_TYPE"
    echo "   Platform: $PLATFORM"
    echo "   Build Number: $BUILD_NUMBER"
    echo ""
    
    # Run deployment steps
    check_env_vars
    install_dependencies
    pre_build_checks
    
    if [ "$SKIP_TESTS" != "true" ]; then
        run_tests
    fi
    
    generate_build_info
    
    # Build for specified platform(s)
    case "$PLATFORM" in
        ios)
            build_ios
            if [ "$SUBMIT" = "true" ]; then
                submit_ios
            fi
            ;;
        android)
            build_android
            if [ "$SUBMIT" = "true" ]; then
                submit_android
            fi
            ;;
        web)
            build_web
            ;;
        all)
            build_ios
            build_android
            build_web
            if [ "$SUBMIT" = "true" ]; then
                submit_ios
                submit_android
            fi
            ;;
        *)
            echo -e "${RED}❌ Invalid platform: $PLATFORM${NC}"
            echo "Valid platforms: ios, android, web, all"
            exit 1
            ;;
    esac
    
    cleanup
    
    echo ""
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo -e "${GREEN}📱 App: $APP_NAME v$VERSION ($BUILD_TYPE)${NC}"
    echo -e "${GREEN}🏗️  Build: $BUILD_NUMBER${NC}"
    echo -e "${GREEN}📦 Platform: $PLATFORM${NC}"
    
    if [ "$SUBMIT" = "true" ]; then
        echo -e "${GREEN}✅ Apps submitted to stores${NC}"
    fi
}

# Error handling
trap 'echo -e "\n${RED}❌ Deployment failed!${NC}" >&2; exit 1' ERR

# Run main function
main "$@"