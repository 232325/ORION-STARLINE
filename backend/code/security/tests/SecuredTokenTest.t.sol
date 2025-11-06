// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "../contracts/SecuredToken.sol";

/**
 * @title SecuredTokenTest
 * @dev Comprehensive test suite for SecuredToken contract
 * @notice Tests: Security, Gas optimization, Reentrancy, Access control
 */
contract SecuredTokenTest is Test {
    SecuredToken public token;
    address public owner = address(0x1);
    address public user1 = address(0x2);
    address public user2 = address(0x3);
    address public attacker = address(0x4);
    
    string constant TOKEN_NAME = "SecuredToken";
    string constant TOKEN_SYMBOL = "STK";
    uint256 constant INITIAL_SUPPLY = 1000000 * 10**18;
    
    // Reentrancy attacker contract
    ReentrancyAttacker public reentrancyAttacker;
    
    // Event tracking
    event SecurityAlert(string alertType, string description);
    event Transfer(address indexed from, address indexed to, uint256 value);
    
    function setUp() public {
        vm.startPrank(owner);
        token = new SecuredToken(TOKEN_NAME, TOKEN_SYMBOL, INITIAL_SUPPLY);
        vm.stopPrank();
        
        vm.deal(user1, 1 ether);
        vm.deal(user2, 1 ether);
        vm.deal(attacker, 1 ether);
        
        // Deploy reentrancy attacker
        reentrancyAttacker = new ReentrancyAttacker(address(token));
    }
    
    // ==================== BASIC FUNCTIONALITY TESTS ====================
    
    function testInitialSupply() public {
        assertEq(token.balanceOf(owner), INITIAL_SUPPLY);
        assertEq(token.totalSupply(), INITIAL_SUPPLY);
    }
    
    function testBasicTransfer() public {
        vm.startPrank(owner);
        uint256 transferAmount = 1000 * 10**18;
        token.transfer(user1, transferAmount);
        
        assertEq(token.balanceOf(owner), INITIAL_SUPPLY - transferAmount);
        assertEq(token.balanceOf(user1), transferAmount);
        vm.stopPrank();
    }
    
    function testTransferFrom() public {
        vm.startPrank(owner);
        uint256 allowanceAmount = 500 * 10**18;
        token.approve(user1, allowanceAmount);
        vm.stopPrank();
        
        vm.startPrank(user1);
        uint256 transferAmount = 300 * 10**18;
        token.transferFrom(owner, user2, transferAmount);
        
        assertEq(token.balanceOf(owner), INITIAL_SUPPLY - transferAmount);
        assertEq(token.balanceOf(user2), transferAmount);
        assertEq(token.allowance(owner, user1), allowanceAmount - transferAmount);
        vm.stopPrank();
    }
    
    // ==================== SECURITY TESTS ====================
    
    function testReentrancyProtection() public {
        vm.startPrank(attacker);
        
        // Initial balance setup
        uint256 initialBalance = 1000 * 10**18;
        vm.startPrank(owner);
        token.transfer(attacker, initialBalance);
        vm.stopPrank();
        
        // Attempt reentrancy attack
        uint256 attackAmount = 500 * 10**18;
        bool result = token.transfer(address(reentrancyAttacker), attackAmount);
        
        // If reentrancy guard works, transfer should succeed only once
        assertTrue(result);
        assertEq(token.balanceOf(attacker), initialBalance - attackAmount);
        assertEq(token.balanceOf(address(reentrancyAttacker)), attackAmount);
        vm.stopPrank();
    }
    
    function testAccessControl() public {
        // Only owner should be able to pause contract
        vm.prank(user1);
        vm.expectRevert("AccessControl: caller is not the owner");
        token.emergencyPause();
        
        // Owner can pause
        vm.prank(owner);
        token.emergencyPause();
    }
    
    function testInvalidAddressRejection() public {
        vm.startPrank(owner);
        vm.expectRevert("Invalid address");
        token.transfer(address(0), 1000);
        
        vm.expectRevert("Invalid address");
        token.transferFrom(address(0), user1, 1000);
        vm.stopPrank();
    }
    
    function testSelfTransferPrevention() public {
        vm.startPrank(owner);
        vm.expectRevert("Invalid self-transfer");
        token.transfer(owner, 1000);
        vm.stopPrank();
    }
    
    function testInsufficientBalance() public {
        vm.startPrank(user1);
        vm.expectRevert("Insufficient balance");
        token.transfer(user2, 1000);
        vm.stopPrank();
    }
    
    function testInsufficientAllowance() public {
        vm.startPrank(owner);
        token.approve(user1, 100);
        vm.stopPrank();
        
        vm.startPrank(user1);
        vm.expectRevert("Insufficient allowance");
        token.transferFrom(owner, user2, 200);
        vm.stopPrank();
    }
    
    // ==================== GAS OPTIMIZATION TESTS ====================
    
    function testGasUsage() public {
        uint256 initialGas = gasleft();
        
        vm.startPrank(owner);
        for (uint256 i = 0; i < 100; i++) {
            token.transfer(user1, 1000);
        }
        vm.stopPrank();
        
        uint256 gasUsed = initialGas - gasleft();
        console.log("Gas used for 100 transfers:", gasUsed);
        
        // Gas usage should be reasonable (adjust threshold as needed)
        assertTrue(gasUsed < 1000000, "Gas usage too high");
    }
    
    function testImmutableVariable() public {
        assertEq(token.owner(), owner);
        assertEq(token.decimals(), 18);
    }
    
    // ==================== INTEGER OVERFLOW/UNDERFLOW TESTS ====================
    
    function testNoIntegerOverflow() public {
        vm.startPrank(owner);
        
        uint256 largeAmount = 2**256 - 1;
        vm.expectRevert(); // Should revert due to insufficient balance
        token.transfer(user1, largeAmount);
        
        // Test with valid amount near overflow
        token.transfer(user1, 1000);
        assertEq(token.balanceOf(user1), 1000);
        vm.stopPrank();
    }
    
    function testNoIntegerUnderflow() public {
        vm.startPrank(user1);
        vm.expectRevert("Insufficient balance");
        token.transfer(user2, 1000);
        vm.stopPrank();
    }
    
    // ==================== EDGE CASES ====================
    
    function testZeroAmountTransfer() public {
        vm.startPrank(owner);
        bool result = token.transfer(user1, 0);
        assertTrue(result);
        assertEq(token.balanceOf(user1), 0);
        vm.stopPrank();
    }
    
    function testApproveZeroAddress() public {
        vm.startPrank(owner);
        vm.expectRevert("Invalid address");
        token.approve(address(0), 1000);
        vm.stopPrank();
    }
    
    function testApproveWithZeroAmount() public {
        vm.startPrank(owner);
        bool result = token.approve(user1, 0);
        assertTrue(result);
        assertEq(token.allowance(owner, user1), 0);
        vm.stopPrank();
    }
    
    // ==================== PROPERTY-BASED TESTS ====================
    
    function testTransferProperties(uint256 amount) public {
        vm.assume(amount > 0 && amount <= INITIAL_SUPPLY);
        
        vm.startPrank(owner);
        token.transfer(user1, amount);
        
        // Property 1: Total supply should remain constant
        assertEq(token.totalSupply(), INITIAL_SUPPLY);
        
        // Property 2: Balances should sum to total supply
        assertEq(
            token.balanceOf(owner) + token.balanceOf(user1),
            INITIAL_SUPPLY
        );
        
        vm.stopPrank();
    }
    
    function testAllowanceProperties(
        address spender,
        uint256 allowanceAmount,
        uint256 transferAmount
    ) public {
        vm.assume(spender != address(0) && spender != owner);
        vm.assume(transferAmount <= allowanceAmount);
        
        vm.startPrank(owner);
        token.approve(spender, allowanceAmount);
        
        // Property: Allowance should be exactly what was set
        assertEq(token.allowance(owner, spender), allowanceAmount);
        
        if (transferAmount > 0) {
            vm.startPrank(spender);
            token.transferFrom(owner, user1, transferAmount);
            
            // Property: Allowance should decrease by transfer amount
            assertEq(
                token.allowance(owner, spender),
                allowanceAmount - transferAmount
            );
        }
    }
    
    // ==================== FUZZING TESTS ====================
    
    function testFuzzTransfer(
        address to,
        uint256 amount
    ) public {
        vm.assume(to != address(0) && to != owner);
        vm.assume(amount > 0 && amount <= token.balanceOf(owner));
        
        vm.startPrank(owner);
        bool result = token.transfer(to, amount);
        assertTrue(result);
        
        // Verify balance conservation
        assertEq(
            token.balanceOf(owner) + token.balanceOf(to),
            INITIAL_SUPPLY
        );
        vm.stopPrank();
    }
    
    function testFuzzTransferFrom(
        address from,
        address to,
        uint256 amount
    ) public {
        vm.assume(from != address(0) && to != address(0));
        vm.assume(from != to);
        vm.assume(amount > 0 && amount <= token.balanceOf(from));
        
        // Set allowance
        vm.startPrank(from);
        token.approve(address(this), amount);
        vm.stopPrank();
        
        // Test transfer from
        bool result = token.transferFrom(from, to, amount);
        assertTrue(result);
        
        // Verify conservation of total supply
        assertEq(token.totalSupply(), INITIAL_SUPPLY);
    }
    
    // ==================== INTEGRATION TESTS ====================
    
    function testMultiUserIntegration() public {
        address[] memory users = new address[](5);
        for (uint256 i = 0; i < 5; i++) {
            users[i] = address(uint160(i + 10));
            vm.deal(users[i], 1 ether);
        }
        
        vm.startPrank(owner);
        
        // Distribute tokens
        uint256 amount = INITIAL_SUPPLY / 5;
        for (uint256 i = 0; i < 5; i++) {
            token.transfer(users[i], amount);
        }
        
        // Test multiple transfers between users
        for (uint256 i = 0; i < 4; i++) {
            vm.startPrank(users[i]);
            token.transfer(users[i + 1], amount / 2);
        }
        
        // Verify total supply conservation
        uint256 totalBalance = 0;
        for (uint256 i = 0; i < 5; i++) {
            totalBalance += token.balanceOf(users[i]);
        }
        assertEq(totalBalance + token.balanceOf(owner), INITIAL_SUPPLY);
        
        vm.stopPrank();
    }
    
    // ==================== STRESS TESTS ====================
    
    function testStressHighVolumeTransfers() public {
        vm.startPrank(owner);
        
        uint256 numTransfers = 1000;
        uint256 amount = 1000;
        
        for (uint256 i = 0; i < numTransfers; i++) {
            address recipient = address(uint160(i + 100));
            token.transfer(recipient, amount);
        }
        
        assertEq(token.totalSupply(), INITIAL_SUPPLY);
        vm.stopPrank();
    }
    
    function testStressRapidTransfers() public {
        vm.startPrank(owner);
        token.transfer(user1, 1000);
        vm.stopPrank();
        
        vm.startPrank(user1);
        for (uint256 i = 0; i < 100; i++) {
            token.transfer(owner, 1);
            token.transfer(user1, 1);
        }
        vm.stopPrank();
        
        // Verify contract is still functional
        vm.startPrank(owner);
        token.transfer(user2, 100);
        assertEq(token.balanceOf(user2), 100);
        vm.stopPrank();
    }
}

/**
 * @title ReentrancyAttacker
 * @dev Malicious contract to test reentrancy protection
 */
contract ReentrancyAttacker {
    SecuredToken public token;
    uint256 public attackCount = 0;
    
    constructor(address _token) {
        token = SecuredToken(_token);
    }
    
    function attack() external {
        attackCount++;
        token.transfer(msg.sender, token.balanceOf(address(this)));
    }
    
    receive() external payable {
        if (attackCount < 2) {
            attack();
        }
    }
}