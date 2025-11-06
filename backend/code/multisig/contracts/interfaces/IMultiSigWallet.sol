// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title IMultiSigWallet
 * @dev Interface for multi-signature wallet
 * @author MultiSig Wallet System
 */
interface IMultiSigWallet {
    // Events
    event TransactionSubmitted(bytes32 indexed transactionId, address indexed submitter);
    event TransactionConfirmed(bytes32 indexed transactionId, address indexed confirmer);
    event TransactionExecuted(bytes32 indexed transactionId);
    event OwnerAdded(address indexed owner);
    event OwnerRemoved(address indexed owner);
    event RequirementChanged(uint256 required);
    
    // Functions
    function submitTransaction(
        address to,
        uint256 value,
        bytes calldata data,
        uint8 operation
    ) external returns (bytes32 transactionId);
    
    function confirmTransaction(bytes32 transactionId) external;
    
    function executeTransaction(bytes32 transactionId) external;
    
    function addOwner(address owner) external;
    
    function removeOwner(address owner) external;
    
    function changeRequirement(uint256 _required) external;
    
    function getTransaction(bytes32 transactionId) external view returns (
        address to,
        uint256 value,
        bytes memory data,
        uint8 operation,
        bool executed,
        uint256 confirmations
    );
    
    function getTransactionIds(uint256 from, uint256 to) external view returns (bytes32[] memory transactionIds);
    
    function getOwners() external view returns (address[] memory owners);
    
    function getRequirement() external view returns (uint256 required);
}