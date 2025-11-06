// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title SecurityUtils
 * @dev Xavfsizlik funksiyalari kutubxonasi
 */
library SecurityUtils {
    // Constants
    uint256 private constant MAX_UINT256 = type(uint256).max;
    
    /**
     * @dev Safe addition with overflow check
     */
    function safeAdd(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 c = a + b;
        require(c >= a, "SafeMath: addition overflow");
        return c;
    }
    
    /**
     * @dev Safe subtraction with underflow check
     */
    function safeSub(uint256 a, uint256 b) internal pure returns (uint256) {
        require(b <= a, "SafeMath: subtraction underflow");
        return a - b;
    }
    
    /**
     * @dev Safe multiplication with overflow check
     */
    function safeMul(uint256 a, uint256 b) internal pure returns (uint256) {
        if (a == 0) return 0;
        uint256 c = a * b;
        require(c / a == b, "SafeMath: multiplication overflow");
        return c;
    }
    
    /**
     * @dev Safe division with division by zero check
     */
    function safeDiv(uint256 a, uint256 b) internal pure returns (uint256) {
        require(b > 0, "SafeMath: division by zero");
        return a / b;
    }
    
    /**
     * @dev Safe modulo with modulo by zero check
     */
    function safeMod(uint256 a, uint256 b) internal pure returns (uint256) {
        require(b > 0, "SafeMath: modulo by zero");
        return a % b;
    }
    
    /**
     * @dev Safe integer comparison
     */
    function equals(int256 a, int256 b) internal pure returns (bool) {
        return a == b;
    }
    
    /**
     * @dev Safe greater than comparison
     */
    function gt(uint256 a, uint256 b) internal pure returns (bool) {
        return a > b;
    }
    
    /**
     * @dev Safe greater than or equal comparison
     */
    function gte(uint256 a, uint256 b) internal pure returns (bool) {
        return a >= b;
    }
    
    /**
     * @dev Safe less than comparison
     */
    function lt(uint256 a, uint256 b) internal pure returns (bool) {
        return a < b;
    }
    
    /**
     * @dev Safe less than or equal comparison
     */
    function lte(uint256 a, uint256 b) internal pure returns (bool) {
        return a <= b;
    }
    
    /**
     * @dev Calculate percentage safely
     */
    function percentage(uint256 amount, uint256 percent, uint256 base) internal pure returns (uint256) {
        require(base > 0, "Base cannot be zero");
        return safeDiv(safeMul(amount, percent), base);
    }
    
    /**
     * @dev Calculate basis points
     */
    function basisPoints(uint256 amount, uint256 bps) internal pure returns (uint256) {
        require(bps <= 10000, "Basis points cannot exceed 100%");
        return percentage(amount, bps, 10000);
    }
    
    /**
     * @dev Check if address is not zero
     */
    function isValidAddress(address addr) internal pure returns (bool) {
        return addr != address(0);
    }
    
    /**
     * @dev Generate unique ID from parameters
     */
    function generateId(string memory prefix, address user, uint256 timestamp, bytes32 additional) 
        internal pure returns (bytes32) {
        return keccak256(abi.encodePacked(prefix, user, timestamp, additional));
    }
    
    /**
     * @dev Validate array bounds
     */
    function validateBounds(uint256 index, uint256 length) internal pure {
        require(index < length, "Array index out of bounds");
    }
    
    /**
     * @dev Check if value is within range
     */
    function isInRange(uint256 value, uint256 min, uint256 max) internal pure returns (bool) {
        return value >= min && value <= max;
    }
    
    /**
     * @dev Check if value is positive
     */
    function isPositive(int256 value) internal pure returns (bool) {
        return value > 0;
    }
    
    /**
     * @dev Check if value is negative
     */
    function isNegative(int256 value) internal pure returns (bool) {
        return value < 0;
    }
}