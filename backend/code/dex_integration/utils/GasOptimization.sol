// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "../interfaces/IERC20.sol";
import "../utils/SafeMath.sol";

/**
 * @dev Gas optimization utilities for DEX operations
 */
library GasOptimizer {
    using SafeMath for uint256;
    
    struct SwapCalculation {
        uint256 inputAmount;
        uint256 expectedOutput;
        uint256 priceImpact;
        uint256 gasEstimate;
        bool isOptimal;
    }
    
    struct LiquidityParams {
        uint256 tokenA;
        uint256 tokenB;
        uint256 minTokenA;
        uint256 minTokenB;
        uint256 gasPrice;
        uint256 deadline;
    }
    
    /**
     * @dev Calculate optimal gas usage for swaps
     */
    function calculateOptimalGas(
        SwapCalculation memory swap,
        uint256 currentGasPrice,
        uint256 maxGasPrice
    ) internal pure returns (uint256 optimalGas) {
        // Base gas cost for different operations
        uint256 baseGas = 21000; // Transaction base
        uint256 swapGas = _estimateSwapGas(swap.inputAmount);
        uint256 gasSafetyMargin = 10000; // 10k gas safety margin
        
        total gas = baseGas.add(swapGas).add(gasSafetyMargin);
        
        // Adjust for gas price sensitivity
        if (currentGasPrice > maxGasPrice) {
            optimalGas = totalGas.mul(80).div(100); // Reduce gas usage for high fees
        } else {
            optimalGas = totalGas;
        }
        
        return optimalGas;
    }
    
    /**
     * @dev Calculate gas estimate for different swap types
     */
    function estimateGasForSwap(uint256 inputAmount, bool isMultiHop) internal pure returns (uint256) {
        uint256 baseGas = 50000; // Base operation gas
        
        if (isMultiHop) {
            baseGas = baseGas.add(30000); // Additional gas for multi-hop
        }
        
        // Scale with amount for larger operations
        if (inputAmount > 1000000 * 10**18) { // > 1M tokens
            baseGas = baseGas.add(10000);
        }
        
        return baseGas;
    }
    
    /**
     * @dev Calculate slippage tolerance based on liquidity
     */
    function calculateDynamicSlippage(
        uint256 poolLiquidity,
        uint256 tradeAmount,
        uint256 baseSlippage
    ) internal pure returns (uint256) {
        if (poolLiquidity == 0 || tradeAmount == 0) {
            return baseSlippage;
        }
        
        // Calculate liquidity ratio
        uint256 liquidityRatio = tradeAmount.mul(10000).div(poolLiquidity);
        
        // Adjust slippage based on liquidity ratio
        if (liquidityRatio > 5000) { // > 50% of liquidity
            return baseSlippage.mul(150).div(100); // 50% higher slippage
        } else if (liquidityRatio > 2000) { // > 20% of liquidity
            return baseSlippage.mul(120).div(100); // 20% higher slippage
        } else {
            return baseSlippage; // No adjustment
        }
    }
    
    /**
     * @dev Batch multiple operations efficiently
     */
    function batchSwapOperations(
        SwapCalculation[] memory swaps,
        address[] memory tokens
    ) internal pure returns (bool) {
        // Calculate total gas for batch operation
        uint256 totalGas = 21000; // Base transaction
        for (uint256 i = 0; i < swaps.length; i++) {
            totalGas = totalGas.add(_estimateSwapGas(swaps[i].inputAmount));
        }
        
        // Batch operations typically save ~30% gas
        return totalGas.mul(70).div(100) < totalGas;
    }
    
    /**
     * @dev Optimize token approval patterns
     */
    function calculateOptimalApprovalAmount(
        uint256 maxUsage,
        uint256 avgUsage,
        uint256 buffer
    ) internal pure returns (uint256) {
        // Use average usage with buffer to minimize approval overhead
        return avgUsage.mul(100 + buffer).div(100);
    }
    
    /**
     * @dev Check if transaction should be batched
     */
    function shouldBatchTransaction(
        uint256 gasUsed,
        uint256 gasPrice,
        uint256 batchSavings
    ) internal pure returns (bool) {
        uint256 cost = gasUsed.mul(gasPrice);
        uint256 savings = batchSavings;
        return savings > cost;
    }
    
    /**
     * @dev Calculate gas-efficient path for multi-hop swaps
     */
    function findOptimalPath(
        address[] memory tokens,
        uint256[] memory amounts,
        uint256[][] memory pools
    ) internal pure returns (address[] memory optimalPath) {
        // Simplified path finding - in practice, this would use graph algorithms
        uint256 maxDepth = 3; // Limit path depth
        
        if (tokens.length <= 2) {
            return tokens; // Direct swap
        }
        
        // For demonstration, return direct path if available
        for (uint256 i = 1; i < tokens.length - 1; i++) {
            if (pools[i-1][i] > 0 && pools[i][i+1] > 0) {
                return _extractSubPath(tokens, i, i+2);
            }
        }
        
        return tokens; // Return original path
    }
    
    /**
     * @dev Internal helper functions
     */
    function _estimateSwapGas(uint256 inputAmount) private pure returns (uint256) {
        if (inputAmount > 100000 * 10**18) {
            return 120000; // Large swap
        } else if (inputAmount > 10000 * 10**18) {
            return 80000; // Medium swap
        } else {
            return 50000; // Small swap
        }
    }
    
    function _extractSubPath(
        address[] memory tokens,
        uint256 start,
        uint256 end
    ) private pure returns (address[] memory) {
        address[] memory subPath = new address[](end - start + 1);
        for (uint256 i = start; i <= end; i++) {
            subPath[i - start] = tokens[i];
        }
        return subPath;
    }
}

/**
 * @dev MEV Protection utilities
 */
library MEVProtection {
    using SafeMath for uint256;
    
    struct ProtectionParams {
        address user;
        uint256 minBlockDelay;
        uint256 maxTransactionsPerBlock;
        uint256 maxValuePerBlock;
        mapping(uint256 => uint256) transactionCount;
        mapping(address => uint256) lastTransactionBlock;
    }
    
    /**
     * @dev Check if transaction is protected from MEV
     */
    function isProtectedFromMEV(
        ProtectionParams memory params,
        uint256 blockNumber,
        uint256 transactionValue
    ) internal view returns (bool) {
        uint256 lastBlock = params.lastTransactionBlock[params.user];
        
        // Check minimum block delay
        if (lastBlock > 0 && blockNumber <= lastBlock.add(params.minBlockDelay)) {
            return false;
        }
        
        // Check transaction count per block
        uint256 currentBlockTxCount = params.transactionCount[blockNumber];
        if (currentBlockTxCount >= params.maxTransactionsPerBlock) {
            return false;
        }
        
        // Check value limits
        // This is a simplified check - in practice would track total value per block
        
        return true;
    }
    
    /**
     * @dev Register transaction for MEV tracking
     */
    function registerTransaction(
        ProtectionParams storage params,
        uint256 blockNumber,
        uint256 transactionValue
    ) internal {
        params.lastTransactionBlock[params.user] = blockNumber;
        params.transactionCount[blockNumber] = params.transactionCount[blockNumber].add(1);
    }
    
    /**
     * @dev Calculate random delay for transaction
     */
    function calculateRandomDelay(
        uint256 seed,
        uint256 minDelay,
        uint256 maxDelay
    ) internal pure returns (uint256) {
        return minDelay.add(seed % (maxDelay - minDelay + 1));
    }
    
    /**
     * @dev Generate transaction hash for front-running protection
     */
    function generateProtectedHash(
        address from,
        address to,
        uint256 value,
        uint256 blockNumber,
        bytes memory data
    ) internal pure returns (bytes32) {
        return keccak256(abi.encodePacked(
            from,
            to,
            value,
            blockNumber,
            data,
            block.chainid
        ));
    }
}

/**
 * @dev Price protection utilities
 */
library PriceProtection {
    using SafeMath for uint256;
    
    struct PriceData {
        uint256 price;
        uint256 timestamp;
        uint256 volume;
        bool isValid;
    }
    
    struct ProtectionSettings {
        uint256 maxPriceImpact;
        uint256 maxSlippage;
        uint256 oracleTimeout;
        uint256 circuitBreakerThreshold;
    }
    
    /**
     * @dev Check price impact against thresholds
     */
    function checkPriceImpact(
        uint256 currentPrice,
        uint256 newPrice,
        ProtectionSettings memory settings
    ) internal pure returns (bool isSafe) {
        if (currentPrice == 0 || newPrice == 0) {
            return false;
        }
        
        uint256 priceImpact = currentPrice > newPrice
            ? currentPrice.sub(newPrice).mul(10000).div(currentPrice)
            : newPrice.sub(currentPrice).mul(10000).div(currentPrice);
            
        return priceImpact <= settings.maxPriceImpact;
    }
    
    /**
     * @dev Check slippage against tolerance
     */
    function checkSlippage(
        uint256 expectedAmount,
        uint256 actualAmount,
        ProtectionSettings memory settings
    ) internal pure returns (bool isSafe) {
        if (expectedAmount == 0) {
            return false;
        }
        
        uint256 slippage = expectedAmount > actualAmount
            ? expectedAmount.sub(actualAmount).mul(10000).div(expectedAmount)
            : actualAmount.sub(expectedAmount).mul(10000).div(expectedAmount);
            
        return slippage <= settings.maxSlippage;
    }
    
    /**
     * @dev Validate oracle price feed
     */
    function validateOraclePrice(
        PriceData memory oraclePrice,
        uint256 currentTimestamp,
        ProtectionSettings memory settings
    ) internal pure returns (bool) {
        if (!oraclePrice.isValid) {
            return false;
        }
        
        uint256 age = currentTimestamp.sub(oraclePrice.timestamp);
        return age <= settings.oracleTimeout;
    }
    
    /**
     * @dev Calculate dynamic slippage based on market conditions
     */
    function calculateDynamicSlippage(
        uint256 baseSlippage,
        uint256 volume,
        uint256 volatility
    ) internal pure returns (uint256) {
        // Higher volume and volatility increase slippage tolerance
        uint256 adjustment = 100;
        
        if (volume > 1000000 * 10**18) {
            adjustment = adjustment.add(50); // +0.5%
        }
        
        if (volatility > 500) { // 5% volatility threshold
            adjustment = adjustment.add(30); // +0.3%
        }
        
        return baseSlippage.mul(adjustment).div(100);
    }
    
    /**
     * @dev Implement circuit breaker for extreme price movements
     */
    function checkCircuitBreaker(
        PriceData memory lastValidPrice,
        PriceData memory currentPrice,
        ProtectionSettings memory settings
    ) internal pure returns (bool triggered) {
        if (!lastValidPrice.isValid || !currentPrice.isValid) {
            return true; // Trigger if no valid prices
        }
        
        uint256 priceChange = currentPrice.price > lastValidPrice.price
            ? currentPrice.price.sub(lastValidPrice.price).mul(10000).div(lastValidPrice.price)
            : lastValidPrice.price.sub(currentPrice.price).mul(10000).div(lastValidPrice.price);
            
        return priceChange > settings.circuitBreakerThreshold;
    }
}