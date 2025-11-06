// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title ContractMonitor
 * @dev Real-time monitoring system for smart contracts
 * @notice Features: Anomaly detection, rate limiting, emergency response
 */
contract ContractMonitor {
    // Monitoring configuration
    struct MonitoringConfig {
        bool isActive;
        uint256 suspiciousTransactionThreshold;
        uint256 timeWindow; // in seconds
        uint256 maxTransactionsPerWindow;
        address[] monitoredContracts;
    }
    
    // Anomaly detection parameters
    struct AnomalyParams {
        uint256 gasPriceAnomalyThreshold; // Percentage above median
        uint256 valueAnomalyThreshold; // Percentage above median
        uint256 frequencyAnomalyThreshold; // Transactions per block
        uint256 flashLoanDetectionThreshold; // Transactions count
    }
    
    // Emergency response actions
    enum EmergencyAction {
        PAUSE_ALL,
        PAUSE_CONTRACT,
        RESTRICT_ACCESS,
        NOTIFY_ADMIN,
        NOTHING
    }
    
    // Monitoring state
    mapping(address => MonitoringConfig) public contractConfigs;
    mapping(address => uint256) public transactionCounts;
    mapping(address => uint256) public lastTransactionTime;
    mapping(address => uint256[]) public recentGasPrices;
    mapping(address => uint256[]) public recentTransactionValues;
    mapping(address => bool) public isPaused;
    mapping(address => mapping(address => bool)) public restrictedAccess;
    
    // Admin and security roles
    address public admin;
    address public securityOfficer;
    mapping(address => bool) public monitors;
    
    // Emergency response
    mapping(address => EmergencyAction) public emergencyActions;
    uint256 public emergencyCooldown = 1 hours;
    mapping(address => uint256) public lastEmergencyAction;
    
    // Statistics and alerts
    event SuspiciousActivityDetected(
        address indexed contractAddress,
        address indexed actor,
        string activityType,
        uint256 severity
    );
    
    event EmergencyActionTriggered(
        address indexed contractAddress,
        EmergencyAction action,
        string reason
    );
    
    event AccessRestricted(
        address indexed contractAddress,
        address indexed actor,
        string reason
    );
    
    event MonitoringAlert(
        address indexed contractAddress,
        string alertType,
        string details
    );
    
    // Modifiers
    modifier onlyAdmin() {
        require(msg.sender == admin, "Unauthorized: Admin only");
        _;
    }
    
    modifier onlySecurityOfficer() {
        require(msg.sender == securityOfficer, "Unauthorized: Security Officer only");
        _;
    }
    
    modifier onlyMonitor() {
        require(monitors[msg.sender] || msg.sender == admin, "Unauthorized: Monitor only");
        _;
    }
    
    modifier emergencyCooldownCheck(address _contract) {
        require(
            block.timestamp >= lastEmergencyAction[_contract] + emergencyCooldown,
            "Emergency action cooldown active"
        );
        _;
    }
    
    constructor() {
        admin = msg.sender;
        securityOfficer = msg.sender;
        monitors[msg.sender] = true;
    }
    
    /**
     * @dev Setup monitoring for a contract
     */
    function setupContractMonitoring(
        address _contract,
        uint256 _suspiciousThreshold,
        uint256 _timeWindow,
        uint256 _maxTransactions
    ) external onlyAdmin {
        contractConfigs[_contract].isActive = true;
        contractConfigs[_contract].suspiciousTransactionThreshold = _suspiciousThreshold;
        contractConfigs[_contract].timeWindow = _timeWindow;
        contractConfigs[_contract].maxTransactionsPerWindow = _maxTransactions;
        contractConfigs[_contract].monitoredContracts.push(_contract);
    }
    
    /**
     * @dev Main monitoring function called by monitored contracts
     */
    function monitorTransaction(
        address _contract,
        address _actor,
        uint256 _value,
        uint256 _gasPrice
    ) external onlyMonitor {
        require(contractConfigs[_contract].isActive, "Contract not monitored");
        
        // Rate limiting check
        if (checkRateLimit(_contract, _actor)) {
            triggerSuspiciousActivity(_contract, _actor, "Rate limit exceeded", 3);
        }
        
        // Gas price anomaly detection
        if (checkGasPriceAnomaly(_contract, _gasPrice)) {
            triggerSuspiciousActivity(_contract, _actor, "Abnormal gas price", 2);
        }
        
        // Transaction value anomaly
        if (checkValueAnomaly(_contract, _value)) {
            triggerSuspiciousActivity(_contract, _actor, "Abnormal transaction value", 2);
        }
        
        // Frequency anomaly detection
        if (checkFrequencyAnomaly(_contract, _actor)) {
            triggerSuspiciousActivity(_contract, _actor, "High frequency transactions", 4);
        }
        
        // Flash loan pattern detection
        if (checkFlashLoanPattern(_contract, _actor)) {
            triggerSuspiciousActivity(_contract, _actor, "Flash loan pattern detected", 5);
            executeEmergencyAction(_contract, EmergencyAction.PAUSE_CONTRACT, "Flash loan attack detected");
        }
        
        // Update transaction data
        updateTransactionData(_contract, _value, _gasPrice);
        
        // Check for suspicious patterns
        analyzeTransactionPattern(_contract, _actor);
    }
    
    /**
     * @dev Rate limiting check
     */
    function checkRateLimit(address _contract, address _actor) internal returns (bool) {
        MonitoringConfig memory config = contractConfigs[_contract];
        uint256 timeWindow = config.timeWindow;
        uint256 currentTime = block.timestamp;
        
        // Reset counter if time window has passed
        if (currentTime >= lastTransactionTime[_actor] + timeWindow) {
            transactionCounts[_actor] = 0;
        }
        
        transactionCounts[_actor]++;
        lastTransactionTime[_actor] = currentTime;
        
        return transactionCounts[_actor] > config.maxTransactionsPerWindow;
    }
    
    /**
     * @dev Gas price anomaly detection
     */
    function checkGasPriceAnomaly(address _contract, uint256 _gasPrice) internal returns (bool) {
        recentGasPrices[_contract].push(_gasPrice);
        
        // Keep only recent prices (last 100 transactions)
        if (recentGasPrices[_contract].length > 100) {
            // Remove oldest element (inefficient but simple)
            for (uint256 i = 0; i < recentGasPrices[_contract].length - 1; i++) {
                recentGasPrices[_contract][i] = recentGasPrices[_contract][i + 1];
            }
            recentGasPrices[_contract].pop();
        }
        
        // Calculate median gas price
        if (recentGasPrices[_contract].length >= 3) {
            uint256 median = calculateMedian(recentGasPrices[_contract]);
            uint256 threshold = (median * 150) / 100; // 50% above median
            
            if (_gasPrice > threshold) {
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * @dev Transaction value anomaly detection
     */
    function checkValueAnomaly(address _contract, uint256 _value) internal returns (bool) {
        recentTransactionValues[_contract].push(_value);
        
        // Keep only recent values
        if (recentTransactionValues[_contract].length > 100) {
            for (uint256 i = 0; i < recentTransactionValues[_contract].length - 1; i++) {
                recentTransactionValues[_contract][i] = recentTransactionValues[_contract][i + 1];
            }
            recentTransactionValues[_contract].pop();
        }
        
        // Check for significantly higher values
        if (recentTransactionValues[_contract].length >= 3) {
            uint256 median = calculateMedian(recentTransactionValues[_contract]);
            uint256 threshold = (median * 1000) / 100; // 1000% above median
            
            if (_value > threshold && median > 0) {
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * @dev Frequency anomaly detection
     */
    function checkFrequencyAnomaly(address _contract, address _actor) internal returns (bool) {
        // Multiple transactions in the same block
        if (block.number == lastTransactionTime[_actor]) {
            return true;
        }
        
        // Very high frequency (more than 10 transactions per minute)
        if (block.timestamp < lastTransactionTime[_actor] + 6) {
            return true;
        }
        
        return false;
    }
    
    /**
     * @dev Flash loan pattern detection
     */
    function checkFlashLoanPattern(address _contract, address _actor) internal returns (bool) {
        // Check for rapid large transactions
        if (recentTransactionValues[_contract].length > 0) {
            uint256 lastValue = recentTransactionValues[_contract][recentTransactionValues[_contract].length - 1];
            if (lastValue > 0) {
                // Same actor making rapid large transactions
                uint256 sameBlockTransactions = 0;
                for (uint256 i = 0; i < transactionCounts[_actor]; i++) {
                    if (block.number == lastTransactionTime[_actor]) {
                        sameBlockTransactions++;
                    }
                }
                
                if (sameBlockTransactions > 3) {
                    return true;
                }
            }
        }
        
        return false;
    }
    
    /**
     * @dev Calculate median of array
     */
    function calculateMedian(uint256[] storage arr) internal view returns (uint256) {
        uint256 length = arr.length;
        if (length == 0) return 0;
        
        // Simple sort (inefficient but works for small arrays)
        uint256[] memory sorted = new uint256[](length);
        for (uint256 i = 0; i < length; i++) {
            sorted[i] = arr[i];
        }
        
        // Bubble sort
        for (uint256 i = 0; i < length; i++) {
            for (uint256 j = i + 1; j < length; j++) {
                if (sorted[i] > sorted[j]) {
                    uint256 temp = sorted[i];
                    sorted[i] = sorted[j];
                    sorted[j] = temp;
                }
            }
        }
        
        // Return median
        if (length % 2 == 0) {
            return (sorted[length / 2 - 1] + sorted[length / 2]) / 2;
        } else {
            return sorted[length / 2];
        }
    }
    
    /**
     * @dev Update transaction data
     */
    function updateTransactionData(address _contract, uint256 _value, uint256 _gasPrice) internal {
        // Store recent transaction data for pattern analysis
        recentGasPrices[_contract].push(_gasPrice);
        recentTransactionValues[_contract].push(_value);
        
        // Maintain array sizes
        if (recentGasPrices[_contract].length > 100) {
            for (uint256 i = 0; i < recentGasPrices[_contract].length - 1; i++) {
                recentGasPrices[_contract][i] = recentGasPrices[_contract][i + 1];
            }
            recentGasPrices[_contract].pop();
        }
        
        if (recentTransactionValues[_contract].length > 100) {
            for (uint256 i = 0; i < recentTransactionValues[_contract].length - 1; i++) {
                recentTransactionValues[_contract][i] = recentTransactionValues[_contract][i + 1];
            }
            recentTransactionValues[_contract].pop();
        }
    }
    
    /**
     * @dev Analyze transaction patterns for complex attacks
     */
    function analyzeTransactionPattern(address _contract, address _actor) internal {
        // Check for sandwich attacks (high gas price before and after)
        if (recentGasPrices[_contract].length >= 3) {
            uint256 recent1 = recentGasPrices[_contract][recentGasPrices[_contract].length - 1];
            uint256 recent2 = recentGasPrices[_contract][recentGasPrices[_contract].length - 2];
            uint256 recent3 = recentGasPrices[_contract][recentGasPrices[_contract].length - 3];
            
            if (recent1 > recent2 && recent3 > recent2) {
                // Pattern: High -> Low -> High (potential sandwich)
                triggerSuspiciousActivity(_contract, _actor, "Potential sandwich attack", 3);
            }
        }
        
        // Check for front-running patterns
        if (recentTransactionValues[_contract].length >= 2) {
            uint256 lastValue = recentTransactionValues[_contract][recentTransactionValues[_contract].length - 1];
            if (lastValue > 0) {
                // Unusually high transaction following normal transactions
                uint256[] memory recentValues = recentTransactionValues[_contract];
                uint256 sum = 0;
                uint256 count = 0;
                
                for (uint256 i = 0; i < recentValues.length - 1 && i < 10; i++) {
                    sum += recentValues[i];
                    count++;
                }
                
                if (count > 0) {
                    uint256 avg = sum / count;
                    if (lastValue > avg * 10) {
                        triggerSuspiciousActivity(_contract, _actor, "Potential front-running", 3);
                    }
                }
            }
        }
    }
    
    /**
     * @dev Trigger suspicious activity response
     */
    function triggerSuspiciousActivity(
        address _contract,
        address _actor,
        string memory _activityType,
        uint256 _severity
    ) internal {
        emit SuspiciousActivityDetected(_contract, _actor, _activityType, _severity);
        
        // Log the activity for further analysis
        emit MonitoringAlert(
            _contract,
            "Suspicious Activity",
            string(abi.encodePacked(_activityType, " by ", _actor))
        );
        
        // Automatic emergency response for high severity
        if (_severity >= 4) {
            executeEmergencyAction(_contract, EmergencyAction.RESTRICT_ACCESS, "High severity suspicious activity");
        }
    }
    
    /**
     * @dev Execute emergency action
     */
    function executeEmergencyAction(
        address _contract,
        EmergencyAction _action,
        string memory _reason
    ) internal emergencyCooldownCheck(_contract) {
        emergencyActions[_contract] = _action;
        lastEmergencyAction[_contract] = block.timestamp;
        
        emit EmergencyActionTriggered(_contract, _action, _reason);
        
        // Execute the action
        if (_action == EmergencyAction.PAUSE_CONTRACT) {
            isPaused[_contract] = true;
            emit MonitoringAlert(_contract, "Contract Paused", _reason);
        } else if (_action == EmergencyAction.RESTRICT_ACCESS) {
            // Restrict access would be implemented in the monitored contract
            emit MonitoringAlert(_contract, "Access Restricted", _reason);
        } else if (_action == EmergencyAction.PAUSE_ALL) {
            // Pause all contracts
            emit MonitoringAlert(address(0), "All Contracts Paused", _reason);
        } else if (_action == EmergencyAction.NOTIFY_ADMIN) {
            emit MonitoringAlert(_contract, "Admin Notification", _reason);
        }
    }
    
    /**
     * @dev Manual emergency pause
     */
    function emergencyPause(address _contract) external onlySecurityOfficer {
        executeEmergencyAction(_contract, EmergencyAction.PAUSE_CONTRACT, "Manual emergency pause");
    }
    
    /**
     * @dev Resume contract operation
     */
    function resumeContract(address _contract) external onlyAdmin {
        isPaused[_contract] = false;
        emit MonitoringAlert(_contract, "Contract Resumed", "Manual resume by admin");
    }
    
    /**
     * @dev Add monitor
     */
    function addMonitor(address _monitor) external onlyAdmin {
        monitors[_monitor] = true;
    }
    
    /**
     * @dev Remove monitor
     */
    function removeMonitor(address _monitor) external onlyAdmin {
        monitors[_monitor] = false;
    }
    
    /**
     * @dev Get monitoring statistics
     */
    function getMonitoringStats(address _contract) external view returns (
        bool isActive,
        uint256 totalTransactions,
        uint256 suspiciousActivities,
        bool isContractPaused
    ) {
        MonitoringConfig memory config = contractConfigs[_contract];
        return (
            config.isActive,
            transactionCounts[_contract],
            0, // This would be tracked separately
            isPaused[_contract]
        );
    }
    
    /**
     * @dev Set anomaly detection parameters
     */
    function setAnomalyParams(
        address _contract,
        uint256 _gasPriceThreshold,
        uint256 _valueThreshold,
        uint256 _frequencyThreshold,
        uint256 _flashLoanThreshold
    ) external onlyAdmin {
        // Store parameters for later use
        // In a full implementation, these would be stored in a mapping
    }
}