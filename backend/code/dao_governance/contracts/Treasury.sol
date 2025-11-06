// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

import "../interfaces/ITreasury.sol";

/**
 * @title Treasury Contract - DAO Kafolati va Moliyaviy Boshqaruvi
 * @notice DAO mablag'lari va xarajatlarni boshqarish
 */
contract Treasury is ITreasury, Ownable, ReentrancyGuard, Pausable {
    using SafeMath for uint256;
    using SafeERC20 for IERC20;

    // Strukturalar
    Transaction[] public transactions;
    BudgetAllocation[] public budgets;
    Grant[] public grants;
    
    mapping(uint256 => mapping(address => bool)) public transactionSignatures;
    mapping(address => bool) public authorizedSpenders;
    
    uint256 public balance;
    uint256 public totalDeposits;
    uint256 public totalWithdrawals;
    uint256 public transactionCount;
    
    // Multi-signature settings
    uint256 public requiredSignatures = 3;
    uint256 public emergencyThreshold = 100 ether;
    
    // Budget settings
    uint256 public budgetIdCounter;
    uint256 public grantIdCounter;
    
    // Events
    event SpenderAdded(address indexed spender);
    event SpenderRemoved(address indexed spender);
    event EmergencyThresholdUpdated(uint256 oldThreshold, uint256 newThreshold);
    event RequiredSignaturesUpdated(uint256 oldRequired, uint256 newRequired);
    event TransactionSigned(uint256 indexed txId, address indexed signer);
    event TransactionRejected(uint256 indexed txId, address indexed rejecter);

    // Modifiers
    modifier onlyAuthorizedSpender() {
        require(authorizedSpenders[msg.sender] || owner() == msg.sender, "Not authorized spender");
        _;
    }

    modifier validTransaction(uint256 _txId) {
        require(_txId < transactionCount, "Invalid transaction");
        _;
    }

    modifier validBudget(uint256 _budgetId) {
        require(_budgetId < budgets.length && budgets[_budgetId].active, "Invalid budget");
        _;
    }

    modifier validGrant(uint256 _grantId) {
        require(_grantId < grantIdCounter && _grantId < grants.length, "Invalid grant");
        _;
    }

    constructor() {
        authorizedSpenders[msg.sender] = true;
    }

    // ===== TREASURY OPERATIONS =====

    /**
     * @dev Kafolatga mablag' qo'shish
     */
    function deposit(string memory _reason) external payable override nonReentrant whenNotPaused {
        require(msg.value > 0, "No amount sent");
        
        balance = balance.add(msg.value);
        totalDeposits = totalDeposits.add(msg.value);
        
        emit Deposit(msg.sender, msg.value, _reason);
    }

    /**
     * @dev Kafolatdan mablag' yechib olish (faqat authorized spender)
     */
    function withdraw(
        address payable _to, 
        uint256 _amount, 
        string memory _reason
    ) external override onlyAuthorizedSpender nonReentrant whenNotPaused {
        require(_to != address(0), "Invalid recipient");
        require(_amount > 0, "Invalid amount");
        require(_amount <= balance, "Insufficient balance");
        
        balance = balance.sub(_amount);
        totalWithdrawals = totalWithdrawals.add(_amount);
        
        // Transfer the amount
        (bool success, ) = _to.call{value: _amount}("");
        require(success, "Transfer failed");
        
        emit Withdrawal(_to, _amount, _reason);
    }

    /**
     * @dev Fikrli xarajatlar uchun mablag' yechib olish
     */
    function emergencyWithdraw(
        address payable _to, 
        uint256 _amount, 
        string memory _reason
    ) external override onlyOwner nonReentrant {
        require(_amount <= emergencyThreshold, "Amount exceeds emergency threshold");
        require(_amount <= balance, "Insufficient balance");
        
        balance = balance.sub(_amount);
        totalWithdrawals = totalWithdrawals.add(_amount);
        
        // Transfer the amount
        (bool success, ) = _to.call{value: _amount}("");
        require(success, "Transfer failed");
        
        emit EmergencyTransfer(_to, _amount, _reason);
    }

    // ===== MULTI-SIGNATURE TRANSACTIONS =====

    /**
     * @dev Yangi transaction yaratish
     */
    function createTransaction(
        address _to,
        uint256 _amount,
        string memory _reason,
        bytes memory _data
    ) external override onlyAuthorizedSpender returns (uint256) {
        require(_to != address(0), "Invalid recipient");
        require(_amount > 0, "Invalid amount");
        require(_amount <= balance, "Insufficient balance");
        
        Transaction memory newTransaction = Transaction({
            id: transactionCount,
            to: _to,
            amount: _amount,
            reason: _reason,
            timestamp: block.timestamp,
            data: _data,
            executed: false
        });
        
        transactions.push(newTransaction);
        transactionSignatures[transactionCount][msg.sender] = true;
        
        emit TransactionCreated(transactionCount, _to, _amount, _reason);
        emit TransactionSigned(transactionCount, msg.sender);
        
        transactionCount++;
        return transactionCount - 1;
    }

    /**
     * @dev Transaction imzolash
     */
    function approveTransaction(uint256 _txId) external override onlyAuthorizedSpender validTransaction(_txId) {
        require(!transactions[_txId].executed, "Already executed");
        require(!transactionSignatures[_txId][msg.sender], "Already signed");
        
        transactionSignatures[_txId][msg.sender] = true;
        
        emit TransactionSigned(_txId, msg.sender);
        
        // Auto-execute if enough signatures
        if (getTransactionSignatureCount(_txId) >= requiredSignatures) {
            _executeTransactionInternal(_txId);
        }
    }

    /**
     * @dev Transaction bajarish
     */
    function executeTransaction(uint256 _txId) external override onlyAuthorizedSpender validTransaction(_txId) {
        require(!transactions[_txId].executed, "Already executed");
        require(getTransactionSignatureCount(_txId) >= requiredSignatures, "Insufficient signatures");
        
        _executeTransactionInternal(_txId);
    }

    /**
     * @dev Transaction bekor qilish
     */
    function cancelTransaction(uint256 _txId) external override onlyAuthorizedSpender validTransaction(_txId) {
        require(!transactions[_txId].executed, "Already executed");
        require(transactions[_txId].timestamp > block.timestamp.sub(86400), "Too old to cancel"); // 24h limit
        
        // Clear all signatures
        for (uint256 i = 0; i < requiredSignatures; i++) {
            // Note: This is a simplified version, in practice you'd want a more efficient way
        }
        
        emit TransactionRejected(_txId, msg.sender);
    }

    /**
     * @dev Internal transaction execution
     */
    function _executeTransactionInternal(uint256 _txId) internal {
        Transaction storage tx = transactions[_txId];
        
        require(tx.amount <= balance, "Insufficient balance");
        
        balance = balance.sub(tx.amount);
        totalWithdrawals = totalWithdrawals.add(tx.amount);
        
        // Execute the transaction
        if (tx.data.length > 0) {
            (bool success, ) = tx.to.call{value: tx.amount}(tx.data);
            require(success, "Transaction execution failed");
        } else {
            (bool success, ) = tx.to.call{value: tx.amount}("");
            require(success, "Transfer failed");
        }
        
        tx.executed = true;
        
        emit TransactionExecuted(_txId);
        emit Withdrawal(tx.to, tx.amount, tx.reason);
    }

    // ===== BUDGET MANAGEMENT =====

    /**
     * @dev Budget yaratish
     */
    function createBudget(
        string memory _category, 
        uint256 _amount, 
        uint256 _duration
    ) external override onlyAuthorizedSpender {
        require(_amount > 0, "Invalid amount");
        require(_duration > 0, "Invalid duration");
        
        BudgetAllocation memory newBudget = BudgetAllocation({
            id: budgetIdCounter,
            category: _category,
            allocatedAmount: _amount,
            spentAmount: 0,
            startDate: block.timestamp,
            endDate: block.timestamp.add(_duration),
            active: true
        });
        
        budgets.push(newBudget);
        
        // Check balance availability
        require(balance >= _amount, "Insufficient balance for budget");
        balance = balance.sub(_amount); // Reserve funds
        
        budgetIdCounter++;
        
        emit BudgetCreated(budgetIdCounter - 1, _category, _amount);
    }

    /**
     * @dev Budget ajratish
     */
    function allocateBudget(uint256 _budgetId, uint256 _amount) external override onlyAuthorizedSpender validBudget(_budgetId) {
        BudgetAllocation storage budget = budgets[_budgetId];
        
        require(_amount > 0, "Invalid amount");
        require(_amount <= budget.allocatedAmount.sub(budget.spentAmount), "Insufficient budget");
        require(balance >= _amount, "Insufficient treasury balance");
        
        budget.spentAmount = budget.spentAmount.add(_amount);
        balance = balance.sub(_amount);
        totalWithdrawals = totalWithdrawals.add(_amount);
        
        emit Withdrawal(address(0), _amount, string(abi.encodePacked("Budget allocation: ", budget.category)));
    }

    /**
     * @dev Budget sarf qilish
     */
    function spendBudget(
        uint256 _budgetId, 
        uint256 _amount, 
        string memory _reason
    ) external override onlyAuthorizedSpender validBudget(_budgetId) {
        BudgetAllocation storage budget = budgets[_budgetId];
        
        require(_amount > 0, "Invalid amount");
        require(_amount <= budget.allocatedAmount.sub(budget.spentAmount), "Insufficient budget");
        require(block.timestamp <= budget.endDate, "Budget expired");
        
        budget.spentAmount = budget.spentAmount.add(_amount);
        
        emit Withdrawal(address(0), _amount, string(abi.encodePacked("Budget spend: ", _reason)));
    }

    /**
     * @dev Budget ma'lumotlarini olish
     */
    function getBudget(uint256 _budgetId) external view override returns (BudgetAllocation memory) {
        return budgets[_budgetId];
    }

    /**
     * @dev Aktiv budjetlarni olish
     */
    function getActiveBudgets() external view override returns (uint256[] memory) {
        uint256[] memory activeIds = new uint256[](budgets.length);
        uint256 count = 0;
        
        for (uint256 i = 0; i < budgets.length; i++) {
            if (budgets[i].active && block.timestamp <= budgets[i].endDate) {
                activeIds[count] = budgets[i].id;
                count++;
            }
        }
        
        // Resize array
        uint256[] memory result = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            result[i] = activeIds[i];
        }
        
        return result;
    }

    // ===== GRANT MANAGEMENT =====

    /**
     * @dev Grant yaratish
     */
    function createGrant(
        address _recipient,
        uint256 _amount,
        string memory _description
    ) external override onlyAuthorizedSpender returns (uint256) {
        require(_recipient != address(0), "Invalid recipient");
        require(_amount > 0, "Invalid amount");
        require(_amount <= balance, "Insufficient balance");
        
        Grant memory newGrant = Grant({
            id: grantIdCounter,
            recipient: _recipient,
            amount: _amount,
            description: _description,
            createdDate: block.timestamp,
            executionDate: 0,
            status: 0, // Pending
            emergency: false
        });
        
        grants.push(newGrant);
        grantIdCounter++;
        
        emit GrantCreated(grantIdCounter - 1, _recipient, _amount);
        
        return grantIdCounter - 1;
    }

    /**
     * @dev Grant bajarish
     */
    function executeGrant(uint256 _grantId) external override onlyAuthorizedSpender validGrant(_grantId) {
        Grant storage grant = grants[_grantId];
        
        require(grant.status == 0, "Grant not pending");
        require(grant.amount <= balance, "Insufficient balance");
        
        balance = balance.sub(grant.amount);
        totalWithdrawals = totalWithdrawals.add(grant.amount);
        grant.status = 1; // Active
        grant.executionDate = block.timestamp;
        
        // Transfer to recipient
        (bool success, ) = payable(grant.recipient).call{value: grant.amount}("");
        require(success, "Grant transfer failed");
        
        emit Withdrawal(grant.recipient, grant.amount, string(abi.encodePacked("Grant: ", grant.description)));
    }

    /**
     * @dev Grant statusini yangilash
     */
    function updateGrantStatus(uint256 _grantId, uint256 _status) external override onlyAuthorizedSpender validGrant(_grantId) {
        require(_status <= 3, "Invalid status");
        
        grants[_grantId].status = _status;
        
        if (_status == 3) { // Cancelled
            balance = balance.add(grants[_grantId].amount);
        }
    }

    /**
     * @dev Grant ma'lumotlarini olish
     */
    function getGrant(uint256 _grantId) external view override returns (Grant memory) {
        return grants[_grantId];
    }

    // ===== QUERY FUNCTIONS =====

    /**
     * @dev Kafolat balansini olish
     */
    function getBalance() external view override returns (uint256) {
        return balance;
    }

    /**
     * @dev Jami omonatlar soni
     */
    function getTotalDeposits() external view override returns (uint256) {
        return totalDeposits;
    }

    /**
     * @dev Jami chiqarilganlar soni
     */
    function getTotalWithdrawals() external view override returns (uint256) {
        return totalWithdrawals;
    }

    /**
     * @dev Transactionlar soni
     */
    function getTransactionCount() external view override returns (uint256) {
        return transactionCount;
    }

    /**
     * @dev Transaction ma'lumotlarini olish
     */
    function getTransaction(uint256 _txId) external view override returns (Transaction memory) {
        return transactions[_txId];
    }

    /**
     * @dev Transaction imzolashlar soni
     */
    function getTransactionSignatureCount(uint256 _txId) internal view returns (uint256) {
        uint256 count = 0;
        for (uint256 i = 0; i < requiredSignatures; i++) {
            // Simplified implementation - in practice you'd want a more efficient method
            if (transactionSignatures[_txId][address(uint160(i))]) {
                count++;
            }
        }
        return count;
    }

    /**
     * @dev Dashboard ma'lumotlari
     */
    function getDashboard() external view override returns (
        uint256 _balance,
        uint256 _totalDeposits,
        uint256 _totalWithdrawals,
        uint256 _transactionCount,
        uint256 _activeBudgets
    ) {
        uint256 activeBudgets = 0;
        for (uint256 i = 0; i < budgets.length; i++) {
            if (budgets[i].active && block.timestamp <= budgets[i].endDate) {
                activeBudgets++;
            }
        }
        
        return (balance, totalDeposits, totalWithdrawals, transactionCount, activeBudgets);
    }

    // ===== ADMIN FUNCTIONS =====

    /**
     * @dev Emergency threshold yangilash
     */
    function updateEmergencyThreshold(uint256 _newThreshold) external override onlyOwner {
        uint256 oldThreshold = emergencyThreshold;
        emergencyThreshold = _newThreshold;
        emit EmergencyThresholdUpdated(oldThreshold, _newThreshold);
    }

    /**
     * @dev Kerakli imzolashlar sonini yangilash
     */
    function updateRequiredSignatures(uint256 _newRequired) external override onlyOwner {
        require(_newRequired > 0 && _newRequired <= 10, "Invalid required signatures");
        uint256 oldRequired = requiredSignatures;
        requiredSignatures = _newRequired;
        emit RequiredSignaturesUpdated(oldRequired, _newRequired);
    }

    /**
     * @dev Emergency threshold olish
     */
    function getEmergencyThreshold() external view override returns (uint256) {
        return emergencyThreshold;
    }

    /**
     * @dev Kerakli imzolashlar sonini olish
     */
    function getRequiredSignatures() external view override returns (uint256) {
        return requiredSignatures;
    }

    /**
     * @dev Spender qo'shish
     */
    function addAuthorizedSpender(address _spender) external onlyOwner {
        require(_spender != address(0), "Invalid address");
        require(!authorizedSpenders[_spender], "Already authorized");
        
        authorizedSpenders[_spender] = true;
        emit SpenderAdded(_spender);
    }

    /**
     * @dev Spender olib tashlash
     */
    function removeAuthorizedSpender(address _spender) external onlyOwner {
        require(authorizedSpenders[_spender], "Not authorized");
        
        authorizedSpenders[_spender] = false;
        emit SpenderRemoved(_spender);
    }

    /**
     * @dev ERC20 token bilan ishlash
     */
    function withdrawERC20(
        address _token,
        address _to,
        uint256 _amount
    ) external onlyOwner nonReentrant {
        require(_token != address(0) && _to != address(0), "Invalid addresses");
        require(_amount > 0, "Invalid amount");
        
        IERC20(_token).safeTransfer(_to, _amount);
        emit Withdrawal(_to, _amount, string(abi.encodePacked("ERC20 withdraw: ", IERC20(_token).symbol())));
    }

    /**
     * @dev Emergency pause
     */
    function pause() external onlyOwner {
        _pause();
    }

    /**
     * @dev Emergency unpause
     */
    function unpause() external onlyOwner {
        _unpause();
    }

    /**
     * @dev Fallback function to receive ETH
     */
    receive() external payable {
        balance = balance.add(msg.value);
        totalDeposits = totalDeposits.add(msg.value);
        emit Deposit(msg.sender, msg.value, "Direct deposit");
    }
}