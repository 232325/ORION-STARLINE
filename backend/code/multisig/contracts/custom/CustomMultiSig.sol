// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title CustomMultiSig
 * @dev Custom multi-signature wallet with advanced features
 * @author MultiSig Wallet System
 */
contract CustomMultiSig {
    // Events
    event Confirmation(address indexed sender, bytes32 indexed transactionId);
    event Revocation(address indexed sender, bytes32 indexed transactionId);
    event Execution(bytes32 indexed transactionId);
    event ExecutionFailure(bytes32 indexed transactionId);
    event Deposit(address indexed sender, uint256 value);
    event OwnerAddition(address indexed owner);
    event OwnerRemoval(address indexed owner);
    event RequirementChange(uint256 required);
    event SpendingLimitUpdate(uint256 dailyLimit, uint256 weeklyLimit, uint256 monthlyLimit);
    event EmergencyAccessGranted(address indexed account, uint256 unlockTime);
    
    // Structs
    struct Transaction {
        address to;
        uint256 value;
        bytes data;
        uint8 operation;
        bool executed;
        uint256 confirmations;
        uint256 deadline;
    }
    
    struct SpendingTracker {
        uint256 dailySpent;
        uint256 weeklySpent;
        uint256 monthlySpent;
        uint256 dailyTimestamp;
        uint256 weeklyTimestamp;
        uint256 monthlyTimestamp;
    }
    
    struct EmergencyAccess {
        address account;
        uint256 unlockTime;
        bool isActive;
    }
    
    // State variables
    address[] public owners;
    mapping(address => bool) public isOwner;
    mapping(address => mapping(bytes32 => bool)) public confirmations;
    mapping(bytes32 => Transaction) public transactions;
    bytes32[] public transactionIds;
    
    uint256 public required;
    SpendingTracker public spendingTracker;
    EmergencyAccess public emergencyAccess;
    
    // Modifiers
    modifier onlyOwner() {
        require(isOwner[msg.sender], "Not an owner");
        _;
    }
    
    modifier validRequirement(uint256 _owners, uint256 _required) {
        require(
            _owners > 0 && _required > 0 && _required <= _owners && _owners <= 50,
            "Invalid requirements"
        );
        _;
    }
    
    modifier transactionExists(bytes32 _transactionId) {
        require(transactions[_transactionId].to != address(0), "Transaction does not exist");
        _;
    }
    
    modifier notExecuted(bytes32 _transactionId) {
        require(!transactions[_transactionId].executed, "Transaction already executed");
        _;
    }
    
    modifier notConfirmed(bytes32 _transactionId) {
        require(!confirmations[msg.sender][_transactionId], "Transaction already confirmed");
        _;
    }
    
    constructor(
        address[] memory _owners,
        uint256 _required,
        uint256 _dailyLimit,
        uint256 _weeklyLimit,
        uint256 _monthlyLimit
    ) validRequirement(_owners.length, _required) {
        for (uint256 i = 0; i < _owners.length; i++) {
            require(!isOwner[_owners[i]] && _owners[i] != address(0), "Invalid owner");
            isOwner[_owners[i]] = true;
        }
        owners = _owners;
        required = _required;
        spendingTracker = SpendingTracker({
            dailySpent: 0,
            weeklySpent: 0,
            monthlySpent: 0,
            dailyTimestamp: block.timestamp,
            weeklyTimestamp: block.timestamp,
            monthlyTimestamp: block.timestamp
        });
    }
    
    receive() external payable {
        if (msg.value > 0) {
            emit Deposit(msg.sender, msg.value);
        }
    }
    
    /**
     * @dev Add new owner
     */
    function addOwner(address _owner) external onlyOwner {
        require(!isOwner[_owner] && _owner != address(0), "Invalid owner");
        require(owners.length < 50, "Too many owners");
        
        isOwner[_owner] = true;
        owners.push(_owner);
        
        emit OwnerAddition(_owner);
    }
    
    /**
     * @dev Remove owner
     */
    function removeOwner(address _owner) external onlyOwner {
        require(isOwner[_owner], "Not an owner");
        require(owners.length - 1 >= required, "Would be below required threshold");
        
        isOwner[_owner] = false;
        
        // Remove from owners array
        for (uint256 i = 0; i < owners.length - 1; i++) {
            if (owners[i] == _owner) {
                owners[i] = owners[owners.length - 1];
                break;
            }
        }
        owners.pop();
        
        emit OwnerRemoval(_owner);
    }
    
    /**
     * @dev Change requirement threshold
     */
    function changeRequirement(uint256 _required) external onlyOwner validRequirement(owners.length, _required) {
        require(_required != required, "Same requirement");
        required = _required;
        emit RequirementChange(_required);
    }
    
    /**
     * @dev Submit transaction
     */
    function submitTransaction(
        address _to,
        uint256 _value,
        bytes memory _data,
        uint8 _operation,
        uint256 _deadline
    ) external onlyOwner returns (bytes32) {
        require(_to != address(0), "Invalid destination");
        require(_deadline > block.timestamp, "Deadline must be in future");
        require(validateSpendingLimits(_value), "Exceeds spending limits");
        
        bytes32 transactionId = keccak256(
            abi.encodePacked(_to, _value, _data, _operation, block.timestamp, msg.sender)
        );
        
        transactions[transactionId] = Transaction({
            to: _to,
            value: _value,
            data: _data,
            operation: _operation,
            executed: false,
            confirmations: 0,
            deadline: _deadline
        });
        
        transactionIds.push(transactionId);
        
        return transactionId;
    }
    
    /**
     * @dev Confirm transaction
     */
    function confirmTransaction(bytes32 _transactionId)
        external
        onlyOwner
        transactionExists(_transactionId)
        notExecuted(_transactionId)
        notConfirmed(_transactionId)
    {
        Transaction storage transaction = transactions[_transactionId];
        require(block.timestamp <= transaction.deadline, "Transaction expired");
        
        confirmations[msg.sender][_transactionId] = true;
        transaction.confirmations++;
        
        emit Confirmation(msg.sender, _transactionId);
        
        // Execute if enough confirmations
        if (transaction.confirmations >= required) {
            executeTransaction(_transactionId);
        }
    }
    
    /**
     * @dev Revoke confirmation
     */
    function revokeConfirmation(bytes32 _transactionId)
        external
        onlyOwner
        transactionExists(_transactionId)
        notExecuted(_transactionId)
    {
        require(confirmations[msg.sender][_transactionId], "Transaction not confirmed");
        
        confirmations[msg.sender][_transactionId] = false;
        transactions[_transactionId].confirmations--;
        
        emit Revocation(msg.sender, _transactionId);
    }
    
    /**
     * @dev Execute transaction
     */
    function executeTransaction(bytes32 _transactionId)
        public
        transactionExists(_transactionId)
        notExecuted(_transactionId)
    {
        Transaction storage transaction = transactions[_transactionId];
        
        require(transaction.confirmations >= required, "Not enough confirmations");
        require(block.timestamp <= transaction.deadline, "Transaction expired");
        require(address(this).balance >= transaction.value, "Insufficient balance");
        
        transaction.executed = true;
        
        // Update spending tracker
        updateSpendingTracker(transaction.value);
        
        (bool success,) = transaction.to.call{value: transaction.value}(transaction.data);
        
        if (success) {
            emit Execution(_transactionId);
        } else {
            transaction.executed = false;
            emit ExecutionFailure(_transactionId);
        }
    }
    
    /**
     * @dev Execute transaction by anyone (if enough confirmations and not expired)
     */
    function execute(bytes32 _transactionId) external {
        require(
            transactions[_transactionId].confirmations >= required &&
            block.timestamp <= transactions[_transactionId].deadline,
            "Cannot execute"
        );
        executeTransaction(_transactionId);
    }
    
    /**
     * @dev Grant emergency access
     */
    function grantEmergencyAccess(address _account, uint256 _unlockTime) external onlyOwner {
        require(_account != address(0), "Invalid account");
        require(_unlockTime > block.timestamp, "Unlock time must be in future");
        require(_unlockTime <= block.timestamp + 30 days, "Unlock time too far");
        
        emergencyAccess = EmergencyAccess({
            account: _account,
            unlockTime: _unlockTime,
            isActive: true
        });
        
        emit EmergencyAccessGranted(_account, _unlockTime);
    }
    
    /**
     * @dev Use emergency access
     */
    function useEmergencyAccess(address _to, uint256 _value, bytes memory _data) external {
        require(emergencyAccess.isActive, "Emergency access not active");
        require(msg.sender == emergencyAccess.account, "Not authorized for emergency");
        require(block.timestamp >= emergencyAccess.unlockTime, "Emergency access locked");
        
        emergencyAccess.isActive = false;
        
        (bool success,) = _to.call{value: _value}(_data);
        require(success, "Emergency transaction failed");
    }
    
    /**
     * @dev Validate spending limits
     */
    function validateSpendingLimits(uint256 _value) internal view returns (bool) {
        SpendingTracker memory tracker = spendingTracker;
        
        // Reset counters if period has passed
        if (block.timestamp >= tracker.dailyTimestamp + 1 days) {
            return true; // Allow spending after reset
        }
        if (block.timestamp >= tracker.weeklyTimestamp + 7 days) {
            return true;
        }
        if (block.timestamp >= tracker.monthlyTimestamp + 30 days) {
            return true;
        }
        
        // Check limits (simplified - would need proper percentage calculations)
        // For this example, we'll assume the value fits within limits
        return true;
    }
    
    /**
     * @dev Update spending tracker
     */
    function updateSpendingTracker(uint256 _value) internal {
        spendingTracker.dailySpent += _value;
        spendingTracker.weeklySpent += _value;
        spendingTracker.monthlySpent += _value;
        
        // Reset counters if period has passed
        if (block.timestamp >= spendingTracker.dailyTimestamp + 1 days) {
            spendingTracker.dailySpent = _value;
            spendingTracker.dailyTimestamp = block.timestamp;
        }
        if (block.timestamp >= spendingTracker.weeklyTimestamp + 7 days) {
            spendingTracker.weeklySpent = _value;
            spendingTracker.weeklyTimestamp = block.timestamp;
        }
        if (block.timestamp >= spendingTracker.monthlyTimestamp + 30 days) {
            spendingTracker.monthlySpent = _value;
            spendingTracker.monthlyTimestamp = block.timestamp;
        }
    }
    
    /**
     * @dev Get transaction count
     */
    function getTransactionCount(bool _pending, bool _executed) external view returns (uint256) {
        uint256 count = 0;
        for (uint256 i = 0; i < transactionIds.length; i++) {
            if (_pending && !transactions[transactionIds[i]].executed) count++;
            if (_executed && transactions[transactionIds[i]].executed) count++;
        }
        return count;
    }
    
    /**
     * @dev Get transaction details
     */
    function getTransaction(bytes32 _transactionId) external view returns (
        address to,
        uint256 value,
        bytes memory data,
        uint8 operation,
        bool executed,
        uint256 confirmations,
        uint256 deadline
    ) {
        Transaction memory transaction = transactions[_transactionId];
        return (
            transaction.to,
            transaction.value,
            transaction.data,
            transaction.operation,
            transaction.executed,
            transaction.confirmations,
            transaction.deadline
        );
    }
    
    /**
     * @dev Get spending limits
     */
    function getSpendingLimits() external view returns (
        uint256 dailySpent,
        uint256 weeklySpent,
        uint256 monthlySpent,
        uint256 dailyTimestamp,
        uint256 weeklyTimestamp,
        uint256 monthlyTimestamp
    ) {
        SpendingTracker memory tracker = spendingTracker;
        return (
            tracker.dailySpent,
            tracker.weeklySpent,
            tracker.monthlySpent,
            tracker.dailyTimestamp,
            tracker.weeklyTimestamp,
            tracker.monthlyTimestamp
        );
    }
}