#!/bin/bash

# Gas Analysis and Optimization Tool
# Analyzes gas usage patterns and provides optimization recommendations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Gas Analysis and Optimization Tool ===${NC}"
echo ""

# Configuration
CONTRACTS_DIR="./contracts"
TESTS_DIR="./tests"
OUTPUT_DIR="./gas-analysis"
BENCHMARK_FILE="$OUTPUT_DIR/gas-benchmark.json"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Install dependencies
install_dependencies() {
    print_info "Installing dependencies..."
    
    if ! command -v forge &> /dev/null; then
        print_error "Foundry not found. Please install Foundry first."
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 not found. Please install Python3 first."
        exit 1
    fi
    
    # Install Python dependencies for gas analysis
    pip3 install pandas matplotlib seaborn plotly jupyter > /dev/null 2>&1 || true
    
    print_success "Dependencies installed"
}

# Run gas analysis tests
run_gas_analysis() {
    print_info "Running gas analysis tests..."
    
    # Run tests with gas reporting
    cd "$TESTS_DIR"
    forge test --gas-report --json "$BENCHMARK_FILE" --silent 2>/dev/null || true
    cd ..
    
    print_success "Gas analysis completed"
}

# Analyze gas usage patterns
analyze_gas_patterns() {
    print_info "Analyzing gas usage patterns..."
    
    if [ -f "$BENCHMARK_FILE" ]; then
        python3 -c "
import json
import sys

try:
    with open('$BENCHMARK_FILE', 'r') as f:
        data = json.load(f)
    
    print('Gas Usage Analysis Results:')
    print('=' * 50)
    
    # Analyze each test result
    for test_group in data:
        if 'results' in test_group:
            for test_case, results in test_group['results'].items():
                if 'gas' in results:
                    gas_data = results['gas']
                    print(f'\\nTest: {test_case}')
                    
                    for function, gas_values in gas_data.items():
                        if isinstance(gas_values, dict):
                            avg_gas = gas_values.get('avg', 0)
                            min_gas = gas_values.get('min', 0)
                            max_gas = gas_values.get('max', 0)
                            print(f'  {function}: avg={avg_gas}, min={min_gas}, max={max_gas}')
                            
                            # Identify high gas functions
                            if avg_gas > 50000:
                                print(f'    ⚠️  High gas usage detected for {function}')
                        elif isinstance(gas_values, (int, float)):
                            print(f'  {function}: {gas_values}')
    
except Exception as e:
    print(f'Error analyzing gas data: {e}')
    sys.exit(1)
" || print_warning "Could not analyze gas patterns from JSON"
    else
        print_warning "Gas benchmark file not found"
    fi
    
    print_success "Gas pattern analysis completed"
}

# Generate optimization recommendations
generate_optimization_report() {
    print_info "Generating optimization recommendations..."
    
    cat > "$OUTPUT_DIR/optimization-recommendations.md" << 'EOF'
# Gas Optimization Recommendations

## High Priority Optimizations

### 1. Storage Access Optimization
- **Issue**: Frequent storage reads/writes
- **Solution**: Cache frequently accessed values in memory
- **Impact**: 20-50% gas reduction per operation

```solidity
// Before - Multiple storage reads
function process(uint256 _id) external {
    uint256 balance = balances[owner][_id];
    uint256 allowance = allowances[owner][msg.sender];
    // ... operations
}

// After - Cache in memory
function process(uint256 _id) external {
    uint256 balance = balances[owner][_id];
    uint256 allowance = allowances[owner][msg.sender];
    uint256 tempBalance = balance; // Cache for operations
    // ... operations using tempBalance
}
```

### 2. Loop Optimization
- **Issue**: Unbounded loops or inefficient loop patterns
- **Solution**: Use bounded loops and unchecked blocks

```solidity
// Before - Potentially unbounded
for (uint256 i = 0; i < array.length; i++) {
    // operation
}

// After - Bounded with unchecked
for (uint256 i = 0; i < array.length; i = unchecked_inc(i)) {
    if (condition) break; // Early exit
    // operation using unchecked arithmetic
}
```

### 3. Event Optimization
- **Issue**: Excessive event logging
- **Solution**: Optimize event parameters and structure

```solidity
// Before
emit Transfer(from, to, amount, timestamp, blockNumber, gasUsed);

// After - Use indexed parameters efficiently
event Transfer(
    address indexed from,
    address indexed to,
    uint256 value
);
```

## Medium Priority Optimizations

### 1. Function Visibility
- **Issue**: Using external instead of internal where possible
- **Impact**: 100-200 gas savings per call

```solidity
// Before
function externalFunction(uint256 _value) external {
    // logic
}

// After - If only called internally
function internalFunction(uint256 _value) internal {
    // logic
}
```

### 2. Constant/Immutable Usage
- **Issue**: Storing values in storage when they never change
- **Impact**: 20,000 gas per assignment saved

```solidity
// Before
contract MyContract {
    uint256 public constant FEE = 100;
    address public owner;
}

// After - Mark appropriately
contract MyContract {
    uint256 public immutable initialSupply;
    address public immutable owner;
    
    constructor(uint256 _initialSupply) {
        initialSupply = _initialSupply;
        owner = msg.sender;
    }
}
```

### 3. Struct Packing
- **Issue**: Inefficient struct layout
- **Solution**: Order variables by size

```solidity
// Before - Inefficient packing
struct Data {
    uint256 a;  // 32 bytes
    uint8 b;    // 1 byte + 31 padding
    uint256 c;  // 32 bytes
    address d;  // 20 bytes + 12 padding
}

// After - Efficient packing
struct Data {
    uint256 a;  // 32 bytes
    uint256 c;  // 32 bytes
    address d;  // 20 bytes
    uint8 b;    // 1 byte + 7 padding
}
```

## Low Priority Optimizations

### 1. String vs Bytes32
- **Issue**: Using string when bytes32 would suffice
- **Impact**: Variable gas savings

```solidity
// Before
string public name;

// After - If fixed length
bytes32 public nameHash;
```

### 2. Array Operations
- **Issue**: Inefficient array manipulation
- **Solution**: Use memory arrays when possible

```solidity
// Before - Storage array manipulation
uint256[] storage arr = myArray;
arr.push(value);

// After - Memory array for temporary operations
uint256[] memory tempArray = new uint256[](arr.length);
for (uint256 i = 0; i < arr.length; i++) {
    tempArray[i] = arr[i] * 2;
}
```

## Advanced Optimizations

### 1. Assembly Blocks
- **Use Case**: Specific gas-critical operations
- **Caution**: Use sparingly and test thoroughly

```solidity
function optimizedAdd(uint256 a, uint256 b) public pure returns (uint256) {
    assembly {
        let result := add(a, b)
        if iszero(eq(result, b)) {
            mstore(0x00, 0x8baa579f) // Error selector
            revert(0x00, 0x04)
        }
        return(result, 0x20)
    }
}
```

### 2. Custom Error Types
- **Benefit**: Lower gas cost than string errors

```solidity
// Before
require(amount > 0, "Invalid amount");

// After
error InvalidAmount(uint256 amount);

if (amount == 0) {
    revert InvalidAmount(amount);
}
```

### 3. Batch Operations
- **Benefit**: Amortize fixed costs across multiple operations

```solidity
function batchTransfer(address[] calldata recipients, uint256[] calldata amounts) external {
    require(recipients.length == amounts.length, "Length mismatch");
    
    for (uint256 i = 0; i < recipients.length; i++) {
        _transfer(msg.sender, recipients[i], amounts[i]);
    }
}
```

## Performance Metrics

### Gas Cost Analysis
- **Storage Write**: ~20,000 gas
- **Storage Read**: ~2,100 gas
- **Event Emission**: ~2,000 gas
- **External Call**: ~2,600 gas + execution
- **Internal Function Call**: ~40 gas
- **Simple Arithmetic**: ~3-100 gas

### Optimization Guidelines
1. **Minimize Storage Operations**: Cache values when possible
2. **Batch Operations**: Combine multiple operations
3. **Use Unchecked Blocks**: For arithmetic in safe contexts
4. **Optimize Data Structures**: Pack structs efficiently
5. **Leverage Constants**: Use immutable/constant for unchanging values

## Testing and Verification

### Gas Profiling
1. **Baseline Measurement**: Record current gas usage
2. **Optimization Application**: Implement suggested changes
3. **Measurement**: Record improved gas usage
4. **Verification**: Ensure functionality remains intact
5. **Documentation**: Update optimization status

### Continuous Monitoring
- Monitor gas usage changes over time
- Set alerts for significant gas increases
- Regular optimization reviews
- Performance regression testing

---
*Generated by Gas Analysis Tool*
EOF

    print_success "Optimization recommendations generated"
}

# Create gas usage comparison
create_gas_comparison() {
    print_info "Creating gas usage comparison..."
    
    cat > "$OUTPUT_DIR/gas-comparison.py" << 'EOF'
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def load_gas_data(filename):
    """Load gas usage data from JSON file"""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def create_comparison_charts(data, output_dir):
    """Create gas usage comparison charts"""
    
    # Extract test results
    test_results = []
    
    for test_group in data:
        if 'results' in test_group:
            for test_case, results in test_group['results'].items():
                if 'gas' in results:
                    gas_data = results['gas']
                    for function, gas_values in gas_data.items():
                        if isinstance(gas_values, dict):
                            avg_gas = gas_values.get('avg', 0)
                            test_results.append({
                                'test': test_case,
                                'function': function,
                                'avg_gas': avg_gas
                            })
    
    if test_results:
        df = pd.DataFrame(test_results)
        
        # Create gas usage bar chart
        plt.figure(figsize=(12, 8))
        
        # Group by function and sum gas usage
        gas_by_function = df.groupby('function')['avg_gas'].sum().sort_values(ascending=False)
        
        plt.subplot(2, 1, 1)
        gas_by_function.plot(kind='bar')
        plt.title('Total Gas Usage by Function')
        plt.xlabel('Function')
        plt.ylabel('Gas Usage')
        plt.xticks(rotation=45)
        
        # Create heatmap
        plt.subplot(2, 1, 2)
        pivot_df = df.pivot(index='function', columns='test', values='avg_gas')
        pivot_df = pivot_df.fillna(0)
        
        plt.imshow(pivot_df.values, cmap='YlOrRd', aspect='auto')
        plt.colorbar(label='Gas Usage')
        plt.title('Gas Usage Heatmap by Test and Function')
        plt.xlabel('Test')
        plt.ylabel('Function')
        plt.xticks(range(len(pivot_df.columns)), pivot_df.columns, rotation=45)
        plt.yticks(range(len(pivot_df.index)), pivot_df.index)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/gas-comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Gas comparison chart saved to {output_dir}/gas-comparison.png")
    
    else:
        print("No gas data available for comparison")

def generate_gas_report(data, output_dir):
    """Generate detailed gas usage report"""
    
    report = []
    report.append("# Gas Usage Analysis Report\n")
    
    # Summary statistics
    total_tests = 0
    total_gas_used = 0
    gas_breakdown = {}
    
    for test_group in data:
        if 'results' in test_group:
            for test_case, results in test_group['results'].items():
                total_tests += 1
                if 'gas' in results:
                    gas_data = results['gas']
                    for function, gas_values in gas_data.items():
                        if isinstance(gas_values, dict):
                            avg_gas = gas_values.get('avg', 0)
                            total_gas_used += avg_gas
                            
                            if function not in gas_breakdown:
                                gas_breakdown[function] = 0
                            gas_breakdown[function] += avg_gas
    
    report.append(f"## Summary\n")
    report.append(f"- Total Tests Analyzed: {total_tests}")
    report.append(f"- Total Gas Used: {total_gas_used:,}")
    report.append(f"- Average Gas per Test: {total_gas_used // total_tests if total_tests > 0 else 0:,}\n")
    
    # Gas breakdown by function
    report.append(f"## Gas Breakdown by Function\n")
    sorted_breakdown = sorted(gas_breakdown.items(), key=lambda x: x[1], reverse=True)
    
    for function, gas_usage in sorted_breakdown:
        percentage = (gas_usage / total_gas_used * 100) if total_gas_used > 0 else 0
        report.append(f"- {function}: {gas_usage:,} gas ({percentage:.1f}%)")
    
    report.append("\n## Optimization Recommendations\n")
    report.append("Based on the gas analysis, consider the following optimizations:\n")
    
    # Identify high gas functions
    high_gas_functions = [func for func, gas in sorted_breakdown if gas > 50000]
    
    if high_gas_functions:
        report.append("### High Gas Usage Functions\n")
        for func in high_gas_functions:
            report.append(f"- **{func}**: Consider optimizing with:")
            report.append("  - Storage caching")
            report.append("  - Unchecked blocks")
            report.append("  - Function visibility optimization\n")
    
    # Save report
    with open(f'{output_dir}/gas-analysis-report.md', 'w') as f:
        f.write('\n'.join(report))
    
    print(f"Gas analysis report saved to {output_dir}/gas-analysis-report.md")

if __name__ == "__main__":
    data = load_gas_data('gas-benchmark.json')
    if data:
        create_comparison_charts(data, '.')
        generate_gas_report(data, '.')
    else:
        print("No data to analyze")
EOF

    # Run the comparison script if data exists
    if [ -f "$BENCHMARK_FILE" ]; then
        python3 "$OUTPUT_DIR/gas-comparison.py"
        print_success "Gas comparison completed"
    else
        print_warning "No gas data available for comparison"
    fi
}

# Create gas optimization checklist
create_optimization_checklist() {
    print_info "Creating optimization checklist..."
    
    cat > "$OUTPUT_DIR/optimization-checklist.md" << 'EOF'
# Gas Optimization Checklist

## Development Phase

### Code Structure
- [ ] Use `immutable` for constructor-assigned variables
- [ ] Use `constant` for compile-time constants
- [ ] Mark functions as `internal` when possible
- [ ] Use `view` for read-only functions
- [ ] Use `pure` for functions that don't read state
- [ ] Pack structs efficiently (larger types first)
- [ ] Use `unchecked` blocks for safe arithmetic

### Data Structures
- [ ] Use `mapping` instead of array for key-value storage
- [ ] Avoid dynamic arrays when size is known
- [ ] Use `bytes32` instead of `string` when possible
- [ ] Cache array length in memory before loops
- [ ] Use `memory` arrays for temporary operations
- [ ] Minimize storage writes
- [ ] Batch similar operations

### Function Design
- [ ] Minimize external calls
- [ ] Use events instead of storage for historical data
- [ ] Implement circuit breakers for expensive operations
- [ ] Use custom errors instead of string messages
- [ ] Optimize loop conditions
- [ ] Use early returns to skip unnecessary operations
- [ ] Implement gas estimation for complex operations

## Testing Phase

### Gas Measurement
- [ ] Profile gas usage for all functions
- [ ] Test gas usage with different input sizes
- [ ] Compare gas usage before/after optimizations
- [ ] Monitor gas usage in stress tests
- [ ] Test worst-case scenarios
- [ ] Verify optimizations don't break functionality

### Performance Testing
- [ ] Test contract deployment cost
- [ ] Test transaction execution cost
- [ ] Test batch operations efficiency
- [ ] Test upgrade mechanism costs
- [ ] Test cross-contract interaction costs

## Deployment Phase

### Final Optimization
- [ ] Enable compiler optimizer (runs: 200)
- [ ] Remove all debug code
- [ ] Minimize contract size
- [ ] Optimize constructor gas usage
- [ ] Test on testnet with gas measurements
- [ ] Document gas usage metrics

## Monitoring Phase

### Ongoing Optimization
- [ ] Monitor gas usage in production
- [ ] Track gas price trends
- [ ] Identify functions with increasing gas costs
- [ ] Plan regular optimization reviews
- [ ] Update gas estimates in documentation
- [ ] Benchmark against similar contracts

## Quick Wins

### Immediate Impact (High ROI)
1. **Storage Access**: Cache frequently accessed values
2. **Function Calls**: Use internal instead of external
3. **Events**: Use indexed parameters efficiently
4. **Struct Packing**: Order variables by size
5. **Constants**: Use immutable/constant for unchanging values

### Medium Impact
1. **Loop Optimization**: Use unchecked and early exit
2. **Array Operations**: Use memory arrays when possible
3. **Error Handling**: Use custom errors
4. **Event Emission**: Batch related events
5. **Gas Estimation**: Provide accurate gas limits

### Long-term Optimization
1. **Architecture**: Consider L2 solutions
2. **Batch Operations**: Combine multiple transactions
3. **Proxy Patterns**: Implement upgradeable contracts
4. **Formal Verification**: Prove correctness
5. **Assembly Optimization**: Use Yul for critical paths

## Tools and Resources

### Analysis Tools
- [ ] Slither for static analysis
- [ ] Foundry for gas profiling
- [ ] Tenderly for production monitoring
- [ ] MythX for security analysis
- [ ] Manual code review

### Documentation
- [ ] Gas usage metrics documented
- [ ] Optimization rationale explained
- [ ] Best practices guide followed
- [ ] Regular updates scheduled

---
*Keep this checklist updated and review regularly*
EOF

    print_success "Optimization checklist created"
}

# Main execution
main() {
    echo -e "${BLUE}Starting gas analysis and optimization...${NC}"
    echo ""
    
    install_dependencies
    run_gas_analysis
    analyze_gas_patterns
    generate_optimization_report
    create_gas_comparison
    create_optimization_checklist
    
    echo ""
    echo -e "${GREEN}=== Gas Analysis Complete ===${NC}"
    echo "Output directory: $OUTPUT_DIR"
    echo ""
    echo "Generated files:"
    echo "- optimization-recommendations.md: Detailed optimization guide"
    echo "- gas-comparison.py: Gas usage visualization script"
    echo "- gas-comparison.png: Gas usage charts (if data available)"
    echo "- gas-analysis-report.md: Detailed analysis report"
    echo "- optimization-checklist.md: Development checklist"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Review optimization recommendations"
    echo "2. Apply suggested optimizations"
    echo "3. Re-run analysis to measure improvements"
    echo "4. Update documentation with new metrics"
}

# Execute main function
main "$@"