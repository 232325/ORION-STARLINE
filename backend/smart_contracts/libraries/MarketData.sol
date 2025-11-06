// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "./SecurityUtils.sol";

/**
 * @title MarketData
 * @dev Market ma'lumotlari va narx feed'larini boshqarish
 */
library MarketData {
    using SecurityUtils for uint256;
    
    // Constants
    uint256 private constant PRICE_PRECISION = 1e8;  // 8 decimal places
    uint256 private constant TIME_PRECISION = 1;     // 1 second
    
    /**
     * @dev Asset type enumeration
     */
    enum AssetType {
        STOCK,
        FOREX,
        METAL,
        CRYPTO
    }
    
    /**
     * @dev Price feed struct
     */
    struct PriceFeed {
        uint256 price;           // Current price
        uint256 timestamp;       // Last update time
        uint256 volume;          // 24h volume
        uint256 change24h;       // 24h price change (basis points)
        address oracle;          // Price oracle address
        bool isActive;           // Whether price feed is active
    }
    
    /**
     * @dev Market statistics struct
     */
    struct MarketStats {
        uint256 totalVolume;     // Total trading volume
        uint256 totalTrades;     // Total number of trades
        uint256 avgPrice;        // Average price
        uint256 high24h;         // 24h high
        uint256 low24h;          // 24h low
        uint256 lastUpdate;      // Last statistics update
    }
    
    /**
     * @dev Price snapshot for historical data
     */
    struct PriceSnapshot {
        uint256 price;
        uint256 timestamp;
        uint256 volume;
    }
    
    /**
     * @dev Calculate price change percentage
     */
    function calculateChange(uint256 oldPrice, uint256 newPrice) 
        internal pure returns (int256 changeBps) {
        if (oldPrice == 0) return 0;
        
        int256 numerator = int256(newPrice) - int256(oldPrice);
        int256 denominator = int256(oldPrice);
        
        return (numerator * 10000) / denominator; // Basis points
    }
    
    /**
     * @dev Calculate volume-weighted average price
     */
    function calculateVWAP(PriceSnapshot[] memory snapshots) 
        internal pure returns (uint256 vwap) {
        if (snapshots.length == 0) return 0;
        
        uint256 totalVolume = 0;
        uint256 weightedSum = 0;
        
        for (uint256 i = 0; i < snapshots.length; i++) {
            totalVolume = totalVolume.safeAdd(snapshots[i].volume);
            weightedSum = weightedSum.safeAdd(
                snapshots[i].price.safeMul(snapshots[i].volume)
            );
        }
        
        return totalVolume == 0 ? 0 : weightedSum.safeDiv(totalVolume);
    }
    
    /**
     * @dev Convert price to different precision
     */
    function convertPrice(uint256 price, uint256 fromPrecision, uint256 toPrecision) 
        internal pure returns (uint256 converted) {
        if (fromPrecision == toPrecision) return price;
        
        if (fromPrecision > toPrecision) {
            uint256 factor = 10 ** (fromPrecision - toPrecision);
            return price / factor;
        } else {
            uint256 factor = 10 ** (toPrecision - fromPrecision);
            return price.safeMul(factor);
        }
    }
    
    /**
     * @dev Calculate time-weighted average price
     */
    function calculateTWAP(PriceSnapshot[] memory snapshots, uint256 startTime, uint256 endTime) 
        internal pure returns (uint256 twap) {
        if (snapshots.length == 0) return 0;
        
        uint256 totalWeight = 0;
        uint256 weightedSum = 0;
        
        for (uint256 i = 0; i < snapshots.length; i++) {
            if (snapshots[i].timestamp >= startTime && snapshots[i].timestamp <= endTime) {
                uint256 weight = snapshots[i].timestamp.safeSub(startTime);
                totalWeight = totalWeight.safeAdd(weight);
                weightedSum = weightedSum.safeAdd(snapshots[i].price.safeMul(weight));
            }
        }
        
        return totalWeight == 0 ? 0 : weightedSum.safeDiv(totalWeight);
    }
    
    /**
     * @dev Validate price feed
     */
    function validatePriceFeed(PriceFeed memory feed) 
        internal pure returns (bool isValid, string memory error) {
        if (feed.price == 0) {
            return (false, "Price cannot be zero");
        }
        
        if (feed.timestamp == 0) {
            return (false, "Timestamp cannot be zero");
        }
        
        if (!feed.isActive) {
            return (false, "Price feed is not active");
        }
        
        if (feed.oracle == address(0)) {
            return (false, "Oracle address is zero");
        }
        
        return (true, "");
    }
    
    /**
     * @dev Calculate moving average
     */
    function calculateMovingAverage(PriceSnapshot[] memory prices, uint256 period) 
        internal pure returns (uint256 ma) {
        require(period > 0, "Period cannot be zero");
        require(prices.length >= period, "Insufficient data for moving average");
        
        uint256 sum = 0;
        for (uint256 i = prices.length - period; i < prices.length; i++) {
            sum = sum.safeAdd(prices[i].price);
        }
        
        return sum / period;
    }
    
    /**
     * @dev Calculate volatility
     */
    function calculateVolatility(PriceSnapshot[] memory prices) 
        internal pure returns (uint256 volatility) {
        if (prices.length < 2) return 0;
        
        uint256 mean = 0;
        for (uint256 i = 0; i < prices.length; i++) {
            mean = mean.safeAdd(prices[i].price);
        }
        mean = mean / prices.length;
        
        uint256 sumSquaredDiff = 0;
        for (uint256 i = 0; i < prices.length; i++) {
            uint256 diff = prices[i].price > mean ? 
                prices[i].price - mean : mean - prices[i].price;
            sumSquaredDiff = sumSquaredDiff.safeAdd(diff.safeMul(diff));
        }
        
        return sumSquaredDiff / prices.length;
    }
    
    /**
     * @dev Get asset type from address
     */
    function getAssetType(address asset) internal pure returns (AssetType) {
        // Simple heuristic based on contract address
        // In real implementation, this would be more sophisticated
        if (uint256(bytes32(abi.encode(asset))) % 4 == 0) {
            return AssetType.STOCK;
        } else if (uint256(bytes32(abi.encode(asset))) % 4 == 1) {
            return AssetType.FOREX;
        } else if (uint256(bytes32(abi.encode(asset))) % 4 == 2) {
            return AssetType.METAL;
        } else {
            return AssetType.CRYPTO;
        }
    }
    
    /**
     * @dev Normalize price for different asset types
     */
    function normalizePrice(uint256 price, AssetType assetType) 
        internal pure returns (uint256 normalized) {
        if (assetType == AssetType.STOCK) {
            return price; // Already in USD cents
        } else if (assetType == AssetType.FOREX) {
            return price * PRICE_PRECISION; // Add precision
        } else if (assetType == AssetType.METAL) {
            return price * 100; // Price per ounce
        } else { // CRYPTO
            return price; // Keep as is
        }
    }
    
    /**
     * @dev Check if price is stale
     */
    function isStale(uint256 timestamp, uint256 maxAge) 
        internal view returns (bool) {
        return (block.timestamp - timestamp) > maxAge;
    }
    
    /**
     * @dev Generate unique market ID
     */
    function generateMarketId(address asset, AssetType assetType) 
        internal pure returns (bytes32) {
        return keccak256(abi.encodePacked(asset, assetType));
    }
}