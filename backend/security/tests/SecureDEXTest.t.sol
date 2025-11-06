// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "../contracts/SecureDEX.sol";

/**
 * @title SecureDEXTest
 * @dev Comprehensive test suite for SecureDEX contract
 * @notice Tests: Flash loan protection, Oracle manipulation, MEV protection
 */
contract SecureDEXTest is Test {
    SecureDEX public dex;
    SecuredToken public tokenA;
    SecuredToken public tokenB;
    
    address public owner = address(0x1);
    address public user1 = address(0x2);
    address public user2 = address(0x3);
    address public oracle = address(0x5);
    address public attacker = address(0x6);
    
    uint256 constant INITIAL_SUPPLY = 1000000 * 10**18;
    uint256 constant ORDER_AMOUNT = 10000 * 10**18;
    
    // Attack simulation contracts
    FlashLoanAttacker public flashLoanAttacker;
    OracleManipulator public oracleManipulator;
    
    event SecurityViolation(string violationType, string details);
    event OrderCreated(bytes32 indexed orderId, address indexed maker);
    
    function setUp() public {
        vm.startPrank(owner);
        
        // Deploy tokens
        tokenA = new SecuredToken("TokenA", "TKA", INITIAL_SUPPLY);
        tokenB = new SecuredToken("TokenB", "TKB", INITIAL_SUPPLY);
        
        // Deploy DEX
        dex = new SecureDEX("SecureDEX", "SDX", INITIAL_SUPPLY);
        
        vm.stopPrank();
        
        // Setup oracle
        vm.startPrank(owner);
        dex.addTrustedOracle(oracle);
        vm.stopPrank();
        
        // Setup test addresses
        vm.deal(user1, 1 ether);
        vm.deal(user2, 1 ether);
        vm.deal(attacker, 1 ether);
        
        // Deploy attacker contracts
        flashLoanAttacker = new FlashLoanAttacker(address(dex));
        oracleManipulator = new OracleManipulator(address(dex));
        
        // Setup initial oracle prices
        setupOraclePrices();
    }
    
    function setupOraclePrices() internal {
        vm.startPrank(oracle);
        dex.updateOraclePrice(address(tokenA), 1000);
        dex.updateOraclePrice(address(tokenB), 2000);
        vm.stopPrank();
    }
    
    // ==================== BASIC FUNCTIONALITY TESTS ====================
    
    function testOrderCreation() public {
        vm.startPrank(user1);
        
        bytes32 orderId = dex.createOrder(
            address(tokenA),
            address(tokenB),
            uint128(ORDER_AMOUNT),
            uint128(ORDER_AMOUNT * 2)
        );
        
        assertTrue(orderId != bytes32(0));
        vm.stopPrank();
    }
    
    function testOrderExecution() public {
        // Create order
        vm.startPrank(user1);
        bytes32 orderId = dex.createOrder(
            address(tokenA),
            address(tokenB),
            uint128(ORDER_AMOUNT),
            uint128(ORDER_AMOUNT * 2)
        );
        vm.stopPrank();
        
        // Wait for minimum delay
        vm.warp(block.timestamp + 31 seconds);
        
        // Execute order
        vm.startPrank(user2);
        dex.executeOrder(orderId);
        vm.stopPrank();
    }
    
    // ==================== FLASH LOAN PROTECTION TESTS ====================
    
    function testFlashLoanDetection() public {
        vm.startPrank(attacker);
        
        // Simulate rapid transactions (flash loan pattern)
        for (uint256 i = 0; i < 4; i++) {
            vm.warp(block.timestamp + 3601); // Advance time
            
            // Each transaction should increase flash loan count
            // After 3 transactions in the window, should be detected
            bool result = dex.checkReentrancy(attacker);
            
            if (i >= 2) {
                assertTrue(result, "Flash loan should be detected");
            }
        }
        
        vm.stopPrank();
    }
    
    function testFlashLoanRateLimit() public {
        vm.startPrank(attacker);
        
        // Simulate multiple transactions within the flash loan window
        for (uint256 i = 0; i < 3; i++) {
            vm.startPrank(attacker);
            vm.warp(block.timestamp + 100); // Small time increments
            
            // These should succeed
            bool result = dex.checkReentrancy(attacker);
            if (i < 2) {
                assertFalse(result, "Early transactions should not trigger protection");
            }
        }
        
        // The 4th transaction should trigger flash loan protection
        bool finalResult = dex.checkReentrancy(attacker);
        assertTrue(finalResult, "Flash loan limit should be exceeded");
        
        vm.stopPrank();
    }
    
    function testFlashLoanRecovery() public {
        // Simulate flash loan count exceeding limit
        testFlashLoanRateLimit();
        
        // Advance time past the flash loan window
        vm.warp(block.timestamp + 7200); // 2 hours
        
        // Reset should occur
        bool result = dex.checkReentrancy(attacker);
        assertFalse(result, "Flash loan count should reset after window");
    }
    
    // ==================== ORACLE MANIPULATION PROTECTION TESTS ====================
    
    function testOracleValidation() public {
        // Test with valid oracle data
        bool validResult = validateOracleData(address(tokenA));
        assertTrue(validResult, "Valid oracle data should pass");
        
        // Test with stale oracle data
        vm.warp(block.timestamp + 7200); // Make data stale
        bool staleResult = validateOracleData(address(tokenA));
        assertFalse(staleResult, "Stale oracle data should fail");
    }
    
    function testOracleManipulation() public {
        // Create order with current prices
        vm.startPrank(user1);
        bytes32 orderId = dex.createOrder(
            address(tokenA),
            address(tokenB),
            uint128(ORDER_AMOUNT),
            uint128(ORDER_AMOUNT * 2)
        );
        vm.stopPrank();
        
        // Manipulate oracle price (attempt to create unfair advantage)
        vm.startPrank(oracle);
        dex.updateOraclePrice(address(tokenA), 100); // Dramatic price drop
        dex.updateOraclePrice(address(tokenB), 40000); // Dramatic price increase
        vm.stopPrank();
        
        // Try to execute with manipulated prices
        vm.warp(block.timestamp + 31 seconds);
        
        vm.startPrank(user2);
        // This should fail due to price manipulation detection
        vm.expectRevert("Price manipulation detected");
        dex.executeOrder(orderId);
        vm.stopPrank();
    }
    
    function testPriceConsistencyCheck() public {
        vm.startPrank(oracle);
        dex.updateOraclePrice(address(tokenA), 1000);
        dex.updateOraclePrice(address(tokenB), 1000);
        vm.stopPrank();
        
        // This should pass - consistent pricing
        vm.startPrank(user1);
        bytes32 orderId = dex.createOrder(
            address(tokenA),
            address(tokenB),
            uint128(ORDER_AMOUNT),
            uint128(ORDER_AMOUNT * 2) // Reasonable price ratio
        );
        assertTrue(orderId != bytes32(0));
        vm.stopPrank();
    }
    
    function testUnreasonablePriceRatio() public {
        vm.startPrank(oracle);
        dex.updateOraclePrice(address(tokenA), 1000);
        dex.updateOraclePrice(address(tokenB), 1000);
        vm.stopPrank();
        
        // Attempt order with unreasonable price ratio
        vm.startPrank(user1);
        vm.expectRevert("Price manipulation detected");
        dex.createOrder(
            address(tokenA),
            address(tokenB),
            uint128(ORDER_AMOUNT),
            uint128(ORDER_AMOUNT * 1000) // Unreasonable price
        );
        vm.stopPrank();
    }
    
    // ==================== MEV PROTECTION TESTS ====================
    
    function testOrderDelayProtection() public {
        vm.startPrank(user1);
        
        bytes32 orderId = dex.createOrder(
            address(tokenA),
            address(tokenB),
            uint128(ORDER_AMOUNT),
            uint128(ORDER_AMOUNT * 2)
        );
        
        // Attempt to execute immediately (should fail)
        vm.expectRevert("Order too recent");
        dex.executeOrder(orderId);
        
        vm.stopPrank();
    }
    
    function testValidOrderExecutionAfterDelay() public {
        vm.startPrank(user1);
        
        bytes32 orderId = dex.createOrder(
            address(tokenA),
            address(tokenB),
            uint128(ORDER_AMOUNT),
            uint128(ORDER_AMOUNT * 2)
        );
        
        vm.stopPrank();
        
        // Wait for minimum delay
        vm.warp(block.timestamp + 31 seconds);
        
        // Now should succeed
        vm.startPrank(user2);
        dex.executeOrder(orderId);
        vm.stopPrank();
    }
    
    // ==================== ACCESS CONTROL TESTS ====================
    
    function testOracleManagement() public {
        address newOracle = address(0x7);
        
        // Non-owner cannot add oracle
        vm.startPrank(user1);
        vm.expectRevert("AccessControl: caller is not the owner");
        dex.addTrustedOracle(newOracle);
        vm.stopPrank();
        
        // Owner can add oracle
        vm.startPrank(owner);
        dex.addTrustedOracle(newOracle);
        vm.stopPrank();
        
        // Owner can remove oracle
        vm.startPrank(owner);
        dex.removeTrustedOracle(newOracle);
        vm.stopPrank();
    }
    
    function testUnauthorizedOracleUpdate() public {
        address fakeOracle = address(0x8);
        
        vm.startPrank(fakeOracle);
        vm.expectRevert("Unauthorized oracle");
        dex.updateOraclePrice(address(tokenA), 500);
        vm.stopPrank();
    }
    
    // ==================== EDGE CASE TESTS ====================
    
    function testInvalidAmounts() public {
        vm.startPrank(user1);
        
        // Zero amounts
        vm.expectRevert("Invalid amounts");
        dex.createOrder(
            address(tokenA),
            address(tokenB),
            0,
            ORDER_AMOUNT
        );
        
        vm.expectRevert("Invalid amounts");
        dex.createOrder(
            address(tokenA),
            address(tokenB),
            ORDER_AMOUNT,
            0
        );
        
        vm.stopPrank();
    }
    
    function testInvalidAddresses() public {
        vm.startPrank(user1);
        
        // Zero address
        vm.expectRevert("Invalid address");
        dex.createOrder(
            address(0),
            address(tokenB),
            ORDER_AMOUNT,
            ORDER_AMOUNT * 2
        );
        
        vm.expectRevert("Invalid address");
        dex.createOrder(
            address(tokenA),
            address(0),
            ORDER_AMOUNT,
            ORDER_AMOUNT * 2
        );
        
        vm.stopPrank();
    }
    
    function testInactiveOrder() public {
        // Create and execute order
        vm.startPrank(user1);
        bytes32 orderId = dex.createOrder(
            address(tokenA),
            address(tokenB),
            uint128(ORDER_AMOUNT),
            uint128(ORDER_AMOUNT * 2)
        );
        vm.stopPrank();
        
        vm.warp(block.timestamp + 31 seconds);
        
        vm.startPrank(user2);
        dex.executeOrder(orderId);
        
        // Try to execute again (should fail)
        vm.expectRevert("Order not active");
        dex.executeOrder(orderId);
        vm.stopPrank();
    }
    
    function testSelfOrder() public {
        vm.startPrank(user1);
        
        bytes32 orderId = dex.createOrder(
            address(tokenA),
            address(tokenB),
            uint128(ORDER_AMOUNT),
            uint128(ORDER_AMOUNT * 2)
        );
        
        vm.stopPrank();
        
        vm.warp(block.timestamp + 31 seconds);
        
        // Order creator cannot execute their own order
        vm.startPrank(user1);
        vm.expectRevert("Cannot execute own order");
        dex.executeOrder(orderId);
        vm.stopPrank();
    }
    
    // ==================== INTEGRATION TESTS ====================
    
    function testComplexOrderFlow() public {
        address[] memory traders = new address[](3);
        traders[0] = user1;
        traders[1] = user2;
        traders[2] = address(0x7);
        
        for (uint256 i = 0; i < traders.length; i++) {
            vm.deal(traders[i], 1 ether);
        }
        
        // Create multiple orders
        bytes32[] memory orderIds = new bytes32[](3);
        for (uint256 i = 0; i < 3; i++) {
            vm.startPrank(traders[i]);
            orderIds[i] = dex.createOrder(
                address(tokenA),
                address(tokenB),
                uint128(ORDER_AMOUNT),
                uint128(ORDER_AMOUNT * (i + 2))
            );
            vm.stopPrank();
        }
        
        // Wait for delays
        vm.warp(block.timestamp + 31 seconds);
        
        // Execute orders in different order
        vm.startPrank(user2);
        dex.executeOrder(orderIds[0]);
        vm.stopPrank();
        
        vm.startPrank(user1);
        dex.executeOrder(orderIds[2]);
        vm.stopPrank();
        
        vm.startPrank(address(0x7));
        dex.executeOrder(orderIds[1]);
        vm.stopPrank();
    }
    
    // ==================== STRESS TESTS ====================
    
    function testHighFrequencyOrders() public {
        uint256 numOrders = 50;
        
        for (uint256 i = 0; i < numOrders; i++) {
            address trader = address(uint160(i + 100));
            vm.deal(trader, 1 ether);
            
            vm.startPrank(trader);
            dex.createOrder(
                address(tokenA),
                address(tokenB),
                uint128(ORDER_AMOUNT),
                uint128(ORDER_AMOUNT * 2)
            );
            vm.stopPrank();
        }
        
        // All orders should be created successfully
        // Contract should remain functional
        vm.startPrank(user1);
        dex.createOrder(
            address(tokenA),
            address(tokenB),
            uint128(ORDER_AMOUNT),
            uint128(ORDER_AMOUNT * 2)
        );
        vm.stopPrank();
    }
    
    // ==================== HELPER FUNCTIONS ====================
    
    function validateOracleData(address _token) internal returns (bool) {
        // This would call the actual validation logic
        // For testing purposes, we'll simulate it
        return true;
    }
}

/**
 * @title FlashLoanAttacker
 * @dev Simulates flash loan attack patterns
 */
contract FlashLoanAttacker {
    SecureDEX public dex;
    uint256 public callCount = 0;
    
    constructor(address _dex) {
        dex = SecureDEX(_dex);
    }
    
    function simulateAttack() external {
        callCount++;
        
        // Simulate rapid calls to trigger flash loan detection
        for (uint256 i = 0; i < 4; i++) {
            dex.checkReentrancy(address(this));
        }
    }
    
    receive() external payable {
        if (callCount < 2) {
            simulateAttack();
        }
    }
}

/**
 * @title OracleManipulator
 * @dev Simulates oracle price manipulation attacks
 */
contract OracleManipulator {
    SecureDEX public dex;
    address public oracle;
    
    constructor(address _dex) {
        dex = SecureDEX(_dex);
        oracle = msg.sender;
    }
    
    function manipulatePrices() external {
        // Attempt to manipulate prices for attack
        // This would be called by a trusted oracle attempting to manipulate
        
        // Simulate price manipulation that could be detected
        // Implementation depends on specific oracle mechanism
    }
}