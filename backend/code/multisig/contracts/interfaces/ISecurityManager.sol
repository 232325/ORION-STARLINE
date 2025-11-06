// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title ISecurityManager
 * @dev Interface for security management features
 * @author MultiSig Wallet System
 */
interface ISecurityManager {
    // Events
    event SecurityLevelChanged(address indexed wallet, uint8 level);
    event WhitelistUpdated(address indexed wallet, address indexed account, bool allowed);
    event BlacklistUpdated(address indexed wallet, address indexed account, bool blocked);
    event RateLimitChanged(address indexed wallet, uint256 newLimit);
    event EmergencyAccessGranted(address indexed wallet, address indexed account);
    event EmergencyAccessRevoked(address indexed wallet, address indexed account);
    
    // Enums
    enum SecurityLevel {
        BASIC,
        STANDARD,
        HIGH,
        ENTERPRISE
    }
    
    enum TransactionStatus {
        PENDING,
        CONFIRMED,
        EXECUTED,
        REJECTED,
        CANCELLED
    }
    
    struct SecurityConfig {
        SecurityLevel level;
        uint256 dailyLimit;
        uint256 weeklyLimit;
        uint256 monthlyLimit;
        uint256 rateLimit; // transactions per time period
        uint256 timeLockDuration;
        bool requireMFA;
        bool allowEmergencyAccess;
        bool whitelistOnly;
        bytes32 whitelistHash;
        bytes32 blacklistHash;
    }
    
    struct TransactionData {
        address from;
        address to;
        uint256 value;
        bytes data;
        uint256 timestamp;
        TransactionStatus status;
        uint256 confirmations;
        uint256 required;
    }
    
    // Functions
    function setSecurityLevel(address wallet, SecurityLevel level) external;
    
    function setSpendingLimits(
        address wallet,
        uint256 daily,
        uint256 weekly,
        uint256 monthly
    ) external;
    
    function updateWhitelist(
        address wallet,
        address account,
        bool allowed
    ) external;
    
    function updateBlacklist(
        address wallet,
        address account,
        bool blocked
    ) external;
    
    function setRateLimit(address wallet, uint256 limit) external;
    
    function validateTransaction(
        address wallet,
        address to,
        uint256 value,
        bytes calldata data
    ) external view returns (bool valid, string memory reason);
    
    function grantEmergencyAccess(
        address wallet,
        address account,
        uint256 unlockTime
    ) external;
    
    function revokeEmergencyAccess(
        address wallet,
        address account
    ) external;
    
    function isWhitelisted(address wallet, address account) external view returns (bool);
    
    function isBlacklisted(address wallet, address account) external view returns (bool);
    
    function getSecurityConfig(address wallet) external view returns (SecurityConfig memory);
}