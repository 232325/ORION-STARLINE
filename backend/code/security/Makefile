# Smart Contract Security & Gas Optimization System
# Makefile for easy project management

.PHONY: help install compile test test-security test-gas deploy deploy-testnet deploy-mainnet security-analysis gas-analysis clean docs format lint

# Default target
.DEFAULT_GOAL := help

# Configuration
NETWORK ?= testnet
RPC_URL ?= 
PRIVATE_KEY ?=
ETHERSCAN_API_KEY ?=

# Colors for output
BOLD := \033[1m
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BOLD)Smart Contract Security & Gas Optimization System$(NC)"
	@echo "$(BOLD)=====================================================$(NC)"
	@echo ""
	@echo "$(BLUE)Available commands:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BLUE)Setup commands:$(NC)"
	@echo "  $(GREEN)install$(NC)        Install dependencies and setup environment"
	@echo ""
	@echo "$(BLUE)Development commands:$(NC)"
	@echo "  $(GREEN)compile$(NC)        Compile all contracts with optimizations"
	@echo "  $(GREEN)test$(NC)           Run all tests"
	@echo "  $(GREEN)test-security$(NC)  Run security-focused tests"
	@echo "  $(GREEN)test-gas$(NC)       Run gas optimization tests"
	@echo "  $(GREEN)test-all$(NC)       Run comprehensive test suite"
	@echo ""
	@echo "$(BLUE)Security commands:$(NC)"
	@echo "  $(GREEN)security-analysis$(NC) Run security analysis tools"
	@echo "  $(GREEN)gas-analysis$(NC)     Run gas analysis tools"
	@echo ""
	@echo "$(BLUE)Deployment commands:$(NC)"
	@echo "  $(GREEN)deploy$(NC)          Deploy to local network"
	@echo "  $(GREEN)deploy-testnet$(NC)  Deploy to testnet"
	@echo "  $(GREEN)deploy-mainnet$(NC)  Deploy to mainnet (DANGER!)"
	@echo ""
	@echo "$(BLUE)Utility commands:$(NC)"
	@echo "  $(GREEN)clean$(NC)           Clean all build files"
	@echo "  $(GREEN)docs$(NC)            Generate documentation"
	@echo "  $(GREEN)format$(NC)          Format code"
	@echo "  $(GREEN)lint$(NC)            Lint code"
	@echo "  $(GREEN)coverage$(NC)        Generate coverage report"

install: ## Install dependencies and setup environment
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@curl -L https://foundry.paradigm.xyz | bash
	@source ~/.bashrc && foundryup
	@pip3 install slither-analyzer mythx-cli web3 eth-account
	@echo "$(GREEN)Dependencies installed successfully!$(NC)"

compile: ## Compile all contracts with optimizations
	@echo "$(BLUE)Compiling contracts...$(NC)"
	@forge build --optimize --optimizer-runs 200
	@echo "$(GREEN)Contracts compiled successfully!$(NC)"

test: ## Run all tests
	@echo "$(BLUE)Running all tests...$(NC)"
	@forge test --gas-report --coverage

test-security: ## Run security-focused tests
	@echo "$(BLUE)Running security tests...$(NC)"
	@forge test --match-path tests/SecuredTokenTest.t.sol --gas-report
	@forge test --match-path tests/SecureDEXTest.t.sol --gas-report
	@echo "$(GREEN)Security tests completed!$(NC)"

test-gas: ## Run gas optimization tests
	@echo "$(BLUE)Running gas tests...$(NC)"
	@forge test --gas-report
	@./scripts/gas_analysis.sh
	@echo "$(GREEN)Gas tests completed!$(NC)"

test-all: ## Run comprehensive test suite
	@echo "$(BLUE)Running comprehensive test suite...$(NC)"
	@./scripts/run_comprehensive_tests.sh

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	@forge test --match-path tests/SecuredTokenTest.t.sol --gas-report

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	@forge test --match-path tests/SecureDEXTest.t.sol

test-fuzz: ## Run fuzzing tests
	@echo "$(BLUE)Running fuzzing tests...$(NC)"
	@forge test --match-path tests/*Test.t.sol --fuzz-runs 10000

security-analysis: ## Run security analysis tools
	@echo "$(BLUE)Running security analysis...$(NC)"
	@./scripts/run_security_analysis.sh

gas-analysis: ## Run gas analysis tools
	@echo "$(BLUE)Running gas analysis...$(NC)"
	@./scripts/gas_analysis.sh

analyze: security-analysis gas-analysis ## Run both security and gas analysis

clean: ## Clean all build files
	@echo "$(BLUE)Cleaning build files...$(NC)"
	@forge clean
	@rm -rf out/ cache/ test-results/ gas-analysis/ security-reports/
	@rm -f gas-report.txt coverage-report.json
	@echo "$(GREEN)Clean completed!$(NC)"

docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	@forge doc --build

format: ## Format code
	@echo "$(BLUE)Formatting code...$(NC)"
	@forge fmt

lint: ## Lint code
	@echo "$(BLUE)Linting code...$(NC)"
	@slither . --print human-summary
	@solhint contracts/*.sol

lint-fix: format lint ## Format code and fix linting issues

coverage: ## Generate coverage report
	@echo "$(BLUE)Generating coverage report...$(NC)"
	@forge coverage --report summary > coverage-report.txt
	@echo "$(GREEN)Coverage report generated: coverage-report.txt$(NC)"

deploy: ## Deploy to local network
	@echo "$(BLUE)Deploying to local network...$(NC)"
	@./scripts/deploy_secure.sh

deploy-testnet: ## Deploy to testnet
	@echo "$(RED)Deploying to testnet...$(NC)"
	@echo "Network: $(NETWORK)"
	@echo "RPC: $(RPC_URL)"
	@NETWORK=testnet ./scripts/deploy_secure.sh

deploy-mainnet: ## Deploy to mainnet (DANGER!)
	@echo "$(RED)WARNING: This will deploy to mainnet!$(NC)"
	@echo "Network: mainnet"
	@read -p "Are you sure you want to continue? [y/N]: " confirm && [ "$$confirm" = "y" ]
	@NETWORK=mainnet ./scripts/deploy_secure.sh

# Security monitoring commands
monitor-setup: ## Setup monitoring for contracts
	@echo "$(BLUE)Setting up monitoring...$(NC)"
	@echo "Monitoring setup commands would go here"

monitor-alerts: ## Configure monitoring alerts
	@echo "$(BLUE)Configuring monitoring alerts...$(NC)"
	@echo "Alert configuration commands would go here"

# Utility commands
check: compile test lint ## Run all checks (compile, test, lint)

setup: install compile test ## Complete setup (install, compile, test)

dev: clean compile test-gas ## Development workflow

security-audit: clean test-all security-analysis ## Full security audit workflow

production: clean test-all security-analysis gas-analysis deploy-testnet ## Production preparation workflow

# Debug commands
debug-test: ## Run tests with debug output
	@echo "$(BLUE)Running tests with debug output...$(NC)"
	@forge test -vvv --gas-report

debug-gas: ## Debug gas usage
	@echo "$(BLUE)Debugging gas usage...$(NC)"
	@forge test --gas-report --debug

# Performance testing
performance: ## Run performance tests
	@echo "$(BLUE)Running performance tests...$(NC)"
	@forge test --match-path tests/*Test.t.sol --fuzz-runs 50000

# Maintenance commands
update: ## Update dependencies
	@echo "$(BLUE)Updating dependencies...$(NC)"
	@forge update
	@pip3 install --upgrade slither-analyzer mythx-cli

audit-deps: ## Audit dependencies for vulnerabilities
	@echo "$(BLUE)Auditing dependencies...$(NC)"
	@pip3 list --outdated
	@npm audit || true

# CI/CD commands
ci: clean compile test-all security-analysis ## CI/CD pipeline
	@echo "$(GREEN)CI pipeline completed successfully!$(NC)"

ci-security: security-analysis ## Security-focused CI pipeline
	@echo "$(GREEN)Security CI pipeline completed!$(NC)"

# Local development commands
serve: ## Start local development server
	@echo "$(BLUE)Starting local development server...$(NC)"
	@python3 -m http.server 8080 || true

# Contract verification
verify: ## Verify contracts on Etherscan
	@echo "$(BLUE)Verifying contracts...$(NC)"
	@forge verify-contract CONTRACT_ADDRESS CONTRACT_NAME --etherscan-api-key $(ETHERSCAN_API_KEY) --chain-id 1

verify-testnet: ## Verify contracts on testnet
	@echo "$(BLUE)Verifying contracts on testnet...$(NC)"
	@forge verify-contract CONTRACT_ADDRESS CONTRACT_NAME --etherscan-api-key $(ETHERSCAN_API_KEY) --chain-id 11155111

# Backup and restore
backup: ## Create backup of important files
	@echo "$(BLUE)Creating backup...$(NC)"
	@tar -czf backup-$(shell date +%Y%m%d-%H%M%S).tar.gz contracts/ tests/ docs/ foundry.toml
	@echo "$(GREEN)Backup created!$(NC)"

# Database operations (if needed)
db-reset: ## Reset local database/state
	@echo "$(BLUE)Resetting database...$(NC)"
	@rm -rf .foundry/ chain.db || true
	@echo "$(GREEN)Database reset!$(NC)"

# Status commands
status: ## Show project status
	@echo "$(BOLD)Project Status$(NC)"
	@echo "=================="
	@echo "Contracts: $$(find contracts -name "*.sol" | wc -l) files"
	@echo "Tests: $$(find tests -name "*.t.sol" | wc -l) files"
	@echo "Scripts: $$(find scripts -name "*.sh" | wc -l) files"
	@echo "Documentation: $$(find docs -name "*.md" | wc -l) files"
	@echo "Network: $$(NETWORK)"
	@echo "Dependencies: $$(forge --version | head -1)"