// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title ITreasury - Kafolat (Treasury) boshqaruv interfeysi
 * @notice DAO mablag'lari va kafolatni boshqarish
 */
interface ITreasury {
    struct Transaction {
        uint256 id;
        address to;
        uint256 amount;
        string reason;
        uint256 timestamp;
        bytes data;
        bool executed;
    }

    struct BudgetAllocation {
        uint256 id;
        string category;
        uint256 allocatedAmount;
        uint256 spentAmount;
        uint256 startDate;
        uint256 endDate;
        bool active;
    }

    struct Grant {
        uint256 id;
        address recipient;
        uint256 amount;
        string description;
        uint256 createdDate;
        uint256 executionDate;
        uint256 status; // 0: Pending, 1: Active, 2: Completed, 3: Cancelled
        bool emergency;
    }

    enum TransactionStatus {
        Pending,
        Approved,
        Rejected,
        Executed,
        Cancelled
    }

    event Deposit(address indexed from, uint256 amount, string reason);
    event Withdrawal(address indexed to, uint256 amount, string reason);
    event TransactionCreated(uint256 indexed txId, address indexed to, uint256 amount, string reason);
    event TransactionExecuted(uint256 indexed txId);
    event BudgetCreated(uint256 indexed budgetId, string category, uint256 amount);
    event GrantCreated(uint256 indexed grantId, address indexed recipient, uint256 amount);
    event EmergencyTransfer(address indexed to, uint256 amount, string reason);

    // Asosiy funksiyalar
    function deposit(string memory _reason) external payable;
    function withdraw(address payable _to, uint256 _amount, string memory _reason) external;
    function emergencyWithdraw(address payable _to, uint256 _amount, string memory _reason) external;

    // Multi-signature funksiyalar
    function createTransaction(
        address _to,
        uint256 _amount,
        string memory _reason,
        bytes memory _data
    ) external returns (uint256);

    function approveTransaction(uint256 _txId) external;
    function executeTransaction(uint256 _txId) external;
    function cancelTransaction(uint256 _txId) external;

    // Budget boshqaruvi
    function createBudget(string memory _category, uint256 _amount, uint256 _duration) external;
    function allocateBudget(uint256 _budgetId, uint256 _amount) external;
    function spendBudget(uint256 _budgetId, uint256 _amount, string memory _reason) external;
    function getBudget(uint256 _budgetId) external view returns (BudgetAllocation memory);
    function getActiveBudgets() external view returns (uint256[] memory);

    // Grant boshqaruvi
    function createGrant(
        address _recipient,
        uint256 _amount,
        string memory _description
    ) external returns (uint256);

    function executeGrant(uint256 _grantId) external;
    function updateGrantStatus(uint256 _grantId, uint256 _status) external;
    function getGrant(uint256 _grantId) external view returns (Grant memory);

    // So'rov funksiyalari
    function getBalance() external view returns (uint256);
    function getTotalDeposits() external view returns (uint256);
    function getTotalWithdrawals() external view returns (uint256);
    function getTransactionCount() external view returns (uint256);
    function getTransaction(uint256 _txId) external view returns (Transaction memory);

    // Dashboard
    function getDashboard() external view returns (
        uint256 balance,
        uint256 totalDeposits,
        uint256 totalWithdrawals,
        uint256 transactionCount,
        uint256 activeBudgets
    );

    // Configuration
    function updateEmergencyThreshold(uint256 _newThreshold) external;
    function updateRequiredSignatures(uint256 _newRequired) external;
    function getEmergencyThreshold() external view returns (uint256);
    function getRequiredSignatures() external view returns (uint256);
}