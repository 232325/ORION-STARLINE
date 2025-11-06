// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title ReentrancyGuard
 * @dev Reentrancy hujumidan himoya
 */
abstract contract ReentrancyGuard {
    // Constants
    uint256 private constant _NOT_ENTERED = 1;
    uint256 private constant _ENTERED = 2;
    
    // State variable
    uint256 private _status;
    
    // Events
    event ReentrancyGuardTriggered(address indexed target, bytes4 indexed functionSelector);
    
    /**
     * @dev Constructor - set initial status
     */
    constructor() {
        _status = _NOT_ENTERED;
    }
    
    /**
     * @dev Modifier to prevent reentrancy
     */
    modifier nonReentrant() {
        require(_status != _ENTERED, "ReentrancyGuard: reentrant call");
        _status = _ENTERED;
        _;
        _status = _NOT_ENTERED;
    }
    
    /**
     * @dev Check if currently reentering
     */
    function isReentering() external view returns (bool) {
        return _status == _ENTERED;
    }
    
    /**
     * @dev Get current status
     */
    function getReentrancyStatus() external view returns (uint256) {
        return _status;
    }
}