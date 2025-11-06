// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@gnosis.pm/safe-contracts/contracts/GnosisSafe.sol";
import "@gnosis.pm/safe-contracts/contracts/proxies/GnosisSafeProxyFactory.sol";
import "@gnosis.pm/safe-contracts/contracts/interfaces/IERC20.sol";

/**
 * @title GnosisSafeManager
 * @dev Gnosis Safe integration with advanced features
 * @author MultiSig Wallet System
 */
contract GnosisSafeManager {
    GnosisSafeProxyFactory public immutable factory;
    address public immutable safeTemplate;
    
    // Custom configurations
    mapping(address => SafeConfig) public safeConfigs;
    mapping(address => address[]) public safeWallets;
    
    struct SafeConfig {
        uint256 threshold;
        uint256 dailyLimit;
        uint256 weeklyLimit;
        uint256 monthlyLimit;
        uint256 timeLock; // Emergency time lock
        address[] owners;
        bool emergencyMode;
        bytes32 metadataHash;
    }
    
    event SafeCreated(
        address indexed safe,
        address[] owners,
        uint256 threshold,
        uint256 dailyLimit
    );
    
    event SafeConfigUpdated(
        address indexed safe,
        SafeConfig newConfig
    );
    
    event EmergencyModeActivated(
        address indexed safe,
        address indexed activator,
        uint256 unlockTime
    );
    
    modifier onlySafeOwner(address safe) {
        require(GnosisSafe(safe).isOwner(msg.sender), "Not a safe owner");
        _;
    }
    
    constructor() {
        factory = new GnosisSafeProxyFactory();
        safeTemplate = address(new GnosisSafe());
    }
    
    /**
     * @dev Create new multi-signature wallet
     */
    function createSafe(
        address[] memory owners,
        uint256 threshold,
        uint256 dailyLimit,
        uint256 weeklyLimit,
        uint256 monthlyLimit,
        uint256 timeLock,
        bytes32 metadataHash
    ) external returns (address safe) {
        require(owners.length >= threshold && threshold > 0, "Invalid threshold");
        require(threshold <= owners.length, "Threshold too high");
        require(timeLock <= 30 days, "Time lock too long");
        
        GnosisSafe proxy = factory.createProxy(safeTemplate);
        safe = address(proxy);
        
        // Initialize safe
        proxy.setup(
            owners,
            threshold,
            address(0),
            bytes(""),
            address(0),
            address(0),
            0,
            address(0)
        );
        
        // Store configuration
        safeConfigs[safe] = SafeConfig({
            threshold: threshold,
            dailyLimit: dailyLimit,
            weeklyLimit: weeklyLimit,
            monthlyLimit: monthlyLimit,
            timeLock: timeLock,
            owners: owners,
            emergencyMode: false,
            metadataHash: metadataHash
        });
        
        safeWallets[msg.sender].push(safe);
        
        emit SafeCreated(safe, owners, threshold, dailyLimit);
        
        return safe;
    }
    
    /**
     * @dev Update safe configuration
     */
    function updateSafeConfig(
        address safe,
        uint256 dailyLimit,
        uint256 weeklyLimit,
        uint256 monthlyLimit,
        uint256 timeLock,
        bytes32 metadataHash
    ) external onlySafeOwner(safe) {
        SafeConfig storage config = safeConfigs[safe];
        config.dailyLimit = dailyLimit;
        config.weeklyLimit = weeklyLimit;
        config.monthlyLimit = monthlyLimit;
        config.timeLock = timeLock;
        config.metadataHash = metadataHash;
        
        emit SafeConfigUpdated(safe, config);
    }
    
    /**
     * @dev Activate emergency mode
     */
    function activateEmergencyMode(address safe) external onlySafeOwner(safe) {
        SafeConfig storage config = safeConfigs[safe];
        require(!config.emergencyMode, "Already in emergency mode");
        
        config.emergencyMode = true;
        uint256 unlockTime = block.timestamp + config.timeLock;
        
        emit EmergencyModeActivated(safe, msg.sender, unlockTime);
    }
    
    /**
     * @dev Get safe configuration
     */
    function getSafeConfig(address safe) external view returns (SafeConfig memory) {
        return safeConfigs[safe];
    }
    
    /**
     * @dev Get all safe wallets for an owner
     */
    function getSafeWallets(address owner) external view returns (address[] memory) {
        return safeWallets[owner];
    }
    
    /**
     * @dev Validate transaction limits
     */
    function validateTransactionLimits(
        address safe,
        uint256 value,
        bytes memory data
    ) external view returns (bool) {
        SafeConfig memory config = safeConfigs[safe];
        
        if (config.emergencyMode) {
            return true; // Emergency mode bypasses limits
        }
        
        // Check daily limit (simplified - would need proper tracking)
        if (value > config.dailyLimit) {
            return false;
        }
        
        // Check if transaction is to a whitelisted address
        // Implementation would depend on specific requirements
        
        return true;
    }
    
    /**
     * @dev Execute transaction through safe
     */
    function executeTransaction(
        address safe,
        address to,
        uint256 value,
        bytes memory data,
        uint8 operation
    ) external onlySafeOwner(safe) returns (bool) {
        require(validateTransactionLimits(safe, value, data), "Transaction exceeds limits");
        
        bytes memory transactionData = abi.encodeWithSignature(
            "execTransaction(address,uint256,bytes,uint8)",
            to,
            value,
            data,
            operation
        );
        
        (bool success,) = safe.call(transactionData);
        return success;
    }
}